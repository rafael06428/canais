"""Start / use / stop a rented RunPod GPU for video clips (run from the workspace).

usage:
  python3 pod.py start            -> creates the pod, prints its id (saved in ~/.runpod_pod)
  python3 pod.py wait             -> waits until the worker answers /health
  python3 pod.py health | log
  python3 pod.py gen <jobs.json> <out_dir>   -> sends every job, downloads the clips
  python3 pod.py stop             -> TERMINATES the pod (billing stops)
needs RUNPOD_API_KEY. Safety: `gen` refuses to run past MAX_MINUTES of pod life (default 110).
"""
import base64, json, os, secrets, sys, time, urllib.request

KEY = os.environ["RUNPOD_API_KEY"]
STATE_F = os.path.expanduser("~/.runpod_pod")
GPU = os.environ.get("RUNPOD_GPU", "NVIDIA GeForce RTX 4090")
IMAGE = os.environ.get("RUNPOD_IMAGE", "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04")
SERVER = "https://raw.githubusercontent.com/rafael06428/canais/" + os.environ.get("SERVER_REF", "main") + "/agent/gpu/server.py"
DISK = int(os.environ.get("RUNPOD_DISK", 80)); CLOUD = os.environ.get("RUNPOD_CLOUD", "COMMUNITY")
MAX_MIN = float(os.environ.get("MAX_MINUTES", 110))


def gql(q):
    req = urllib.request.Request("https://api.runpod.io/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    r = json.loads(urllib.request.urlopen(req, timeout=60).read())
    if r.get("errors"): raise RuntimeError(r["errors"])
    return r["data"]


def st():
    return json.load(open(STATE_F))


def call(path, body=None, raw=False, timeout=120):
    s = st(); url = f"https://{s['id']}-8000.proxy.runpod.net{path}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"X-Token": s["token"], "Content-Type": "application/json", "User-Agent": "curl/8.5"})
    b = urllib.request.urlopen(req, timeout=timeout).read()
    return b if raw else json.loads(b)


def start():
    token = secrets.token_hex(16)
    args = ("bash -c 'pip install -q -U diffusers transformers accelerate imageio imageio-ffmpeg ftfy sentencepiece && "
            f"curl -sL {SERVER} -o /server.py && python /server.py'")
    q = f'''mutation {{ podFindAndDeployOnDemand(input: {{
        cloudType: {CLOUD}, gpuCount: 1, gpuTypeId: "{GPU}", name: "canal-video",
        imageName: "{IMAGE}", containerDiskInGb: {DISK}, volumeInGb: 0, ports: "8000/http",
        dockerArgs: {json.dumps(args)}, env: [{{key: "TOKEN", value: "{token}"}}] }}) {{ id costPerHr machineId }} }}'''
    d = gql(q)["podFindAndDeployOnDemand"]
    json.dump({"id": d["id"], "token": token, "t0": time.time()}, open(STATE_F, "w"))
    print("pod", d["id"], "cost/h", d["costPerHr"])


def wait(limit=1800):
    t = time.time()
    while time.time() - t < limit:
        try:
            h = call("/health", timeout=20); print("ready", h); return h
        except Exception as e:
            print("waiting", type(e).__name__, str(e)[:80], flush=True); time.sleep(20)
    raise SystemExit("pod not ready")


def gen(jobs_f, out):
    os.makedirs(out, exist_ok=True); jobs = json.load(open(jobs_f))
    for j in jobs:
        if os.path.exists(f"{out}/{j['id']}.mp4"): continue
        j = dict(j); j["image_b64"] = base64.b64encode(open(j.pop("image"), "rb").read()).decode()
        print(call("/gen", j))
    left = [j["id"] for j in jobs if not os.path.exists(f"{out}/{j['id']}.mp4")]
    while left:
        if (time.time() - st()["t0"]) / 60 > MAX_MIN: print("MAX_MINUTES reached, stopping"); stop(); return
        h = call("/health", timeout=30)
        for i in list(left):
            if i in h["done"]:
                open(f"{out}/{i}.mp4", "wb").write(call(f"/out/{i}.mp4", raw=True, timeout=300)); left.remove(i); print("got", i, flush=True)
            elif i in h["failed"]:
                print("failed", i, h["failed"][i]); left.remove(i)
        if left: time.sleep(20)


def stop():
    s = st(); print(gql(f'mutation {{ podTerminate(input: {{podId: "{s["id"]}"}}) }}')); os.remove(STATE_F)


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "start": start()
    elif c == "wait": wait()
    elif c == "health": print(call("/health"))
    elif c == "log": print(call("/log", raw=True).decode())
    elif c == "gen": gen(sys.argv[2], sys.argv[3])
    elif c == "stop": stop()
