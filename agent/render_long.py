"""Render the long 16:9 video: depth parallax, Ken Burns, particles/fog/fire flicker, chapter titles.

usage: python3 render_long.py <episode_dir>
  needs episode_dir/{episode.json, voice.json, img/NNN.jpg+npy, music.wav}
  writes episode_dir/long.mp4
"""
import json, math, os, subprocess, sys
from multiprocessing import Process
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 24
SC = float(__import__("os").environ.get("ZOOM_MARGIN", 1.08))   # was 1.14: less zoom = less upscaling blur
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FT = ImageFont.truetype(FB, 64); FS = ImageFont.truetype(FB, 34); FBIG = ImageFont.truetype(FB, 104)
ED = sys.argv[1]
EP = json.load(open(f"{ED}/episode.json")); V = json.load(open(f"{ED}/voice.json"))
SCENES = [s for c in EP["chapters"] for s in c["scenes"]]
CHAP = [ci for ci, c in enumerate(EP["chapters"]) for _ in c["scenes"]]
NS = len(SCENES); DUR = V["dur"]
import os as _os
if _os.environ.get("RENDER_UNTIL"): DUR = min(DUR, float(_os.environ["RENDER_UNTIL"]))   # partial preview render
B = V["blocks"]
starts = [0.0] + [B[i][0] - 0.2 for i in range(1, NS)]
ends = starts[1:] + [DUR]
CH_T = {}
for i in range(NS):
    if CHAP[i] not in CH_T: CH_T[CHAP[i]] = starts[i]
XG, YG = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
XC, YC = XG - W / 2, YG - H / 2
cache = {}


def load(i):
    if i not in cache:
        if len(cache) > 4: cache.pop(next(iter(cache)))
        im = cv2.imread(f"{ED}/img/{i:03d}.jpg")
        s = max(W * SC / im.shape[1], H * SC / im.shape[0])
        im = cv2.resize(im, (int(im.shape[1] * s) + 1, int(im.shape[0] * s) + 1), interpolation=cv2.INTER_LANCZOS4)
        d = np.load(f"{ED}/img/{i:03d}.npy").astype(np.float32)
        d = cv2.resize(d, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_CUBIC)
        y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
        dc = np.ascontiguousarray(d[y0:y0 + H, x0:x0 + W]) - 0.5
        c = im[y0:y0 + H, x0:x0 + W].astype(np.float32)
        b, r = c[..., 0], c[..., 2]
        fire = cv2.GaussianBlur(np.clip((r - 150) / 80, 0, 1) * np.clip((r - b * 1.6) / 60, 0, 1), (0, 0), 14)
        cache[i] = (im, dc, fire)
    return cache[i]


ez = lambda x: (lambda v: v * v * (3 - 2 * v))(max(0.0, min(1.0, x)))


CLIPS = {}
ZERO = None


def clip_frame(i, T):
    """Animated scene: frames of ED/clips/NNN.mp4 (5 s, generated on a GPU), slowed down to at most 0.6x, then held."""
    global ZERO
    if i not in CLIPS:
        if len(CLIPS) > 1: CLIPS.pop(next(iter(CLIPS)))
        cap = cv2.VideoCapture(f"{ED}/clips/{i:03d}.mp4"); fr = []
        while True:
            ok, f = cap.read()
            if not ok: break
            s = max(W / f.shape[1], H / f.shape[0])
            f = cv2.resize(f, (int(f.shape[1] * s) + 1, int(f.shape[0] * s) + 1), interpolation=cv2.INTER_LANCZOS4)
            y0, x0 = (f.shape[0] - H) // 2, (f.shape[1] - W) // 2
            fr.append(np.ascontiguousarray(f[y0:y0 + H, x0:x0 + W]))
        CLIPS[i] = fr
    fr = CLIPS[i]; d = max(0.1, ends[i] - starts[i]); n = len(fr)
    speed = 1.0 if d <= n / 24 else max(0.6, (n / 24) / d)
    x = min(n - 1.001, max(0.0, (T - starts[i]) * 24 * speed)); a = int(x); w = x - a
    out = fr[a].astype(np.float32) * (1 - w) + fr[a + 1].astype(np.float32) * w
    if ZERO is None: ZERO = np.zeros((H, W), np.float32)
    return out, ZERO


