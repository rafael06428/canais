"""Render one vertical Short (1080x1920) with its own looping narration.

usage: python3 render_short.py <short_dir> <label> <footer>
  needs short_dir/{voice.json, music.wav, img/NNN.jpg(+npy)} — one image per narration block
  writes short_dir/short.mp4
The last block's image is the first block's image, and the narration's last sentence
is completed by the first one, so the Short loops seamlessly.
"""
import json, math, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 24
SD, LABEL, FOOT = sys.argv[1], sys.argv[2], sys.argv[3]
V = json.load(open(f"{SD}/voice.json")); DUR = V["dur"]; B = V["blocks"]; N = len(B)
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FC = ImageFont.truetype(FB, 86); FL = ImageFont.truetype(FB, 54); FSm = ImageFont.truetype(FB, 36)
starts = [0.0] + [B[i][0] - 0.12 for i in range(1, N)]; ends = starts[1:] + [DUR]
XG, YG = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
XC, YC = XG - W / 2, YG - H / 2
cache = {}


def load(i):
    if i not in cache:
        im = cv2.imread(f"{SD}/img/{i:03d}.jpg"); s = max(W * 1.12 / im.shape[1], H * 1.12 / im.shape[0])
        im = cv2.resize(im, (int(im.shape[1] * s) + 1, int(im.shape[0] * s) + 1), interpolation=cv2.INTER_LANCZOS4)
        try:
            d = np.load(f"{SD}/img/{i:03d}.npy").astype(np.float32)
            d = cv2.resize(d, (im.shape[1], im.shape[0])) - 0.5
        except Exception:
            d = np.zeros(im.shape[:2], np.float32)
        y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
        cache[i] = (im, np.ascontiguousarray(d[y0:y0 + H, x0:x0 + W]))
    return cache[i]


def shot(i, T):
    im, dc = load(i); u = max(0.0, min(1.0, (T - starts[i]) / max(0.1, ends[i] - starts[i])))
    # first and last block share the same image: last zooms out to where the first starts
    z = 1.08 - 0.08 * u if i == N - 1 else (1.0 + 0.08 * u if i % 2 == 0 else 1.08 - 0.08 * u)
    k = (u - 0.5) * 2 * (0 if i in (0, N - 1) else (1 if i % 2 else -1))
    px = k * 22.0
    mx = im.shape[1] / 2 + XC / z + k * 26 - px * dc * 2
    my = im.shape[0] / 2 + YC / z
    return cv2.remap(im, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.5 * np.clip(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1) ** 1.5)[..., None]
SHADE = np.clip((yy - H * 0.55) / (H * 0.35), 0, 1)[..., None] * 0.55
rg = np.random.default_rng(5); GR = [rg.normal(0, 4, (H, W, 1)).astype(np.float32) for _ in range(4)]
words = V["words"]
chunks, cur = [], []
for k, w in enumerate(words):
    cur.append(w)
    nxt = words[k + 1] if k + 1 < len(words) else None
    if len(cur) == 3 or w[0][-1] in ".,?!:;…" or nxt is None or nxt[3] != w[3]:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)


def frame(T):
    i = max(k for k in range(N) if starts[k] <= T) if T > 0 else 0
    a = shot(i, T)
    if i > 0 and T - starts[i] < 0.35:
        w = (T - starts[i]) / 0.35; a = a * w + shot(i - 1, T) * (1 - w)
    a = a * VIG * (1 - SHADE) + GR[int(T * FPS) % 4]
    im = Image.fromarray(cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(im)
    tw = d.textlength(LABEL, font=FL)
    d.rounded_rectangle([W / 2 - tw / 2 - 30, 170, W / 2 + tw / 2 + 30, 270], 20, fill=(150, 0, 0)); d.text((W / 2, 220), LABEL, font=FL, fill=(255, 255, 255), anchor="mm")
    f = FSm
    while d.textlength(FOOT, font=f) > W - 80: f = ImageFont.truetype(FB, f.size - 2)
    d.text((W / 2, 1700), FOOT, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    for c in chunks:
        if c[0][1] - 0.05 <= T < c[-1][2] + 0.1:
            line = " ".join(w[0] for w in c).upper(); f = FC
            while d.textlength(line, font=f) > W - 110: f = ImageFont.truetype(FB, f.size - 6)
            x = W / 2 - d.textlength(line, font=f) / 2
            for w in c:
                s = w[0].upper()
                if w[1] <= T + 0.03:
                    d.text((x, 1340), s, font=f, fill=(255, 214, 10) if T < w[2] else (255, 255, 255), anchor="lm", stroke_width=9, stroke_fill=(0, 0, 0))
                x += d.textlength(s + " ", font=f)
            break
    return im


if __name__ == "__main__":
    if len(sys.argv) > 4:
        ts = [starts[i] + 0.8 for i in range(N)]
        sheet = Image.new("RGB", (270 * len(ts), 480))
        for j, T in enumerate(ts): sheet.paste(frame(T).resize((270, 480)), (j * 270, 0))
        sheet.save(f"{SD}/preview.jpg", quality=85); sys.exit()
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{SD}/music.wav",
                            "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{SD}/short.mp4"], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)):
        enc.stdin.write(frame(f / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("short done", SD, round(DUR, 1))
