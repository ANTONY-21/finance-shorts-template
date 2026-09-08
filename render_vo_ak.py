#!/usr/bin/env python3
"""Re-render all VO beats with AK's REAL voice reference. v3 lesson: same original ref for every beat, no chaining."""
import base64
import json
import time
import urllib.request

REF = '/root/ak-ai-company/news-engine/assets/ak_voice_ref_final.wav'
EP = 'molunsye7p6ei8'
OUT = '/opt/kinocut-work/ch02_video1/vo_ak'

import os
os.makedirs(OUT, exist_ok=True)

env = {}
for line in open('/opt/hermes/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k] = v
KEY = env['RUNPOD_API_KEY']

ref_b64 = base64.b64encode(open(REF, 'rb').read()).decode()
script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))

results = {}
for b in script['beats']:
    if not b.get('vo'):
        continue
    bid = b['id']
    payload = {
        "input": {
            "text": b['vo'],
            "seed": 4242 + bid,
            "task": "tts",
            "reference_audio_b64": ref_b64,
        }
    }
    req = urllib.request.Request(
        f"https://api.runpod.ai/v2/{EP}/runsync",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=115).read())
        audio = resp.get('output', {}).get('audio_b64')
        if audio:
            p = f"{OUT}/vo_{bid:02d}.wav"
            open(p, 'wb').write(base64.b64decode(audio))
            results[bid] = {"ok": True, "path": p}
            print(f"beat {bid}: OK")
        else:
            results[bid] = {"ok": False, "err": str(resp)[:150]}
            print(f"beat {bid}: NO AUDIO")
    except Exception as e:
        results[bid] = {"ok": False, "err": str(e)[:150]}
        print(f"beat {bid}: FAIL {str(e)[:100]}")
    time.sleep(1)

json.dump(results, open('/opt/kinocut-work/ch02_video1/vo_ak_results.json', 'w'), indent=1)
ok = sum(1 for v in results.values() if v.get('ok'))
print(f"DONE: {ok}/{len(results)}")
