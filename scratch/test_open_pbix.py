import subprocess
import os
import time
import urllib.request
import json

pbi_exe = r'C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\PBIDesktop.exe'
pbix_path = r'C:\Users\shams\us-midterms-2026-observatory\MidtermsObservatory-automation-test.pbix'
repo_dir = r'C:\Users\shams\us-midterms-2026-observatory'

env = os.environ.copy()
env['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS'] = '--remote-debugging-port=9222'

print(f"Launching PBIDesktop.exe with {pbix_path}...")
proc = subprocess.Popen([pbi_exe, pbix_path], cwd=repo_dir, env=env)
print("Spawned PID:", proc.pid)

for i in range(30):
    time.sleep(1)
    try:
        req = urllib.request.urlopen("http://localhost:9222/json", timeout=1)
        targets = json.loads(req.read().decode())
        pages = [t for t in targets if t.get('type') == 'page']
        print(f"[{i}s] Connected! Pages found: {len(pages)}")
        for p in pages:
            print("   ", p.get('title'), "|", p.get('url'))
        dialog = next((t for t in pages if 'desktopDialogHost' in t.get('url', '')), None)
        if dialog:
            print("DIALOG DETECTED!")
        report = next((t for t in pages if 'reportView' in t.get('url', '')), None)
        if report and i > 15:
            break
    except Exception as e:
        if i % 3 == 0:
            print(f"[{i}s] Waiting for CDP...")
