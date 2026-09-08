#!/usr/bin/env python3
"""Render all VO beats via voxcpm-tts-baked endpoint, seed-pinned, save wavs."""
import base64
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
EP = 'molunsye7p6ei8'
OUT = '/opt/kinocut-work/ch02_video1/vo'

results = {}
for b in script['beats']:
    if not b.get('vo'):
        continue
    bid = b['id']
    txt = b['vo']
    if bid == 1:
        txt = "(A confident young Indian male finance creator, clear energetic tone)" + txt
    payload = {"input": {"text": txt, "seed": 4242 + bid, "task": "tts"}}
    req = urllib.request.Request(
        f"https://api.runpod.ai/v2/{EP}/runsync",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=115).read())
        audio = resp.get('output', {}).get('audio_b64')
        if audio:
            wav_path = f"{OUT}/vo_{bid:02d}.wav"
            open(wav_path, 'wb').write(base64.b64decode(audio))
            results[bid] = {"ok": True, "path": wav_path}
            print(f"beat {bid}: OK -> {wav_path}")
        else:
            results[bid] = {"ok": False, "err": str(resp)[:200]}
            print(f"beat {bid}: NO AUDIO {str(resp)[:120]}")
    except Exception as e:
        results[bid] = {"ok": False, "err": str(e)[:200]}
        print(f"beat {bid}: FAIL {str(e)[:120]}")
    time.sleep(1)

json.dump(results, open('/opt/kinocut-work/ch02_video1/vo_results.json', 'w'), indent=1)
ok = sum(1 for v in results.values() if v.get('ok'))
print(f"DONE: {ok}/{len(results)}")
