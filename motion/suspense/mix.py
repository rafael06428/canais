# usage: python3 mix.py v4 '<marks json>' '<sfx json>'   sfx: [[t, type, gain, {opts}], ...]
import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, '/home/claude/canais/agent'); import audio
SR = audio.SR; name = sys.argv[1]; marks = json.loads(sys.argv[2]); sfx = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []
audio.mix(f'{name}_voice.wav', f'{name}_voice.json', f'{name}_mix0.wav', marks, tail=0.004, fade=False)
m, _ = sf.read(f'{name}_mix0.wav', dtype='float32'); n = len(m)
def add(t, x, g=1.0):
    s = int(t * SR); e = min(n, s + len(x));
    if s < n: m[s:e] += x[:e - s] * g
def tt(d): return np.arange(int(SR * d)) / SR
def noise(k, seed): return np.random.default_rng(seed).normal(0, 1, k)
def crack(d=0.9, seed=1, **_):
    t = tt(d); k = len(t); x = noise(k + 40, seed); hi = x[:k] - audio.lp_fast(x, 20)[:k]; lo = audio.lp_fast(x, 40)[:k]
    return hi / np.abs(hi).max() * np.exp(-t / .05) * .5 + lo / np.abs(lo).max() * np.exp(-t / .12) * .5 + np.sin(2 * np.pi * 55 * t) * np.exp(-t / .25) * .6
def thump(d=1.4, f=46, **_): t = tt(d); return np.sin(2 * np.pi * f * t * (1 - .15 * t / d)) * np.exp(-t / .35)
def groan(d=2.6, f0=70, f1=38, **_): t = tt(d); ph = 2 * np.pi * np.cumsum(np.linspace(f0, f1, len(t))) / SR; return (np.sin(ph) + .4 * np.sin(2.01 * ph)) * np.sin(np.pi * t / d) ** 2
def ping(d=1.8, f=1150, **_): t = tt(d); y = np.sin(2 * np.pi * f * t) * np.exp(-t / .35); k = int(SR * .33); y[k:] += .35 * y[:-k]; return y
def tone(d=6.0, f=420, **_): t = tt(d); return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.sin(np.pi * t / d) ** 2
def static(d=2.0, seed=3, **_): t = tt(d); k = len(t); x = noise(k + 30, seed); y = x[:k] - audio.lp_fast(x, 14)[:k]; return y / np.abs(y).max() * np.clip(np.minimum(t / .08, (d - t) / .25), 0, 1) * (.75 + .25 * np.sin(2 * np.pi * 7 * t))
def wind(d=6.0, seed=4, **_): t = tt(d); k = len(t); x = noise(k + 300, seed); y = audio.lp_fast(x, 90)[:k]; return y / np.abs(y).max() * np.sin(np.pi * t / d) ** 1.5 * (.7 + .3 * np.sin(2 * np.pi * .4 * t))
def beat():  # one lub-dub
    t = tt(.5); return np.sin(2 * np.pi * 52 * t) * np.exp(-t / .045) + .7 * np.concatenate([np.zeros(int(SR * .16)), (np.sin(2 * np.pi * 62 * t) * np.exp(-t / .04))[:len(t) - int(SR * .16)]])
def heart(d=8.0, bpm0=60, bpm1=120, g0=.3, g1=1.0, **_):
    out = np.zeros(int(SR * d), np.float32); b = beat(); t = 0.0
    while t < d - .5:
        u = t / d; s = int(t * SR); e = min(len(out), s + len(b)); out[s:e] += b[:e - s] * (g0 + (g1 - g0) * u); t += 60.0 / (bpm0 + (bpm1 - bpm0) * u)
    return out
G = dict(crack=crack, thump=thump, groan=groan, ping=ping, tone=tone, static=static, wind=wind, heart=heart)
for item in sfx:
    t, typ, g = item[0], item[1], item[2]; o = item[3] if len(item) > 3 else {}
    add(t, G[typ](**o).astype(np.float32), g)
f = int(SR * 1.6); m[-f:] *= np.linspace(1, 0, f); m = m / max(1e-6, np.abs(m).max()) * .93
sf.write(f'{name}_mix.wav', m, SR); print('mix', name, round(n / SR, 2), 's')
