#!/usr/bin/env python3
"""v4b: sequential render of missing beats. Poll full-length, save on COMPLETED."""
import base64, json, os, subprocess, time

EP = 'jkbr7vf3f3c1qz'
REF = "/root/ak-ai-company/news-engine/assets/ak_voice_ref_v6.wav"
OUT = '/opt/kinocut-work/ch02_video1/vo_ak_v4'
os.makedirs(OUT, exist_ok=True)
KEY = [l.strip().split('=',1)[1] for l in open('/opt/hermes/.env') if l.startswith('RUNPOD_API_KEY=')][0]

script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))
JOBS = {b['id']: b['vo'] for b in script['beats'] if b.get('vo') and b['vo'] != 'None'}
missing = [b for b in sorted(JOBS) if not os.path.exists(f'{OUT}/vo_{b:02d}.wav')]
print("missing:", missing, flush=True)
REF_B64 = base64.b64encode(open(REF,'rb').read()).decode()

def submit(text):
    spec = {"model_type": "index_tts2", "prompt": text,
            "temperature": 0.9, "top_p": 0.95, "media": {"audio_guide": REF_B64}}
    body = json.dumps({"input": {"spec": spec}}).encode()
    r = subprocess.run(["curl","--http1.1","-s","-X","POST",
        "-H", f"Authorization: Bearer {KEY}", "-H","Content-Type: application/json",
        "--data-binary","@-", f"https://api.runpod.ai/v2/{EP}/run"],
        input=body, capture_output=True, timeout=60)
    return json.loads(r.stdout).get("id")

for bid in missing:
    jid = submit(JOBS[bid])
    print(f"beat {bid}: {jid}", flush=True)
    if not jid:
        continue
    t0 = time.time()
    while time.time() - t0 < 600:
        time.sleep(12)
        r = subprocess.run(["curl","--http1.1","-s","-H",f"Authorization: Bearer {KEY}",
            f"https://api.runpod.ai/v2/{EP}/status/{jid}"], capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout)
        st = d.get("status")
        if st == "COMPLETED":
            out = d.get("output") or {}
            if out.get("media_b64"):
                open(f"{OUT}/vo_{bid:02d}.wav","wb").write(base64.b64decode(out["media_b64"]))
                print(f"beat {bid}: OK {time.time()-t0:.0f}s", flush=True)
            break
        if st == "FAILED":
            print(f"beat {bid}: FAILED", flush=True)
            break
print("RENDER COMPLETE", flush=True)
