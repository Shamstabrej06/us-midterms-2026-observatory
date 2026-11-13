import urllib.request, json, asyncio, websockets

async def close_backstage():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
    async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const backBtn = document.querySelector('.back-button, button[aria-label="Back"], .file-menu-back-button, .backArrow');
            if (backBtn) {
                backBtn.click();
                return 'clicked back button';
            }
            return 'no back button';
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print(res.get('result', {}).get('result', {}).get('value'))

asyncio.run(close_backstage())
