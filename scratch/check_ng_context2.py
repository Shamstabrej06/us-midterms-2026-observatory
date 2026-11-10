import asyncio
import json
import urllib.request
import websockets

async def check_ng_context2():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            const el = document.querySelector('desktop-exploration');
            if (!el) return 'no el';
            const ctx = el.__ngContext__;
            return Array.from(ctx || []).map((x, i) => {
                if (!x) return null;
                if (typeof x === 'object') {
                    return (x.constructor ? x.constructor.name : 'obj') + ': ' + Object.keys(x).slice(0, 5).join(',');
                }
                return typeof x;
            });
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check_ng_context2())
