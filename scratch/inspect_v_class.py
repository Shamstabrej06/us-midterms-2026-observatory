import asyncio
import json
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            let wpRequire = null;
            window.webpackChunkdesktop.push([
                [Math.random()],
                {},
                (req) => { wpRequire = req; }
            ]);
            const mod = wpRequire(425335);
            return {
                V_str: mod.V ? mod.V.toString().substring(0, 1000) : 'no V',
                V_fac: mod.V && mod.V.ɵfac ? mod.V.ɵfac.toString() : 'no fac'
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check())
