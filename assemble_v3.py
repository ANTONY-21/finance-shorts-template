#!/usr/bin/env python3
"""Assemble v3: AK real voice (voxcpm proven endpoint), slow pacing, source board scroll = 15.5s (matched to rules VO).
Beat order (12 segs):
 1 hook(card) 2 brand 3 gold chart 4 rupee card 5 compare bars 6 SOURCE BOARD(slow, rules voice)
 7 host 8 rules cards(no VO - board covered it... no: rules voice is ON board seg; seg8 gets risk VO? keep mapping below)
Mapping:
 seg6 board  <- vo_07 (rules, 15.52s = board duration)
 seg7 host   <- vo_06 (host opinion, 6.56s)
 seg8 rules  <- none needed... but board already spoke rules; seg8 = risk vo_08
 seg9 verdict card <- vo_09? Wait original: 7=rules 8=risk 9=verdict 10=cta.
Final: 1:v01 2:v02 3:v03 4:v04 5:v05 6(board):v07 7(host):v06 8(risk):v08 9(verdict):v09 10(cta):v10 12 disclaimer none
"""
import json
import os
import subprocess

BASE = '/opt/kinocut-work/ch02_video1'

def dur(p):
    r = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0',p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

vis = {
    1:  f'{BASE}/cards/hook_card_v2.jpg',
    2:  f'{BASE}/media/videos/motion/1080p60/brand_sting.mp4',
    3:  f'{BASE}/media/videos/charts/1080p60/beat3_gold.mp4',
    4:  f'{BASE}/cards/rupee_card_v2.jpg',
    5:  f'{BASE}/media/videos/charts/1080p60/beat5_compare.mp4',
    6:  f'{BASE}/recordings/source_board_slow.mp4',
    7:  f'{BASE}/host/beat6.mp4',
    8:  f'{BASE}/media/videos/motion/1080p60/rules_motion.mp4',
    9:  f'{BASE}/cards/risk_card.jpg',
    10: f'{BASE}/cards/verdict_card.jpg',
    11: f'{BASE}/cards/cta_card.jpg',
    12: f'{BASE}/cards/disclaimer.jpg',
}
vo = {1:'vo_ak_v3/vo_01.wav',2:'vo_ak_v3/vo_02.wav',3:'vo_ak_v3/vo_03.wav',4:'vo_ak_v3/vo_04.wav',
      5:'vo_ak_v3/vo_05.wav',6:'vo_ak_v3/vo_07.wav',7:'vo_ak_v3/vo_06.wav',8:'vo_ak_v3/vo_08.wav',
      9:'vo_ak_v3/vo_09.wav',10:'vo_ak_v3/vo_10.wav'}

segs = []
for bid in range(1, 13):
    v = vis[bid]
    assert os.path.exists(v), f"missing {v}"
    d = dur(f'{BASE}/{vo[bid]}') if bid in vo else 4.0
    segs.append({'beat': bid, 'visual': v, 'vo': vo.get(bid), 'dur': round(d, 2)})

total = sum(s['dur'] for s in segs)
print(f'total {total:.1f}s')
json.dump({'timeline': segs, 'total': total}, open(f'{BASE}/timeline_v3.json','w'), indent=1)

os.makedirs(f'{BASE}/out3', exist_ok=True)
clips = []
for s in segs:
    out = f"{BASE}/out3/seg_{s['beat']:02d}.mp4"
    if s['visual'].endswith('.jpg'):
        subprocess.run(["ffmpeg","-y","-v","error","-loop","1","-i",s['visual'],"-t",f"{s['dur']:.2f}",
            "-vf","scale=1280:720,zoompan=z='min(zoom+0.0003,1.04)':d=1:s=1280x720:fps=30",
            "-r","30","-pix_fmt","yuv420p",out], check=True)
    else:
        subprocess.run(["ffmpeg","-y","-v","error","-stream_loop","-1","-i",s['visual'],"-t",f"{s['dur']:.2f}",
            "-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0d1b2a,fps=30",
            "-an","-pix_fmt","yuv420p",out], check=True)
    clips.append(out)
    print(f"seg {s['beat']:02d}: {s['dur']:.2f}s")

srcs = [s['visual'] for s in segs]
assert len(srcs) == len(set(srcs)), 'dup visual'
with open(f'{BASE}/out3/concat.txt','w') as f:
    for c in clips: f.write(f"file '{c}'\n")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",f"{BASE}/out3/concat.txt","-c","copy",f"{BASE}/out3/video_noaudio.mp4"], check=True)

inputs, filters, idx, pos = [], [], 0, 0
for s in segs:
    if s['vo']:
        inputs += ["-i", f"{BASE}/{s['vo']}"]
        filters.append(f"[{idx+1}:a]adelay={int(pos*1000)}|{int(pos*1000)}[a{idx}]")
        idx += 1
    pos += s['dur']
amix = "".join(f"[a{i}]" for i in range(idx)) + f"amix=inputs={idx}:normalize=0[vo]"
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out3/video_noaudio.mp4"] + inputs +
    ["-filter_complex", ";".join(filters) + ";" + amix, "-map","0:v","-map","[vo]",
     "-c:v","copy","-c:a","aac","-b:a","192k",f"{BASE}/out3/video_vo.mp4"], check=True)

subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out3/video_vo.mp4","-stream_loop","-1",
    "-i",f"{BASE}/audio/music_bed.mp3",
    "-filter_complex",f"[0:a]volume=1.0[vo];[1:a]volume=0.079[m];[m]atrim=0:{total:.2f}[ms];[vo][ms]amix=inputs=2:normalize=0,alimiter=limit=0.95,afade=t=out:st={total-2.5:.2f}:d=2.3[aout]",
    "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k",f"{BASE}/out3/mixed.mp4"], check=True)
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out3/mixed.mp4",
    "-af","loudnorm=I=-14:TP=-1.5:LRA=11","-c:v","copy","-c:a","aac","-b:a","192k",
    f"{BASE}/out/FINAL_v3_noCap.mp4"], check=True)
print(f"FINAL_v3 assembled {total:.1f}s")

# captions from AK-voice wav (whisper) — reuse make_captions pattern pointing at vo_ak_v3
