"""Optional developer helper: Pillow draws only original synthetic text cards."""
import argparse,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from sample_cases import BENCH_TITLE,BENCH,PRODUCT
p=argparse.ArgumentParser();p.add_argument('--font',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]/'examples/media';root.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype(a.font,29);small=ImageFont.truetype(a.font,23);title=ImageFont.truetype(a.font,40)
for name,heading,body in [('benchmark','原创虚拟对标',BENCH),('product','原创虚拟商品资料',PRODUCT)]:
    im=Image.new('RGB',(780,1080),'#f5f3ed');draw=ImageDraw.Draw(im);draw.rounded_rectangle((28,28,752,1052),24,fill='#ffffff',outline='#cbd8c9',width=2)
    draw.text((65,65),'仅用于功能演示 · 非真实笔记',font=small,fill='#66776b');draw.text((65,125),heading,font=title,fill='#203c34')
    y=220
    for paragraph in body.splitlines():
        for line in textwrap.wrap(paragraph,21):draw.text((65,y),line,font=font,fill='#203c34');y+=48
        y+=20
    draw.text((65,980),'无真实账号、用户截图或商业数据',font=small,fill='#66776b');im.save(root/(name+'.png'))
