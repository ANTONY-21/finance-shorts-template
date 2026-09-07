#!/usr/bin/env python3
"""Topic-aware card generator for daily factory videos (720x1280, brand style).
Reads script_lines.json → renders one card per beat with the same navy/orange brand."""
import json, os, sys, re
from PIL import Image, ImageDraw, ImageFont

base = sys.argv[1]
lines = json.load(open(f'{base}/script_lines.json'))
out = f'{base}/cards_v6'
os.makedirs(out, exist_ok=True)
W, H = 720, 1280
NAVY=(13,17,32); ORANGE=(255,122,24); GOLD=(255,184,28); WHITE=(245,247,250); GREY=(120,130,145)
F = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
def font(sz, b=True): return ImageFont.truetype(F if b else FR, sz)
def ctext(d, y, t, f, c):
    bb = d.textbbox((0,0), t, font=f); d.text(((W-bb[2])//2, y), t, font=f, fill=c)
def wrap(d, t, f, maxw):
    words, rows, cur = t.split(), [], ""
    for w in words:
        test = (cur+" "+w).strip()
        if d.textbbox((0,0), test, font=f)[2] <= maxw: cur = test
        else: rows.append(cur); cur = w
    if cur: rows.append(cur)
    return rows[:4]

def card(name, kicker, kicker_col, body, body_col=WHITE):
    img = Image.new('RGB', (W,H), NAVY); d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,8], fill=ORANGE)
    ctext(d, 160, kicker.upper()[:24], font(46), kicker_col)
    y = 340
    for row in wrap(d, body, font(52), W-120):
        ctext(d, y, row, font(52), body_col); y += 84
    d.text((60, H-70), "Sources on screen · Not financial advice", font=font(22, False), fill=GREY)
    img.save(f'{out}/{name}.jpg', quality=92)

kinds = ["hook","number","title","context","compare","take","rule1","rule2","rule3","risk","verdict","cta"]
cols = {"hook":GOLD,"number":(46,204,113),"title":GOLD,"risk":(255,68,68),"verdict":GOLD,"cta":ORANGE}
for i, line in enumerate(lines):
    kind = kinds[i] if i < len(kinds) else "context"
    text = re.sub(r'^(Hook|Big Callout|Title Question|Context|Comparison|Honest Take|Rule \d|Risk|Verdict|CTA)[:?]\s*', '', line).strip()
    card(f'b{i+1:02d}', kind, cols.get(kind, GREY), text)
print(len(lines), "cards →", out)
