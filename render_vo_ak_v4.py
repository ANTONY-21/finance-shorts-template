#!/usr/bin/env python3
"""v4 VO: re-render ALL beats with IndexTTS2 (AK's accepted voice, identity 0.93-0.955 verified)
+ SAME reference for every beat (no chaining) + fixed sampling params = consistent single voice.
Output: /opt/kinocut-work/ch02_video1/vo_ak_v4/vo_NN.wav"""
import base64, json, os, subprocess, time

EP = 'jkbr7vf3f3c1qz'
REF = "/root/ak-ai-company/news-engine/assets/ak_voice_ref_v6.wav"
OUT = '/opt/kinocut-work/ch02_video1/vo_ak_v4'
os.makedirs(OUT, exist_ok=True)

def key():
    return subprocess.run(["bash","-c","grep -m1 '^RUNPOD_API_KEY' /opt/hermes/.env | cut -d= -f2"],
                          capture_output=True, text=True).stdout.strip()

script = json.load(open('/opt/kinocut-work/ch02_video1/script.json'))
JOBS = [(b['id'], b['vo']) for b in script['beats'] if b.get('vo') and b['vo'] != 'None']
REF_B64 = base64.b64encode(open(REF,'rb').read()).decode()
KEY = key()

def submit(text):
    spec = {"model_type": "index_tts2", "prompt": text,
            "temperature": 0.9, "top_p": 0.95,
            "media": {"audio_guide": REF_B64}}
    body = json.dumps({"input": {"spec": spec}}).encode()
    r = subprocess.run(["curl","--http1.1","-s","-X","POST",
        "-H", f"Authorization: Bearer {KEY}", "-H","Content-Type: application/json",
        "--data-binary", f"@-", f"https://api.runpod.ai/v2/{EP}/run"],
        input=body, capture_output=True, timeout=60)
    try:
        return json.loads(r.stdout)["id"]
    except Exception:
        print("submit fail:", r.stdout[:150])
        return None

def poll(jid, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(10)
        r = subprocess.run(["curl","--http1.1","-s",
            "-H", f"Authorization: Bearer {KEY}",
            f"https://api.runpod.ai/v2/{EP}/status/{jid}"], capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout)
        if d.get("status") in ("COMPLETED","FAILED"):
            return d
    return {"status":"TIMEOUT"}

results = {}
queue = list(JOBS)
in_flight = {}
while queue or in_flight:
    while queue and len(in_flight) < 2:
        bid, text = queue.pop(0)
        jid = submit(text)
        if jid:
            in_flight[jid] = bid
            print(f"beat {bid}: submitted {jid[:10]}", flush=True)
        else:
            results[bid] = False
    time.sleep(8)
    for jid, bid in list(in_flight.items()):
        d = poll(jid, timeout=30)  # single check per loop
        if d.get("status") in ("COMPLETED","FAILED","TIMEOUT"):
            del in_flight[jid]
            if d.get("status") == "COMPLETED" and isinstance(d.get("output"), dict) and d["output"].get("media_b64"):
                open(f"{OUT}/vo_{bid:02d}.wav","wb").write(base64.b64decode(d["output"]["media_b64"]))
                results[bid] = True
                print(f"beat {bid}: OK", flush=True)
            elif d.get("status") == "FAILED":
                print(f"beat {bid}: FAILED — retrying once", flush=True)
                queue.append((bid, dict(JOBS)[bid]))  # one retry
                results[bid] = False
            # TIMEOUT: leave for next check cycle
json.dump(results, open(f'{OUT}/results.json','w'), indent=1)
print(f"DONE: {sum(1 for v in results.values() if v)}/{len(JOBS)}")
