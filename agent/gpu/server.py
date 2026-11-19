"""Video worker that runs on a rented RunPod GPU.
Port 8000, every call needs header X-Token = $TOKEN:
  GET  /health           -> status json
  POST /gen  {id, model, image_b64, prompt, negative, width, height, frames, steps, seed, fps}
  GET  /out/<id>.mp4     -> finished clip
  GET  /log              -> last lines of the log
The pod is started and stopped from the workspace (gpu/pod.py); this file only generates clips.
"""
import base64, io, json, os, queue, threading, time, traceback
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("TOKEN", "")
OUT = "/workspace/out"; os.makedirs(OUT, exist_ok=True)
LOG = []; JOBS = queue.Queue(); STATE = {"loaded": None, "busy": None, "done": [], "failed": {}}
START = time.time()


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a); print(s, flush=True); LOG.append(s); del LOG[:-400]


PIPE = {}


def load(model):
    import torch
    if STATE["loaded"] == model: return PIPE[model]
    PIPE.clear(); torch.cuda.empty_cache(); log("loading", model)
    if model == "wan5b":
        from diffusers import WanImageToVideoPipeline, AutoencoderKLWan
        vae = AutoencoderKLWan.from_pretrained("Wan-AI/Wan2.2-TI2V-5B-Diffusers", subfolder="vae", torch_dtype=torch.float32)
        p = WanImageToVideoPipeline.from_pretrained("Wan-AI/Wan2.2-TI2V-5B-Diffusers", vae=vae, torch_dtype=torch.bfloat16)
        p.enable_model_cpu_offload()
        try: p.vae.enable_tiling()       # decode in tiles: avoids running out of GPU memory at 1280x704
        except Exception as e: log("no vae tiling", e)
    elif model == "ltx":
        from diffusers import LTXImageToVideoPipeline
        p = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.bfloat16)
        p.to("cuda")
        try: p.vae.enable_tiling()
        except Exception: pass
    else:
        raise ValueError("unknown model " + model)
    PIPE[model] = p; STATE["loaded"] = model; log("loaded", model); return p


def run(job):
    import torch
    from PIL import Image
    from diffusers.utils import export_to_video
    p = load(job.get("model", "wan5b"))
    img = Image.open(io.BytesIO(base64.b64decode(job["image_b64"]))).convert("RGB")
    W, H = int(job.get("width", 1280)), int(job.get("height", 704))
    img = img.resize((W, H))
    g = torch.Generator("cuda").manual_seed(int(job.get("seed", 1)))
    t0 = time.time()
    kw = dict(image=img, prompt=job["prompt"], negative_prompt=job.get("negative", ""), height=H, width=W,
              num_frames=int(job.get("frames", 121)), num_inference_steps=int(job.get("steps", 30)), generator=g)
    if job.get("model", "wan5b") == "wan5b": kw["guidance_scale"] = float(job.get("guidance", 5.0))
    frames = p(**kw).frames[0]
    export_to_video(frames, f"{OUT}/{job['id']}.mp4", fps=int(job.get("fps", 24)))
    log("done", job["id"], round(time.time() - t0), "s")


def worker():
    while True:
        job = JOBS.get(); STATE["busy"] = job["id"]
        try: run(job); STATE["done"].append(job["id"])
        except Exception as e: STATE["failed"][job["id"]] = str(e)[:300]; log("FAIL", job["id"], traceback.format_exc()[-1500:])
        STATE["busy"] = None


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def ok(self, obj, code=200, ctype="application/json"):
        b = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def auth(self):
        if not TOKEN or self.headers.get("X-Token") != TOKEN: self.ok({"error": "token"}, 403); return False
        return True

    def do_GET(self):
        if not self.auth(): return
        if self.path == "/health":
            import shutil
            return self.ok({**STATE, "queue": JOBS.qsize(), "uptime_min": round((time.time() - START) / 60, 1), "disk_free_gb": shutil.disk_usage("/workspace").free // 2**30})
        if self.path == "/log": return self.ok("\n".join(LOG[-80:]).encode(), ctype="text/plain")
        if self.path.startswith("/out/"):
            f = OUT + "/" + os.path.basename(self.path)
            if os.path.exists(f): return self.ok(open(f, "rb").read(), ctype="video/mp4")
            return self.ok({"error": "not ready"}, 404)
        self.ok({"error": "?"}, 404)

    def do_POST(self):
        if not self.auth(): return
        n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/gen": JOBS.put(body); return self.ok({"queued": body["id"], "queue": JOBS.qsize()})
        if self.path == "/clear":   # drop jobs that haven't started
            n = 0
            while not JOBS.empty(): JOBS.get_nowait(); n += 1
            return self.ok({"cleared": n})
        self.ok({"error": "?"}, 404)


if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    log("server up"); ThreadingHTTPServer(("0.0.0.0", 8000), H).serve_forever()
