#!/usr/bin/env python3
"""PAPER-CUTOUT STYLE renderer (vox/papercraft feel) — procedural, zero GPU.
Per beat: navy brand bg + torn-paper strips (jagged edges, real data lines) + sticky-note
cards for rules. Animated: pop-in line-by-line + tiny rotation wobble → 90-frame mp4/card.
Usage: python3 paper_style.py <video_base> [--static]   (writes cards_paper/bXX.mp4+.jpg)
"""
import subprocess, json, os, sys, re, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

base = sys.argv[1]
STATIC = '--static' in sys.argv
lines = json.load(open(f'{base}/script_lines.json'))
out = f'{base}/cards_paper'
os.makedirs(out, exist_ok=True)
W, H = 720, 1280
NAVY=(13,17,32); DARK=(5,7,14); ORANGE=(255,122,24); GOLD=(255,184,28)
PAPER=(232,222,196); PAPER_DARK=(210,198,170); WHITE=(245,247,250); GREY=(120,130,145)
INK=(90,80,60); GREEN=(46,204,113); RED=(255,68,68)
F = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
FR = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
def font(sz, b=True): return ImageFont.truetype(F if b else FR, sz)
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

def torn_strip(w, h, seed, color=PAPER, jag=13):
    """Procedural torn paper with jagged edges + grain. Returns RGBA."""
    random.seed(seed)
    img = Image.new('RGBA', (w+60, h+60), (0,0,0,0))
    d = ImageDraw.Draw(img)
    pts, steps = [], 22
    for i in range(steps): pts.append((30 + w*i/steps, 30 + random.randint(-jag, jag)))
    for i in range(steps): pts.append((30 + w + random.randint(-jag, jag), 30 + h*i/steps))
    for i in range(steps): pts.append((30 + w - w*i/steps, 30 + h + random.randint(-jag, jag)))
    for i in range(steps): pts.append((30 + random.randint(-jag, jag), 30 + h - h*i/steps))
    d.polygon(pts, fill=color+(255,))
    # grain: darken randomly-spaced pixels slightly (paper fibers)
    px = img.load()
    for _ in range(int(w*h/28)):
        x, y = random.randint(2, w+57), random.randint(2, h+57)
        r, g, b, a = px[x, y]
        if a: px[x, y] = (max(0,r-14), max(0,g-14), max(0,b-14), a)
    return img

