#!/usr/bin/env python3
"""Captions v4: whisper word timestamps on AK v4 (IndexTTS2) voice → captions_v6.ass"""
import json, os, subprocess
from faster_whisper import WhisperModel

BASE = '/opt/kinocut-work/ch02_video1'
model = WhisperModel('base', device='cpu', compute_type='int8')

tl = json.load(open(f'{BASE}/timeline.json'))['timeline']
vo_map = {1:'vo_01',2:'vo_02',3:'vo_03',4:'vo_04',5:'vo_05',6:'vo_06',
          7:'vo_07a',8:'vo_07b',9:'vo_07c',10:'vo_08',11:'vo_09',12:'vo_10'}

events = []
pos = 0
for s in tl:
    bid = s['id']
    if bid in vo_map:
        wav = f"{BASE}/vo_ak_v4/{vo_map[bid]}.wav"
        segments, _ = model.transcribe(wav, word_timestamps=True)
        words = []
        for seg in segments:
            for w in seg.words:
                words.append({"w": w.word.strip(), "start": w.start, "end": w.end})
        line, line_start = [], None
        for w in words:
            if line_start is None:
                line_start = w['start']
            line.append(w)
            if len(line) >= 4:
                start = pos + line_start
                end = pos + w['end']
                events.append((start, max(end, start + 0.5), ' '.join(x['w'] for x in line)))
                line, line_start = [], None
        if line:
            start = pos + line_start
            end = pos + words[-1]['end']
            events.append((start, max(end, start + 0.5), ' '.join(x['w'] for x in line)))
    pos += s['dur']

def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

header = """[Script Info]
ScriptType: v4.00
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Style: Cap,DejaVu Sans,40,&H00FFFFFF,&H00000000,&H00000000,&H7F000000,-1,0,0,0,100,100,0,0,1,2,0,50,50,35,2,1

[Events]
"""
lines = [f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{t}" for a, b, t in events]
open(f'{BASE}/captions_v6.ass','w').write(header + "\n".join(lines))
print(f"{len(events)} caption events written")