def scene(i, T):
    if os.path.exists(f"{ED}/clips/{i:03d}.mp4"): return clip_frame(i, T)
    im, dc, fire = load(i); u = max(0.0, min(1.0, (T - starts[i]) / max(0.1, ends[i] - starts[i])))
    z = 1.0 + 0.07 * u if i % 2 == 0 else 1.07 - 0.07 * u
    dirs = [(1, 0), (-1, 0), (0.6, 0.5), (-0.6, -0.5), (1, 0.3), (-1, 0.3)]
    ddx, ddy = dirs[i % 6]; k = (u - 0.5) * 2
    if i == 0: ddx = ddy = 0
    px, py = ddx * k * 26.0, ddy * k * 14.0
    pan = (ddx * k * 30.0, ddy * k * 16.0)
    amp = SCENES[i].get("shake", 0) * 3
    sx = amp * (math.sin(T * 41.0) * 0.6 + math.sin(T * 67.3 + 1) * 0.4)
    sy = amp * (math.sin(T * 53.1 + 2) * 0.6 + math.sin(T * 79.7) * 0.4)
    icx, icy = im.shape[1] / 2, im.shape[0] / 2
    mx = icx + XC / z + pan[0] + sx - px * dc * 2
    my = icy + YC / z + pan[1] + sy - py * dc * 2
    out = cv2.remap(im, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    if SCENES[i].get("fx") == "fire":
        fl = 0.5 * math.sin(T * 9.1) + 0.3 * math.sin(T * 15.7 + 1) + 0.2 * math.sin(T * 23.3 + 2)
        out += (fire * (fl * 34))[..., None] * np.array([0.3, 0.6, 1.0], np.float32)
    return out, dc


def fbm(w, h, seed):
    rng = np.random.default_rng(seed); o = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for oc in range(5):
        g = rng.random((max(2, 3 * 2 ** oc), max(2, 5 * 2 ** oc))).astype(np.float32)
        o += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC); tot += amp; amp *= 0.55
    return o / tot


FW, FH = 960, 270
FOG = np.tile(fbm(FW, FH, 1), (1, 2))


def fog(T):
    a = int((T * 26) % FW)
    return cv2.resize(np.clip((FOG[:, a:a + 480] - 0.42) * 2.6, 0, 1), (W, H))


QW, QH = 480, 270
rng = np.random.default_rng(11)
P = {k: dict(x=rng.random(n) * QW, y=rng.random(n) * QH, s=0.6 + rng.random(n) * 0.8, p=rng.random(n) * 6.28, b=0.4 + rng.random(n) * 0.6)
     for k, n in (("emb", 140), ("ash", 650), ("dust", 90), ("snow", 400), ("rain", 260))}


def particles(T, kind):
    L = np.zeros((QH, QW, 3), np.float32)
    def put(x, y, col, b):
        np.add.at(L, (np.clip(y.astype(np.int32), 0, QH - 1), np.clip(x.astype(np.int32), 0, QW - 1)), b[:, None] * np.array(col, np.float32))
    if kind == "fire":
        e = P["emb"]; put((e["x"] + np.sin(T * 1.3 + e["p"]) * 9 + T * 7) % QW, (e["y"] - T * 26 * e["s"]) % QH, (40, 130, 255), e["b"] * (0.6 + 0.4 * np.sin(T * 6 + e["p"])) * 1.2)
        e = P["ash"]; n = 250; put(((e["x"] + T * 9 * e["s"]) % QW)[:n], ((e["y"] + T * 20 * e["s"]) % QH)[:n], (150, 150, 150), e["b"][:n] * 0.5)
    elif kind == "ash":
        e = P["ash"]; put((e["x"] + np.sin(T * 0.9 + e["p"]) * 6 + T * 9 * e["s"]) % QW, (e["y"] + T * 20 * e["s"]) % QH, (150, 150, 150), e["b"] * 0.55)
    elif kind == "snow":
        e = P["snow"]; put((e["x"] + np.sin(T * 0.7 + e["p"]) * 10 + T * 6) % QW, (e["y"] + T * 14 * e["s"]) % QH, (235, 235, 235), e["b"] * 0.7)
    elif kind == "dust":
        e = P["dust"]; put((e["x"] + T * 3 * e["s"]) % QW, (e["y"] + np.sin(T * 0.5 + e["p"]) * 5 - T * 2) % QH, (120, 170, 200), e["b"] * 0.35 * (0.5 + 0.5 * np.sin(T * 1.7 + e["p"])))
    if kind == "rain":
        S2 = np.zeros((QH, QW, 3), np.float32); e = P["rain"]
        for k in range(4):
            y = (e["y"] + (T - k * 0.006) * 420 * e["s"]) % QH; x = (e["x"] - (T - k * 0.006) * 60) % QW
            np.add.at(S2, (np.clip(y.astype(np.int32), 0, QH - 1), np.clip(x.astype(np.int32), 0, QW - 1)), (e["b"] * 0.25)[:, None] * np.array((210, 200, 190), np.float32))
        L += S2
    L = cv2.GaussianBlur(L, (0, 0), 0.8 if kind != "snow" else 1.2)
    return cv2.resize(L, (W, H))


