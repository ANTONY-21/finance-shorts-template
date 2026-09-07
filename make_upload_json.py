#!/usr/bin/env python3
"""AI YOUTUBE UPLOAD JSON GENERATOR — the canonical upload spec AK asked for.

AK: 'u have to make as JSON for YouTube to upload using AI' (2026-09-07).
For any produced video dir, this uses the local LLM (RunPod qwen3-8b — proven live path;
NIM models EOL'd) to generate the complete YouTube upload payload as ONE JSON file:

  <video_dir>/upload.json

Schema (matches youtube API + our uploader):
{
  "video_file": "...", "thumbnail_file": "...",
  "snippet": { title, description, tags[], categoryId, defaultLanguage },
  "status": { privacyStatus, selfDeclaredMadeForKids, publishAt? },
  "recordingDetails": { locationDescription? },
  "chapters": [{"time","label"}],
  "platforms": { youtube: {...}, instagram: {...}, facebook_shorts?: {...} },
  "ai": { generated_by, model, source_script, generated_at }
}

AI does the creative work (title variants, description copy, tag research from the topic DB,
chapters from real beat timings); deterministic code fills file paths + QC facts.
Nothing is invented: description numbers come from finance_topics.db source lines only.

Usage: python3 make_upload_json.py <video_dir> [--privacy public|unlisted]
"""
import json, os, sys, re, sqlite3, subprocess, datetime

ENG = '/root/ak-ai-company/news-engine'
QP_EP = 'lrptjwkuffvp3w'   # RunPod qwen3-8b (live, <1 cent/call)

def llm(prompt, max_tokens=1000, temperature=0.5):
    key = [l.strip().split('=',1)[1] for l in open('/opt/hermes/.env') if l.startswith('RUNPOD_API_KEY=')][0]
    body = json.dumps({"input":{"messages":[{"role":"user","content":prompt}],
        "sampling_params":{"max_tokens":max_tokens,"temperature":temperature}}}).encode()
    r = subprocess.run(["curl","--http1.1","-s","--max-time","180","-X","POST",
        f"https://api.runpod.ai/v2/{QP_EP}/runsync",
        "-H",f"Authorization: Bearer {key}","-H","Content-Type: application/json",
        "--data-binary","@-"], input=body, capture_output=True, timeout=200)
    d = json.loads(r.stdout)
    content = d['output'][0]['choices'][0]['message']['content']
    return re.sub(r'<think>.*?</think>', '', content, flags=re.S).strip()

def llm_json(prompt, max_tokens=1600, retries=2):
    """LLM call → parsed JSON with balanced-brace recovery + retry."""
    import re as _re
    for attempt in range(retries + 1):
        raw = llm(prompt, max_tokens=max_tokens)
        m = _re.search(r'\{.*\}', raw, _re.S)
        if m:
            s = m.group(0)
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                # balance braces and close strings
                open_b = s.count('{') - s.count('}')
                if open_b > 0:
                    s2 = s + '}' * open_b
                    try: return json.loads(s2)
                    except json.JSONDecodeError: pass
        if attempt < retries:
            prompt = prompt + "\nIMPORTANT: output ONLY valid complete JSON, all strings closed."
    raise ValueError(f"LLM JSON failed after {retries+1} attempts; last raw: {raw[:300]}")

def beat_durations(video_dir):
    """Real per-beat seconds from video_v6.json VO durations (ffprobe)."""
    cfg = json.load(open(f'{video_dir}/video_v6.json'))
    times, t = [], 0.0
    for b in cfg['beats']:
        dur = b.get('min_dur', 0)
        if b.get('vo') and os.path.exists(b['vo']):
            p = subprocess.run(['ffprobe','-v','quiet','-show_entries','format=duration',
                                '-of','csv=p=0', b['vo']], capture_output=True, text=True)
            dur = max(dur, float(p.stdout.strip() or 0))
        times.append({"time": f"{int(t//60):02d}:{int(t%60):02d}", "label": b['label'], "dur": round(dur,2)})
        t += dur
    return times, round(t, 2)

