"""Mix narration with a generated dark ambient bed, low rumble and whooshes on chapter changes.

usage: python3 audio.py <voice.wav> <voice.json> <out.wav> [chapter_times_json]
"""
import json, sys
import numpy as np, soundfile as sf

SR = 24000


def lp_fast(x, k):  # moving-average low-pass (fast)
    c = np.cumsum(np.concatenate([[0], x])); return (c[k:] - c[:-k]) / k


def bed(n, seed=3):
    t = np.arange(n) / SR; rng = np.random.default_rng(seed)
    chords = [(110.0, 130.81, 164.81), (98.0, 123.47, 146.83), (87.31, 110.0, 130.81), (103.83, 130.81, 155.56)]
    pad = np.zeros(n, np.float32); seg = int(SR * 16)
    for s in range(0, n, seg):
        e = min(n, s + seg + SR * 2); tt = t[s:e]; ch = chords[(s // seg) % 4]
        env = np.clip(np.minimum((tt - tt[0]) / 3, (tt[-1] - tt) / 3), 0, 1)
        for f in ch:
            for det in (-0.6, 0.6):
                pad[s:e] += (np.sin(2 * np.pi * (f + det) * tt) * 0.5 + np.sin(2 * np.pi * (f / 2 + det) * tt) * 0.3) * env
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * t / 23)
    noise = rng.normal(0, 1, n + 400).astype(np.float32)
    rumble = lp_fast(lp_fast(noise, 200)[:n + 200], 200)[:n]
    rumble /= max(1e-6, np.abs(rumble).max())
    air = lp_fast(noise, 12)[:n]; air /= max(1e-6, np.abs(air).max())
    return pad / max(1e-6, np.abs(pad).max()) * 0.09 + rumble * 0.07 + air * 0.006


def whoosh(n_len=1.4, seed=0):
    n = int(SR * n_len); rng = np.random.default_rng(seed); x = rng.normal(0, 1, n + 60)
    w = lp_fast(x, 30)[:n] - lp_fast(x, 60)[:n]
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    boom = np.sin(2 * np.pi * 48 * np.arange(n) / SR) * np.exp(-np.arange(n) / (SR * 0.5))
    return (w / max(1e-6, np.abs(w).max()) * env * 0.16 + boom * 0.22 * (np.arange(n) > n * 0.45)).astype(np.float32)


def mix(vwav, vjson, out, marks=None, tail=1.0, fade=True):
    v, sr = sf.read(vwav, dtype="float32"); assert sr == SR
    pad = int(SR * tail); n = len(v) + pad; v = np.concatenate([v, np.zeros(pad, np.float32)])
    b = bed(n)
    # duck the bed under speech
    env = lp_fast(np.abs(v), 2400); env = np.concatenate([env, np.zeros(n - len(env), np.float32)])
    duck = 1 - 0.45 * np.clip(env / (env.max() * 0.25 + 1e-6), 0, 1)
    m = v * 0.95 + b * duck
    for k, t in enumerate(marks or []):
        s = max(0, int((t - 0.9) * SR)); w = whoosh(seed=k); e = min(n, s + len(w)); m[s:e] += w[:e - s]
    if fade:
        f = int(SR * 2); m[-f:] *= np.linspace(1, 0, f)
    m = m / max(1e-6, np.abs(m).max()) * 0.93
    sf.write(out, m, SR)


if __name__ == "__main__":
    marks = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else []
    mix(sys.argv[1], sys.argv[2], sys.argv[3], marks)
    print("audio done")
