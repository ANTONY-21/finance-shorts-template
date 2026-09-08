#!/usr/bin/env python3
"""Voice consistency gate: cosine similarity of each beat's speaker embedding vs the AK reference.
Any beat < 0.80 similarity = MIXED VOICE, re-render it."""
import os

import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav

REF = '/root/ak-ai-company/news-engine/assets/ak_voice_ref_final.wav'
VO_DIR = '/opt/kinocut-work/ch02_video1/vo_ak'

encoder = VoiceEncoder()
ref_wav = preprocess_wav(REF)
ref_emb = encoder.embed_utterance(ref_wav)

print("beat | similarity | verdict")
bad = []
for i in range(1, 11):
    p = f"{VO_DIR}/vo_{i:02d}.wav"
    if not os.path.exists(p):
        print(f"{i:02d}  | MISSING")
        bad.append(i)
        continue
    w = preprocess_wav(p)
    emb = encoder.embed_utterance(w)
    sim = float(np.dot(ref_emb, emb) / (np.linalg.norm(ref_emb) * np.linalg.norm(emb)))
    v = "OK" if sim >= 0.80 else "MIXED <<<"
    print(f"{i:02d}  | {sim:.3f}      | {v}")
    if sim < 0.80:
        bad.append(i)
print("\nbad beats:", bad)
