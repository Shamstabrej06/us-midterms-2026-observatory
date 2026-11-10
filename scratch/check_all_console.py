import asyncio
import json
import urllib.request
import websockets

async def check_all_console():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Log.enable"}))
        await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))

        # Check existing console or errors
        eval_script = """
        (() => {
            return {
                windowErrors: window.__lastErrors || [],
                angularErrors: window.ng ? 'ng present' : 'no ng'
            };
        })()
        """
        await ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {"expression": eval_script, "returnByValue": True}}))
        
        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=3)
                msg = json.loads(raw)
                if msg.get("id") == 3:
                    print("Eval res:", json.dumps(msg.get("result", {}).get("result", {}).get("value"), indent=2))
                elif msg.get("method") == "Runtime.consoleAPICalled":
                    args = msg.get("params", {}).get("args", [])
                    t = msg.get("params", {}).get("type")
                    vals = [str(a.get("value", a.get("description", ""))) for a in args]
                    print(f"[{t}] {' '.join(vals)[:300]}")
            except asyncio.TimeoutError:
                break

asyncio.run(check_all_console())
