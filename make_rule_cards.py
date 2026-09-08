#!/usr/bin/env python3
"""Generate 3 rule cards (rule1/rule2/rule3) as JPGs, matching the deck's visual style.
Then the rules beat is split into 3 sub-beats in video.json, each card shown while its rule
is spoken — visuals no longer 'fast' ahead of the voice."""
from PIL import Image, ImageDraw, ImageFont

BASE = '/opt/kinocut-work/ch02_video1'
W, H = 1280, 720
NAVY = (13, 27, 42)
GOLD = (255, 191, 0)
WHITE = (240, 240, 240)
RED = (230, 57, 70)

def font(size, bold=True):
    p = f"/usr/share/fonts/truetype/dejavu/DejaVuSans-{'Bold' if bold else ''}.ttf"
    return ImageFont.truetype(p, size)

cards = [
    ("rule1", "RULE 1", "Keep gold at", "5–10%", "of your portfolio — not more."),
    ("rule2", "RULE 2", "Buy monthly —", "SIP", "not a lump sum at a record."),
    ("rule3", "RULE 3", "Use gold", "ETFs", "not jewellery — no making charges."),
]
for name, kicker, l1, big, l2 in cards:
    img = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # kicker
    d.text((90, 120), kicker, font=font(44), fill=GOLD)
    d.rectangle([90, 185, 290, 192], fill=GOLD)
    # lines
    d.text((90, 260), l1, font=font(56), fill=WHITE)
    d.text((90, 350), big, font=font(120), fill=GOLD)
    d.text((90, 530), l2, font=font(44), fill=WHITE)
    img.save(f"{BASE}/cards/{name}.jpg", quality=92)
    print(f"cards/{name}.jpg")
