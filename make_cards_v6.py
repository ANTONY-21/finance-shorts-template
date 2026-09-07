#!/usr/bin/env python3
"""V6 vertical cards (720x1280) — hook, rupee, rules 1/2/3 (AK-liked style), risk, verdict,
CTA, number callouts ($4,477 / 94.47 / -45%), title card. Style: dark navy, orange/gold accents,
orange bordered boxes for rules (AK liked), giant numerals for callouts."""
from PIL import Image, ImageDraw, ImageFont

BASE = '/opt/kinocut-work/ch02_video1'
W, H = 720, 1280
NAVY = (11, 22, 36)
NAVY2 = (17, 32, 51)
GOLD = (255, 184, 28)
ORANGE = (255, 94, 20)
WHITE = (242, 242, 242)
GREY = (150, 160, 172)
RED = (235, 60, 60)
GREEN = (60, 200, 120)

def font(size, bold=True):
    p = f"/usr/share/fonts/truetype/liberation/{'LiberationSans-Bold' if bold else 'LiberationSans-Regular'}.ttf"
    return ImageFont.truetype(p, size)

def base():
    img = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # subtle top/bottom gradient bands
    d.rectangle([0, 0, W, 8], fill=ORANGE)
    return img, d

def ctext(d, y, text, f, fill, x=None):
    w = d.textbbox((0, 0), text, font=f)[2]
    d.text((x if x is not None else (W - w) // 2, y), text, font=f, fill=fill)

def srcbar(d, text):
    d.rectangle([0, H - 90, W, H], fill=NAVY2)
    ctext(d, H - 62, text, font(26, False), GREY)

# ---- HOOK card
img, d = base()
ctext(d, 240, "GOLD", font(120), GOLD)
ctext(d, 400, "Rs 1,35,000", font(110), WHITE)
ctext(d, 560, "for 10 grams", font(44, False), GREY)
ctext(d, 700, "The number everyone is", font(38, False), WHITE)
ctext(d, 760, "talking about", font(38, False), WHITE)
srcbar(d, "Data: yfinance · World Gold Council")
img.save(f"{BASE}/cards_v6/hook.jpg", quality=92)

# ---- NUMBER CALLOUT: price
img, d = base()
ctext(d, 380, "RECORD", font(54), GREY)
ctext(d, 480, "$4,477", font(150), ORANGE)
ctext(d, 700, "per ounce", font(44, False), WHITE)
srcbar(d, "Source: TradingView · OANDA · live")
img.save(f"{BASE}/cards_v6/num_price.jpg", quality=92)

# ---- RUPEE card
img, d = base()
ctext(d, 200, "THE REAL DRIVER", font(44), GOLD)
ctext(d, 320, "Rs 94.47", font(140), ORANGE)
ctext(d, 510, "1 USD = 94.47 INR", font(40, False), WHITE)
ctext(d, 600, "weakest rupee ever", font(36, False), GREY)
ctext(d, 760, "Weak rupee → gold in rupees", font(38, False), WHITE)
ctext(d, 820, "rises faster", font(38, False), WHITE)
srcbar(d, "Source: yfinance USDINR=X")
img.save(f"{BASE}/cards_v6/rupee.jpg", quality=92)

# ---- COMPARE callout
img, d = base()
ctext(d, 200, "THIS MONTH", font(48), GOLD)
rows = [("GOLD", "+5.5%", GREEN), ("BITCOIN", "+24.2%", GREEN), ("NIFTY", "-2.9%", RED)]
y = 380
for name, val, col in rows:
    ctext(d, y, name, font(44, False), WHITE, x=90)
    w = d.textbbox((0, 0), val, font=font(64))[2]
    d.text((W - w - 90, y - 20), val, font=font(64), fill=col)
    y += 180
srcbar(d, "Source: yfinance · 30-day window")
img.save(f"{BASE}/cards_v6/compare.jpg", quality=92)

# ---- RULES cards (AK-liked style: orange border boxes, orange header)
def rule_card(fname, kicker, big, line2):
    img, d = base()
    ctext(d, 170, "3 RULES", font(50), GOLD)
    d.rectangle([90, 320, W - 90, 580], outline=ORANGE, width=5)
    ctext(d, 350, kicker, font(40, False), ORANGE, x=130)
    ctext(d, 420, big, font(72), WHITE, x=130)
    ctext(d, 680, line2, font(40, False), WHITE)
    srcbar(d, "Standard portfolio rule · not advice")
    img.save(f"{BASE}/cards_v6/{fname}", quality=92)

rule_card("rule1.jpg", "RULE 1", "5–10%", "of your portfolio. Not more.")
rule_card("rule2.jpg", "RULE 2", "SIP", "Buy monthly, not lump sum at a record.")
rule_card("rule3.jpg", "RULE 3", "ETFs", "Not jewellery. No making charges.")

# ---- RISK callout: giant -45%
img, d = base()
ctext(d, 240, "GOLD'S PAST DRAWDOWN", font(44), GREY)
ctext(d, 380, "-45%", font(180), RED)
ctext(d, 640, "2011 peak → 2015 low", font(40, False), WHITE)
ctext(d, 700, "then 4 YEARS below the peak", font(40, False), WHITE)
ctext(d, 850, "Record price = record dip risk", font(38, False), ORANGE)
srcbar(d, "Source: LBMA/WTG 2011 peak $1,920 → 2015 low $1,050")
img.save(f"{BASE}/cards_v6/risk.jpg", quality=92)

# ---- VERDICT
img, d = base()
ctext(d, 180, "MY VERDICT", font(50), GOLD)
ctext(d, 300, "Don't chase", font(76), WHITE)
ctext(d, 440, "the record", font(76), WHITE)
d.rectangle([90, 610, W - 90, 760], outline=GREEN, width=5)
ctext(d, 640, "No gold? Start small", font(44), GREEN)
d.rectangle([90, 800, W - 90, 950], outline=ORANGE, width=5)
ctext(d, 830, "Own too much? Stop adding", font(40), ORANGE)
srcbar(d, "Not financial advice · educational")
img.save(f"{BASE}/cards_v6/verdict.jpg", quality=92)

# ---- CTA
img, d = base()
ctext(d, 420, "FOLLOW", font(110), ORANGE)
ctext(d, 590, "One honest money rule", font(40, False), WHITE)
ctext(d, 650, "every week", font(40, False), WHITE)
ctext(d, 780, "No hype. No guarantees.", font(34, False), GREY)
img.save(f"{BASE}/cards_v6/cta.jpg", quality=92)

# ---- TITLE card (brand)
img, d = base()
ctext(d, 420, "GOLD AT", font(70), WHITE)
ctext(d, 520, "ALL-TIME HIGHS", font(70), GOLD)
ctext(d, 700, "buy now or wait?", font(46, False), GREY)
img.save(f"{BASE}/cards_v6/title.jpg", quality=92)

# ---- DISCLAIMER
img, d = base()
ctext(d, 520, "Not financial advice.", font(44, False), GREY)
ctext(d, 590, "Educational only. AI-generated.", font(34, False), GREY)
ctext(d, 660, "Data: yfinance · World Gold Council · TradingView", font(28, False), GREY)
img.save(f"{BASE}/cards_v6/disclaimer.jpg", quality=92)

import os
print(sorted(os.listdir(f"{BASE}/cards_v6")))
