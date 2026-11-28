# The Getaway Case: production agent (runs every day at 8:07 Brasília)

Channel: **The Getaway Case**, @thegetawaycase, ID `UCr_vWFky1S1NzTMWirhhEIQ`
(Studio: https://studio.youtube.com/channel/UCr_vWFky1S1NzTMWirhhEIQ). English, US audience.
Owner talks Portuguese: every message to the owner is in Portuguese, short.
Separate from **You Were There POV** (`agent/AGENT.md`, ID `UCqNclACz0xvuvrYg3RP6BkQ`): never touch that channel's videos or files.

## Cadence (owner's decision, 2026-11-28)
- **One long video every 2 days** (8 to 10 min, 16:9) + **4 vertical cuts (Shorts)** of it, so there are **2 Shorts every day**.
- Every run starts by reading `getaway/state.json`. If `today - last_long < 2 days` (America/Sao_Paulo dates), **stop quietly** (no notification).
  The Shorts of those days were already scheduled by the previous run.
- On a production day everything is uploaded in this run, scheduled with YouTube's **Programar** (times in Brasília, fuso "(GMT-0300) Horário local"):
  - long video: **day D 15:00** (≈ 1 pm US Eastern, best time for the US audience);
  - cuts: **D 21:00, D+1 14:00, D+1 21:00, D+2 12:00**.
  If a time is already past when uploading, use the next free slot of the same list shifted by +1 h.

## Hard rules (owner)
1. Every real video is a **researched true story** with beginning, middle and end; **sources in the description** (at least 3, with links when possible).
2. **No graphic violence**, not even in fiction. Prefer heists, hijackings, cons, escapes, disappearances.
3. **Never accuse living people who were not convicted.** Where there is doubt, say it in the narration ("investigators believe…", "it has never been proven…").
4. Narration and on-screen text **in English**. Every upload: **Altered or synthetic content = Yes**, not made for kids, no paid promotion (gcUpload does it).
5. **No movie/TV clips, no photos of real people, no logos of real companies as artwork.** Draw everything with code; documents are labelled **RECONSTRUCTION** and cite their source in small text.
6. **Fiction** (only public-domain tales published before 1929) is always marked: title with "(Classic Tale)" or "| Author", narration starts with "This is a story by…", description says "a work of fiction".
7. Originality: each episode has its own research, script and scenes. Never reuse a script structure word for word (YouTube demonetizes repetitive channels).
8. **Famous topics first** (owner, 2026-11-26): take the next item of `getaway/topics.json` that isn't in `state.json` `videos`.

## Style (reference: episode 1, Frank Abagnale, https://youtu.be/uMQw3If6BYY)
Animated motion graphics drawn by code, inspired by the edit of the RunnyIA video the owner liked: dark navy background, glitch cuts, checklists that tick,
counters and rings that count up, a search bar that types itself, document/record cards with a stamp, timelines with a red block that slams down,
quote cards that type, a big two-line twist at the end. Palette: bg #06131f, ice #e6f1f6, orange #ff6b3d, cyan #7fd6ff, sub #9dbccd, red #ff3b47.
Fonts: Anton (titles, numbers), Inter (support), DejaVu Sans Mono (labels/records).
- Full working example: `getaway/engine/example_abagnale.html` (8 scenes, all helpers: `W(block, word)`, `pop`, `slideX`, `stamp`, `type`, `rgb`, counters, rings, timeline).
- **Text must stay readable when the frame is shrunk to 1080 px wide inside a vertical Short**: titles ≥ 90 px, body ≥ 44 px, labels ≥ 26 px.
- A new visual element at least every 2-3 s (pop-in, check, counter, stamp, zoom). Scene cut = glitch + whoosh.
- Optional maps: `npm install d3-geo topojson-client world-atlas` and draw an SVG route (see `motion/suspense/` on branch `claude/modelo-animacao` for a map camera).

## Steps

### 0. Setup
```
add_repo rafael06428/canais (push) → git clone --depth 1 https://github.com/rafael06428/canais /home/claude/canais
pip install -q --break-system-packages edge-tts numpy pillow
```
Playwright + Chromium, ffmpeg, Anton/Inter fonts are in the image (`NODE_PATH=$(npm root -g)` for node scripts).
Read `getaway/state.json` → stop quietly if it isn't a production day (see Cadence). Check that the PC is reachable
(`mcp__remote-devices__Claude_Browser__tabs_context`); if not, notify the owner (PushNotification, Portuguese) and stop.

### 1. Topic and research
Take the next topic from `getaway/topics.json`. Do **6+ searches/fetches** on reliable sources (court records, FBI vault, major newspapers,
museum sites, books, Wikipedia only as a map to primary sources). Write down names, dates, numbers, quotes (short) and **what is disputed**.
Find the **twist** (the myth vs the record, the detail nobody remembers, the open question). That twist is the title, the thumbnail and the last line.

### 2. Script → `/home/claude/gc/script.json` (list of narration blocks, 1 block = 1 scene)
- **1,150 to 1,400 words** (8 to 10 min with the voice at +6%). 25 to 35 blocks of 30-60 words.
- Structure: cold open (first 15 s: the most shocking fact + "but the records say…"/question), the legend/setup, step by step (how the plan worked),
  the turning point, the evidence, what is still unknown (honest), the twist line, soft CTA ("Which part surprised you? Tell me in the comments.").
- Short sentences, concrete numbers, present-tense moments. No graphic detail. Attribute every disputed claim.
- Also write `/home/claude/gc/meta.json`: `title` (≤ 70 chars, concrete detail, no clickbait lies), `description` (2 hook lines, chapters added later, Sources list,
  "Narration and visuals were made with AI voice and code-generated animation.", 3 hashtags), `tags` (10-15), `thumb_lines` (≤ 4 words big + 1 small line).

### 3. Voice
```
mkdir -p /home/claude/gc && cp /home/claude/canais/getaway/engine/* /home/claude/gc/ && cd /home/claude/gc
python3 voice.py          # voice.wav, voice.json, timing.js
```
If edge-tts fails on certificates, check `SSL_CERT_FILE` / `/root/.ccr/ca-bundle.crt` (voice.py already loads it) and retry; if the proxy refuses
`speech.platform.bing.com`, notify the owner which domain to allow and stop.

### 4. Animation page → `/home/claude/gc/index.html`
Copy `example_abagnale.html` to `index.html` and rewrite the scenes for the new story (keep the CSS/helpers; one `.scene` per block or per 2 blocks;
sync every element to the narration with `W(b, 'word')`). Keep render(t) a pure function of time (no CSS animations, no timers).
Check before rendering: `NODE_PATH=$(npm root -g) node shot.cjs <8-12 times at the busiest moments>` then `python3 sheet.py sheet.jpg f_*.jpg` and **Read the sheet**.
Fix overlaps, cut text, empty frames. Repeat until clean.

### 5. Render, sound, thumbnail
```
NODE_PATH=$(npm root -g) node render.cjs     # 2 workers, ~25-35 min for 9 min: run in background and poll
# sfx.json: whoosh+glitch at each scene start, tick on checks/digits, thump on stamps, typing during typed text, rattle on counters
python3 mix.py && bash finish.sh             # long.mp4
```
Thumbnail: edit `thumb.html` (1280x720: one record/object on the left, 3-4 huge words on the right, orange keyword) → `node thumb.cjs` → Read `thumb.jpg`.
Check `long.mp4`: ffprobe duration (8-12 min, never over 15 min), extract 4 frames and Read them.
Chapters: build "0:00 Intro" + one line per section from `voice.json` block starts and put them in the description.

### 6. Cuts → 4 Shorts
Write `/home/claude/gc/cuts.json` (see `getaway/episodes/2026-11-27-abagnale/cuts.json`): 4 cuts of **25-45 s**, each made of 1-3 segments
`[t0, t1]` taken from block boundaries in `voice.json`, each standing alone with its own hook (2-3 lines, one *orange* word) and a strong last line.
Types: (1) the shocking number/fact, (2) the method step by step, (3) the evidence/record, (4) the twist or quote.
`python3 /home/claude/canais/getaway/cuts.py /home/claude/gc` → Read every `cuts/<slug>.jpg`.
Short titles: one concrete strange detail + "#Shorts" (e.g. "Inmate #25367: The Catch Me If You Can Con Man's Prison Card #Shorts").
Description: hook line, "Full story: {LONG_URL}", short sources line, AI line, 3 hashtags.

### 7. Publish (built-in browser on the owner's PC)
1. `upload_src.json` (see the Abagnale example): stamp `YYYYMMDD-<slug>`, items: long (file `long.mp4`, thumb `thumb.jpg`, `publish_at` D 15:00) and the 4 cuts
   with their `publish_at`. `python3 /home/claude/canais/getaway/publish.py /home/claude/gc /home/claude/canais` → puts files on branch **`media-getaway`**
   (never use `media`, which belongs to the other agent) and prints the upload.json URL.
2. **Don't disturb the other agent.** The You Were There POV agent uses the same built-in browser from 9:13. Before switching channel, check the Studio tab
   has no upload in progress (`ytcp-uploads-dialog` visible with "Envio em"/"Enviando"); if it has, wait (up to 20 min), then go on.
3. Switch Studio to The Getaway Case: avatar (top right) → **Mudar de conta** (click it for real: it opens a submenu) → **The Getaway Case**.
   Check `location.href` contains `UCr_vWFky1S1NzTMWirhhEIQ`.
4. Open `https://studio.youtube.com/channel/UCr_vWFky1S1NzTMWirhhEIQ/videos/upload?d=ud`, click once on the page (focus), paste `getaway/upload.js` as text
   with javascript_tool (CSP blocks eval), then for each item: `window.__res=null; gcUpload(ITEM).then(r=>window.__res=r).catch(e=>window.__res='ERR '+e); 'started'`
   and poll `window.__state+' | '+window.__res` (the JS tool times out at ~45 s). Upload the **long first**, then replace `{LONG_URL}` in the cuts' descriptions
   with its link (`https://youtu.be/<id>`), then the cuts. Reload the upload URL and paste upload.js again before each item.
   - **Before `gcSchedule` runs, take a screenshot** (`Claude_Browser__computer` screenshot): with the pane hidden the date calendar only renders after one.
     The safest way: when `window.__state` is `steps`, take a screenshot.
   - `gcSchedule` = time first (type + Enter + blur), then click the day in the calendar; it checks the model and throws if it didn't stick.
     **Never press Escape with the calendar closed** (it closes the upload dialog and the video becomes a draft).
   - If an item ends as **Rascunho** (draft): Conteúdo > Shorts/Vídeos → "Editar rascunho" → Avançar 3x → paste gcSchedule → take a screenshot →
     `gcSchedule(document.querySelector('ytcp-uploads-dialog'), 'YYYY-MM-DD HH:MM')` → click `#done-button` (Programar). If scheduling fails twice,
     publish it as Público right away (never leave a draft) and say so in the notification.
   - "Ainda estamos verificando seu conteúdo": click Ok, keep the dialog open until "Verificações concluídas", then click Programar.
5. Verify: Conteúdo > Vídeos shows the long as **Programado** for D 15:00 and Conteúdo > Shorts shows the 4 cuts **Programado** at their times.
6. **Switch Studio back to You Were There POV** (same menu) and check `location.href` contains `UCqNclACz0xvuvrYg3RP6BkQ`. Always, even after an error.

### 8. Wrap up
- Update `getaway/state.json`: `last_long` = D, append to `videos` {date, slug, kind:"long", title, url, publish_at} and one entry per cut (kind "cut").
- Save the episode sources in `getaway/episodes/<YYYY-MM-DD>-<slug>/` (script.json, voice.json, meta.json, cuts.json, upload_src.json, sfx.json, index.html).
- Commit on `main` and push (end the message with the attribution lines from the system reminder).
- One **PushNotification** in Portuguese: topic, long link + time, the 4 Shorts times.
- On a failure you can't fix in 2 tries: notify the owner in Portuguese with what failed and what is ready, switch Studio back to You Were There POV, stop.

## Notes
- Upload limit before phone verification: ~10/day; 5 uploads per production day is safe.
- Shorts must be ≤ 60 s and vertical; cuts.py makes 1080x1920 with word-by-word captions (Anton, spoken word in orange).
- Owner's channel profile (Portuguese): project doc `claude/canal-crime-real/perfil.md`.
