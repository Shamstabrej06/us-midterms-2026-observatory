import asyncio
import json
import urllib.request
import websockets

async def inspect_report_elements():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        code = """
        (() => {
            const tags = Array.from(document.querySelectorAll('*')).map(e => e.tagName.toLowerCase());
            const uniqueTags = [...new Set(tags)];
            return {
                tags: uniqueTags
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("ReportView tags:", res.get("result", {}).get("result", {}).get("value"))

asyncio.run(inspect_report_elements())
