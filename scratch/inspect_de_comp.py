import asyncio
import json
import urllib.request
import websockets

async def inspect_component():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            const de = document.querySelector('desktop-exploration');
            if (!de) return 'no desktop-exploration';
            const ctx = de.__ngContext__;
            // In Ivy, ctx is an LView array. ctx[8] or around there is the component instance.
            const comp = ctx.find(x => x && typeof x === 'object' && x.constructor && x.constructor.name.includes('DesktopExploration'));
            if (comp) {
                return {
                    name: comp.constructor.name,
                    keys: Object.keys(comp),
                    explorationProxyKeys: comp.explorationProxy ? Object.keys(comp.explorationProxy) : null
                };
            }
            return {
                ctxTypes: ctx.map(x => x ? (x.constructor ? x.constructor.name : typeof x) : null).filter(Boolean)
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("Component result:", res.get("result", {}).get("result", {}).get("value"))

asyncio.run(inspect_component())
