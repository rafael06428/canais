"""Scene images from Pollinations (free Flux) + MiDaS depth maps for parallax.

usage: python3 images.py <prompts_json> <out_dir> [WxH]
  prompts_json: ["prompt 0", "prompt 1", ...]  ->  out_dir/NNN.jpg (1344x768) + out_dir/NNN.npy (depth)
Already-downloaded images are skipped, so the script can be re-run after a failure.
"""
import io, json, os, sys, time, urllib.error, urllib.parse, urllib.request
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1344, 768
STYLE = ", cinematic film still, photorealistic, dramatic natural lighting, 35mm, shallow depth of field, no text, no watermark, no letters"


KEY = os.environ.get("POLLINATIONS_KEY", "").strip()      # free account key (sk_...): real Flux, no rate limit
MODELS = [m.strip() for m in os.environ.get("IMG_MODEL", "klein,flux").split(",") if m.strip()]   # first = best; next ones are fallbacks


CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()     # free Cloudflare Workers AI: 10,000 neurons/day
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()
CF_KLEIN_MAX = int(os.environ.get("CF_KLEIN_MAX", 55))     # ~100 neurons each at 1024x576; the rest use flux-1-schnell (~58)
_cf_count = 0


def cf_run(model, prompt, seed, W, H):
    import base64, uuid
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACC}/ai/run/@cf/black-forest-labs/{model}"
    hdr = {"Authorization": f"Bearer {CF_TOK}", "User-Agent": "Mozilla/5.0"}
    if model.startswith("flux-2"):                         # FLUX.2 models take multipart form data
        b = uuid.uuid4().hex; parts = []
        for k, v in (("prompt", prompt), ("width", W), ("height", H), ("seed", seed)):
            parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n')
        body = ("".join(parts) + f"--{b}--\r\n").encode(); hdr["Content-Type"] = f"multipart/form-data; boundary={b}"
    else:
        body = json.dumps({"prompt": prompt, "steps": 4}).encode()   # flux-1-schnell rejects a "seed" field (400); hdr["Content-Type"] = "application/json"
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=hdr), timeout=180) as r:
        data = r.read(); ct = r.headers.get("Content-Type", "")
    if "json" in ct:
        j = json.loads(data)
        if not j.get("success", True): raise RuntimeError(str(j.get("errors"))[:200])
        return base64.b64decode(j["result"]["image"])
    return data


def fetch(prompt, seed, W=W, H=H):
    global _cf_count
    q = urllib.parse.quote(prompt + STYLE, safe="")
    if CF_ACC and CF_TOK:
        w, h = (1024, 576) if W >= H else (576, 1024)
        models = (["flux-2-klein-4b"] if _cf_count < CF_KLEIN_MAX else []) + ["flux-1-schnell"]
        last = None
        for m in models:
            try:
                b = cf_run(m, (prompt + STYLE)[:2000], seed, w, h); _cf_count += 1; return b
            except Exception as e:
                last = e; print("cloudflare", m, "failed:", str(e)[:120], flush=True)
        if not KEY: raise last
    if KEY:
        last = None
        for m in MODELS:   # e.g. out of pollen for the better model -> try the cheaper one
            url = f"https://gen.pollinations.ai/image/{q}?width={W}&height={H}&model={urllib.parse.quote(m, safe='')}&nologo=true&private=true&seed={seed}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {KEY}"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                last = e
                if e.code not in (402, 403, 429): raise
        raise last
    else:
        url = f"https://image.pollinations.ai/prompt/{q}?width={W}&height={H}&model=flux&nologo=true&seed={seed}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def clean(b, W=W, H=H):
    im = Image.open(io.BytesIO(b)).convert("RGB")
    w, h = im.size
    if min(w, h) < 340:
        raise ValueError(f"too small {w}x{h}")
    if not KEY:
        im = im.crop((0, 0, w, int(h * 0.93)))        # anonymous tier: drop the bottom strip (watermark)
    g = np.asarray(im.convert("L"), np.float32)
    def edge(rows):                                   # skip flat letterbox bands (white/black lines)
        n = 0
        for r in rows:
            if r.std() < 7 and n < len(rows) * 0.12: n += 1
            else: break
        return n
    t, b = edge(g), edge(g[::-1]); l, r = edge(g.T), edge(g.T[::-1])
    if t or b or l or r:
        im = im.crop((l + 2 * (l > 0), t + 2 * (t > 0), im.width - r - 2 * (r > 0), im.height - b - 2 * (b > 0)))
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


_depth = None
def depth(path):
    global _depth
    import onnxruntime as ort
    if _depth is None:
        _depth = ort.InferenceSession(os.path.join(HERE, "midas_small.onnx"))
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    x = cv2.resize(im, (256, 256), interpolation=cv2.INTER_CUBIC)
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    d = _depth.run(None, {"0": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    d = (d - d.min()) / max(1e-6, d.max() - d.min())          # 1 = near
    return cv2.GaussianBlur(d.astype(np.float32), (0, 0), 2)


def main(prompts, out, W=W, H=H):
    os.makedirs(out, exist_ok=True)
    for i, p in enumerate(prompts):
        f = f"{out}/{i:03d}.jpg"
        if not os.path.exists(f):
            if os.environ.get("IMG_FAKE"):
                src = sorted(x for x in os.listdir(os.environ["IMG_FAKE"]) if x.endswith(".jpg"))
                clean(open(os.path.join(os.environ["IMG_FAKE"], src[i % len(src)]), "rb").read(), W, H).save(f, quality=93)
            for a in range(0 if os.path.exists(f) else 6):
                try:
                    clean(fetch(p, 1000 + i * 7 + a, W, H), W, H).save(f, quality=93); break
                except Exception as e:
                    print("retry", i, a, e, flush=True); time.sleep(18 + a * 6)
            if not os.path.exists(f):
                raise SystemExit(f"image {i} failed")
            time.sleep(float(os.environ.get("IMG_GAP", 1 if (KEY or CF_ACC) else 14)))  # anonymous tier: ~1 request per 15 s
        if not os.path.exists(f[:-4] + ".npy"):
            np.save(f[:-4] + ".npy", depth(f).astype(np.float16))
        print(f"img {i + 1}/{len(prompts)}", flush=True)


if __name__ == "__main__":
    size = [int(x) for x in sys.argv[3].split("x")] if len(sys.argv) > 3 else (W, H)
    main(json.load(open(sys.argv[1])), sys.argv[2], *size)
