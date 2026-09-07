#!/usr/bin/env python3
"""Long slow-scroll capture of the REAL TradingView XAUUSD page (mobile viewport 720x1280).
30 frames x 0.4s dwell = ~12s of scroll material for the host-slot replacement."""
import asyncio, os
from playwright.async_api import async_playwright

OUT = "/opt/kinocut-work/ch02_video1/recordings/site2"

async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 720, "height": 1280}, is_mobile=True,
                              user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) Mobile Safari/537.36")
        await pg.goto("https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD", timeout=60000)
        await pg.wait_for_timeout(7000)
        for i in range(30):
            await pg.screenshot(path=f"{OUT}/f{i:03d}.png")
            await pg.evaluate("window.scrollBy(0, 10)")
            await pg.wait_for_timeout(400)
        await b.close()
    print("captured", len(os.listdir(OUT)), "frames")

asyncio.run(main())
