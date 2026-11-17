#!/bin/bash
# Installs everything the daily agent needs in a fresh workspace.
pip install -q --break-system-packages edge-tts onnxruntime opencv-python-headless soundfile pillow numpy 2>&1 | grep -v WARNING
which ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg)
python3 -c "import edge_tts, onnxruntime, cv2, soundfile; print('setup ok')"
