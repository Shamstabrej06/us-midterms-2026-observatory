import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    print("Available targets:")
    for t in targets:
        print(" -", t.get("title"), "|", t.get("url"))
    
    # Check modelView or tmdlView
    m_target = next((t for t in targets if "modelView" in t.get("url", "")), None)
    if m_target:
        async with websockets.connect(m_target["webSocketDebuggerUrl"], max_size=10*1024*1024) as ws:
            code = """
            (() => {
                const tables = Array.from(document.querySelectorAll('.tableName, .table-name, [class*="table"]')).map(e => e.innerText.trim()).filter(Boolean);
                const allText = document.body.innerText.slice(0, 500);
                return { tables: tables.slice(0, 20), allText: allText };
            })()
            """
            await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
            res = json.loads(await ws.recv())
            print("modelView result:", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check())
