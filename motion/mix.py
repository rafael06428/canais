import sys, json, numpy as np, soundfile as sf
sys.path.insert(0, '/home/claude/canais/agent')
import audio
SR = audio.SR
audio.mix('voice.wav', 'timing.json', 'mix0.wav', [12.0, 24.6, 35.2, 38.9, 49.3, 66.0, 81.4, 98.5, 102.8], tail=0.004, fade=False)
m, sr = sf.read('mix0.wav', dtype='float32'); n = len(m); rng = np.random.default_rng(5)
def add(t, x, g=1.0):
    s = int(t * SR); e = min(n, s + len(x)); m[s:e] += x[:e - s] * g
def crack(dur=0.9, seed=0):
    r = np.random.default_rng(seed); k = int(SR * dur); x = r.normal(0, 1, k + 40)
    hi = x[:k] - audio.lp_fast(x, 20)[:k]; lo = audio.lp_fast(x, 40)[:k]
    tt = np.arange(k) / SR
    env = np.exp(-tt / 0.05) + 0.35 * np.exp(-tt / 0.3) * (r.random(k) > 0.985).cumsum().clip(0, 1)
    thump = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt / 0.25)
    y = hi / np.abs(hi).max() * env * 0.5 + lo / np.abs(lo).max() * np.exp(-tt / 0.12) * 0.5 + thump * 0.6
    return y.astype(np.float32)
def groan(dur=2.6, f0=70, f1=38):
    k = int(SR * dur); tt = np.arange(k) / SR; f = np.linspace(f0, f1, k); ph = 2 * np.pi * np.cumsum(f) / SR
    return ((np.sin(ph) + 0.4 * np.sin(2.01 * ph)) * np.sin(np.pi * tt / dur) ** 2).astype(np.float32)
def ping(dur=1.8, f=1150):
    k = int(SR * dur); tt = np.arange(k) / SR; y = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.35)
    d = int(SR * 0.33); y[d:] += 0.35 * y[:-d]; return y.astype(np.float32)
add(40.85, crack(seed=1), 0.30); add(42.05, crack(1.1, seed=2), 0.36); add(39.4, groan(), 0.10); add(46.0, groan(2.8, 60, 30), 0.16)
add(103.9, ping(), 0.05); add(106.4, ping(), 0.045); add(108.9, ping(f=1300), 0.05)
f = int(SR * 1.6); m[-f:] *= np.linspace(1, 0, f)
m = m / max(1e-6, np.abs(m).max()) * 0.93
sf.write('mix.wav', m, SR); print('mix', round(n / SR, 2), 's')
