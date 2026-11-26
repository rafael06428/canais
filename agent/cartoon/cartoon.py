"""Cartoon-style episode builder (long video + Shorts + subtitles + thumbnail), no AI images.

usage: python3 cartoon.py <episode_dir> [step]
  steps (each skipped when its output exists; pass a name to force only that step):
  voice, audio, srt, data, shots, long, thumb, shorts
episode.json is the same as for make.py, but each scene has a "v" object (see README.md in this folder)
instead of an image prompt, and each Short block has "src" (index of a long scene to show) and optional "fx".
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); AG = os.path.dirname(HERE)
ED = os.path.abspath(sys.argv[1]); ONLY = sys.argv[2] if len(sys.argv) > 2 else None
EP = json.load(open(f"{ED}/episode.json"))
SCENES = [s for c in EP["chapters"] for s in c["scenes"]]
VOICE = EP.get("voice", "en-US-AndrewMultilingualNeural")
WORKERS = int(os.environ.get("WORKERS", 3)); FPS = 30


def run(*a, **k):
    print("$", " ".join(map(str, a))[:200], flush=True); subprocess.run(list(map(str, a)), check=True, **k)


def step(name, out):
    if ONLY: return ONLY == name
    return not os.path.exists(out)


# 1. narration (a 3.2 s pause before the title card)
if step("voice", f"{ED}/voice.json"):
    tc = EP.get("title_card", {}).get("after_scene", -1)
    blocks = [{"text": s["text"], **({"gap": 3.2} if i == tc - 1 else {})} for i, s in enumerate(SCENES)]
    json.dump({"voice": VOICE, "rate": EP.get("rate", "+0%"), "blocks": blocks}, open(f"{ED}/voice_in.json", "w"))
    run(sys.executable, f"{AG}/voice.py", f"{ED}/voice_in.json", f"{ED}/voice")

# 2. music bed + whooshes (make.py's audio step)
if step("audio", f"{ED}/music.wav"):
    run(sys.executable, f"{AG}/make.py", ED, "audio")

# 3. subtitles
if step("srt", f"{ED}/subs.srt"):
    run(sys.executable, f"{AG}/make.py", ED, "srt")

# 4. Short narrations + data.js for the page
if step("data", f"{ED}/cartoon/data.js"):
    os.makedirs(f"{ED}/cartoon", exist_ok=True)
    for f in ("engine.js", "page.html", "render.cjs"): shutil.copy(f"{HERE}/{f}", f"{ED}/cartoon/{f}")
    SV = []
    for k, sh in enumerate(EP["shorts"]):
        SD = f"{ED}/shorts/{k}"; os.makedirs(SD, exist_ok=True)
        if not os.path.exists(f"{SD}/voice.json"):
            json.dump({"voice": VOICE, "rate": sh.get("rate", "+4%"), "lead": 0.05, "gap": 0.28, "tail": 0.12,
                       "blocks": [{"text": b["text"]} for b in sh["blocks"]]}, open(f"{SD}/voice_in.json", "w"))
            run(sys.executable, f"{AG}/voice.py", f"{SD}/voice_in.json", f"{SD}/voice")
        if not os.path.exists(f"{SD}/music.wav"):
            run(sys.executable, "-c", f"import sys; sys.path.insert(0, {AG!r}); import audio; audio.mix({SD + '/voice.wav'!r}, None, {SD + '/music.wav'!r}, [], tail=0.0, fade=False)")
        SV.append(json.load(open(f"{SD}/voice.json")))
    with open(f"{ED}/cartoon/data.js", "w") as f:
        f.write("window.EP=" + json.dumps(EP) + ";\nwindow.VOICE=" + json.dumps(json.load(open(f"{ED}/voice.json"))) + ";\nwindow.SHORTV=" + json.dumps(SV) + ";\n")
    for f in ("engine.js", "page.html", "render.cjs"): shutil.copy(f"{HERE}/{f}", f"{ED}/cartoon/{f}")

# 5. key frames for review: the middle of every scene, 12 per contact sheet
if ONLY == "shots":
    V = json.load(open(f"{ED}/voice.json")); B = V["blocks"]
    ts = [round((B[i][0] + B[i][1]) / 2 + 0.6, 2) for i in range(len(B))]
    shutil.rmtree(f"{ED}/shots", ignore_errors=True)
    run("node", f"{ED}/cartoon/render.cjs", ED, "shots", f"{ED}/shots", *ts)
    fs = sorted(os.listdir(f"{ED}/shots"))
    for g in range(0, len(fs), 12):
        from PIL import Image, ImageDraw, ImageFont
        S = Image.new("RGB", (480 * 3, 270 * 4)); F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        for j, f in enumerate(fs[g:g + 12]):
            im = Image.open(f"{ED}/shots/{f}").resize((480, 270)); ImageDraw.Draw(im).text((6, 4), str(g + j), font=F, fill=(255, 255, 0), stroke_width=3, stroke_fill=(0, 0, 0))
            S.paste(im, ((j % 3) * 480, (j // 3) * 270))
        S.save(f"{ED}/shots/sheet_{g // 12:02d}.jpg", quality=82)

# 6. long video: WORKERS parallel chunks, concat, mux with music.wav
if step("long", f"{ED}/long.mp4"):
    V = json.load(open(f"{ED}/voice.json")); N = int(V["dur"] * FPS) + 1
    cuts = [N * i // WORKERS for i in range(WORKERS + 1)]
    procs = [subprocess.Popen(["node", f"{ED}/cartoon/render.cjs", ED, "long", str(cuts[i]), str(cuts[i + 1]), f"{ED}/part{i}.mp4"]) for i in range(WORKERS)]
    if any(p.wait() for p in procs): raise SystemExit("render failed")
    open(f"{ED}/parts_c.txt", "w").write("".join(f"file '{ED}/part{i}.mp4'\n" for i in range(WORKERS)))
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{ED}/parts_c.txt", "-i", f"{ED}/music.wav",
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{ED}/long.mp4")

# 7. thumbnail 1280x720
if step("thumb", f"{ED}/thumb.jpg"):
    run("node", f"{ED}/cartoon/render.cjs", ED, "thumb", f"{ED}/thumb.jpg")

# 8. Shorts (1080x1920), looping narration
if step("shorts", f"{ED}/shorts/done"):
    for k, sh in enumerate(EP["shorts"]):
        SD = f"{ED}/shorts/{k}"
        if os.path.exists(f"{SD}/short.mp4"): continue
        V = json.load(open(f"{SD}/voice.json")); N = int(V["dur"] * FPS)
        run("node", f"{ED}/cartoon/render.cjs", ED, "short", k, 0, N, f"{SD}/video.mp4")
        run("ffmpeg", "-y", "-loglevel", "error", "-i", f"{SD}/video.mp4", "-i", f"{SD}/music.wav", "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{SD}/short.mp4")
    open(f"{ED}/shorts/done", "w").write("ok")

print("cartoon episode ready:", ED)
