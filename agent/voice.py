"""Narration with Microsoft Edge neural voices (free) + word timings.

usage: python3 voice.py <text_json> <out_base>
  text_json: {"voice": "...", "rate": "+0%", "blocks": [{"id": .., "text": ".."}, ...]}
  writes <out_base>.wav (24 kHz mono) and <out_base>.json:
  {"dur": s, "words": [[word, t0, t1, block_index]], "blocks": [[t0, t1]]}
"""
import asyncio, io, json, os, subprocess, sys
import numpy as np, soundfile as sf

SR = 24000
GAP_BLOCK = 0.55   # pause between blocks (scenes)
PROXY = os.environ.get("HTTPS_PROXY") or None


async def synth(text, voice, rate):
    import edge_tts
    last = None
    for attempt in range(4):
        try:
            com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary", proxy=PROXY)
            audio = bytearray(); words = []
            async for ch in com.stream():
                if ch["type"] == "audio":
                    audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    t0 = ch["offset"] / 1e7; words.append([ch["text"], t0, t0 + ch["duration"] / 1e7])
            if not audio:
                raise RuntimeError("empty audio")
            return bytes(audio), words
        except Exception as e:  # network hiccup: retry
            last = e; await asyncio.sleep(3 * (attempt + 1))
    raise last


def fake(text):
    """Offline test voice (Kokoro, if present locally). Not used in production."""
    from kokoro_onnx import Kokoro
    global _k
    if "_k" not in globals(): _k = Kokoro(os.environ["VOICE_FAKE"] + "/kokoro.onnx", os.environ["VOICE_FAKE"] + "/voices.bin")
    a, _ = _k.create(text, voice="am_michael", speed=1.0, lang="en-us"); a = a.astype(np.float32)
    d = len(a) / SR; ws = text.split(); L = sum(len(w) + 1 for w in ws); c = 0; words = []
    for w in ws:
        t0 = d * c / L; c += len(w) + 1; words.append([w.strip('.,?!;:"'), t0, d * c / L])
    return a, words


def mp3_to_np(b):
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "-", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       input=b, capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def trim(a, words):
    """Trim leading/trailing silence; shift word times accordingly."""
    nz = np.where(np.abs(a) > 0.008)[0]
    if not len(nz):
        return a, words
    s = max(0, nz[0] - 600); e = min(len(a), nz[-1] + 1800)
    off = s / SR
    return a[s:e], [[w, max(0, t0 - off), max(0, t1 - off)] for w, t0, t1 in words]


def norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def align(text, words):
    """Give each original token (with its punctuation) the timing of the matching spoken word."""
    toks = text.split(); out = []; j = 0
    for tk in toks:
        n = norm(tk); hit = None
        for k in range(j, min(j + 4, len(words))):
            wn = norm(words[k][0])
            if wn and n and (n.startswith(wn) or wn.startswith(n)):
                hit = k; break
        if hit is None:
            if out: out[-1][0] += " " + tk if not n else ""
            if n:
                t = out[-1][2] if out else 0.0
                out.append([tk, t, t + 0.25])
            continue
        t0, t1 = words[hit][1], words[hit][2]
        while hit + 1 < len(words) and n.startswith(norm(tk[:0]) + "".join(norm(w[0]) for w in words[hit:hit + 2])):
            hit += 1; t1 = words[hit][2]
        out.append([tk, t0, t1]); j = hit + 1
    return out


def build(spec, out):
    voice = spec.get("voice", "en-US-AndrewMultilingualNeural"); rate = spec.get("rate", "+0%")
    lead = spec.get("lead", 0.25)
    parts = [np.zeros(int(SR * lead), np.float32)]; t = lead; allw = []; spans = []
    for bi, b in enumerate(spec["blocks"]):
        if os.environ.get("VOICE_FAKE"):
            a, words = fake(b["text"])
        else:
            mp3, words = asyncio.run(synth(b["text"], voice, rate))
            a, words = trim(mp3_to_np(mp3), words)
        words = align(b["text"], words)
        d = len(a) / SR
        allw += [[w, t + t0, t + t1, bi] for w, t0, t1 in words]
        spans.append([t, t + d]); parts.append(a); t += d
        g = b.get("gap", spec.get("gap", GAP_BLOCK))
        if bi == len(spec["blocks"]) - 1: g = spec.get("tail", g)
        parts.append(np.zeros(int(SR * g), np.float32)); t += g
        print(f"voice {bi + 1}/{len(spec['blocks'])} {d:.1f}s", flush=True)
    a = np.concatenate(parts); a = a / max(1e-6, np.abs(a).max()) * 0.92
    sf.write(out + ".wav", a, SR)
    json.dump({"dur": len(a) / SR, "words": allw, "blocks": spans}, open(out + ".json", "w"), ensure_ascii=False)
    print("voice done", round(len(a) / SR, 1), "s", len(allw), "words")


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
