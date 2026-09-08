#!/usr/bin/env python3
"""Synced screen recordings: slow scroll, wall-clock frames at 10fps, full viewport."""
import json, time, base64
from playwright.sync_api import sync_playwright

OUT = '/opt/kinocut-work/ch02_video1/recordings'
import os
os.makedirs(OUT, exist_ok=True)

TARGETS = [
    # (name, url, duration_s, scroll_steps [(at_s, to_y)])
    ("gold_price", "https://www.moneycontrol.com/commodity/gold-price.html", 12, [(0,0),(3,400),(6,900),(9,1400)]),
    ("gold_etf", "https://www.moneycontrol.com/mutual-funds/best-gold-etfs/", 10, [(0,0),(3,500),(6,1000),(8,1500)]),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width":1280,"height":720}, user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    for name, url, dur, steps in TARGETS:
        page = ctx.new_page()
        try:
            page.goto(url, timeout=45000, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
        except Exception as e:
            print(f"{name}: load failed {e}")
            continue
        fps = 10
        frames = []
        t0 = time.time()
        si = 0
        while time.time() - t0 < dur:
            t = time.time() - t0
            # scroll to the next step whose time arrived
            while si < len(steps) and steps[si][0] <= t:
                page.evaluate(f"window.scrollTo({{top:{steps[si][1]}, behavior:'smooth'}})")
                si += 1
            shot = page.screenshot(type="jpeg", quality=80)
            frames.append(shot)
            # timer-driven, no CDP
            target = len(frames) / fps
            while time.time() - t0 < target + len(frames) * 0:
                pass
        # write mp4 from jpeg sequence
        seq_dir = f"{OUT}/{name}_frames"
        os.makedirs(seq_dir, exist_ok=True)
        for i, f in enumerate(frames):
            open(f"{seq_dir}/f{i:04d}.jpg", "wb").write(f)
        print(f"{name}: {len(frames)} frames captured")
        page.close()
    browser.close()
