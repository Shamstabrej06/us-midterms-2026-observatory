import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    for t in targets:
        name = t.get("title", "")
        url = t.get("url", "")
        if "desktopDialogHost" in url or "reportView" in url:
            print(f"=== TARGET: {url} ===")
            try:
                async with websockets.connect(t["webSocketDebuggerUrl"], max_size=10*1024*1024) as ws:
                    code = "(() => ({ title: document.title, text: document.body.innerText.slice(0, 1000) }))()"
                    await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
                    res = json.loads(await ws.recv())
                    print("Body text:\n", res.get("result", {}).get("result", {}).get("value", {}).get("text"))
            except Exception as e:
                print("Error:", e)

asyncio.run(check())
