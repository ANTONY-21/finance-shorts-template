#!/usr/bin/env python3
"""
video.json-driven assembly — DYNAMIC: durations come from actual VO files, visuals from the
timeline json, music bed configured in the json. Edit video.json → rerun → new master.

Schema (video.json):
{
  "music": {"path": "...", "volume": 0.11, "fade_out": 2.5},
  "captions": {"enabled": true, "style": "...force_style..."},
  "beats": [
    {"id": 1, "visual": "/abs/path.jpg|.mp4", "vo": "/abs/path.wav"|null,
     "visual_mode": "zoompan"|"fit"|"native", "min_dur": 4.0,   // min_dur only when vo null
     "label": "hook"}
  ]
}
Durations = real VO durations (or min_dur for silent beats). Nothing is hardcoded per-beat.
"""
import json, os, subprocess, sys

BASE = '/opt/kinocut-work/ch02_video1'
CFG  = json.load(open(f'{BASE}/video.json'))

def dur(p):
    r = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration','-of','csv=p=0',p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

# ---- 1. Build timeline from json (durations = real audio) ----
segs = []
for b in CFG['beats']:
    d = dur(b['vo']) if b.get('vo') else b.get('min_dur', 4.0)
    segs.append({'id': b['id'], 'label': b.get('label',''), 'visual': b['visual'],
                 'vo': b.get('vo'), 'mode': b.get('visual_mode','fit'), 'dur': round(d,2)})
    assert os.path.exists(b['visual']), f"missing visual {b['visual']}"
    if b.get('vo'): assert os.path.exists(b['vo']), f"missing vo {b['vo']}"

total = sum(s['dur'] for s in segs)
print(f'timeline: {len(segs)} beats, total {total:.1f}s')
json.dump({'timeline': segs, 'total': round(total,2)}, open(f'{BASE}/timeline.json','w'), indent=1)

# ---- 2. Render per-beat clips ----
os.makedirs(f'{BASE}/out4', exist_ok=True)
clips = []
for s in segs:
    out = f"{BASE}/out4/seg_{s['id']:02d}.mp4"
    vf = {"zoompan": "scale=1280:720,zoompan=z='min(zoom+0.0003,1.04)':d=1:s=1280x720:fps=30",
          "fit": "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0x0d1b2a,fps=30",
          "native": "scale=1280:720,fps=30"}[s['mode']]
    if s['visual'].endswith(('.jpg','.png')):
        subprocess.run(["ffmpeg","-y","-v","error","-loop","1","-i",s['visual'],"-t",f"{s['dur']:.2f}",
                        "-vf",vf,"-r","30","-pix_fmt","yuv420p",out], check=True)
    else:
        # NEVER stream_loop a shorter clip into a longer slot — loop restart shows early-animation
        # frames (defect caught twice by AK). Play once, then HOLD the final frame (tpad clone).
        subprocess.run(["ffmpeg","-y","-v","error","-i",s['visual'],"-t",f"{s['dur']:.2f}",
            "-vf",vf + ",tpad=stop_mode=clone:stop_duration=30",
            "-an","-t",f"{s['dur']:.2f}","-pix_fmt","yuv420p",out], check=True)
    clips.append(out)
    print(f"beat {s['id']:02d} [{s['label']}]: {s['dur']:.2f}s ({s['mode']})")

with open(f'{BASE}/out4/concat.txt','w') as f:
    for c in clips: f.write(f"file '{c}'\n")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",f"{BASE}/out4/concat.txt",
                "-c","copy",f"{BASE}/out4/video_noaudio.mp4"], check=True)

# ---- 3. VO mix (each VO starts exactly at its beat) ----
inputs, filters, idx, pos = [], [], 0, 0
for s in segs:
    if s['vo']:
        inputs += ["-i", s['vo']]
        filters.append(f"[{idx+1}:a]adelay={int(pos*1000)}|{int(pos*1000)}[a{idx}]")
        idx += 1
    pos += s['dur']
amix = "".join(f"[a{i}]" for i in range(idx)) + f"amix=inputs={max(idx,1)}:normalize=0[vo]"
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out4/video_noaudio.mp4"] + inputs +
    ["-filter_complex", ";".join(filters) + ";" + amix, "-map","0:v","-map","[vo]",
     "-c:v","copy","-c:a","aac","-b:a","192k",f"{BASE}/out4/video_vo.mp4"], check=True)

# ---- 4. Music bed (from json config) — full-length bed, NO looping ----
mus = CFG.get('music', {})
bed = mus.get('path', f'{BASE}/audio/music_bed_v4.wav')
mvol = mus.get('volume', 0.11)
fo = mus.get('fade_out', 2.5)
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out4/video_vo.mp4","-i",bed,
    "-filter_complex",
    f"[0:a]volume=1.0[vo];[1:a]volume={mvol}[m];[m]atrim=0:{total:.2f}[ms];"
    f"[vo][ms]amix=inputs=2:normalize=0,alimiter=limit=0.95,"
    f"afade=t=out:st={total-fo:.2f}:d={fo-0.2:.2f}[aout]",
    "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k",f"{BASE}/out4/mixed.mp4"], check=True)

# ---- 5. Loudnorm master ----
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out4/mixed.mp4",
    "-af","loudnorm=I=-14:TP=-1.5:LRA=11","-c:v","copy","-c:a","aac","-b:a","192k",
    f"{BASE}/out/FINAL_v4_noCap.mp4"], check=True)

# ---- 6. Captions (word-synced, burned) ----
cap = CFG.get('captions', {})
if cap.get('enabled'):
    style = cap.get('style', "FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Bold=1,Alignment=2,MarginV=40")
    subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/out/FINAL_v4_noCap.mp4",
        "-vf",f"subtitles={BASE}/captions_v4.ass:force_style='{style}'",
        "-c:v","libx264","-preset","medium","-crf","20","-c:a","copy",
        f"{BASE}/out/FINAL_v4.mp4"], check=True)
    print("FINAL_v4.mp4 (captions burned)")
else:
    print("FINAL_v4_noCap.mp4 (captions disabled)")

print(f"DONE — {total:.1f}s master driven by video.json")
