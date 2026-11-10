import asyncio
import json
import urllib.request
import websockets

async def check_testability():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            const el = getAllAngularRootElements()[0];
            const t = getAngularTestability(el);
            return {
                testabilityKeys: Object.keys(t),
                hasInternals: !!window.internals,
                internalsHost: window.internals ? Object.keys(window.internals.host || {}) : null
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("Testability:", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check_testability())
