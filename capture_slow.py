#!/usr/bin/env python3
"""Slow scroll capture of source board, duration matched to the rules VO beat."""
import os, sys, time
from playwright.sync_api import sync_playwright

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 14.0
OUTF = sys.argv[2] if len(sys.argv) > 2 else '/opt/kinocut-work/ch02_video1/recordings/source_board_slow.mp4'

STEPS_N = 5
page_h = 2600

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width":1280,"height":720})
    page = ctx.new_page()
    page.goto("file:///opt/kinocut-work/ch02_video1/recordings/source_board.html")
    page.wait_for_timeout(1200)
    fps = 10
    frames = []
    t0 = time.time()
    si = 0
    # SLOW: stops at 20% intervals of DUR, small increments (2.5s per stop, was 2.5s for 500px -> now spread over DUR)
    stops = [(DUR*i/STEPS_N, int(page_h*i/STEPS_N)) for i in range(STEPS_N)]
    while time.time() - t0 < DUR:
        t = time.time() - t0
        while si < len(stops) and stops[si][0] <= t:
            page.evaluate(f"window.scrollTo({{top:{stops[si][1]}, behavior:'smooth'}})")
            si += 1
        frames.append(page.screenshot(type="jpeg", quality=85))
        target = len(frames)/fps
        while time.time()-t0 < target: pass
    seq = '/opt/kinocut-work/ch02_video1/recordings/sb_slow_frames'
    os.makedirs(seq, exist_ok=True)
    for i,f in enumerate(frames):
        open(f"{seq}/f{i:04d}.jpg","wb").write(f)
    print(f"captured {len(frames)} frames for {DUR}s")
    browser.close()
