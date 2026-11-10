import asyncio
import json
import urllib.request
import websockets

async def check_mod():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            let wpRequire = null;
            window.webpackChunkdesktop.push([[Math.random()], {}, (req) => { wpRequire = req; }]);
            const mod = wpRequire(290950);
            return {
                keys: Object.keys(mod)
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("Result:", res.get("result", {}).get("result", {}).get("value"))

asyncio.run(check_mod())
