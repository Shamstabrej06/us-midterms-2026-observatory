import asyncio
import json
import urllib.request
import websockets

async def reload_and_capture_logs():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
        await ws.send(json.dumps({"id": 3, "method": "Log.enable"}))

        print("Listening for console messages...")
        # Reload the reportView page
        await ws.send(json.dumps({"id": 4, "method": "Page.reload"}))

        for _ in range(50):
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=2))
                m = msg.get("method")
                if m == "Runtime.consoleAPICalled":
                    args = msg.get("params", {}).get("args", [])
                    t = msg.get("params", {}).get("type")
                    vals = [a.get("value", a.get("description", "")) for a in args]
                    val_str = " ".join(str(v) for v in vals)
                    if t in ("error", "warning") or any(k in val_str.lower() for k in ["pbir", "error", "fail", "page", "exception", "definition"]):
                        print(f"[{t}] {val_str[:300]}")
            except asyncio.TimeoutError:
                break

asyncio.run(reload_and_capture_logs())
