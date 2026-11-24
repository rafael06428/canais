# You Were There POV: daily production agent

Every day this agent makes and publishes, with no human review:
- **1 long video** (10 to 13 min, 16:9, English) in the format *"24 Hours in X: Would You Have Survived?"*
- **4 Shorts** (30 to 45 s, 9:16), each with its own **looping narration**
- **English subtitles (SRT)** on the long video, uploaded every time

Channel: **You Were There POV**, @youwereintime, ID `UCqNclACz0xvuvrYg3RP6BkQ`.
Reference episode: https://youtu.be/wCn41oG4bnA (24 Hours in Pompeii).

## Hard rules (from the channel owner)
- **Do not use fal.ai, Wan or any paid generation.** Images: **Cloudflare Workers AI free tier** (`images.py` with `CF_ACCOUNT_ID`/`CF_API_TOKEN`: FLUX.2 klein 4B for the first 55 images of a run, then flux-1-schnell; 10,000 free neurons/day, reset 00:00 UTC ≈ 21:00 Brasília). In practice the quota covers only ~74 images (klein costs more than estimated): set `CF_KLEIN_MAX=30` or plan for the anonymous Pollinations fallback (run images.py with CF_*/POLLINATIONS_KEY unset). For Shorts, center-cropping good long-video images to 9:16 (+ depth via `images.depth`) looks better than the anonymous model. Voice: Microsoft Edge neural voices (free, `voice.py`).
- Budget the daily quota: ~90 long-video scenes + ~18 Short images. Don't re-roll more than ~10 images. If Cloudflare answers with a quota/limit error, the script falls back to Pollinations (anonymous = weak model): re-check those images strictly and reuse good nearby images instead of publishing bad ones.
- The free image tier is ~1 request / 15 s (≈30 min for 90 images) and its model is weak with ships, boats and crowds of objects: it often swaps "lifeboat" for a sailing ship. Prefer concrete, simple prompts ("small wooden rowboat full of people in coats"), avoid naming famous ships/landmarks inside interior or object prompts, and when a re-roll still fails, reuse a good image from a nearby scene (copy both `.jpg` and `.npy`).
- **Every Short needs an audio loop.** The last block stops mid-sentence and the first block completes it, e.g. last: *"They never knew they"* + first: *"only had eighteen hours."*
- **Always upload the subtitles.**
- Publish directly as **Public**. Use the settings Not made for kids, Altered/synthetic content = Yes, No paid promotion.
- Originality: every episode needs its own researched story. Never re-use a script structure word for word, because YouTube demonetizes repetitive or templated channels.
- Be historically accurate. Where historians disagree, say so in the narration ("most historians think…").
- Nothing graphic: describe danger and death with restraint, as in the Pompeii episode. No gore in prompts.

## Steps

### 0. Setup (fresh workspace)
```
add_repo rafael06428/canais (push)  →  git clone --depth 1 https://github.com/rafael06428/canais /home/claude/canais
bash /home/claude/canais/agent/setup.sh
```
If the task prompt gives a Pollinations key, `export POLLINATIONS_KEY=<key>` before any `make.py` call (models klein → flux fallback; ~10 s per image, no rate limit). With a key, images take ~15 min instead of ~30, and quality is much higher. Never write the key into the repo (it is public).
Check the network (with a key also check `https://gen.pollinations.ai/image/models`): `python3 -c "import urllib.request;urllib.request.urlopen('https://image.pollinations.ai/prompt/test?width=64&height=64',timeout=30)"`
and `edge-tts --proxy "$HTTPS_PROXY" --text test --write-media /tmp/t.mp3`.
If either is refused by the proxy, stop. Send the owner one PushNotification saying which domain must be allowed in Claude Settings > Capabilities (`image.pollinations.ai`, `speech.platform.bing.com`).

