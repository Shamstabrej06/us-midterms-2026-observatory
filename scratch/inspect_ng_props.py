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
            const el = getAllAngularRootElements()[0];
            const props = [];
            for (let k in el) {
                if (k.startsWith('__ng') || k.startsWith('_ng') || k.startsWith('ng')) {
                    props.push({ key: k, type: typeof el[k] });
                }
            }
            return {
                props: props
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check_ng())
