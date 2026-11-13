import urllib.request, json, asyncio, websockets

async def check_ribbon():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
    async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const btns = Array.from(document.querySelectorAll('button, .file-menu-item, [role="menuitem"], .fabric-menu-item')).map(b => ({
                text: b.innerText ? b.innerText.trim() : '',
                id: b.id,
                title: b.title,
                aria: b.getAttribute('aria-label')
            })).filter(b => b.text || b.aria || b.title);
            return btns.slice(0, 50);
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value'), indent=2))

asyncio.run(check_ribbon())