FOGLV = {"fire": 0.16, "ash": 0.22, "smoke": 0.32, "snow": 0.12, "rain": 0.1}
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.45 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1) ** 1.5)[..., None]
rg = np.random.default_rng(5); GR = [rg.normal(0, 4.5, (H, W, 1)).astype(np.float32) for _ in range(4)]
FOGCOL = np.array([150, 160, 175], np.float32)
XF = 0.45
SHARP = float(__import__("os").environ.get("SHARPEN", 0.6))


def full(i, T):
    a, dc = scene(i, T); fx = SCENES[i].get("fx", "none")
    if fx in FOGLV:
        al = np.clip(fog(T) * FOGLV[fx] * (0.55 - dc), 0, 0.6)[..., None]; a = a * (1 - al) + FOGCOL * al
    if fx in ("fire", "ash", "snow", "dust", "rain"):
        a += particles(T, fx) * 1.6
    if fx == "old":
        a = a.mean(axis=2, keepdims=True) * np.array([0.82, 0.95, 1.08], np.float32) + 8
        a *= 1 + 0.04 * math.sin(T * 37) * math.sin(T * 5.3)
        r2 = np.random.default_rng(int(T * FPS))
        if r2.random() < 0.25:
            x = int(r2.integers(0, W)); a[:, x:x + 2] += 40
    return a


TC = EP.get("title_card")  # {"after_scene": n, "lines": ["BIG", "small"]}


def frame(T):
    i = max(k for k in range(NS) if starts[k] <= T) if T > 0 else 0
    a = full(i, T)
    if i > 0 and T - starts[i] < XF:
        w = ez((T - starts[i]) / XF); a = a * w + full(i - 1, T) * (1 - w)
    a = a * VIG
    if SHARP > 0:   # unsharp mask: recovers detail lost by upscaling 1024px images to 1080p
        a = cv2.addWeighted(a, 1 + SHARP, cv2.GaussianBlur(a, (0, 0), 1.6), -SHARP, 0)
    a = a + GR[int(T * FPS) % 4] * 0.6
    im = Image.fromarray(cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(im, "RGBA")
    for c, t0 in CH_T.items():
        title = EP["chapters"][c].get("title", "")
        t = T - t0
        if title and 0 <= t < 4.6:
            al = min(1, t / 0.4, (4.6 - t) / 0.6); f = FT
            while d.textlength(title, font=f) > W - 160: f = ImageFont.truetype(FB, f.size - 4)
            tw = d.textlength(title, font=f)
            d.rectangle([0, H - 250, W, H - 130], fill=(0, 0, 0, int(150 * al)))
            d.rectangle([W / 2 - tw / 2, H - 140, W / 2 + tw / 2, H - 134], fill=(200, 40, 30, int(255 * al)))
            d.text((W / 2, H - 192), title, font=f, fill=(255, 255, 255, int(255 * al)), anchor="mm")
    if TC:
        tt = starts[min(NS - 1, TC["after_scene"])] + 0.3
        if tt <= T < tt + 5:
            t = T - tt; al = min(1, t / 0.5, (5 - t) / 0.7); f = FBIG
            while d.textlength(TC["lines"][0], font=f) > W - 160: f = ImageFont.truetype(FB, f.size - 4)
            d.text((W / 2, H / 2 - 30), TC["lines"][0], font=f, fill=(255, 255, 255, int(255 * al)), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, int(200 * al)))
            if len(TC["lines"]) > 1:
                d.text((W / 2, H / 2 + 60), TC["lines"][1], font=FS, fill=(255, 200, 60, int(255 * al)), anchor="mm")
    return im


def part(p, n):
    Nf = int(DUR * FPS); per = math.ceil(Nf / n); f0, f1 = p * per, min(Nf, (p + 1) * per)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p", f"{ED}/part{p}.mp4"], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        enc.stdin.write(frame(f / FPS).tobytes())
        if (f - f0) % 1200 == 0: print("render part", p, f - f0, "/", f1 - f0, flush=True)
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "preview":
        ts = [min(DUR - 0.1, starts[i] + 1.5) for i in range(0, NS, max(1, NS // 8))][:8]
        sheet = Image.new("RGB", (1920, 720))
        for j, T in enumerate(ts): sheet.paste(frame(T).resize((480, 270)), ((j % 4) * 480, (j // 4) * 360))
        sheet.save(f"{ED}/preview_long.jpg", quality=85); print("preview", ts); sys.exit()
    n = os.cpu_count() or 2
    ps = [Process(target=part, args=(p, n)) for p in range(n)]
    [p.start() for p in ps]; [p.join() for p in ps]
    open(f"{ED}/parts.txt", "w").write("".join(f"file 'part{p}.mp4'\n" for p in range(n)))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{ED}/parts.txt", "-i", f"{ED}/music.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{ED}/long.mp4"], check=True)
    for p in range(n): os.remove(f"{ED}/part{p}.mp4")
    print("long done")
