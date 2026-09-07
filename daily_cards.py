#!/usr/bin/env python3
"""Topic-aware card generator for daily factory videos (720x1280, brand style).
Reads script_lines.json → renders one card per beat with the same navy/orange brand."""
import subprocess, json, os, sys, re
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
    return rows

KICKER_MAP = {"hook": "THE PATTERN", "number": "THE NUMBER", "title": "THE QUESTION",
              "context": "THE BACKDROP", "compare": "THE COMPARISON", "take": "HONEST TAKE",
              "risk": "THE RISK", "verdict": "THE VERDICT", "cta": "JOIN THE CLUB"}
def card_layers(name, kicker, kicker_col, body, body_col=WHITE):
    """Render card as ANIMATED mp4 (AK style ref): kicker fades in, body rows pop in
    line-by-line, footer fades in. 90 frames @30fps = 3s; assembly holds last frame."""
    # pre-layout all elements
    label = KICKER_MAP.get(kicker, kicker.replace("rule ", "RULE "))
    for sz in (52, 46, 40, 36, 32, 28):
        rows = wrap(ImageDraw.Draw(Image.new('RGB',(W,H))), body, font(sz), W-120)
        if len(rows) * (sz + 32) <= 620:
            break
    f = font(sz)
    y0 = 340
    layout = [("kicker", 160, [label.upper()[:24]], font(46), kicker_col)]
    y = y0
    for row in rows:
        layout.append(("row", y, [row], f, body_col)); y += sz + 32
    layout.append(("foot", H-70, ["Sources on screen · Not financial advice"], font(22, False), GREY))

    n_frames = 90
    # timing: kicker frames 0-14 fade; rows start 12, each next +10; footer after rows
    starts = {"kicker": 0, "foot": 12 + len(rows)*10}
    for i, el in enumerate([l for l in layout if l[0]=="row"]):
        starts[f"row{i}"] = 12 + i*10
    fr = 0
    tmp = f'{out}/_af'
    os.makedirs(tmp, exist_ok=True)
    for fi in range(n_frames):
        img = Image.new('RGB', (W,H), NAVY); d = ImageDraw.Draw(img)
        d.rectangle([0,0,W,8], fill=ORANGE)
        for idx, el in enumerate(layout):
            key = el[0] if el[0] in ("kicker","foot") else f"row{idx-1}"
            st = starts.get(key, 0)
            t = min(1.0, max(0.0, (fi - st) / 8.0))   # 8-frame ease
            if t <= 0: continue
            # pop-in: scale-lite + rise from +18px
            ease = 1 - (1-t)**2
            yy = el[1] + int(18*(1-ease))
            # alpha via blend towards navy
            col = tuple(int(NAVY[k]+(el[4][k]-NAVY[k])*ease) for k in range(3))
            for txt_i, txt in enumerate(el[2]):
                ctext(d, yy + (0 if el[0]!="row" else 0), txt, el[3], col)
        img.save(f'{tmp}/f{fi:03d}.jpg', quality=88)
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-i',f'{tmp}/f%03d.jpg',
                    '-vf','tpad=stop_mode=clone:stop_duration=4','-pix_fmt','yuv420p',
                    f'{out}/{name}.mp4'], check=True)
    import shutil; shutil.rmtree(tmp)
    img = Image.new('RGB', (W,H), NAVY); d = ImageDraw.Draw(img)
    d.rectangle([0,0,W,8], fill=ORANGE)
    for el in layout:
        for txt in el[2]: ctext(d, el[1], txt, el[3], el[4])
    img.save(f'{out}/{name}.jpg', quality=92)   # static fallback for thumbnails/crop

import subprocess as _sp
def card(name, kicker, kicker_col, body, body_col=WHITE):
    card_layers(name, kicker, kicker_col, body, body_col)

kinds = ["hook","number","title","context","compare","take","rule1","rule2","rule3","risk","verdict","cta"]
cols = {"hook":GOLD,"number":(46,204,113),"title":GOLD,"risk":(255,68,68),"verdict":GOLD,"cta":ORANGE}
for i, line in enumerate(lines):
    kind = kinds[i] if i < len(kinds) else "context"
    text = re.sub(r'^(Hook|Big Callout|Title Question|Context|Comparison|Honest Take|Rule \d|Risk|Verdict|CTA)[:?]\s*', '', line).strip()
    card(f'b{i+1:02d}', kind, cols.get(kind, GREY), text)
print(len(lines), "cards →", out)
