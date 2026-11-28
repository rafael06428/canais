"""Trilha ambiente + efeitos gerados por código + narração -> mix.wav (loudnorm -15 LUFS).

usage: python3 mix.py   (na pasta do episódio: voice.wav, voice.json, sfx.json)
sfx.json: lista de eventos [{"t": 12.3, "fx": "whoosh|tick|thump|glitch|typing|rattle", "g": 1.0, "d": 1.2}]
  - typing e rattle usam "d" (duração em s); os outros ignoram.
  - Sugestão: whoosh+glitch em cada corte de cena, tick nos checks/dígitos, thump em carimbos/impactos,
    typing junto com textos que se digitam, rattle em contadores que sobem.
Duração final = total da narração + 1,2 s.
"""
import json, subprocess, wave
import numpy as np

SR = 48000
T = json.load(open("voice.json"))
DUR = T["total"] + 1.2
N = int(DUR * SR)
rng = np.random.default_rng(7)
t = np.arange(N) / SR


def env(n, a, r):
    e = np.ones(n); a = min(a, n); r = min(r, n)
    e[:a] = np.linspace(0, 1, a); e[n - r:] *= np.linspace(1, 0, r); return e


# música: drone grave + pad + pulso lento (suspense)
drone = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 82.4 * t) + 0.15 * np.sin(2 * np.pi * 110.3 * t)
drone *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
pad = 0.12 * np.sin(2 * np.pi * 329.6 * t + 0.4 * np.sin(2 * np.pi * 0.3 * t)) + 0.1 * np.sin(2 * np.pi * 392 * t)
pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t + 1)
pulse = np.zeros(N); beat = 60 / 92; kn = int(0.35 * SR); kt = np.arange(kn) / SR
kick = np.sin(2 * np.pi * (45 + 70 * np.exp(-kt * 25)) * kt) * np.exp(-kt * 9)
for k in range(0, int(DUR / beat), 2):
    s = int(k * beat * SR)
    if s + kn < N: pulse[s:s + kn] += kick * 0.9
music = (drone * 0.25 + pad * 0.6 + pulse * 0.35) * env(N, int(1.5 * SR), int(2.5 * SR)) * 0.32

fx = np.zeros(N)


def add(sig, at, g=1.0):
    s = int(at * SR)
    if s < 0: sig = sig[-s:]; s = 0
    e = min(N, s + len(sig))
    if e > s: fx[s:e] += sig[:e - s] * g


def whoosh(d=0.55):
    n = int(d * SR); x = rng.standard_normal(n); sw = np.linspace(0.02, 0.25, n) ** 1.5
    y = np.empty(n); acc = 0.0
    for i in range(n): acc += sw[i] * (x[i] - acc); y[i] = acc
    return y * np.sin(np.linspace(0, np.pi, n)) ** 2 * 1.4


def tick():
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 120) * 0.5


def thump(d=0.6, f0=55):
    n = int(d * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * (f0 + 90 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 6) + 0.25 * rng.standard_normal(n) * np.exp(-tt * 40)


def glitch(d=0.22):
    n = int(d * SR); x = np.zeros(n)
    for k in range(0, n, int(0.02 * SR)):
        f = rng.uniform(300, 3000); m = min(n, k + int(0.015 * SR)); tt = np.arange(m - k) / SR
        x[k:m] = np.sign(np.sin(2 * np.pi * f * tt)) * 0.25
    return x * env(n, 50, 400)


def click():
    n = int(0.018 * SR); tt = np.arange(n) / SR
    return rng.standard_normal(n) * np.exp(-tt * 400) * 0.35


WH = whoosh()
for ev in json.load(open("sfx.json")):
    a, g, k = ev["t"], ev.get("g", 1.0), ev["fx"]
    if k == "whoosh": add(WH, a - 0.3, 0.55 * g)
    elif k == "glitch": add(glitch(), a, 0.5 * g)
    elif k == "tick": add(tick(), a, g)
    elif k == "thump": add(thump(), a, 0.8 * g)
    elif k == "typing":
        x = a
        while x < a + ev.get("d", 1.0): add(click(), x + rng.uniform(-0.01, 0.01), g); x += 0.07 * rng.uniform(0.7, 1.3)
    elif k == "rattle":
        x = a
        while x < a + ev.get("d", 1.0): add(tick(), x, 0.25 * g); x += 0.05
fx *= 0.5

with wave.open("voice.wav") as wf:
    v = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64) / 32768
vo = np.zeros(N); vo[:min(N, len(v))] = v[:N]
win = int(0.25 * SR)
sm = np.convolve(np.abs(vo), np.ones(win) / win, mode="same")
mix = vo + music * (1 - 0.45 * np.clip(sm * 12, 0, 1)) + fx
mix /= max(1e-9, np.max(np.abs(mix))) / 0.92
with wave.open("mix_raw.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "mix_raw.wav", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", "48000", "mix.wav"], check=True)
print("mix ok", round(DUR, 2))
