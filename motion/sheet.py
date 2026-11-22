import sys, glob
from PIL import Image, ImageDraw
files = sorted(sys.argv[2:], key=lambda f: float(f.split('f_')[1][:-4]))
per = 6
for s in range(0, len(files), per):
    chunk = files[s:s+per]; W, H = 960, 540
    im = Image.new('RGB', (W*2, H*3), 'black'); d = ImageDraw.Draw(im)
    for i, f in enumerate(chunk):
        t = Image.open(f).resize((W, H), Image.LANCZOS); x, y = (i % 2)*W, (i//2)*H; im.paste(t, (x, y)); d.rectangle([x, y, x+90, y+26], fill='black'); d.text((x+6, y+6), f.split('f_')[1][:-4], fill='yellow')
    im.save(f"{sys.argv[1]}_{s//per}.jpg", quality=85)
