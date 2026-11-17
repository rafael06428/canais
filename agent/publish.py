"""Put today's files on the public `media` branch (force-pushed, so the repo doesn't grow)
and write upload.json with the raw URLs the browser uploader fetches.

usage: python3 publish.py <episode_dir> <repo_dir>
GitHub serves raw files up to 100 MB, so big videos are split into 90 MB chunks.
"""
import json, os, shutil, subprocess, sys, time

ED, REPO = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
EP = json.load(open(f"{ED}/episode.json"))
OWNER_REPO = "rafael06428/canais"
CHUNK = 90 * 1024 * 1024
stamp = time.strftime("%Y%m%d") + "-" + EP["slug"]
MEDIA = "/tmp/media_branch"
RAW = f"https://raw.githubusercontent.com/{OWNER_REPO}/media/{stamp}/"


def git(*a, cwd=MEDIA):
    subprocess.run(["git", "-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", *a], cwd=cwd, check=True)


def add(src, name):
    size = os.path.getsize(src); urls = []
    with open(src, "rb") as f:
        k = 0
        while True:
            b = f.read(CHUNK)
            if not b: break
            part = f"{name}.part{k}" if size > CHUNK else name
            open(f"{MEDIA}/{stamp}/{part}", "wb").write(b); urls.append(RAW + part); k += 1
    return urls


# chapter timestamps for the description (YouTube needs 0:00 first)
V = json.load(open(f"{ED}/voice.json")); k = 0; chap = []
for ci, c in enumerate(EP["chapters"]):
    t = 0 if ci == 0 else int(V["blocks"][k][0])
    chap.append(f"{t // 60}:{t % 60:02d} {c.get('yt_chapter') or c.get('title') or 'Intro'}"); k += len(c["scenes"])
EP["description"] = EP["description"].replace("{CHAPTERS}", "\n".join(chap))

shutil.rmtree(MEDIA, ignore_errors=True); os.makedirs(f"{MEDIA}/{stamp}")
git("init", "-q", "-b", "media")
git("remote", "add", "origin", subprocess.check_output(["git", "remote", "get-url", "origin"], cwd=REPO, text=True).strip())
up = {"stamp": stamp,
      "long": {"files": add(f"{ED}/long.mp4", "long.mp4"), "name": f"{EP['slug']}.mp4",
               "title": EP["title_yt"], "description": EP["description"], "tags": EP.get("tags", []),
               "srt": add(f"{ED}/subs.srt", "subs.srt")[0], "thumb": add(f"{ED}/thumb.jpg", "thumb.jpg")[0]},
      "shorts": []}
for k, sh in enumerate(EP["shorts"]):
    up["shorts"].append({"files": add(f"{ED}/shorts/{k}/short.mp4", f"short{k}.mp4"), "name": f"{EP['slug']}_short{k}.mp4",
                         "title": sh["title"], "description": sh["description"]})
json.dump(up, open(f"{MEDIA}/{stamp}/upload.json", "w"), indent=1, ensure_ascii=False)
json.dump(up, open(f"{ED}/upload.json", "w"), indent=1, ensure_ascii=False)
git("add", "-A"); git("commit", "-qm", f"media {stamp}")
git("push", "-f", "-q", "origin", "media")
print("published", RAW + "upload.json")
