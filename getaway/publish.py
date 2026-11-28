"""Põe os arquivos do The Getaway Case no ramo público `media-getaway` (um commit só, force-push)
e escreve upload.json com as URLs raw que o navegador baixa para enviar ao YouTube.

usage: python3 publish.py <ep_dir> <repo_dir>
  ep_dir/upload_src.json: {"stamp": "20261128-abagnale",
     "items": [{"key": "long"|"cut-<slug>", "file": "long.mp4", "thumb": "thumb.jpg"|null,
                "title": "...", "description": "...", "tags": [...], "srt": "subs.srt"|null,
                "publish_at": "2026-11-28 15:00"|null}]}
Os itens ainda não publicados do upload.json anterior (fila de cortes) continuam no ramo:
o script baixa o ramo atual, mantém as pastas listadas em getaway/state.json "keep_media" e acrescenta a nova.
Usa ramo próprio para não apagar o `media` do You Were There POV (que é force-pushed pelo outro agente).
"""
import json, os, shutil, subprocess, sys

ED, REPO = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
SRC = json.load(open(f"{ED}/upload_src.json"))
OWNER_REPO = "rafael06428/canais"
BR = "media-getaway"
CHUNK = 90 * 1024 * 1024
stamp = SRC["stamp"]
MEDIA = "/tmp/media_getaway"
RAW = f"https://raw.githubusercontent.com/{OWNER_REPO}/{BR}/"
STATE = json.load(open(f"{REPO}/getaway/state.json"))
origin = subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=REPO, text=True).strip()


def git(*a):
    subprocess.run(["git", "-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", *a], cwd=MEDIA, check=True)


shutil.rmtree(MEDIA, ignore_errors=True)
r = subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", BR, origin, MEDIA])
if r.returncode != 0:   # ramo ainda não existe
    os.makedirs(MEDIA); git("init", "-q", "-b", BR); git("remote", "add", "origin", origin)
keep = set(STATE.get("keep_media", [])) | {stamp}
for d in os.listdir(MEDIA):
    if d != ".git" and d not in keep:
        shutil.rmtree(f"{MEDIA}/{d}")
os.makedirs(f"{MEDIA}/{stamp}", exist_ok=True)


def add(src, name):
    size = os.path.getsize(src); urls = []
    with open(src, "rb") as f:
        k = 0
        while True:
            b = f.read(CHUNK)
            if not b: break
            part = f"{name}.part{k}" if size > CHUNK else name
            open(f"{MEDIA}/{stamp}/{part}", "wb").write(b); urls.append(RAW + f"{stamp}/{part}"); k += 1
    return urls


up = {"stamp": stamp, "items": []}
for it in SRC["items"]:
    j = {"key": it["key"], "files": add(f"{ED}/{it['file']}", os.path.basename(it["file"])),
         "name": f"{stamp}-{it['key']}.mp4", "title": it["title"], "description": it["description"],
         "tags": it.get("tags", []), "publish_at": it.get("publish_at"),
         "thumb": add(f"{ED}/{it['thumb']}", os.path.basename(it["thumb"]))[0] if it.get("thumb") else None,
         "srt": add(f"{ED}/{it['srt']}", os.path.basename(it["srt"]))[0] if it.get("srt") else None}
    up["items"].append(j)
json.dump(up, open(f"{MEDIA}/{stamp}/upload.json", "w"), indent=1, ensure_ascii=False)
json.dump(up, open(f"{ED}/upload.json", "w"), indent=1, ensure_ascii=False)
# um commit só (órfão) para o ramo não crescer
git("checkout", "-q", "--orphan", "tmp_pub"); git("add", "-A"); git("commit", "-qm", f"media {stamp}")
git("push", "-f", "-q", "origin", f"tmp_pub:{BR}")
print("published", RAW + f"{stamp}/upload.json")
