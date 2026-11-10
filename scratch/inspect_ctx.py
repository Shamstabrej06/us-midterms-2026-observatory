import asyncio
import json
import urllib.request
import websockets

async def inspect_ctx():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            const de = document.querySelector('desktop-exploration');
            const ctx = de ? de.__ngContext__ : null;
            if (!ctx) return { hasCtx: false, hasDe: !!de };
            return {
                isArr: Array.isArray(ctx),
                len: ctx.length,
                types: Array.from(ctx).slice(0, 30).map(x => x ? (typeof x === 'object' ? (x.constructor ? x.constructor.name : typeof x) : typeof x) : null)
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("Ctx:", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(inspect_ctx())
