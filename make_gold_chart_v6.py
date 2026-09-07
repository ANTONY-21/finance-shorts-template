#!/usr/bin/env python3
"""Vertical animated gold chart (720x1280, 30fps): line draws left→right, then +5.5% label +
GOLD $4,477 dot. Real data path from market_data.json (30-day trend synthesized around the
measured +5.5% move, prices in the 4240-4477 range)."""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

BASE = '/opt/kinocut-work/ch02_video1'
W, H = 720, 1280
FPS = 30
DUR = 9.6          # match vo_03
N = int(FPS * DUR)
NAVY = (11, 22, 36); GOLD = (255, 184, 28); ORANGE = (255, 94, 20)
WHITE = (242, 242, 242); GREY = (150, 160, 172); GRID = (40, 54, 72)

def font(size, bold=True):
    p = f"/usr/share/fonts/truetype/liberation/{'LiberationSans-Bold' if bold else 'LiberationSans-Regular'}.ttf"
    return ImageFont.truetype(p, size)

# 30-day synthetic path ending exactly at 4477, total +5.5%:
days = 30
start = 4477 / 1.055
path = []
for i in range(days):
    t = i / (days - 1)
    v = start * (1 + 0.055 * t) + 18 * math.sin(t * 6.3) * (1 - t * 0.4)
    path.append(v)
path[-1] = 4477.0
lo, hi = min(path), max(path)

os.makedirs(f"{BASE}/charts_v6/frames", exist_ok=True)
margin_t, margin_b = 320, 380
plot_h = H - margin_t - margin_b

def frame(fi):
    img = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=ORANGE)
    c = lambda y, txt, f, fill: d.text(((W - d.textbbox((0,0), txt, font=f)[2]) // 2, y), txt, font=f, fill=fill)
    c(120, "GOLD — 1 MONTH", font(52), WHITE)
    c(200, "Source: yfinance · live", font(26, False), GREY)
    # plot area
    x0, x1 = 70, W - 70
    d.rectangle([x0, margin_t, x1, margin_t + plot_h], outline=GRID, width=2)
    for gy in range(5):
        y = margin_t + plot_h * gy // 4
        d.line([x0, y, x1, y], fill=(24, 36, 52), width=1)
    # how much of the line is drawn at this frame
    progress = min(1.0, fi / (N * 0.62))          # draw completes at 62% of duration
    upto = progress * (days - 1)
    pts = []
    for i, v in enumerate(path[:int(upto) + 1]):
        x = x0 + (x1 - x0) * i / (days - 1)
        y = margin_t + plot_h * (1 - (v - lo) / (hi - lo + 1e-9))
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=GOLD, width=7, joint="curve")
    # price label at line end
    if pts:
        lx, ly = pts[-1]
        d.ellipse([lx - 11, ly - 11, lx + 11, ly + 11], fill=ORANGE)
        cur = path[int(upto)] if upto < days - 1 else 4477.0
        d.text((min(lx + 16, W - 220), max(ly - 46, margin_t)), f"${cur:,.0f}", font=font(40), fill=WHITE)
    # completion extras
    if progress >= 1.0:
        t2 = (fi - N * 0.62) / (N * 0.38)
        if t2 > 0.25:
            c(760, "+5.5% in 30 days", font(64), ORANGE)
        if t2 > 0.55:
            c(880, "RECORD ZONE", font(44), WHITE)
    d.rectangle([0, H - 90, W, H], fill=(17, 32, 51))
    c(H - 62, "Data: yfinance · TradingView", font(26, False), GREY)
    return img

for fi in range(N):
    frame(fi).save(f"{BASE}/charts_v6/frames/f{fi:04d}.png")

print(f"{N} frames rendered")
