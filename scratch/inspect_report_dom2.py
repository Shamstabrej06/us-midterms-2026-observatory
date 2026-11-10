import asyncio
import json
import urllib.request
import websockets

async def inspect():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws.recv()

        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": "location.href"}
        }))
        res = json.loads(await ws.recv())
        print("URL response:", res)

        await ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {"expression": "document.body.innerHTML.length"}
        }))
        res2 = json.loads(await ws.recv())
        print("Body length response:", res2)

asyncio.run(inspect())
