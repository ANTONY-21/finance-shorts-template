#!/usr/bin/env python3
"""Re-render all VO beats on the PROVEN voxcpm endpoint (s2bcgge6abt3m2) with the PROVEN contract:
reference_audio + prompt_text + language + seed. AK's real voice. Same original ref for every beat."""
import base64
import json
import os
import time
import urllib.request

REF_WAV = '/root/ak-ai-company/news-engine/assets/ak_voice_ref_final.wav'
EP = 's2bcgge6abt3m2'
OUT = '/opt/kinocut-work/ch02_video1/vo_ak_v2'
os.makedirs(OUT, exist_ok=True)

env = {}
for line in open('/opt/hermes/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k] = v
KEY = env['RUNPOD_API_KEY']

REF_B64 = base64.b64encode(open(REF_WAV, 'rb').read()).decode()
# prompt_text = what is actually spoken in the reference (complete sentences — v3 lesson)
PROMPT_TEXT = open('/root/ak-ai-company/news-engine/assets/ak_voice_fresh_transcript.txt').read().split('.')[0:3]
PROMPT_TEXT = '. '.join(s.strip() for s in PROMPT_TEXT if s.strip()) + '.'
print('prompt_text:', PROMPT_TEXT[:150])

script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))

def render(text, seed):
    body = json.dumps({"input": {"text": text, "reference_audio": REF_B64,
                                 "prompt_text": PROMPT_TEXT, "language": "en",
                                 "seed": seed}}).encode()
    req = urllib.request.Request(f"https://api.runpod.ai/v2/{EP}/run", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["id"]

def poll(jid, timeout_s=600):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        time.sleep(8)
        req = urllib.request.Request(f"https://api.runpod.ai/v2/{EP}/status/{jid}",
                                     headers={"Authorization": f"Bearer {KEY}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        if d.get("status") == "COMPLETED":
            return d
        if d.get("status") in ("FAILED", "CANCELLED"):
            raise RuntimeError(str(d)[:200])
    raise TimeoutError(jid)

results = {}
for b in script['beats']:
    if not b.get('vo'):
        continue
    bid = b['id']
    try:
        jid = render(b['vo'], 4242 + bid)
        print(f"beat {bid}: submitted {jid[:12]}")
        d = poll(jid)
        audio = (d.get('output') or {}).get('audio_b64')
        if audio:
            p = f"{OUT}/vo_{bid:02d}.wav"
            open(p, 'wb').write(base64.b64decode(audio))
            results[bid] = {"ok": True, "path": p}
            print(f"beat {bid}: OK")
        else:
            results[bid] = {"ok": False, "err": "no audio"}
            print(f"beat {bid}: NO AUDIO")
    except Exception as e:
        results[bid] = {"ok": False, "err": str(e)[:150]}
        print(f"beat {bid}: FAIL {str(e)[:120]}")

json.dump(results, open('/opt/kinocut-work/ch02_video1/vo_ak_v2_results.json', 'w'), indent=1)
ok = sum(1 for v in results.values() if v.get('ok'))
print(f"DONE: {ok}/{len(results)}")
