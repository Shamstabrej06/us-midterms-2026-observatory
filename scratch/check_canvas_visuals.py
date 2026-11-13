import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json").read().decode())
    r_target = next((t for t in targets if "reportView" in t.get("url", "")), None)
    async with websockets.connect(r_target["webSocketDebuggerUrl"], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const containers = Array.from(document.querySelectorAll('.visualContainerHost, visual-container, .visualContainer, [class*="visual"]')).map(e => ({
                tag: e.tagName,
                class: typeof e.className === 'string' ? e.className : '',
                text: e.innerText ? e.innerText.slice(0, 100).replace(/\\n/g, ' ') : ''
            }));
            const canvas = document.querySelector('.canvas, .canvasArea, .visualArea, [class*="canvas"]');
            const pageTabs = Array.from(document.querySelectorAll('.page-tab-name, [role="tab"]')).map(e => ({
                text: e.innerText.trim(),
                selected: e.getAttribute('aria-selected') || e.className
            }));
            return {
                containersCount: containers.length,
                containersSample: containers.slice(0, 15),
                canvasHtml: canvas ? canvas.outerHTML.slice(0, 500) : 'no canvas',
                pageTabs: pageTabs
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": code, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(check())
