#!/usr/bin/env python3
"""Whisper word-level timestamps per VO beat -> caption JSONs (word-synced)."""
import json
import os

from faster_whisper import WhisperModel

OUT = '/opt/kinocut-work/ch02_video1/captions'
os.makedirs(OUT, exist_ok=True)
model = WhisperModel('base', device='cpu', compute_type='int8')

script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))
all_caps = {}
for b in script['beats']:
    if not b.get('vo'):
        continue
    bid = b['id']
    wav = f'/opt/kinocut-work/ch02_video1/vo_ak/vo_{bid:02d}.wav'
    if not os.path.exists(wav):
        wav = f'/opt/kinocut-work/ch02_video1/vo/vo_{bid:02d}.wav'
    segments, info = model.transcribe(wav, word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)})
    all_caps[bid] = words
    print(f"beat {bid}: {len(words)} words")

json.dump(all_caps, open('/opt/kinocut-work/ch02_video1/captions/word_captions.json', 'w'), indent=1)
print('captions saved')
