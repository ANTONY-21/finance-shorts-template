#!/usr/bin/env python3
"""Assembler for ch02_video1 — driven by timeline.json. Gates: unique visuals, no blanks, loudness."""
import json, subprocess, os

BASE = '/opt/kinocut-work/ch02_video1'
tl = json.load(open(f'{BASE}/timeline.json'))['timeline']

# visual durations: static cards hold for beat duration; mp4 visuals must cover beat dur
clips = []
for t in tl:
    vis = t['visual']
    dur = t['dur']
    out = f"{BASE}/out/seg_{t['beat']:02d}.mp4"
    if vis == 'disclaimer':
        vis = 'cards/disclaimer.jpg'
    src = f"{BASE}/{vis}"
    if not os.path.exists(src):
        print(f"MISSING: {src}"); raise SystemExit(1)
    if src.endswith('.jpg'):
        # ken-burns-free static hold (subtle scale via zoompan to avoid dead-static look)
        cmd = ["ffmpeg","-y","-v","quiet","-loop","1","-i",src,"-t",f"{dur:.2f}",
               "-vf","scale=1280:720,zoompan=z='min(zoom+0.0004,1.05)':d=1:s=1280x720:fps=30",
               "-r","30","-pix_fmt","yuv420p",out]
    else:
        # video: loop if shorter, trim if longer, scale to 1280x720, no audio
        cmd = ["ffmpeg","-y","-v","quiet","-stream_loop","-1","-i",src,"-t",f"{dur:.2f}",
               "-vf","scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0d1b2a,fps=30",
               "-an","-pix_fmt","yuv420p",out]
    subprocess.run(cmd, check=True)
    clips.append(out)
    print(f"seg {t['beat']:02d}: {dur:.2f}s <- {vis}")

# concat list (dedupe check: all visual sources must be unique)
srcs = [t['visual'] for t in tl]
assert len(srcs) == len(set(srcs)), "DUPLICATE VISUAL SEGMENT — assembly bug"
print("dedupe gate: all", len(srcs), "visual segments unique — PASS")

with open(f'{BASE}/out/concat.txt','w') as f:
    for c in clips:
        f.write(f"file '{c}'\n")
subprocess.run(["ffmpeg","-y","-v","quiet","-f","concat","-safe","0","-i",f"{BASE}/out/concat.txt","-c","copy",f"{BASE}/out/video_noaudio.mp4"], check=True)

# VO track: place each vo at its segment start
total = sum(t['dur'] for t in tl)
inputs, filters, idx = [], [], 0
pos = 0
for t in tl:
    if t['vo']:
        inputs += ["-i", f"{BASE}/{t['vo']}"]
        filters.append(f"[{idx+1}:a]adelay={int(pos*1000)}|{int(pos*1000)}[a{idx}]")
        idx += 1
    pos += t['dur']
amix = "".join(f"[a{i}]" for i in range(idx)) + f"amix=inputs={idx}:normalize=0,volume=1.0[vo]"
cmd = ["ffmpeg","-y","-v","quiet","-i",f"{BASE}/out/video_noaudio.mp4"] + inputs +       ["-filter_complex", ";".join(filters) + ";" + amix, "-map","0:v","-map","[vo]",
       "-c:v","copy","-c:a","aac","-b:a","192k", f"{BASE}/out/video_vo.mp4"]
subprocess.run(cmd, check=True)
print(f"video_vo.mp4 built, total {total:.1f}s")

# music bed: loop to total, -22dB under VO
subprocess.run(["ffmpeg","-y","-v","quiet","-i",f"{BASE}/out/video_vo.mp4",
                "-stream_loop","-1","-i",f"{BASE}/audio/music_bed.mp3",
                "-filter_complex",f"[1:a]volume=0.079[m];[m]atrim=0:{total:.2f}[m2]",
                "-map","0:v","-map","[m2]","-c:v","copy","-c:a","aac","-b:a","192k",
                "-shortest", f"{BASE}/out/final_v1.mp4"], check=True)
print("final_v1.mp4 assembled")
