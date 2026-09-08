#!/usr/bin/env python3
"""Assemble v2: AK voice + word-synced captions + source-board recording + enriched order.
New structure (more info, source page, explainer scroll):
  1 hook (card)          ~4.5s
  2 brand                ~3.7s
  3 gold chart (manim)   8.6s
  4 rupee driver (card)  10.2s
  5 compare bars (manim) 7.2s
  6 SOURCE BOARD scroll  14.0s  <- new: data page w/ sources
  7 host (identity)      7.7s
  8 rules (manim)        13.8s
  9 risk (card)          8.6s
 10 verdict (card)       8.6s
 11 CTA (card)           5.0s
 12 disclaimer           4.0s
"""
import json
import subprocess
import os

BASE = '/opt/kinocut-work/ch02_video1'

# 1. VO durations (AK voice)
def dur(p):
    r = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0',p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

vo_map = {
    1: 'vo_ak/vo_01.wav', 2: 'vo_ak/vo_02.wav', 3: 'vo_ak/vo_03.wav',
    4: 'vo_ak/vo_04.wav', 5: 'vo_ak/vo_05.wav', 6: None,  # source board: no VO? use vo_06 (host line moved) — actually repurpose: beat6 host VO plays over source board? No: keep host VO with host beat.
    7: 'vo_ak/vo_06.wav',  # host line now beat 7
    8: 'vo_ak/vo_07.wav',
    9: 'vo_ak/vo_08.wav',
    10: 'vo_ak/vo_09.wav',
    11: 'vo_ak/vo_10.wav',
}
# source board beat: no VO — add narration? We have no spare VO. Use silence with music + captions overlay showing sources. Simpler: put vo_06 (host) here and host beat gets vo_10? No — keep design: source board is a visual explainer beat with beat-8 'rules' voice? Cleanest: source board plays during beat 8 (rules) — voice explains rules while page shows data incl rules table.

beats = []
# visual per beat
vis_map = {
    1: f'{BASE}/cards/hook_card_v2.jpg',
    2: f'{BASE}/media/videos/motion/1080p60/brand_sting.mp4',
    3: f'{BASE}/media/videos/charts/1080p60/beat3_gold.mp4',
    4: f'{BASE}/cards/rupee_card_v2.jpg',
    5: f'{BASE}/media/videos/charts/1080p60/beat5_compare.mp4',
    6: f'{BASE}/recordings/source_board.mp4',
    7: f'{BASE}/host/beat6.mp4',
    8: f'{BASE}/media/videos/motion/1080p60/rules_motion.mp4',
    9: f'{BASE}/cards/risk_card.jpg',
    10: f'{BASE}/cards/verdict_card.jpg',
    11: f'{BASE}/cards/cta_card.jpg',
    12: f'{BASE}/cards/disclaimer.jpg',
}
vo_assign = {1:'vo_ak/vo_01.wav',2:'vo_ak/vo_02.wav',3:'vo_ak/vo_03.wav',4:'vo_ak/vo_04.wav',
             5:'vo_ak/vo_05.wav',6:'vo_ak/vo_07.wav',  # rules voice over source board (7 in vo files = rules)
             7:'vo_ak/vo_06.wav',  # host line over host beat
             8:'vo_ak/vo_08.wav',9:'vo_ak/vo_09.wav',10:'vo_ak/vo_10.wav',12:None}

segs = []
for bid in range(1, 13):
    vis = vis_map[bid]
    if not os.path.exists(vis):
        raise SystemExit(f"MISSING {vis}")
    vo = vo_assign.get(bid)
    d = dur(f'{BASE}/{vo}') if vo else 4.0
    segs.append({'beat': bid, 'visual': vis, 'vo': vo, 'dur': round(d, 2)})

total = sum(s['dur'] for s in segs)
print(f"total: {total:.1f}s across {len(segs)} beats")
json.dump({'timeline': segs, 'total': total}, open(f'{BASE}/timeline_v2.json','w'), indent=1)

# render segments (static cards = zoompan, videos = pad-scale)
os.makedirs(f'{BASE}/out2', exist_ok=True)
clips = []
for s in segs:
    out = f"{BASE}/out2/seg_{s['beat']:02d}.mp4"
    if s['visual'].endswith('.jpg'):
        subprocess.run(["ffmpeg","-y","-v","error","-loop","1","-i",s['visual'],"-t",f"{s['dur']:.2f}",
            "-vf","scale=1280:720,zoompan=z='min(zoom+0.0004,1.05)':d=1:s=1280x720:fps=30",
            "-r","30","-pix_fmt","yuv420p",out], check=True)
    else:
        subprocess.run(["ffmpeg","-y","-v","error","-stream_loop","-1","-i",s['visual'],"-t",f"{s['dur']:.2f}",
            "-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0d1b2a,fps=30",
            "-an","-pix_fmt","yuv420p",out], check=True)
    clips.append(out)
    print(f"seg {s['beat']:02d}: {s['dur']:.2f}s")

srcs = [s['visual'] for s in segs]
assert len(srcs) == len(set(srcs)), "duplicate visual"
with open(f'{BASE}/out2/concat.txt','w') as f:
    for c in clips: f.write(f"file '{c}'\n")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",f"{BASE}/out2/concat.txt","-c","copy",f"{BASE}/out2/video_noaudio.mp4"], check=True)

# VO mix
inputs, filters, idx, pos = [], [], 0, 0
for s in segs:
    if s['vo']:
        inputs += ["-i", f"{BASE}/{s['vo']}"]
        filters.append(f"[{idx+1}:a]adelay={int(pos*1000)}|{int(pos*1000)}[a{idx}]")
        idx += 1
    pos += s['dur']
amix = "".join(f"[a{i}]" for i in range(idx)) + f"amix=inputs={idx}:normalize=0[vo]"
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out2/video_noaudio.mp4"] + inputs +
    ["-filter_complex", ";".join(filters) + ";" + amix, "-map","0:v","-map","[vo]",
     "-c:v","copy","-c:a","aac","-b:a","192k",f"{BASE}/out2/video_vo.mp4"], check=True)
print("VO mixed")

# music + loudness
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out2/video_vo.mp4","-stream_loop","-1",
    "-i",f"{BASE}/audio/music_bed.mp3",
    "-filter_complex",f"[0:a]volume=1.0[vo];[1:a]volume=0.079[m];[m]atrim=0:{total:.2f}[ms];[vo][ms]amix=inputs=2:normalize=0,alimiter=limit=0.95,afade=t=out:st={total-2.5:.2f}:d=2.3[aout]",
    "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k",f"{BASE}/out2/mixed.mp4"], check=True)
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out2/mixed.mp4",
    "-af","loudnorm=I=-14:TP=-1.5:LRA=11","-c:v","copy","-c:a","aac","-b:a","192k",
    f"{BASE}/out/FINAL_AK.mp4"], check=True)
print(f"FINAL_AK.mp4 done, {total:.1f}s")
