import asyncio
import json
import urllib.request
import websockets

async def check_internals():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            return {
                internals: window.internals ? Object.keys(window.internals) : null,
                desktop: window.desktop ? Object.keys(window.desktop) : null,
                angularRoots: typeof getAllAngularRootElements === 'function' ? getAllAngularRootElements().map(e => e.tagName) : null
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("Internals:", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check_internals())
