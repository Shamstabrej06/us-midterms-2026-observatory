import urllib.request, json, asyncio, websockets

async def click_file():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
    async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const fileBtn = document.getElementById('Ribbon-file');
            if (fileBtn) {
                fileBtn.click();
                return 'clicked file button';
            }
            return 'file button not found';
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print(res.get('result', {}).get('result', {}).get('value'))
        await asyncio.sleep(0.5)
        code2 = """
        (() => {
            return Array.from(document.querySelectorAll('.file-menu-item, [role="menuitem"], .menu-item')).map(e => e.innerText.trim()).filter(Boolean);
        })()
        """
        await ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {'expression': code2, 'returnByValue': True}}))
        res2 = json.loads(await ws.recv())
        print('File menu items:', res2.get('result', {}).get('result', {}).get('value'))

asyncio.run(click_file())
