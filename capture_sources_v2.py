#!/usr/bin/env python3
"""Source-page recordings v2 — Moneycontrol blocks us; use sites that allow + our OWN manim data sheet.
Fallback sources: (1) goldprice.org widget page, (2) our own rendered 'data source' board (HTML w/ real numbers)."""
import os
import time

from playwright.sync_api import sync_playwright

OUT = '/opt/kinocut-work/ch02_video1/recordings'
os.makedirs(OUT, exist_ok=True)

# source board built locally: real numbers + source labels, scrollable
HTML = '''<!DOCTYPE html><html><head><style>
body{background:#0d1b2a;color:#e0e1dd;font-family:monospace;margin:0;padding:40px}
h1{color:#E8552F;font-size:42px} h2{color:#778da9;margin-top:50px}
table{border-collapse:collapse;margin:20px 0;font-size:26px}
td{padding:14px 28px;border:1px solid #1b263b}
.num{color:#E8552F;font-weight:bold;font-size:34px}
.src{color:#778da9;font-size:18px}
.hl{background:#1b263b}
</style></head><body>
<h1>GOLD — THE DATA</h1>
<h2>1. Price (source: yfinance, live 2026-09-06)</h2>
<table><tr><td>Spot (international)</td><td class="num">$4,477 / oz</td></tr>
<tr><td>30-day change</td><td class="num">+5.5%</td></tr>
<tr><td>India price (10 grams)</td><td class="num">₹1,35,979</td></tr></table>
<h2>2. The rupee driver (source: yfinance USDINR=X)</h2>
<table><tr><td>USD/INR</td><td class="num">94.47</td></tr>
<tr><td>Status</td><td class="num hl">ALL-TIME WEAK</td></tr>
<tr><td>Effect on gold (INR)</td><td>Rupee down 1% → gold up ~1% in INR</td></tr></table>
<h2>3. This month (30-day window, yfinance)</h2>
<table><tr><td>Gold</td><td class="num">+5.5%</td></tr>
<tr><td>Bitcoin</td><td class="num">+24.2%</td></tr>
<tr><td>Nifty 50</td><td class="num" style="color:#f87171">−2.9%</td></tr></table>
<h2>4. Demand (source: World Gold Council, Moneycontrol 2026-09)</h2>
<table><tr><td>Gold ETF inflow streak (India)</td><td class="num hl">11 straight months</td></tr>
<tr><td>Central bank buying</td><td>Q2 2026: ~290 tonnes</td></tr>
<tr><td>Risk: worst drawdown</td><td class="num" style="color:#f87171">−28% (2011→2015, 5yr recovery)</td></tr></table>
<h2>5. Rules recap</h2>
<table><tr><td>Allocation</td><td class="num">5–10% of portfolio</td></tr>
<tr><td>Method</td><td class="num">Monthly SIP</td></tr>
<tr><td>Vehicle</td><td class="num">Gold ETF (no making charges)</td></tr></table>
<p class="src">Not financial advice. Educational only. AI-generated. Data: yfinance · World Gold Council · Moneycontrol</p>
</body></html>'''

open('/opt/kinocut-work/ch02_video1/recordings/source_board.html', 'w').write(HTML)

STEPS = [(0, 0), (2.5, 500), (5, 1100), (7.5, 1700), (10, 2300)]
DUR = 14

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.goto("file:///opt/kinocut-work/ch02_video1/recordings/source_board.html")
    page.wait_for_timeout(1500)
    fps = 10
    frames = []
    si = 0
    t0 = time.time()
    while time.time() - t0 < DUR:
        t = time.time() - t0
        while si < len(STEPS) and STEPS[si][0] <= t:
            page.evaluate(f"window.scrollTo({{top:{STEPS[si][1]}, behavior:'smooth'}})")
            si += 1
        frames.append(page.screenshot(type="jpeg", quality=85))
        target = len(frames) / fps
        while time.time() - t0 < target:
            pass
    seq = f"{OUT}/source_board_frames"
    os.makedirs(seq, exist_ok=True)
    for i, f in enumerate(frames):
        open(f"{seq}/f{i:04d}.jpg", "wb").write(f)
    print(f"source_board: {len(frames)} frames")
    browser.close()
