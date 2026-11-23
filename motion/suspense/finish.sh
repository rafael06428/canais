#!/bin/bash
# usage: bash finish.sh v4 outname   (after render + mix)
set -e; n=$1; out=$2; cd /home/claude/sus
ls scenes_$n/s*.mp4 | grep -v tmp | sort | sed "s/^/file '/; s/$/'/" > list_$n.txt
dur=$(python3 -c "import json;print(json.load(open('${n}_voice.json'))['dur'])")
ffmpeg -y -loglevel error -f concat -safe 0 -i list_$n.txt -c copy ${n}_video.mp4
ffmpeg -y -loglevel error -i ${n}_video.mp4 -i ${n}_mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart -t $dur ${n}_master.mp4
ffmpeg -y -loglevel error -i ${n}_master.mp4 -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p -c:a copy -movflags +faststart $out
ffprobe -v error -show_entries format=duration,size -of default=nw=1 $out
