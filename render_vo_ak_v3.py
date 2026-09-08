#!/usr/bin/env python3
"""v3: AK voice on proven voxcpm endpoint, SMALL ref (v6-era size ~730KB), short prompt_text.
Renders all 10 beats sequentially. Retry once per beat on failure."""
import base64
import json
import os
import time
import urllib.request

REF_WAV = '/root/ak-ai-company/news-engine/assets/ak_voice_ref_small.wav'
EP = 's2bcgge6abt3m2'
OUT = '/opt/kinocut-work/ch02_video1/vo_ak_v3'
os.makedirs(OUT, exist_ok=True)

env = {}
for line in open('/opt/hermes/.env'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        env[k] = v
KEY = env['RUNPOD_API_KEY']

REF_B64 = base64.b64encode(open(REF_WAV, 'rb').read()).decode()
# short, exact prompt_text: first 2 sentences of the trimmed ref window (26.6s onward)
PROMPT_TEXT = ("I work in cybersecurity and spend much of my time collaborating with colleagues, "
               "customers and technical vendors.")
print('ref b64 len:', len(REF_B64))

script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))

def render(text, seed):
    body = json.dumps({"input": {"text": text, "reference_audio": REF_B64,
                                 "prompt_text": PROMPT_TEXT, "language": "en",
                                 "seed": seed}}).encode()
    req = urllib.request.Request(f"https://api.runpod.ai/v2/{EP}/run", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["id"]

def poll(jid, timeout_s=240):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        time.sleep(6)
        req = urllib.request.Request(f"https://api.runpod.ai/v2/{EP}/status/{jid}",
                                     headers={"Authorization": f"Bearer {KEY}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        st = d.get("status")
        if st == "COMPLETED":
            return d
        if st in ("FAILED", "CANCELLED"):
            raise RuntimeError(str(d)[:150])
    raise TimeoutError("poll timeout")

results = {}
for b in script['beats']:
    if not b.get('vo'):
        continue
    bid = b['id']
    ok = False
    for attempt in (1, 2):
        try:
            jid = render(b['vo'], 4242 + bid + (100 * attempt))
            print(f"beat {bid} try{attempt}: {jid[:12]}")
            d = poll(jid)
            audio = (d.get('output') or {}).get('audio_b64')
            if audio:
                p = f"{OUT}/vo_{bid:02d}.wav"
                open(p, 'wb').write(base64.b64decode(audio))
                results[bid] = {"ok": True}
                print(f"beat {bid}: OK")
                ok = True
                break
        except Exception as e:
            print(f"beat {bid} try{attempt}: FAIL {str(e)[:100]}")
    if not ok:
        results[bid] = {"ok": False}

json.dump(results, open('/opt/kinocut-work/ch02_video1/vo_ak_v3_results.json', 'w'), indent=1)
okc = sum(1 for v in results.values() if v.get('ok'))
print(f"DONE: {okc}/{len(results)}")