### 1. Pick today's topic (automatic)
- If `agent/topics_done.json` already has an entry with today's date (America/Sao_Paulo), a video was already published today: stop quietly (no notification).
- Read `agent/topics_done.json` and never repeat a topic.
- **Topic chosen by the owner:** if `agent/topic_queue.json` exists, take the first item whose `date` is today or earlier (or that has no `date`) and isn't in `topics_done.json`. Use it as today's topic, follow its `notes`, still do the 6+ research calls, and remove it from the queue in the wrap-up commit. If the queue is empty, choose the topic automatically as below.
- Do 3 to 5 WebSearches for what's being searched now: history anniversaries this week, recent discoveries, trending documentaries or films, viral history topics. Pick the most clickable topic that fits **"you are there, hour by hour, would you survive?"** Good fits: disasters, sieges, famous last days, escapes, expeditions, plagues, shipwrecks, eruptions, heists, battles seen from a soldier or civilian.
- Rotate eras and regions. Don't pick the same century or region two days in a row.
- Then research the facts: at least 6 WebSearch/WebFetch calls on reliable sources (museums, universities, encyclopedias, primary accounts). Note real names, numbers, times and quotes from eyewitnesses.

### 2. Write `/home/claude/ep/episode.json`
Narration target: **1,600 to 1,900 words** (about 11 to 12 min). Second person, present tense, short sentences, sensory details, and a choice at every hour.
Structure (like Pompeii):
1. Cold open, about 20 s: the countdown hook ("X hours from now…"), one vivid detail to remember, and the promise "by the end you'll know whether you would have survived".
2. Title card right after the hook (`title_card.after_scene` = index of the scene after the hook).
3. Seven to nine chapters, each a time of day or phase, with rising stakes and a real choice the people faced.
4. A cutaway to one real historical person whose story runs in parallel (like the admiral Pliny).
5. Rediscovery or aftermath: how we know, with real evidence.
6. The answer: who survived and why, closing the loop on the opening detail, then a soft CTA ("Which choice would you have made? Tell me in the comments").

```json
{
 "slug": "titanic",                       // a-z, 0-9, dashes
 "title": "24 Hours on the Titanic",      // used in footers
 "title_yt": "24 Hours on the Titanic: Would You Have Survived?",   // ≤ 70 chars
 "description": "2-3 hook lines…\n\n{CHAPTERS}\n\nSources: …\n\nVisuals and narration are AI-generated, based on historical accounts.\n\n#History #POV #Titanic",
 "tags": ["titanic", "history", "pov", "…"],     // 10-15
 "voice": "en-US-AndrewMultilingualNeural",       // keep this voice for the brand
 "thumb_text": "2 HOURS\nTO LIVE",                // max 2 short lines, all caps
 "thumb_scene": 3,                                // most dramatic scene index
 "title_card": {"after_scene": 3, "lines": ["24 HOURS ON THE TITANIC", "WOULD YOU HAVE SURVIVED?"]},
 "chapters": [
   {"title": "", "yt_chapter": "Intro", "scenes": [
     {"text": "One or two sentences of narration (12-28 words).",
      "prompt": "Visual description in English: first-person or over-the-shoulder POV, era-accurate clothes and architecture, time of day, light, mood, camera angle. No text, no gore.",
      "fx": "none|dust|fire|ash|smoke|snow|rain|old", "shake": 0}
   ]},
   {"title": "11:40 PM  ·  THE ICEBERG", "yt_chapter": "11:40 PM: The iceberg", "scenes": [ … ]}
 ],
 "shorts": [
   {"label": "2 HOURS LEFT", "title": "You Have 2 Hours Left on the Titanic #Shorts",
    "description": "One hook line. Full story: {LONG_URL}\n\nAI-generated visuals and narration, based on historical accounts.\n\n#Titanic #History #POV #Shorts",
    "blocks": [
      {"text": "only had two hours.", "prompt": "vertical composition, …"},
      {"text": "…", "prompt": "…"},
      {"text": "…the last sentence, cut off right before the first block's words. They never knew they", "prompt": null}
    ]}
 ]
}
```
- **80 to 100 scenes.** Each scene is one image on screen for 4 to 9 s. Vary the shots (wide, close-up, hands, faces, objects, crowd, aerial) and keep consistent characters and clothing.
- `fx`: `fire` = flames, embers, flicker; `ash` = falling ash; `smoke` = haze; `snow` / `rain`; `dust` = calm interior motes; `old` = archival look for rediscovery or present-day scenes; `none`. `shake` 0 to 3 is only for impacts and explosions.
- **Shorts:** 4 of them, each **5 to 7 blocks, 70 to 110 words**, built around different moments (the hook, the choice, the parallel person, the shocking evidence). Each Short must work on its own and end on the loop. The last block's `prompt` is `null`, because it reuses the first image. Prompts are for vertical 9:16 frames.

