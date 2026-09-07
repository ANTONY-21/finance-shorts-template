#!/usr/bin/env python3
"""Dump whisper word output for each VO to find mis-transcriptions before caption burn."""
import sys
from faster_whisper import WhisperModel

m = WhisperModel("base", device="cpu", compute_type="int8")
for vid in ["vo_08", "vo_07c", "vo_06"]:
    path = f"/opt/kinocut-work/ch02_video1/vo_ak_v4/{vid}.wav"
    segs, _ = m.transcribe(path, word_timestamps=True)
    ws = [w.word.strip() for s in segs for w in s.words]
    print(vid, "::", " ".join(ws))
