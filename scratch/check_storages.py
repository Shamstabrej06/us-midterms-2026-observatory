import asyncio
import json
import urllib.request
import websockets

async def check_target(t):
    print(f"=== Checking {t['title']} ({t['url']}) ===")
    try:
        async with websockets.connect(t['webSocketDebuggerUrl'], max_size=100*1024*1024) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Log.enable"}))
            await ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
            
            # Check localStorage / sessionStorage
            script = """
            (() => {
                const s = {};
                for (let i = 0; i < localStorage.length; i++) {
                    const k = localStorage.key(i);
                    s['local:' + k] = localStorage.getItem(k);
                }
                for (let i = 0; i < sessionStorage.length; i++) {
                    const k = sessionStorage.key(i);
                    s['session:' + k] = sessionStorage.getItem(k);
                }
                return s;
            })()
            """
            await ws.send(json.dumps({"id": 3, "method": "Runtime.evaluate", "params": {"expression": script, "returnByValue": True}}))
            res = json.loads(await ws.recv())
            val = res.get("result", {}).get("result", {}).get("value", {})
            for k, v in val.items():
                if any(w in k.lower() or w in str(v).lower() for w in ['error', 'fail', 'report', 'exception']):
                    print(f"  Storage {k}: {str(v)[:200]}")
    except Exception as e:
        print("  Error:", e)

async def main():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    for t in targets:
        if t.get('type') == 'page':
            await check_target(t)

asyncio.run(main())
