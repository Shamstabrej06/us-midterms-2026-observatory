import urllib.request, json, asyncio, websockets

async def check():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
    async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const pages = Array.from(document.querySelectorAll('.navigation-wrapper .page-item, .pages-nav .page, [role="tab"], .tab-item')).map(e => e.innerText.trim());
            const visuals = Array.from(document.querySelectorAll('.visualContainerHost, visual-container')).length;
            const textSnippets = Array.from(document.querySelectorAll('h1, h2, h3, .visualTitle, text')).map(e => e.textContent.trim()).filter(Boolean).slice(0, 20);
            return {
                pages: pages,
                visualsCount: visuals,
                textSnippets: textSnippets,
                bodySnippet: document.body.innerText.substring(0, 300)
            };
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value'), indent=2))

asyncio.run(check())
