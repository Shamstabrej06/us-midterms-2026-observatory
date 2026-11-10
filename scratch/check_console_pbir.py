import asyncio
import json
import urllib.request
import websockets

async def check_console_errors():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Log.enable"}))
        await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))

        # Collect console messages for 3 seconds
        end_time = asyncio.get_event_loop().time() + 3
        while asyncio.get_event_loop().time() < end_time:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=1))
                m = msg.get("method")
                if m == "Runtime.consoleAPICalled":
                    args = msg.get("params", {}).get("args", [])
                    t = msg.get("params", {}).get("type")
                    vals = [a.get("value", a.get("description", "")) for a in args]
                    val_str = " ".join(str(v) for v in vals)
                    if t in ("error", "warning") or any(k in val_str.lower() for k in ["pbir", "schema", "page", "section", "report"]):
                        print(f"[{t}] {val_str[:250]}")
            except asyncio.TimeoutError:
                break

asyncio.run(check_console_errors())
