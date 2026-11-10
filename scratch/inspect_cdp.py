import asyncio
import json
import urllib.request
import websockets

async def check_cdp():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    print(f"Total targets: {len(targets)}")
    for t in targets:
        print("Target:", t.get("type"), "|", t.get("title"), "|", t.get("url"))
        ws_url = t.get("webSocketDebuggerUrl")
        if ws_url and "reportView.html" in t.get("url", ""):
            async with websockets.connect(ws_url) as ws:
                # Enable runtime and console
                await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
                r1 = await ws.recv()
                
                # Evaluate title or document state
                await ws.send(json.dumps({
                    "id": 2,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "document.body.innerText"}
                }))
                r2 = json.loads(await ws.recv())
                body_text = r2.get("result", {}).get("result", {}).get("value", "")
                print(f"Body innerText snippet (first 300 chars):\n{body_text[:300]}")
                
                # Check for dialogs or error messages in DOM
                await ws.send(json.dumps({
                    "id": 3,
                    "method": "Runtime.evaluate",
                    "params": {"expression": "document.title"}
                }))
                r3 = json.loads(await ws.recv())
                print("Document title:", r3.get("result", {}).get("result", {}).get("value"))

asyncio.run(check_cdp())
