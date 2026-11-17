"""Build a full episode (long video + Shorts + subtitles + thumbnail) from episode.json.

usage: python3 make.py <episode_dir> [step]
  steps run in order and are skipped when their output already exists:
  voice, images, audio, preview, long, srt, thumb, shorts
  Pass a step name to run only that step.
"""
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.abspath(sys.argv[1]); ONLY = sys.argv[2] if len(sys.argv) > 2 else None
EP = json.load(open(f"{ED}/episode.json"))
SCENES = [s for c in EP["chapters"] for s in c["scenes"]]
VOICE = EP.get("voice", "en-US-AndrewMultilingualNeural")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(*a):
    print("$", " ".join(a), flush=True); subprocess.run(a, check=True)


def step(name, out):
    if ONLY: return ONLY == name
    return not os.path.exists(out)


def py(script, *a): run(sys.executable, os.path.join(HERE, script), *a)


# 1. narration
if step("voice", f"{ED}/voice.json"):
    json.dump({"voice": VOICE, "rate": EP.get("rate", "+0%"), "blocks": [{"text": s["text"]} for s in SCENES]}, open(f"{ED}/voice_in.json", "w"))
    py("voice.py", f"{ED}/voice_in.json", f"{ED}/voice")

# 2. images
if step("images", f"{ED}/img/{len(SCENES) - 1:03d}.npy"):
    json.dump([s["prompt"] for s in SCENES], open(f"{ED}/prompts.json", "w"))
    py("images.py", f"{ED}/prompts.json", f"{ED}/img")

# 3. music bed + whooshes at chapter changes
if step("audio", f"{ED}/music.wav"):
    V = json.load(open(f"{ED}/voice.json")); marks = []; k = 0
    for ci, c in enumerate(EP["chapters"]):
        if ci > 0: marks.append(V["blocks"][k][0])
        k += len(c["scenes"])
    json.dump(marks, open(f"{ED}/marks.json", "w"))
    py("audio.py", f"{ED}/voice.wav", f"{ED}/voice.json", f"{ED}/music.wav", f"{ED}/marks.json")

# 4. contact sheet to check the look before the long render
if step("preview", f"{ED}/preview_long.jpg"):
    py("render_long.py", ED, "preview")

# 5. long video
if step("long", f"{ED}/long.mp4"):
    py("render_long.py", ED)

# 6. subtitles (SRT) from word timings
if step("srt", f"{ED}/subs.srt"):
    V = json.load(open(f"{ED}/voice.json")); cues = []; cur = []
    for k, w in enumerate(V["words"]):
        cur.append(w); nxt = V["words"][k + 1] if k + 1 < len(V["words"]) else None
        txt = " ".join(x[0] for x in cur)
        if nxt is None or len(cur) >= 8 or len(txt) > 42 or w[0][-1] in ".?!" or nxt[3] != w[3] or nxt[1] - w[2] > 0.6:
            cues.append((cur[0][1], cur[-1][2] + 0.15, txt)); cur = []
    ts = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}"
    with open(f"{ED}/subs.srt", "w") as f:
        for n, (a, b, t) in enumerate(cues, 1):
            b = min(b, cues[n][0] - 0.01) if n < len(cues) else b
            f.write(f"{n}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
    print("srt", len(cues), "cues")

# 7. thumbnail 1280x720
if step("thumb", f"{ED}/thumb.jpg"):
    im = Image.open(f"{ED}/img/{EP.get('thumb_scene', 0):03d}.jpg").convert("RGB").resize((1280, 731)).crop((0, 5, 1280, 725))
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.25)).enhance(1.15)
    import numpy as np
    g = np.clip(1 - np.arange(1280) / 760, 0, 1) ** 1.3 * 0.62
    im = Image.fromarray((np.asarray(im).astype(np.float32) * (1 - g[None, :, None])).astype("uint8"))
    d = ImageDraw.Draw(im, "RGBA")
    lines = EP.get("thumb_text", EP["title"]).upper().split("\n")
    y = 360 - len(lines) * 70
    for k, line in enumerate(lines):
        f = ImageFont.truetype(FB, 120)
        while d.textlength(line, font=f) > 600: f = ImageFont.truetype(FB, f.size - 4)
        d.text((50, y), line, font=f, fill=(255, 214, 10) if k == 0 else (255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
        y += f.size + 20
    d.rectangle([50, y + 10, 330, y + 22], fill=(200, 30, 30))
    im.save(f"{ED}/thumb.jpg", quality=90)

# 8. Shorts with their own looping narration
if step("shorts", f"{ED}/shorts/done"):
    for k, sh in enumerate(EP["shorts"]):
        SD = f"{ED}/shorts/{k}"; os.makedirs(f"{SD}/img", exist_ok=True)
        if os.path.exists(f"{SD}/short.mp4"): continue
        blocks = sh["blocks"]
        json.dump({"voice": VOICE, "rate": sh.get("rate", "+4%"), "lead": 0.05, "gap": 0.28, "tail": 0.12,
                   "blocks": [{"text": b["text"]} for b in blocks]}, open(f"{SD}/voice_in.json", "w"))
        py("voice.py", f"{SD}/voice_in.json", f"{SD}/voice")
        json.dump([b["prompt"] for b in blocks[:-1]], open(f"{SD}/prompts.json", "w"))
        py("images.py", f"{SD}/prompts.json", f"{SD}/img", "768x1344")
        last = len(blocks) - 1
        shutil.copy(f"{SD}/img/000.jpg", f"{SD}/img/{last:03d}.jpg"); shutil.copy(f"{SD}/img/000.npy", f"{SD}/img/{last:03d}.npy")
        run(sys.executable, "-c", f"import sys; sys.path.insert(0, {HERE!r}); import audio; audio.mix({SD + '/voice.wav'!r}, None, {SD + '/music.wav'!r}, [], tail=0.0, fade=False)")
        run(sys.executable, os.path.join(HERE, "render_short.py"), SD, sh["label"], sh.get("footer", f"Full story: {EP['title']}"))
    open(f"{ED}/shorts/done", "w").write("ok")

print("episode ready:", ED)
