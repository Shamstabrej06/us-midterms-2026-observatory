import asyncio
import json
import urllib.request
import websockets

async def check_ng_context():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            const el = document.querySelector('desktop-exploration') || document.querySelector('explore-host');
            if (!el) return 'no el';
            const ctx = el.__ngContext__;
            if (!ctx) return 'no ctx';
            // Search ctx for explorationProxy or wireContractSerializerAdapter
            const items = [];
            for (let i = 0; i < ctx.length; i++) {
                const item = ctx[i];
                if (item && typeof item === 'object') {
                    const keys = Object.keys(item);
                    if (keys.includes('explorationProxy') || keys.includes('wireContractSerializerAdapter') || keys.includes('reportLayout')) {
                        items.push({ index: i, keys: keys.slice(0, 10) });
                    }
                }
            }
            return {
                ctxLen: ctx.length,
                matched: items
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check_ng_context())
