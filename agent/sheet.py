"""Contact sheet with index labels: python3 sheet.py <img_dir> <first> <last> <out.jpg>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
d, a, b, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
fs = [f"{d}/{i:03d}.jpg" for i in range(a, b + 1) if os.path.exists(f"{d}/{i:03d}.jpg")]
im0 = Image.open(fs[0]); w = 384; h = round(w * im0.height / im0.width); cols = 4
S = Image.new("RGB", (w * cols, h * ((len(fs) + cols - 1) // cols)))
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
for k, p in enumerate(fs):
    t = Image.open(p).resize((w, h)); ImageDraw.Draw(t).text((8, 6), os.path.basename(p)[:3], font=f, fill=(255, 255, 0), stroke_width=3, stroke_fill=(0, 0, 0))
    S.paste(t, ((k % cols) * w, (k // cols) * h))
S.save(out, quality=82)
