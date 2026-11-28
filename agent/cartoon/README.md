# Cartoon style (default since 2026-11-25)

Round-head cartoon characters, flat backgrounds with a soft blur, a date badge in the top-right corner,
a red chapter banner, a speech bubble now and then, and big captions where the spoken word turns yellow.
Everything is drawn by code (SVG in Chromium), so it needs no image generation and no image quota.
First episode: "24 Hours in the Great Storm of 1703" (2026-11-25). Example episode file: `episodes/2026-11-25-great-storm-1703.json`
(and its builder script `episodes/2026-11-25-great-storm-1703.build.py`, the easiest way to write a new one).

## Build
```
cd /home/claude/canais/agent/cartoon
python3 cartoon.py /home/claude/ep voice && python3 cartoon.py /home/claude/ep audio && python3 cartoon.py /home/claude/ep srt
python3 cartoon.py /home/claude/ep data          # Short narrations + cartoon/data.js (re-run after every episode.json edit)
python3 cartoon.py /home/claude/ep shots         # one frame per scene -> shots/sheet_NN.jpg: READ THEM ALL and fix
python3 cartoon.py /home/claude/ep thumb
WORKERS=2 python3 cartoon.py /home/claude/ep long   # ~0.45 s per frame per worker on 2 CPUs: ~65 min for 10 min of video. Run in background.
python3 cartoon.py /home/claude/ep shorts        # ~4 min per Short
```
Spot checks: `node <ep>/cartoon/render.cjs <ep> shots <outdir> <t1> <t2> ...` (long, seconds) and
`node <ep>/cartoon/render.cjs <ep> sshots <k> <outdir> <t1> ...` (Short k). Then `publish.py` exactly as before.
After a text change, delete voice.json, music.wav, subs.srt and the Shorts' voice.json/music.wav so they are rebuilt.

## episode.json
Same fields as the image pipeline (title, title_yt, description with {CHAPTERS}, tags, thumb_text, title_card, chapters, shorts),
plus `"style": "cartoon"`, and:
- each scene: `{"text": "...", "v": {...visual...}}` (no "prompt")
- `thumb_scene` (scene index), `thumb_t` (seconds into that scene), `thumb_dx` (shift its items right to make room for the text)
- each Short block: `{"text", "prompt": null, "src": <long scene index>, "fx": <optional x to centre the 9:16 crop>}`.
  The last block (the loop) automatically shows the first block's picture.
- **Standalone Short** (a story that is not in the long video): give each block its own `"v"` object (same format as a scene) instead of `"src"`,
  and `"focus"` inside it for the 9:16 crop. You can mix: some blocks with `"src"`, some with `"v"`. Add `"footer"` to the Short.

### The "v" object
`{"bg": ..., "items": [...], "time": "day|dusk|night|dawn|grey", "storm": 0-3, "fx": [...], "badge": ["NOV 26, 1703", "8 AM"],
  "bubble": {"text", "x", "y", "at", "tail": "left|right|center"}, "bubble2": {...}, "cam": "in|out|left|right|zoom|none", "focus": 640, "cut": true}`
- World is 1280x720. People stand with their feet at y≈600-640. `focus` = x the Shorts crop centres on.
- `badge` persists until another scene sets one. `null` sub-line is allowed.
- Any number can be the string `"@word"`: the moment that word is spoken in this scene (e.g. `"at": "@swallower"`).
- `storm` 2-3 adds rain, wind lines, rolling deck, big swells (outdoors only). `fx`: wind, rain, lightning, spray, shake, snow, ash, sepia, night.
- `shakeAt`: seconds; `zoomAt` with cam "zoom".

Backgrounds (`bg`): sea, sands, deck, below (between decks), beach (coastal town), london (rooftops city), river, cellar, room
(`wall`, `fireplace`, `winX`), desk (study with books), fields (`flood`: 0-1), underwater, church, black, plain (`color`).
Add new ones in `engine.js` → `BG` (keep the flat style: solid fills, #1a1a1a outlines, 4 px).

Items (`k`):
- `p` person: `role` (you, sailor, sailor2, officer, admiral, townsman, boatman, woman, maid, queen, defoe, winstanley, bishop, wife, diver, modern;
  `look` overrides colours: coat, dress, capc, hair, wig, hat...), `x`, `y` (feet), `s`, `face` (calm, worry, shock, stern, sad, happy, sleep, look),
  `pose` (idle, walk, run, point, armsup, cheer, cling, wave, write, pray, hold, row, cover, sit, kneel, sleep), `flip`, `enter` ("left"/"right"),
  `dx`+`dxDur` (walk across), `shiver`, `lean`. Add roles in `ROLES` for new eras (e.g. Roman tunic, 1940s soldier).
- `ship` (3-masted, `tilt`, `tiltDur`, `broken` masts 0-3, `sink` 0-1 + `sinkAt`, `sails` furled/set, `lights`, `dx`), `boat`, `roofs`
  (`n`, `fall`: list of times per house), `tree` (`fallAt`), `windmill` (`speed`, `fireAt`), `lighthouse` (`goneAt`), `bed`, `table`,
  `candle`, `lantern`, `paper` (title, sub, at, rot), `text` (big word: text, sub, fs, y, c, at), `count` (animated number: to, pre, post, at, dur),
  `gauge` (barometer: from/to 0-1), `rope` (`snapAt`), `cannon`, `wave` (a big wave crossing the screen), `debris`, `flag`, `raw` (any SVG).
- Every item accepts `from`/`until` (seconds) to appear/disappear inside the scene.

## Rules that keep it looking good
- One idea per scene, at most 3 characters, the "you" character in about half the scenes (same role every time).
- Use a speech bubble or a big word/number in roughly every third scene: it is what makes this style watchable.
- Keep text in bubbles short (≤ 18 characters) and big words ≤ 20 characters.
- Nothing graphic: deaths happen off screen (sinking ships, a cut to black, a number).
- Look at every contact sheet before rendering: overlapping people, text off screen, rain indoors, wrong badge.
