"""Narração (edge-tts, voz en-US-AndrewMultilingualNeural) com o tempo de cada palavra.

usage: python3 voice.py   (na pasta do episódio, com script.json = lista de blocos de texto em inglês)
Gera voice.wav (48 kHz mono), voice.json {"total", "blocks": [{"start","dur","text","words":[{"w","t","d"}]}]}
e timing.js (window.TIMING=...) para a página de animação.
Cada bloco = uma cena. Pausa de GAP s entre blocos.
"""
import ssl, os, json, asyncio, subprocess
import edge_tts.communicate as c

c._SSL_CTX = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt") \
    if os.path.exists(os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt") else c._SSL_CTX
import edge_tts

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "+6%"
GAP = 0.45
PROXY = os.environ.get("HTTPS_PROXY") or None


async def block(i, text):
    last = None
    for attempt in range(10):   # o serviço da Edge às vezes derruba conexões: tenta de novo
        try:
            try:
                com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary", proxy=PROXY)
            except TypeError:
                com = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
            words, audio = [], bytearray()
            async for ch in com.stream():
                if ch["type"] == "audio": audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    words.append({"w": ch["text"], "t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7})
            if not audio: raise RuntimeError("empty audio")
            open(f"b{i}.mp3", "wb").write(audio)
            return words
        except Exception as e:
            last = e; await asyncio.sleep(2 + 2 * attempt)
    raise last


async def main():
    blocks = json.load(open("script.json"))
    out, t0, parts = [], 0.0, []
    for i, text in enumerate(blocks):
        words = await block(i, text)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"b{i}.mp3", "-ar", "48000", "-ac", "1", f"b{i}.wav"], check=True)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"b{i}.wav"]).decode())
        out.append({"start": t0, "dur": dur, "text": text, "words": [{**w, "t": w["t"] + t0} for w in words]})
        parts.append(f"b{i}.wav"); t0 += dur + GAP
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(GAP), "gap.wav"], check=True)
    open("concat.txt", "w").write("".join(f"file '{p}'\nfile 'gap.wav'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-ar", "48000", "-ac", "1", "voice.wav"], check=True)
    V = {"total": t0, "blocks": out}
    json.dump(V, open("voice.json", "w"), indent=1)
    open("timing.js", "w").write("window.TIMING=" + json.dumps(V) + ";")
    print("total", round(t0, 2), "s,", len(out), "blocks")


asyncio.run(main())
