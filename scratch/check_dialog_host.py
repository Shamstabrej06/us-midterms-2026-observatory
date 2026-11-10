import asyncio
import json
import urllib.request
import websockets

async def check_dialog():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "desktopDialogHost" in t.get("url", "")), None)
    if not target:
        print("No desktopDialogHost target")
        return

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws.recv()

        eval_script = """
        (() => {
            return {
                title: document.title,
                text: document.body.innerText.trim(),
                buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim())
            };
        })()
        """
        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": eval_script, "returnByValue": True}
        }))
        res = json.loads(await ws.recv())
        print("Dialog content:\n", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check_dialog())
