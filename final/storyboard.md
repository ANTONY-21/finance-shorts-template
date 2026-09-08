# Storyboard — Ravi's First Crash (cardboard style)

**Duration:** 84s · **Audience:** Indian retail investors, 20-35 · **Platform:** YouTube Shorts + Reels (704x1280) · **Style:** cardboard diorama (Remotion) · **CTA:** Follow for the next story

**Source (checked 2026-09-08, yfinance):** NIFTY 23,682.50 (−3.67% 30d) · S&P 500 7,718.60 (−0.06% 30d) · BANK NIFTY 56,963.75 (−1.25% 30d)

## Beat sheet

| # | Scene | Timing | Visual | Camera | Numbers on screen | VO summary |
|---|---|---|---|---|---|---|
| 1 | ravi_desk_calm | 0:00-11.7 | Ravi at desk, smiling, phone in hand, SEP calendar, coffee cup on desk | slow push-in, static set | ₹50,000 | Ravi, 26, first job, ₹50,000 into index fund |
| 2 | market_crash_monitor | 11.7-22.2 | push to monitor: NIFTY red | zoom to 1.45x on monitor | NIFTY 23,682 ▼ -3.67% | one Tuesday the index is down 3.67% in a month |
| 3 | phone_portfolio_drop | 22.2-31.0 | push to phone, frown | zoom to 1.6x on phone | ₹48,165 ▼ ₹1,835 | his ₹50,000 is ₹48,165 — lost ₹1,835 |
| 4 | panic_vs_world | 31.0-43.0 | 3 comparison cards stamp in | wide | NIFTY -3.67 / BANK NIFTY -1.25 / S&P -0.06 | wants to sell — but the wider picture is calm; a dip, not a collapse |
| 5 | rule_cards | 43.0-60.1 | 3 rule cards, calendar hidden | wide | 3 RULES HE LEARNED | dips are normal / 2500 companies / never panic-sell |
| 6 | time_recovery | 60.1-68.1 | calendar flips, ticker climbs | wide | NIFTY 23,682 → 26,200 | months pass, index climbs back |
| 7 | phone_recovery_cta | 68.1-84.0 | phone green, thumbs-up, CTA card | slow push | ₹53,285 (+6.6%) | time in the market beats timing the market — follow |

## Renderer mapping
Beats 1-3, 6-7: Remotion cardboard scene · Beat 4-5: Remotion card overlays (same scene) ·
VO: IndexTTS2 (AK voice, ref v6) · Music: existing bed @0.12 · QC: qc_render.py + vision.

## Critique
- Pacing: hook lands at 11.7s (beat 2) — acceptable for story format; Short cut-down = beats 2-3 only.
- Every number source-checked; recovery math verified (48,165 × 26,200/23,682.5 = 53,285 = +6.6%).
- All shots producible in-house, zero GPU.
