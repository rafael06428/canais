# Modelo de vídeo em animação gráfica (estilo "Endurance")

Vídeo 100% feito por código na nuvem do Claude: sem imagens de IA, sem computador do dono, sem custo.
Primeiro vídeo feito assim: "Endurance" (1:55, 1920x1080, 30 fps), em 22/11/2026.

## Arquivos deste modelo (nesta pasta; nos docs do projeto estão em `claude/modelo-animacao/` com sufixo `.txt`)
Salve cada um sem o sufixo `.txt` numa pasta de trabalho (ex.: /home/claude/video).
- `index.html.txt`  página 1920x1080 com as camadas das cenas e todo o CSS (paleta, tipografia, cards, HUD)
- `anim.js.txt`     a animação: linha do tempo GSAP pausada + `render(t)`; expõe `window.seek(t)` e `window.DUR`
- `build_map.mjs.txt` gera `data.js` (mapa real com d3-geo + world-atlas). Só para vídeos com mapa
- `render.cjs.txt`  filma a página: 2 workers, um mp4 por cena (JPEG q92 → ffmpeg), depois concat
- `shot.cjs.txt` + `sheet.py.txt`  capturam quadros-chave e montam folhas de contato para revisar
- `mix.py.txt`      mixa a narração com trilha ambiente e efeitos (usa agent/audio.py do repo)

## Passo a passo
1. `git clone --depth 1 https://github.com/rafael06428/canais` e `bash canais/agent/setup.sh` (edge-tts, ffmpeg).
   Na pasta de trabalho: `npm init -y && npm install gsap` (+ `d3-geo topojson-client world-atlas d3-delaunay` se tiver mapa).
2. Roteiro: blocos de narração (1 bloco = 1 cena). Narração com `python3 canais/agent/voice.py spec.json voice`
   (voz `en-US-AndrewMultilingualNeural`). ATENÇÃO: ele grava `voice.wav` e `voice.json`; não chame o spec de voice.json.
   O json traz o tempo de cada palavra: use esses tempos para sincronizar cada elemento com a fala.
3. Escreva `index.html` + `anim.js` para o novo tema, reaproveitando o CSS e os helpers do modelo.
4. Antes de renderizar tudo: `node shot.cjs <tempos...>` nos momentos mais cheios de cada cena,
   `python3 sheet.py saida f_*.jpg` e OLHE as folhas com Read. Corrija sobreposições e textos cortados.
5. `node render.cjs` (em segundo plano; ~8 min para 2 min de vídeo), depois:
   `ffmpeg -f concat -safe 0 -i list.txt -c copy video.mp4` e
   `ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -t <DUR> final.mp4`.
6. Confira duração (ffprobe) e quadros do arquivo final. Envie uma cópia leve (`-crf 23`) ao dono.

## Regras técnicas que evitam retrabalho
- Tudo é função pura do tempo: nada de CSS animation/transition nem setTimeout. `seek(t)` = `tl.seek(t,false)` + `render(t)`.
- GSAP só para opacidade e transform de HTML. Transform de SVG, viewBox (câmera), contadores e traçado de rotas: à mão no `render(t)`.
- Playwright: `require('playwright')` em arquivo .cjs (import ESM não acha o pacote global). Chromium já vem instalado.
- Desempenho: caminho SVG pesado custa ~0,5 s por quadro. Use litoral 50m (10m só em recortes pequenos) e
  `display:none` nas camadas totalmente cobertas. Alvo: menos de 0,2 s por quadro.
- Câmera do mapa = viewBox animado; larguras de traço e rótulos usam a variável CSS `--ik` (1/zoom) para manter tamanho de tela.
- Cortes entre cenas caem em quadro exato da mesma linha do tempo, então o concat com `-c copy` fica sem emenda.

## Estilo visual (mantenha para a identidade do canal)
- Paleta: fundo azul-noite #06131f, gelo #e6f1f6, destaque laranja #ff6b3d, ciano #7fd6ff, texto secundário #9dbccd.
- Fontes: Anton (títulos e números, caixa alta) + Inter (apoio). Já instaladas no ambiente.
- Card à esquerda com barra laranja: chamada pequena em laranja, título grande em Anton, uma linha de apoio.
- HUD: marca no canto superior esquerdo, data/contador no direito, linha do tempo embaixo com eventos que acendem.
- Uma ideia por tela, números grandes com contagem, rotas que se desenham, vinheta escura, partículas leves.
- Um momento "ilustrado" por vídeo (no Endurance: o navio em silhueta sendo esmagado) para quebrar o ritmo dos mapas.
- Som: narração + trilha ambiente gerada + poucos efeitos pontuais nas viradas.

## Motor novo: vídeos de suspense e crime real (pasta `motion/suspense/` do repositório)
Os 4 testes de suspense (Voo 19, D.B. Cooper, The Tell-Tale Heart, sinal Wow!) usam um motor mais simples, sem GSAP.
Ele só existe no repositório rafael06428/canais, ramo `claude/modelo-animacao`, pasta `motion/suspense/`:
- `lib.js` + `base.css`: motor comum (trilhas de valores, cenas, cards, contadores, máquina de escrever, carimbo, partículas, câmera de mapa)
- `vN.html`: um vídeo por arquivo (v2 = D.B. Cooper é a referência para crime real); `vN_spec.json`: a narração de cada um
- `mapkit.mjs` + `build_vN.mjs`: geram `vN_map.js` quando o vídeo tem mapa
- `render.cjs`, `shot.cjs`, `sheet.py`, `mix.py`, `finish.sh`: capturar quadros, renderizar, mixar o áudio e fechar o arquivo

Como usar (os scripts esperam a pasta /home/claude/sus):
1. Copie `motion/suspense/` para /home/claude/sus; lá: `npm init -y && npm install d3-geo topojson-client world-atlas`.
2. Narração: `python3 canais/agent/voice.py vN_spec.json vN_voice`, depois gere `vN_timing.js` com `window.TIMING=<conteúdo de vN_voice.json>;`.
3. `OUT=quadros node shot.cjs vN <tempos>` e `python3 sheet.py quadros/folha quadros/f_*.jpg` para revisar antes de renderizar.
4. `node render.cjs vN`, `python3 mix.py vN '<marcas>' '<efeitos>'`, `bash finish.sh vN saida.mp4`.
No código do vídeo, `W(bloco, 'palavra')` devolve o instante em que a narração diz aquela palavra: use para sincronizar tudo.

## Roteiros de suspense já escritos
Documento "Roteiros de suspense: 4 testes": https://claude.ai/artifact/JnNPpUfqQzDabAiT4nT3tA
(histórias famosas: Voo 19 / Triângulo das Bermudas, D.B. Cooper, "The Tell-Tale Heart" de Poe, sinal "Wow!"). Narração e textos de tela em inglês; relatórios ao dono em português.
