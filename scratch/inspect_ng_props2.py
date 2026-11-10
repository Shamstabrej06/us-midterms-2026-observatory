import asyncio
import json
import urllib.request
import websockets

async def check_ng():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            try {
                const roots = typeof getAllAngularRootElements === 'function' ? getAllAngularRootElements() : [];
                return {
                    rootsCount: roots.length,
                    rootTag: roots[0] ? roots[0].tagName : null
                };
            } catch(e) {
                return { error: e.toString() };
            }
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(res)

asyncio.run(check_ng())
