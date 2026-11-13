import subprocess
import os
import time
import urllib.request
import json
import asyncio
import websockets
import base64

pbi_exe = r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe'
pbix_path = r'C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory.pbix'
repo_dir = r'C:\Users\shams\us-midterms-2026-observatory'

env = os.environ.copy()
env['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--remote-debugging-port=9222'

print("Launching PBIDesktop with MidtermsObservatory.pbix...")
proc = subprocess.Popen([pbi_exe, pbix_path], cwd=repo_dir, env=env)
print("Spawned PID:", proc.pid)

time.sleep(12)

async def capture():
    for _ in range(15):
        try:
            req = urllib.request.urlopen("http://localhost:9222/json", timeout=2)
            targets = json.loads(req.read().decode())
            r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
            if r_target:
                print("Connected to reportView, capturing screenshot...")
                async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=20*1024*1024) as ws:
                    await ws.send(json.dumps({'id': 1, 'method': 'Page.captureScreenshot', 'params': {'format': 'png'}}))
                    res = json.loads(await ws.recv())
                    img_data = base64.b64decode(res['result']['data'])
                    out_path = r'C:\Users\shams\us-midterms-2026-observatory\powerbi\screenshots\midtermsobservatory_ready_state.png'
                    with open(out_path, 'wb') as f:
                        f.write(img_data)
                    print(f"Saved ready state screenshot to {out_path} ({len(img_data)} bytes)")
                    return
        except Exception as e:
            print("Waiting for ready state...", e)
            time.sleep(1)

asyncio.run(capture())

# Terminate process cleanly
proc.terminate()
print("Terminated process cleanly.")
