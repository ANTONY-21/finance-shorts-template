#!/usr/bin/env python3
"""Re-render vo_08 with corrected drawdown number (-45%) via IndexTTS2 on wan2gp."""
import json, base64, subprocess, time

BASE = '/opt/kinocut-work/ch02_video1'
KEY = [l.strip().split('=', 1)[1] for l in open('/opt/hermes/.env') if l.startswith('RUNPOD_API_KEY=')][0]

text = ("But know the risk: gold has fallen almost forty five percent from its peak before, "
        "and stayed down for years. Record price means record risk of a dip.")
ref = base64.b64encode(open('/root/ak-ai-company/news-engine/assets/ak_voice_ref_v6.wav', 'rb').read()).decode()

spec = {"model_type": "index_tts2", "prompt": text,
        "temperature": 0.9, "top_p": 0.95,
        "media": {"audio_guide": ref}}
body = json.dumps({"input": {"spec": spec}}).encode()
r = subprocess.run(["curl", "--http1.1", "-s", "-X", "POST",
                    "-H", f"Authorization: Bearer {KEY}",
                    "-H", "Content-Type: application/json", "--data-binary", "@-",
                    "https://api.runpod.ai/v2/jkbr7vf3f3c1qz/runsync"],
                   input=body, capture_output=True, timeout=600)
d = json.loads(r.stdout)
print("status:", d.get("status"))
out = d.get("output") or {}
if isinstance(out, dict) and out.get("media_b64"):
    open(f'{BASE}/vo_ak_v4/vo_08.wav', 'wb').write(base64.b64decode(out["media_b64"]))
    p = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', f'{BASE}/vo_ak_v4/vo_08.wav'],
                       capture_output=True, text=True)
    print("vo_08.wav re-rendered:", p.stdout.strip(), "s")
else:
    print("keys:", list(out.keys())[:8], str(d.get("error"))[:200])