def paste_shadow(base, el, center, deg):
    r = el.rotate(deg, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', r.size, (0,0,0,0))
    sh.putalpha(r.split()[3].point(lambda v: int(v*0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(11))
    base.paste(Image.new('RGB', r.size, DARK),
               (center[0]-r.size[0]//2+9, center[1]-r.size[1]//2+11), sh)
    base.paste(r, (center[0]-r.size[0]//2, center[1]-r.size[1]//2), r)

def paper_card(i, kind, text):
    """One paper-style beat card → static jpg + animated mp4."""
    label = KICKER_MAP.get(kind, kind.replace("rule ", "RULE "))
    body = re.sub(r'^(Hook|Big Callout|Title Question|Context|Comparison|Honest Take|Rule \d|Risk|Verdict|CTA)[:?]\s*', '', text).strip()
    d0 = ImageDraw.Draw(Image.new('RGB',(W,H)))
    sz = 44
    for s in (44, 40, 36, 32, 28):
        if len(wrap(d0, body, font(s), W-160)) * (s+30) <= 480: sz = s; break
    rows = wrap(d0, body, font(sz), W-160)
    f = font(sz)

    def draw_frame(state):
        """state: dict kicker/row_i/foot -> 0..1 ease"""
        img = Image.new('RGB', (W,H), NAVY)
        d = ImageDraw.Draw(img)
        d.rectangle([0,0,W,10], fill=ORANGE)
        # headline block (fades)
        k = state['kicker']
        if k > 0:
            bb = d.textbbox((0,0), label.upper(), font=font(44))
            d.text(((W-bb[2])//2, 150+int(12*(1-k))), label.upper(), font=font(44), fill=_mix(NAVY, GOLD, k))
        y = 300
        for ri, row in enumerate(rows):
            e = state.get('row', {}).get(ri, 0)
            if e > 0:
                bb = d.textbbox((0,0), row, font=f)
                d.text(((W-bb[2])//2, y+int(14*(1-e))), row, font=f, fill=_mix(NAVY, WHITE, e))
            y += sz + 30
        # paper props (fade in last): torn strip with kind-specific data
        pe = state.get('props', 0)
        if pe > 0:
            strip = torn_strip(400, 190, seed=i*7+3)
            sd = ImageDraw.Draw(strip)
            f3 = font(24)
            data = data_lines(kind, i)
            for li, line in enumerate(data):
                sd.text((70, 60+li*36), line, font=f3, fill=_mix(PAPER, INK, pe))
            paste_shadow(img, strip, (430, 1020), (-4 + i*1.3 % 8 - 4))
            # sticky note for rules
            if kind.startswith("rule"):
                note = torn_strip(240, 220, seed=i*11+1, color=(255,214,90), jag=4)
                nd = ImageDraw.Draw(note)
                nd.text((60, 80), "RULE", font=font(34), fill=(120,95,20))
                nd.text((60, 130), kind.split()[-1].replace("rule",""), font=font(52), fill=(120,95,20))
                paste_shadow(img, note, (140, 830), 6)
        fe = state.get('foot', 0)
        if fe > 0:
            d.text((60, H-64), "Sources on screen · Not financial advice",
                   font=font(20, False), fill=_mix(NAVY, GREY, fe))
        return img

    img_full = draw_frame({'kicker':1, 'row':{ri:1 for ri in range(len(rows))}, 'props':1, 'foot':1})
    img_full.save(f'{out}/b{i:02d}.jpg', quality=92)
    if STATIC: return

    # animated: 90 frames — kicker 0-8, rows stagger, props, foot
    tmp = f'{out}/_pf'; os.makedirs(tmp, exist_ok=True)
    n = 90
    for fi in range(n):
        st = {'kicker': ease(fi, 0, 8),
              'row': {ri: ease(fi, 8+ri*7, 8+ri*7+8) for ri in range(len(rows))},
              'props': ease(fi, 20+len(rows)*7, 28+len(rows)*7),
              'foot': ease(fi, 34+len(rows)*7, 42+len(rows)*7)}
        fr = draw_frame(st)
        # wobble: ±0.6° rotation oscillation on the whole frame (paper feel)
        if fi > 30:
            ang = 0.6 * math.sin((fi-30)/9)
            fr = fr.rotate(ang, resample=Image.BICUBIC, fillcolor=NAVY)
        fr.save(f'{tmp}/f{fi:03d}.jpg', quality=88)
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-i',f'{tmp}/f%03d.jpg',
                    '-vf','tpad=stop_mode=clone:stop_duration=4','-pix_fmt','yuv420p',
                    f'{out}/b{i:02d}.mp4'], check=True)
    import shutil; shutil.rmtree(tmp)

def ease(fi, start, end):
    t = min(1.0, max(0.0, (fi-start)/max(1,end-start)))
    return 1-(1-t)**2
def _mix(a, b, t):
    return tuple(int(a[k]+(b[k]-a[k])*t) for k in range(3))

def data_lines(kind, i):
    """Real data on the torn strip — parse source_line.txt correctly.
    Expected format: 'label value (chg% ), label value (chg%)' — extract named pairs."""
    try:
        src = open(f'{base}/source_line.txt').read().strip()
    except FileNotFoundError:
        src = ""
    # parse AFTER the label prefix (skip 'yfinance live 2026-09-07:' etc), split on '),'
    data_part = src.split(':', 1)[1].strip() if ':' in src else src
    segs = [s.strip() if s.strip().endswith(')') else s.strip() + ')'
            for s in re.split(r'\)\s*,\s*', data_part) if s.strip()]
    rows = []
    for seg in segs[:3]:
        m = re.match(r"^([A-Za-z&' ]+?)\s+([\d,]+(?:\.\d+)?)\s*(?:\((.+?)\))?$", seg)
        if m:
            label = m.group(1).strip().title()[:10]
            val = m.group(2)
            chg = m.group(3) or ""
            rows.append(f"{label} {val}" + (f"  {chg}" if chg else ""))
    if not rows:
        rows = ["Source on screen"]
    return rows[:3]

kinds = ["hook","number","title","context","compare","take","rule1","rule2","rule3","risk","verdict","cta"]
for i, line in enumerate(lines):
    kind = kinds[i] if i < len(kinds) else "context"
    paper_card(i+1, kind, line)
    print(f"  paper card b{i+1:02d} ({kind})", flush=True)
print(len(lines), "paper cards →", out)
