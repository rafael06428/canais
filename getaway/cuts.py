"""Cortes verticais (Shorts 1080x1920) a partir do vídeo longo do The Getaway Case.

usage: python3 cuts.py <ep_dir>
  ep_dir precisa ter: long.mp4 (16:9), mix.wav (áudio final do longo), voice.json (tempos por palavra,
  formato do getaway/voice.py), cuts.json:
  [{"slug": "records", "hook": ["LINE ONE", "LINE *TWO*"], "segments": [[t0, t1], ...]}, ...]
  (palavras entre *asteriscos* no hook saem em laranja)
Gera ep_dir/cuts/<slug>.mp4 (H.264, ~3 MB) e ep_dir/cuts/<slug>.jpg (quadro de conferência).
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ED = os.path.abspath(sys.argv[1])
W, H = 1080, 1920
VY = 640                      # topo do vídeo 16:9 (1080x608)
ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
BG = (6, 19, 31); ICE = (230, 241, 246); OR = (255, 107, 61); SUB = (157, 188, 205)


def run(*a):
    subprocess.run(a, check=True)


def background(path, hook):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # grade leve
    for x in range(0, W, 80): d.line([(x, 0), (x, H)], fill=(12, 30, 44))
    for y in range(0, H, 80): d.line([(0, y), (W, y)], fill=(12, 30, 44))
    # marca
    fb = ImageFont.truetype(ANTON, 46)
    d.text((70, 90), "THE GETAWAY", font=fb, fill=ICE)
    tw = d.textlength("THE GETAWAY ", font=fb); d.text((70 + tw, 90), "CASE", font=fb, fill=OR)
    # gancho (2-3 linhas), *palavra* em laranja
    fh = ImageFont.truetype(ANTON, 96); y = 220
    for line in hook:
        parts = line.split("*"); x = 70
        tot = sum(d.textlength(p, font=fh) for p in parts)
        if tot > W - 140:   # reduz se não couber
            f2 = ImageFont.truetype(ANTON, int(96 * (W - 140) / tot)); fh_line = f2
        else:
            fh_line = fh
        for i, p in enumerate(parts):
            d.text((x, y), p, font=fh_line, fill=OR if i % 2 else ICE); x += d.textlength(p, font=fh_line)
        y += int(fh_line.size * 1.18)
    d.rectangle([70, y + 14, 290, y + 26], fill=OR)
    # moldura do vídeo
    d.rectangle([0, VY - 4, W, VY + 608 + 4], fill=(27, 52, 71))
    # rodapé
    fs = ImageFont.truetype(INTER, 34)
    t = "Full story on the channel"
    d.text(((W - d.textlength(t, font=fs)) / 2, H - 190), t, font=fs, fill=SUB)
    im.save(path)


def ass_time(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def captions(path, words):
    """Legenda palavra por palavra, em blocos de até 3 palavras; a palavra falada em laranja."""
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Anton,96,&H00F6F1E6,&H00F6F1E6,&H001F1306,&H64000000,0,0,0,0,100,100,1,0,1,6,2,8,60,60,1360,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    chunks, cur = [], []
    for w in words:
        if " " in w["w"].strip():          # token longo (datas/números): bloco próprio
            if cur: chunks.append(cur); cur = []
            chunks.append([w]); continue
        cur.append(w)
        if len(cur) == 3 or w["w"].rstrip().endswith((".", "?", "!", ":")):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    lines = []
    for ch in chunks:
        for i, w in enumerate(ch):
            t0 = w["t"]; t1 = ch[i + 1]["t"] if i + 1 < len(ch) else w["t"] + max(w["d"], 0.25) + 0.15
            txt = " ".join(("{\\c&H3D6BFF&}" + x["w"].upper() + "{\\c&HF6F1E6&}") if j == i else x["w"].upper() for j, x in enumerate(ch))
            lines.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t1)},Cap,,0,0,0,,{txt}")
    open(path, "w").write(head + "\n".join(lines) + "\n")


def main():
    V = json.load(open(f"{ED}/voice.json"))
    allw = [w for b in V["blocks"] for w in b["words"]]
    cuts = json.load(open(f"{ED}/cuts.json"))
    os.makedirs(f"{ED}/cuts", exist_ok=True)
    for c in cuts:
        slug = c["slug"]; tmp = f"{ED}/cuts/_{slug}"; os.makedirs(tmp, exist_ok=True)
        # 1) junta os trechos (vídeo + áudio) num 16:9 só
        parts = []
        for k, (a, b) in enumerate(c["segments"]):
            p = f"{tmp}/seg{k}.mp4"
            run("ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f"{ED}/long.mp4", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f"{ED}/mix.wav",
                "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", p)
            parts.append(p)
        open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
        run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-c", "copy", f"{tmp}/joined.mp4")
        # 2) palavras do corte, já no tempo do corte
        ws, off = [], 0.0
        for a, b in c["segments"]:
            for w in allw:
                if a - 0.05 <= w["t"] < b - 0.1:
                    ws.append({"w": w["w"], "t": w["t"] - a + off, "d": w["d"]})
            off += b - a
        captions(f"{tmp}/cap.ass", ws)
        background(f"{tmp}/bg.png", c["hook"])
        # 3) monta o vertical
        fc = (f"[1:v]scale=1080:608,setsar=1[v];[0:v][v]overlay=0:{VY}:shortest=1,"
              f"ass={tmp}/cap.ass:fontsdir=/usr/share/fonts/truetype/google-fonts/ofl/anton[o]")
        out = f"{ED}/cuts/{slug}.mp4"
        run("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", f"{tmp}/bg.png", "-i", f"{tmp}/joined.mp4",
            "-filter_complex", fc, "-map", "[o]", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-maxrate", "1100k", "-bufsize", "2200k",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out)
        mid = off * 0.45
        run("ffmpeg", "-y", "-loglevel", "error", "-ss", f"{mid:.2f}", "-i", out, "-frames:v", "1", f"{ED}/cuts/{slug}.jpg")
        size = os.path.getsize(out) / 1e6
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).decode())
        print(f"{slug}: {dur:.1f}s {size:.2f} MB")


main()
