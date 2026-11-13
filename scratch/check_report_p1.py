import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
    async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const tabs = Array.from(document.querySelectorAll('.page-tab-name, [role="tab"], .tab-item')).map(e => e.innerText.trim()).filter(Boolean);
            const visuals = Array.from(document.querySelectorAll('.visualContainerHost, visual-container, .visual')).length;
            const titles = Array.from(document.querySelectorAll('h1, h2, h3, .visualTitle, text')).map(e => e.textContent.trim()).filter(Boolean).slice(0, 30);
            return {
                title: document.title,
                tabs: tabs,
                visuals: visuals,
                titles: titles
            };
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value'), indent=2))

asyncio.run(check())
