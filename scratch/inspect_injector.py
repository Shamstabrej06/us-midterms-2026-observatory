import asyncio
import json
import urllib.request
import websockets

async def check():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        # Let's inspect Angular services in reportView
        code = """
        (() => {
            try {
                // Find any elements with ng-version
                const el = document.querySelector('[ng-version]');
                if (!el) return 'no ng-version el';
                // Look for injector
                const injector = (window.ng && window.ng.getInjector) ? window.ng.getInjector(el) : null;
                return {
                    hasInjector: !!injector
                };
            } catch(e) {
                return { error: e.toString() };
            }
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check())
