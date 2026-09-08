#!/usr/bin/env python3
"""QC gate for programmatic renders (Remotion/Blender/playwright).
Usage: python3 qc_render.py <video.mp4> [--frames 3]
Checks: duration/frames complete, resolution, no truncated streams (nb_read_frames vs
duration*fps), extracts sample frames for vision review, checks file sanity.
Exit 0 = PASS, 1 = FAIL (lists reasons)."""
import subprocess, sys, json, os, tempfile, re

def ffprobe(path):
    r = subprocess.run(['ffprobe','-v','error','-show_entries',
        'stream=codec_type,duration,width,height,nb_frames:format=duration',
        '-of','json', path], capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout)

def count_frames(path):
    r = subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
        '-show_entries','stream=nb_read_frames','-of','csv=p=0', path],
        capture_output=True, text=True, timeout=300)
    digits = re.findall(r'\d+', r.stdout)
    return int(digits[0]) if digits else -1

def main():
    path = sys.argv[1]
    n_frames_want = None
    if '--frames' in sys.argv:
        n_frames_want = int(sys.argv[sys.argv.index('--frames')+1])
    fails, warns = [], []
    if not os.path.exists(path) or os.path.getsize(path) < 10000:
        print(f"FAIL: file missing or too small ({os.path.getsize(path) if os.path.exists(path) else 0} bytes)"); sys.exit(1)
    d = ffprobe(path)
    v = next((s for s in d['streams'] if s['codec_type']=='video'), None)
    a = next((s for s in d['streams'] if s['codec_type']=='audio'), None)
    if not v: fails.append("no video stream")
    else:
        w,h = v.get('width'), v.get('height')
        if (w,h) not in [(704,1280),(1280,720),(1080,1920),(1920,1080)]:
            warns.append(f"unusual resolution {w}x{h}")
        # container duration vs real decoded frames (stream truncation trap)
        dur = float(v.get('duration') or d['format']['duration'])
        real = count_frames(path)
        if real <= 0: fails.append(f"frame count unreadable ({real})")
        elif n_frames_want and abs(real - n_frames_want) > 2:
            fails.append(f"frames {real} != expected {n_frames_want} (truncated render?)")
        elif abs(real - dur*30) > max(6, dur*30*0.05):
            fails.append(f"frames {real} vs duration*30 {dur*30:.0f} mismatch >5%")
    if not a: warns.append("no audio stream (silent render — OK for cardboard scenes pre-VO)")
    # sample frames for vision
    outdir = tempfile.mkdtemp(prefix='qc_')
    dur = float(v.get('duration') or d['format']['duration']) if v else 4
    for i, t in enumerate([dur*0.25, dur*0.55, dur*0.85]):
        fp = f"{outdir}/qc_f{i}.jpg"
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',path,'-frames:v','1',fp], timeout=60)
        if os.path.exists(fp): print(f"frame sample: {fp} (t={t:.1f}s)")
    print(json.dumps({"video": path, "FAIL": fails, "WARN": warns, "duration": round(dur,2), "frames_real": real if v else None}, indent=1))
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
