#!/usr/bin/env python3
"""Submit all VO beats to voxcpm endpoint, seed-pinned (v6 lesson)."""
import json
import time
import urllib.request

script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))
env = {}
for line in open('/opt/hermes/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k] = v
KEY = env['RUNPOD_API_KEY']
EP = 's2bcgge6abt3m2'

results = {}
for b in script['beats']:
    if not b.get('vo'):
        continue
    bid = b['id']
    txt = b['vo']
    if bid == 1:
        # voice-design control prefix for consistent brand voice (voxcpm design mode)
        txt = "(A confident young Indian male finance creator, clear energetic tone)" + txt
    payload = {"input": {"text": txt, "seed": 4242 + bid, "task": "tts"}}
    req = urllib.request.Request(
        f"https://api.runpod.ai/v2/{EP}/run",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    try:
        job = json.loads(urllib.request.urlopen(req, timeout=30).read())
        results[bid] = job.get('id')
        print(f"beat {bid}: submitted {job.get('id')}")
    except Exception as e:
        results[bid] = f"FAIL {e}"
        print(f"beat {bid}: FAIL {e}")
    time.sleep(1)

json.dump(results, open('/opt/kinocut-work/ch02_video1/vo_jobs.json', 'w'), indent=1)
ok = sum(1 for v in results.values() if not str(v).startswith('FAIL'))
print(f"submitted: {ok}/{len(results)}")