### 3. Build
```
cd /home/claude/canais/agent && python3 make.py /home/claude/ep voice && python3 make.py /home/claude/ep images
python3 make.py /home/claude/ep audio && python3 make.py /home/claude/ep preview
```
**Look at the images**: build contact sheets of `img/*.jpg` (e.g. 12 per sheet) and Read them all. The free image model often draws ships/buildings distorted or adds wrong objects when prompts are long or name famous landmarks: for any bad image, rewrite the prompt shorter and more concrete (subject, setting, light; avoid brand/landmark names), delete `img/NNN.*`, rerun `make.py … images`. Then **look at** `/home/claude/ep/preview_long.jpg` with Read. If an image is broken, off-topic, has text or gore, or anachronisms, rewrite that scene's prompt, delete `img/NNN.*` and rerun `make.py … images`.
Then run `python3 make.py /home/claude/ep` (long render ~40 min, srt, thumb, shorts). Use a long timeout or `run_in_background` and poll.
Check: `ffprobe` the durations, Read `thumb.jpg`, and run `python3 render_short.py ep/shorts/K "<label>" "<footer>" preview` for each Short, then Read `preview.jpg`.

### 4. Publish
`python3 publish.py /home/claude/ep /home/claude/canais` puts the files on the `media` branch and writes `ep/upload.json`.
In the **built-in browser** (`mcp__remote-devices__Claude_Browser__*`), tab on `https://studio.youtube.com/channel/UCqNclACz0xvuvrYg3RP6BkQ/videos/upload?d=ud`:
1. Paste `agent/upload.js` with javascript_tool, then start the long video job: `window.__res=null; ytUpload({...upload.long, thumb: upload.long.thumb}).then(r=>window.__res=r).catch(e=>window.__res='ERR '+e); 'started'`. Poll `window.__state+' | '+window.__res` every ~45 s until it returns a link.
   (`ytUpload` also sets tags, video language = Inglês and category = Educação. If the dialog shows the file name as title, the title/description didn't stick: set them again before publishing.)
   **Focus:** when the browser pane is hidden the page has no focus and `execCommand` silently fails (title stays the file name, tags empty). Before starting any job, click once on an empty area of the page with `Claude_Browser__computer` and check `document.hasFocus()` is true. CSP blocks `eval`, so paste upload.js as text.
2. **Subtitles:** open `https://studio.youtube.com/video/<ID>/translations`. If asked, set the video language to English. Hover the English row and click its **Adicionar** button (use `find "Adicionar"`), then Upload file (Enviar arquivo), then **With timing** (Com marcação de tempo), then Continue (Continuar). Before Continue, override `HTMLInputElement.prototype.click` for `type=file` so the native picker doesn't open. Then set `#captions-file-loader` from the SRT URL (fetch, `DataTransfer`, `change`) and click **Publish (Publicar)**. Confirm the row shows Published (Publicada).
   **Never navigate away before the long upload's bytes are done** (the dialog's "Envio em X%"); otherwise YouTube shows "Envio interrompido" and resuming rejects a re-fetched file ("Arquivo incorreto"). `ytUpload` now waits for it; check the Videos list shows the video without "Envio interrompido" before opening the subtitles page.
3. Shorts: for each item in `upload.shorts`, replace `{LONG_URL}` with the long video link and run the same `ytUpload`. Reload the upload URL before each one (or, to keep `ytUpload` defined, close the "Processando vídeo" dialog and open Criar > Enviar vídeos with real clicks: `ytUpload`'s own menu click doesn't work after the first upload).
   If the Cloudflare quota is already spent when the run starts (429 "used up your daily free allocation"), the anonymous Pollinations model works (~45 min for 93 images, many 503 retries): it often makes men look feminine, can't draw a capsized ship and ignores small objects, so add "rugged, stubble, bearded" to male prompts and re-roll ~20-25 images.
