import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; fs=sys.argv[2:]
cols=2; w,h=960,540
rows=(len(fs)+cols-1)//cols
S=Image.new('RGB',(w*cols,h*rows),'black')
d=ImageDraw.Draw(S)
for i,f in enumerate(fs):
    im=Image.open(f).resize((w,h)); S.paste(im,((i%cols)*w,(i//cols)*h)); d.text(((i%cols)*w+10,(i//cols)*h+10),f,fill='yellow')
S.save(out,quality=85)
