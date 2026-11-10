import asyncio
import json
import urllib.request
import websockets

async def test_in_browser():
    with open(r'C:\Users\shams\us-midterms-2026-observatory\scratch\deserialized_exploration.json', 'r', encoding='utf-8') as f:
        wire_contract_str = f.read()

    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        # Check window or find services
        find_script = """
        (() => {
            // Let's see if we can find reportSerializerV2 or wireContractSerializerAdapter
            const allProps = [];
            for (let k in window) {
                if (window[k] && typeof window[k] === 'object') {
                    allProps.push(k);
                }
            }
            return {
                props: allProps.filter(p => !p.startsWith('webkit') && !p.startsWith('chrome'))
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": find_script, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("Window props:", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(test_in_browser())
