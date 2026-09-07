#!/usr/bin/env python3
"""V6 assembly — reads video_v6.json, drives everything: per-beat segment rendering (tpad
clone-hold, NEVER loop), concat, VO placement at exact beat starts, music bed, loudnorm,
kinetic captions (2-3 words per chip). Renders BOTH 9:16 vertical and 16:9 horizontal."""
import json, os, subprocess, math

import os, sys
BASE = os.environ.get('VIDEO_BASE', sys.argv[1] if len(sys.argv) > 1 else '/opt/kinocut-work/ch02_video1')
FPS = 30

def sh(cmd, timeout=900):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"CMD FAILED: {cmd[:120]}\n{r.stderr[-400:]}")
    return r.stdout

def dur(p):
    return float(sh(f"ffprobe -v quiet -show_entries format=duration -of csv=p=0 '{p}'").strip())

def build(aspect, cfg, outname):
    vert = aspect == '9:16'
    W, H = (720, 1280) if vert else (1280, 720)
    tmp = f"{BASE}/v6_{ 'vert' if vert else 'horz' }"
    os.makedirs(tmp, exist_ok=True)
    timeline = []
    t = 0.0
    for b in cfg['beats']:
        vo_d = dur(b['vo']) if b.get('vo') else 0
        slot = max(vo_d, b.get('min_dur', 0), 1.2)
        slot = round(slot, 3)
        visual = b['visual']
        seg = f"{tmp}/seg_{b['id']:02d}.mp4"
        # prefer animated card mp4 when it exists (daily_cards v1.5)
        cand = visual.rsplit('.',1)[0] + '.mp4'
        import os as _os
        if _os.path.exists(cand) and '/cards_v6/' in visual:
            visual = cand
        if visual.endswith('.mp4') and '/cards_v6/' in visual:
            # animated card: re-encode to slot length (slow the 3s animation across slot via tpad-clone)
            sh(f"ffmpeg -y -v error -stream_loop -1 -i '{visual}' -t {slot:.3f} -vf scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p -an -c:v libx264 -preset fast -crf 19 '{seg}'")
        elif visual.endswith(('.jpg', '.png')):
            # zoompan on static image at target WxH
            zr = "min(zoom+0.0006,1.12)"
            vf = (f"scale={W*2}:{H*2},zoompan=z='{zr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                  f"d={int(slot*FPS)+1}:s={W}x{H}:fps={FPS},format=yuv420p")
            sh(f"ffmpeg -y -v error -loop 1 -i '{visual}' -t {slot:.3f} -vf \"{vf}\" -r {FPS} -an -c:v libx264 -preset fast -crf 19 '{seg}'")
        else:
            vd = dur(visual)
            if vd >= slot:
                cut = f"-t {slot:.3f}"
            else:
                cut = ""  # will tpad
            # scale/crop to target aspect
            if vert:
                vf = "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30,format=yuv420p"
            else:
                vf = "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=30,format=yuv420p"
            if vd < slot:
                hold = slot - vd
                sh(f"ffmpeg -y -v error -i '{visual}' {cut} -vf \"tpad=stop_mode=clone:stop_duration={hold:.3f},{vf}\" -an -c:v libx264 -preset fast -crf 19 '{seg}'")
            else:
                sh(f"ffmpeg -y -v error -i '{visual}' {cut} -vf \"{vf}\" -an -c:v libx264 -preset fast -crf 19 '{seg}'")
        timeline.append({"id": b['id'], "label": b['label'], "start": round(t, 3), "dur": slot, "vo": b.get('vo')})
        t += slot
    # concat
    with open(f"{tmp}/concat.txt", "w") as f:
        for s in timeline:
            f.write(f"file '{tmp}/seg_{s['id']:02d}.mp4'\n")
    total = t
    # audio: VO at exact starts
    inputs, filters, labels = [], [], []
    for i, s in enumerate(timeline):
        if s['vo']:
            inputs += ["-i", s['vo']]
            filters.append(f"[{i+1}:a]adelay={int(s['start']*1000)}|{int(s['start']*1000)}[a{i}]")
            labels.append(f"[a{i}]")
    music = cfg['music']
    inputs += ["-i", music['path']]
    mvol = music['volume']
    fade = music['fade_out']
    filt = ";".join(filters) + ";" if filters else ""
    filt += (f"[{len(timeline)+1 if False else len([x for x in inputs])//2}:a]" if False else f"[{len(inputs)//2 - 1}:a]")
    # simpler: recompute music index
    music_idx = len([x for x in inputs]) // 2  # after loop inputs consumed: len(vo)*2, then music at that index
    # rebuild filter explicitly
    parts = []
    nvo = 0
    for i, s in enumerate(timeline):
        if s['vo']:
            parts.append(f"[{nvo+1}:a]adelay={int(s['start']*1000)}|{int(s['start']*1000)}[a{nvo}]")
            nvo += 1
    vo_labels = "".join(f"[a{i}]" for i in range(nvo))
    fade_start = max(0, total - fade)
    amix_in = (vo_labels + f"[{len([x for x in inputs])//2 - 0}:a]") if False else (vo_labels + f"[{nvo*1 + 0}:a]")
    # music input index = number of VO inputs (0-based among -i list after primary? all inputs are media)
    # inputs order: vo1..voK, music → indices 0..K (but first input slot unused! we only add vos)
    music_idx = nvo
    parts.append(f"[{music_idx+1}:a]volume={mvol},afade=t=out:st={fade_start:.2f}:d={fade}[m]")
    parts.append(f"{vo_labels if vo_labels else ''}[m]amix=inputs={nvo+1}:duration=longest:dropout_transition=0:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    full = ";".join(parts)
    concat = f"{tmp}/concat.txt"
    master = f"{tmp}/{outname}_noCap.mp4"
    sh(f"ffmpeg -y -v error -f concat -safe 0 -i '{concat}' {' '.join(inputs)} -filter_complex \"{full}\" -map 0:v -map \"[aout]\" -c:v copy -c:a aac -b:a 192k -t {total:.3f} '{master}'")
    return timeline, master, total

def kinetic_captions(cfg, timeline, out_ass):
    """2-3 word chips centered mid-lower, from whisper word timings."""
    from faster_whisper import WhisperModel
    model = WhisperModel('base', device='cpu', compute_type='int8')
    events = []
    for s in timeline:
        if not s['vo']:
            continue
        segments, _ = model.transcribe(s['vo'], word_timestamps=True)
        seg_words = [x for seg in segments for x in seg.words]
        raw_words = [w.word.strip() for w in seg_words]
        # word-level merge: "1" + ".26000" → "126,000"; digit+fraction splits → decimals
        merged = []
        skip_next = False
        for j, wd in enumerate(raw_words):
            if skip_next:
                skip_next = False
                continue
            if wd in ("1", "$79") and j + 1 < len(raw_words) and raw_words[j+1].startswith("."):
                nxt = raw_words[j+1]
                if wd == "1" and nxt == ".26000":
                    merged.append("126,000")
                elif wd == "$79" and nxt.startswith(","):
                    merged.append("$79,000")
                else:
                    merged.append(wd + nxt)
                skip_next = True
                continue
            merged.append(wd)
        words = [{"w": wd, "start": seg_words[k].start, "end": seg_words[k].end}
                 for k, wd in enumerate(merged)]
        # group into chips of 2-3 words
        i = 0
        while i < len(words):
            n = 2 if i + 2 >= len(words) else 3
            chunk = words[i:i+n]
            start = s['start'] + chunk[0]['start']
            end = s['start'] + chunk[-1]['end']
            text = " ".join(x['w'] for x in chunk)
            text = text.replace(" %", "%")  # whisper splits '30 %' → rejoin
            # whisper mis-transcription corrections (finance terms + numerals)
            for bad, good in (("ATFs", "ETFs"), ("ATF", "ETF"), ("jewelry", "jewellery"),
                              ("1 .26000", "126,000"), ("$79 ,000", "$79,000"),
                              ("5 .5 %", "5.5%"), ("2 -5 %", "2-5%"), ("22 .4 %", "22.4%")):
                text = text.replace(bad, good)
            events.append((start, max(end, start + 0.45), text))
            i += n
    def ts(t):
        h = int(t // 3600); m = int((t % 3600) // 60); sec = t % 60
        return f"{h}:{m:02d}:{sec:05.2f}"
    header = f"""[Script Info]
ScriptType: v4.00
PlayResX: {'720' if 'vert' in out_ass else '1280'}
PlayResY: {'1280' if 'vert' in out_ass else '720'}

[V4+ Styles]
Style: Cap,Liberation Sans,54,&H00FFFFFF,&H00000000,&HB4000000,&H7F000000,-1,0,0,0,100,100,0.6,0,1,3,2,60,60,30,1

[Events]
"""
    lines = [f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{t}" for a, b, t in events]
    open(out_ass, 'w').write(header + "\n".join(lines))
    return len(events)

if __name__ == "__main__":
    cfg = json.load(open(f"{BASE}/video_v6.json"))
    for aspect, name in (("9:16", "FINAL_v6_vertical"), ("16:9", "FINAL_v6_horizontal")):
        timeline, master, total = build(aspect, cfg, name)
        print(f"{aspect}: {total:.1f}s, {len(timeline)} beats")
        tag = 'vert' if aspect == '9:16' else 'horz'
        n = kinetic_captions(cfg, timeline, f"{BASE}/captions_v6_{tag}.ass")
        print(f"  captions: {n} chips")
        final = f"{BASE}/out/{name}.mp4"
        fs = "FontSize=46,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Shadow=1,Alignment=2,MarginV=210"
        vf = (f"subtitles=filename={BASE}/captions_v6_{tag}.ass:force_style='{fs}',"
              f"setsar=1")
        sh(f"ffmpeg -y -v error -i '{master}' -vf \"{vf}\" -c:v libx264 -preset medium -crf 20 -c:a copy '{final}'")  # vf quoted as one arg
        print(f"  → {final}")
