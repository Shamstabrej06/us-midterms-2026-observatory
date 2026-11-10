import asyncio
import json
import urllib.request
import websockets

async def get_details():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "desktopDialogHost" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"]) as ws:
        # First let's click 'See details' or find details element
        code = """
        (() => {
            const seeDetailsBtn = Array.from(document.querySelectorAll('button, a')).find(e => e.innerText && e.innerText.includes('See details'));
            if (seeDetailsBtn) seeDetailsBtn.click();
            return {
                clicked: !!seeDetailsBtn,
                fullHtml: document.body.innerHTML,
                fullText: document.body.innerText
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        val = res.get("result", {}).get("result", {}).get("value", {})
        print("Clicked see details:", val.get("clicked"))
        
        # Wait a moment and read text again
        await asyncio.sleep(0.5)
        await ws.send(json.dumps({"id": 2, "method": "Runtime.evaluate", "params": {"expression": "document.body.innerText", "returnByValue": True}}))
        res2 = json.loads(await ws.recv())
        print("Details text:\n", res2.get("result", {}).get("result", {}).get("value"))

asyncio.run(get_details())
