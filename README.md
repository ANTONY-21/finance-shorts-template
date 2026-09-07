# Finance Shorts Template

Vertical 9:16 (+ horizontal 16:9) finance/news shorts video pipeline.
Built from the gold-price video (V6) — JSON-timeline driven, fully local, rerunnable.

## How it works

1. **`video_v6.json`** = single source of truth. Each beat: `{id, label, visual, visual_mode, vo, min_dur}`.
2. **`assemble_v6.py`** derives every duration from the real VO files (ffprobe) — nothing hardcoded.
   Renders BOTH aspects from the same timeline (zoompan for cards, scale+crop for videos,
   `tpad=stop_mode=clone` frame-hold — never `-stream_loop`).
   Audio: VO placed at exact beat starts (adelay), music bed mixed under, loudnorm -14 LUFS.
   **amix must use `duration=longest`** (with adelayed inputs `first` = silent tail bug).
   **`setsar=1` at final encode** (zoompan poisons SAR → players stretch the frame).
3. **`make_cards_v6.py`** — PIL vertical cards (hook, number callouts, rules, risk, verdict, CTA).
4. **`make_gold_chart_v6.py`** — PIL animated chart (line draw → label → record zone).
5. **`capture_site_long.py`** — playwright slow-scroll capture of a REAL website (mobile viewport,
   is_mobile, 720x1280) → frame-sequence → site-scroll clip. Real data on screen, not mockups.
6. **Voice** — IndexTTS2 via RunPod wan2gp (`{"input":{"spec":{"model_type":"index_tts2","prompt":text,
   "media":{"audio_guide":<raw-b64-of-ref>}}}}`), SAME reference file every beat = consistent voice.
7. **Captions** — faster_whisper word timestamps → 2-3 word kinetic chips, force_style burned.
   Correction map applied to whisper output (finance terms: ATFs→ETFs etc.) before burning.
8. **Data accuracy** — every number needs a source line checked BEFORE render. Carry-over figures
   from earlier versions silently rot.

## Regenerate for a new topic

1. Copy the folder, write a new `script.json` (10-14 beats with vo text per beat).
2. Render all VOs (same ref wav). Split multi-part beats at word boundaries (faster_whisper).
3. Update `video_v6.json` beats to point at your visuals (cards/captures/charts).
4. `python3 make_cards_v6.py && python3 capture_site_long.py`
5. `/opt/news-engine-venv/bin/python assemble_v6.py` → `out/FINAL_v6_vertical.mp4` + `FINAL_v6_horizontal.mp4`.

## QC before shipping

- audio stream duration == video duration (amix silent-tail check)
- ffprobe sample_aspect_ratio == 1:1 (ratio check)
- 0 black frames; peak <= -1 dB
- every number on screen matches the VO and has a source line
- captions spell-checked (whisper dumps words — see check_whisper_words.py)
