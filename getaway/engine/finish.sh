#!/bin/bash
# Junta as partes do render com o áudio: long.mp4 (para o YouTube) e confere a duração.
# usage: bash finish.sh   (na pasta do episódio, depois de node render.cjs e python3 mix.py)
set -e
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy video.mp4
ffmpeg -y -loglevel error -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest -movflags +faststart long.mp4
ffprobe -v error -show_entries format=duration,size -of default=nw=1 long.mp4
