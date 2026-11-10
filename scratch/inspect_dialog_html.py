import asyncio
import json
import urllib.request
import websockets

async def check_dialog_dom():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "desktopDialogHost" in t.get("url", "")), None)
    if not target:
        print("No dialog host")
        return

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            return {
                url: window.location.href,
                bodyHtml: document.body.innerHTML,
                windowProps: Object.keys(window).filter(k => k.toLowerCase().includes('dialog') || k.toLowerCase().includes('data') || k.toLowerCase().includes('error'))
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        val = res.get("result", {}).get("result", {}).get("value")
        print("Dialog URL:", val.get("url"))
        print("Props:", val.get("windowProps"))
        print("Body HTML:\n", val.get("bodyHtml"))

asyncio.run(check_dialog_dom())
