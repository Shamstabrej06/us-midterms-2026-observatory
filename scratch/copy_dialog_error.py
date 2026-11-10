import asyncio
import json
import urllib.request
import websockets
import subprocess

async def copy_details():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "desktopDialogHost" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"]) as ws:
        code = """
        (() => {
            const copyBtn = Array.from(document.querySelectorAll('button, a')).find(e => e.innerText && e.innerText.includes('Copy'));
            if (copyBtn) {
                copyBtn.click();
                return 'clicked copy';
            }
            return 'no copy btn';
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(res.get("result", {}).get("result", {}).get("value"))

asyncio.run(copy_details())

# Now get clipboard from powershell
out = subprocess.check_output(["powershell", "-command", "Get-Clipboard"]).decode("utf-8", errors="ignore")
print("CLIPBOARD CONTENT:\n", out)
