import urllib.request, json, asyncio, websockets

async def click_close():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    d_target = next((t for t in targets if 'desktopDialogHost' in t.get('url', '')), None)
    if not d_target:
        print('No dialog')
        return
    async with websockets.connect(d_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const btn = document.querySelector('button[data-testid="close-button"]') || Array.from(document.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Close'));
            if (btn) {
                btn.click();
                return 'clicked close';
            }
            return 'not found';
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print('Close button click:', res.get('result', {}).get('result', {}).get('value'))

asyncio.run(click_close())
