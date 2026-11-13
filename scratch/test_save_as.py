import urllib.request, json, asyncio, websockets

async def test_save():
    targets = json.loads(urllib.request.urlopen('http://localhost:9222/json').read().decode())
    r_target = next((t for t in targets if 'reportView' in t.get('url', '')), None)
    async with websockets.connect(r_target['webSocketDebuggerUrl'], max_size=10*1024*1024) as ws:
        code = """
        (() => {
            const h = window.internals ? window.internals.host : null;
            if (!h) return 'no host';
            const targetPath = "C:\\\\Users\\\\shams\\\\us-midterms-2026-observatory\\\\MidtermsObservatory.pbix";
            const targetFolder = "C:\\\\Users\\\\shams\\\\us-midterms-2026-observatory";
            return h.invokeCsFunc("FileOperationsHostService", "TrySaveAsFile", [targetPath, targetFolder])
                .then(res => ({ success: true, res: res }))
                .catch(err => ({ error: err.toString() }));
        })()
        """
        await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': code, 'awaitPromise': True, 'returnByValue': True}}))
        res = json.loads(await ws.recv())
        print(json.dumps(res.get('result', {}).get('result', {}).get('value'), indent=2))

asyncio.run(test_save())