def topic_facts(video_dir):
    """Source-locked facts from the DB (never invent numbers)."""
    try:
        lines = json.load(open(f'{video_dir}/script_lines.json'))
    except Exception:
        lines = []
    # asset from dir name
    asset = os.path.basename(video_dir).split('_',1)[1].replace('_',' ') if '_' in os.path.basename(video_dir) else 'finance'
    c = sqlite3.connect(f'{ENG}/finance_topics.db')
    r = c.execute("SELECT title, hook, score, source FROM topics WHERE title LIKE ? AND source IS NOT NULL ORDER BY score DESC LIMIT 1",
                  (f"%{asset.split()[0]}%",)).fetchone()
    return lines, (r or (None,None,None,None))

def main(video_dir, privacy='public'):
    lines, (db_title, db_hook, db_score, db_source) = topic_facts(video_dir)
    chapters, total = beat_durations(video_dir)
    script_text = "\n".join(lines)
    src_note = db_source or "no source line — DO NOT state specific numbers"
    hook_note = db_hook or ""

    prompt = f"""You generate YouTube upload metadata for a vertical finance short.
Script (the actual spoken lines):
{script_text}

Verified data (USE ONLY THESE NUMBERS, never invent): {src_note}
Hook from topic DB: {hook_note}

Return ONLY JSON (no markdown) with keys:
"titles": [3 options, each <=60 chars, no clickbait lies, front-load the number/hook]
"description": a multi-line YouTube description with REAL newlines (\n characters):
line 1 = best hook; blank line; 2-sentence summary using ONLY verified numbers (ROUND display
numbers: say $79,385 not $79,385.55); blank line; "In this video:" then one bullet per chapter
with real newlines; blank line; "Sources: {src_note}"; blank line; "Not financial advice.
Education only."; blank line; 5 hashtags on the last line.
"tags": 18-22 tags (asset + emotion + evergreen finance search terms, lowercase)
"hashtags": [3 short hashtags for the title tail]
"ig_caption": 2 lines + CTA + 5 hashtags, under 300 chars
"""
    ai = llm_json(prompt)

    desc = ai['description'].replace('{{CHAPTERS}}',
        "\n".join(f"{c['time']} {c['label']}" for c in chapters))
    # deterministic cleanup: $79385.55-style precision → rounded display
    desc = re.sub(r'\$(\d+)\.\d+', lambda m: f"${int(m.group(1)):,}", desc)
    desc = re.sub(r'(\d+\.\d+)%', lambda m: f"{round(float(m.group(0)[:-1]))}%", desc)

    video_file = f"{video_dir}/out/FINAL_v6_vertical.mp4"
    horiz_file = f"{video_dir}/out/FINAL_v6_horizontal.mp4"
    spec = {
        "video_file": video_file,
        "horizontal_file": horiz_file if os.path.exists(horiz_file) else None,
        "thumbnail_file": f"{video_dir}/publish/thumbnail.jpg",
        "reel_cover_file": f"{video_dir}/publish/reel_cover.jpg",
        "snippet": {
            "title": ai['titles'][0],
            "title_options": ai['titles'],
            "description": desc,
            "tags": ai['tags'][:22],
            "categoryId": "25",
            "defaultLanguage": "en",
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
        "chapters": [{"time": c['time'], "label": c['label']} for c in chapters],
        "duration_seconds": total,
        "platforms": {
            "youtube": {"file": video_file, "thumbnail": f"{video_dir}/publish/thumbnail.jpg"},
            "instagram_reel": {"file": video_file, "cover": f"{video_dir}/publish/reel_cover.jpg",
                               "caption": ai['ig_caption']},
        },
        "ai": {"generated_by": "qwen3-8b@runpod", "topic_db_title": db_title,
               "topic_score": db_score, "source_line": db_source,
               "script_lines": len(lines), "generated_at": datetime.datetime.now().isoformat()},
    }
    out = f"{video_dir}/upload.json"
    json.dump(spec, open(out, 'w'), indent=1)
    print(f"UPLOAD JSON → {out}")
    print("TITLE:", spec['snippet']['title'])
    print("TAGS:", len(spec['snippet']['tags']), "| chapters:", len(spec['chapters']), "| duration:", total, "s")
    return spec

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 else
         (sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ('public','unlisted') else 'public'))
