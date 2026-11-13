import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    r_target = next((t for t in targets if "reportView" in t.get("url", "")), None)
    if not r_target:
        print("No reportView target found!")
        return
    async with websockets.connect(r_target["webSocketDebuggerUrl"], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const getInfo = () => {
                const navTabs = Array.from(document.querySelectorAll('.page-tab-name, .tab-item, [role="tab"]')).map(e => e.innerText.trim()).filter(Boolean);
                const visualContainers = document.querySelectorAll('.visualContainerHost, visual-container, .visualContainer');
                const errors = Array.from(document.querySelectorAll('.errorMessage, .error, .banner-error, .notification')).map(e => e.innerText.trim()).filter(Boolean);
                const textNodes = Array.from(document.querySelectorAll('text, span, div')).map(e => e.innerText ? e.innerText.trim() : '').filter(t => t.length > 3 && t.length < 50);
                return {
                    title: document.title,
                    navTabs: navTabs,
                    visualContainersCount: visualContainers.length,
                    errors: errors,
                    sampleTexts: Array.from(new Set(textNodes)).slice(0, 30)
                };
            };
            return getInfo();
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check())
