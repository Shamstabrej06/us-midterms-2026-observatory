import asyncio
import json
import urllib.request
import websockets

async def inspect():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)
    print("Connecting to:", target["webSocketDebuggerUrl"])

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws.recv()

        eval_script = """
        (() => {
            const tabs = Array.from(document.querySelectorAll('.page-tab-name, .navigation-bar-entry, [role="tab"], .tab-item')).map(e => e.innerText.trim());
            const visualHosts = document.querySelectorAll('.visualContainerHost, .visualContainer, visual-container').length;
            const textboxes = document.querySelectorAll('.textbox').length;
            const title = document.title;
            return {
                title: title,
                tabs: tabs,
                visualCount: visualHosts,
                textboxCount: textboxes
            };
        })()
        """
        await ws.send(json.dumps({
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {"expression": eval_script, "returnByValue": True}
        }))
        res = json.loads(await ws.recv())
        print("DOM State:\n", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(inspect())
