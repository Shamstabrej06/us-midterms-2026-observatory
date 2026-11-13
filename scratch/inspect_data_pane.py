import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    r_target = next((t for t in targets if "reportView" in t.get("url", "")), None)
    async with websockets.connect(r_target["webSocketDebuggerUrl"], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const dataPane = document.querySelector('.data-pane, .fields-pane, .schemaExplorer, [data-testid*="data-pane"], [data-testid*="field"]');
            const treeItems = Array.from(document.querySelectorAll('[role="treeitem"], .tree-node, .tree-item, .table-name, .field-name')).map(e => e.innerText.trim()).filter(Boolean);
            const canvasText = Array.from(document.querySelectorAll('.canvas, .exploreCanvas, [data-automation-type="reportCanvas"]')).map(e => e.innerText.trim()).filter(Boolean);
            return {
                treeItems: treeItems.slice(0, 30),
                canvasText: canvasText,
                hasDataPane: !!dataPane
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check())
