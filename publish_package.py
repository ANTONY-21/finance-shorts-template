#!/usr/bin/env python3
"""FULL YOUTUBE/INSTAGRAM PACKAGE BUILDER — everything a finance short needs to publish.

Per video:
  1. Thumbnail (1280x720, big 2-3 word text, orange/navy brand, from the video's own hook card)
  2. Title (scored, keyword-led, <60 chars, from finance_topics.db hook)
  3. Description (first 2 lines = hook + live data, then chapters, sources, disclaimer, hashtags)
  4. Tags (20: asset + emotion + evergreen finance)
  5. Hashtags (3 for title, 5-8 for description/IG caption)
  6. IG caption (short version + hashtags, link-in-bio CTA)
  7. IG Reels cover (crop from thumbnail 1080x1920 safe zone)
  8. Upload metadata json (title/desc/tags/category=25 News&Politics, made_for_kids=false)

Usage: python3 publish_package.py <video_base> <topic_title>
e.g.   python3 publish_package.py /opt/kinocut-work/btc_video1 "bitcoin crash cycle"
Writes <base>/publish/{thumbnail.jpg, reel_cover.jpg, metadata.json, instagram.txt}
"""
import json, os, sys, sqlite3, urllib.request, datetime, subprocess

def topic_row(title_part):
    c = sqlite3.connect('/root/ak-ai-company/news-engine/finance_topics.db')
    r = c.execute("""SELECT title, asset, emotion, bucket, hook, score, source FROM topics
                     WHERE title LIKE ? ORDER BY score DESC LIMIT 1""",
                  (f"%{title_part}%",)).fetchone()
    return r

def live_data(asset):
    ids = {"Bitcoin": "bitcoin", "Gold": "pax-gold", "Silver": "tether-gold"}
    if asset not in ids: return None
    try:
        d = json.load(urllib.request.urlopen(
            f"https://api.coingecko.com/api/v3/coins/{ids[asset]}", timeout=20))
        md = d["market_data"]
        return {"now": round(md["current_price"]["usd"], 2),
                "chg30d": round(md["price_change_percentage_30d"], 1),
                "ath": round(md["ath"]["usd"], 0)}
    except Exception:
        return None

TAGS_EVERGREEN = ["finance", "money", "investing", "stock market", "personal finance",
                  "financial education", "investing for beginners", "wealth", "shorts"]
IG_TAGS = ["#finance", "#investing", "#moneytips", "#financialfreedom", "#stockmarket",
           "#cryptocurrency", "#wealthbuilding", "#money"]

def build(video_base, title_part):
    t = topic_row(title_part)
    if not t:
        print("TOPIC NOT FOUND:", title_part); return
    title_db, asset, emotion, bucket, hook, score, source = t
    data = live_data(asset)
    out = f"{video_base}/publish"
    os.makedirs(out, exist_ok=True)

    # ---- 1. THUMBNAIL: 1280x720 from hook card (center-crop of the 720x1280 card) ----
    # prefer the big-number callout card for the thumbnail; fall back to hook card
    for cand in ("num_price", "rupee", "hook", "b02", "b01"):
        p = f"{video_base}/cards_v6/{cand}.jpg"
        if os.path.exists(p):
            card = p
            break
    else:
        card = f"{video_base}/cards_v6/hook.jpg"
    if os.path.exists(card):
        from PIL import Image, ImageDraw, ImageFont
        img = Image.open(card)
        W, H = img.size  # 720x1280
        # crop the visual center band (the big number zone)
        # fit whole card onto 1280x720 with navy sides (no slice — number stays whole)
        canvas = Image.new('RGB', (1280, 720), (13, 17, 32))
        ih = 720
        iw = int(W * ih / H)
        scaled = img.resize((iw, ih), Image.Resampling.LANCZOS)
        canvas.paste(scaled, ((1280 - iw) // 2, 0))
        band = canvas
        d = ImageDraw.Draw(band)
        f = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 64)
        label = f"{asset.upper()} {emotion.upper()}"[:20]
        bbox = d.textbbox((0,0), label, font=f)
        tw = bbox[2]-bbox[0]
        d.rectangle([(1280-tw)//2-24, 24, (1280+tw)//2+24, 118], fill=(13,17,32))
        d.text(((1280-tw)//2, 42), label, font=f, fill=(255,184,28))
        band.save(f"{out}/thumbnail.jpg", quality=92)
        # ---- 7. IG Reel cover: 1080x1920 with the video centered + top/bottom brand ----
        vid = f"{video_base}/out/FINAL_v6_vertical.mp4"
        if os.path.exists(vid):
            subprocess.run(['ffmpeg','-y','-v','error','-i',vid,
                '-vf',"select=eq(n\\,90),scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x0d1120",
                '-frames:v','1', f"{out}/reel_cover.jpg"], timeout=120)

    # ---- 2. TITLE: hook condensed <60 chars ----
    yt_title = hook if len(hook) <= 60 else hook[:57].rsplit(' ',1)[0] + "…"
    # ---- 3. DESCRIPTION ----
    data_line = ""
    if data:
        data_line = f"Live data: {asset} ${data['now']:,} · 30d {data['chg30d']:+}% · ATH ${data['ath']:,}\n"
    desc = f"""{hook}

{data_line}
In this video: the {asset.lower()} {emotion.lower()} explained in under 2 minutes — what happened, why it matters for your money, and the 3 rules to act on it.

⏱ Chapters
00:00 The number
00:20 What it means
00:45 The 3 rules
01:15 The risk
01:25 Verdict

📊 Sources: CoinGecko live API · TradingView (shown on screen) · {datetime.date.today()}
⚠️ Not financial advice. Education only.

{asset.lower()} {"#"+asset.replace(' ','')} #finance #investing #money #shorts"""
    # ---- 4. TAGS ----
    tags = [asset.lower(), f"{asset.lower()} {emotion.lower()}", f"{asset.lower()} news",
            f"{asset.lower()} explained", "finance shorts", "money mistakes"] + TAGS_EVERGREEN
    tags = tags[:20]
    # ---- 6. IG caption ----
    ig = f"""{hook}

{data_line or 'Real data, no hype.'}Follow for one honest money rule every week.

{chr(10).join(IG_TAGS[:6])}"""
    meta = {
        "video": f"{video_base}/out/FINAL_v6_vertical.mp4",
        "youtube": {"title": yt_title, "description": desc, "tags": tags,
                    "categoryId": "25", "madeForKids": False,
                    "privacyStatus": "public", "thumbnail": f"{out}/thumbnail.jpg"},
        "instagram": {"caption": ig, "cover": f"{out}/reel_cover.jpg",
                      "video": f"{video_base}/out/FINAL_v6_vertical.mp4"},
        "topic": {"db_title": title_db, "score": score, "source": source},
        "generated": datetime.datetime.now().isoformat(),
    }
    json.dump(meta, open(f"{out}/metadata.json","w"), indent=1)
    open(f"{out}/instagram.txt","w").write(ig)
    print(f"PACKAGE BUILT → {out}/")
    print(f"  TITLE: {yt_title}")
    print(f"  thumbnail.jpg + reel_cover.jpg + metadata.json + instagram.txt")
    return meta

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
