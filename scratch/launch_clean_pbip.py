import subprocess
import os
import time
import urllib.request
import json

pbi_exe = r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe'
repo_dir = r'C:\Users\shams\us-midterms-2026-observatory'
pbip_path = os.path.join(repo_dir, 'MidtermsObservatory.pbip')

env = os.environ.copy()
env['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--remote-debugging-port=9222'

print(f"Launching PBIDesktop.exe with {pbip_path}...")
proc = subprocess.Popen([pbi_exe, pbip_path], cwd=repo_dir, env=env)
print("Spawned direct PID:", proc.pid)

for i in range(25):
    time.sleep(1)
    try:
        req = urllib.request.urlopen("http://localhost:9222/json", timeout=1)
        data = json.loads(req.read().decode())
        print(f"[{i}s] CDP connected on port 9222! Found {len(data)} targets:")
        for t in data:
            print("   Target:", t.get("type"), "|", t.get("title"), "|", t.get("url"))
        break
    except Exception as e:
        if i % 3 == 0:
            print(f"[{i}s] Waiting for CDP: {e}")