4. Verify on `…/videos/short` and `…/videos/upload` that everything is Public. If one failed, retry it once and don't duplicate.

**Daily upload limit:** until the channel is phone-verified YouTube allows only ~10 uploads a day; when reached, `ytUpload` throws `daily upload limit reached` and the video stays as a **draft** (Rascunho). Record such items in `pending` (step 5) and, at the start of the next run's publish step, open each pending draft (`https://studio.youtube.com/video/<ID>/edit` → Visibilidade → Público → Salvar) before uploading new ones.
**Pending items without an ID** (`"id": null` with a `job` URL): the draft was lost when the dialog closed, so the video file lives on the `pending` branch. At the start of the publish step, fetch the `job` JSON (a list of ready ytUpload jobs, `{LONG_URL}` already filled), upload each with `ytUpload` before today's videos, then set `pending` to [] for that day. When the limit hits, don't close the dialog with X (that discards the upload); leave it open, note the video ID from the dialog's link if shown, or push the file to the `pending` branch as above. `publish.py` force-pushes only `media`, so the `pending` branch is safe; delete the `pending` branch once its jobs are published.
**Notes from 2026-11-23 (YouTube Studio changes):**
- The built-in browser may be signed in to another channel (The Getaway Case): if the upload URL gives "Ops, você não tem permissão", open the avatar menu > Mudar de conta > You Were There POV.
- YouTube now shows "Ainda estamos verificando seu conteúdo" when you click Publicar before checks finish. Don't click "Publicar mesmo assim": click Voltar, then close the dialog with X (once the bytes are done it is saved as a private draft). Upload the other videos meanwhile; ~5-10 min later open each draft (Conteúdo > Editar rascunho), click Avançar 3x, choose Público, click Publicar (checks done, no warning).
- With the pane hidden the page often doesn't render and `execCommand` fails ("title did not stick"); take a screenshot first to force a render, scroll the title box into view, then set title/description again in the open dialog.
- Subtitles: Idiomas page now has **Enviar manualmente** > Com marcação de tempo > Continuar; setting `#captions-file-loader` uploads it directly; then Editar legendas > Publicar ("Legendas em inglês enviadas").
- Shorts from 9:16 center crops of long-video images (pre-filled `shorts/K/img/NNN.jpg` + `.npy`) save the image quota; the quota ran out after ~100 images (CF_KLEIN_MAX=30).

**Notes from 2026-11-24:**
- The Cloudflare quota was already spent at the start of the run (429 "used up your daily free allocation") and the Pollinations key answered 402: the anonymous fallback (`env -u CF_ACCOUNT_ID -u CF_API_TOKEN -u POLLINATIONS_KEY`) took ~75 min for 97 images with many 402/503 retries. Wrap `make.py … images` in a retry loop (it exits after 6 failed tries on one image). Don't `pkill -f "make.py … images"` while a watcher loop's own command line contains that text (it kills the loop too).
- "Ainda estamos verificando seu conteúdo": simplest fix is to click **Ok** in that warning, keep the upload dialog open, wait until the footer says "Verificações concluídas" (~4 min long, ~2 min Short), then click Publicar. No draft step needed.
- Shorts after the first: real clicks on Criar (top right) then Enviar vídeos keep `ytUpload` defined; check `ytcp-uploads-file-picker input[type=file]` exists before starting (the first menu click sometimes only opens the menu).
- After uploading the SRT, Editar legendas > Publicar must show the toast "Legendas em Inglês publicadas"; check it.

The thumbnail upload is skipped automatically until the channel is phone-verified. Once it is verified, the custom thumbnail goes up with the long video.

### 5. Wrap up
- Append `{"date", "slug", "title", "long_url", "shorts": [...], "pending": [{"id", "title"}]}` to `agent/topics_done.json`, commit on `main` (end the message with the attribution lines from the system reminder) and `git push`.
- Send the owner one **PushNotification** in Portuguese: topic and links, short.
- On a failure you can't fix in 2 tries, notify the owner in Portuguese with what failed and what is ready, then stop.
