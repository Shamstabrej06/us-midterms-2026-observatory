import asyncio
import json
import urllib.request
import websockets

async def inspect():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)
    print("Connecting to:", target["webSocketDebuggerUrl"])

    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        eval_script = """
        (() => {
            const tabs = Array.from(document.querySelectorAll('.page-tab-name, .navigation-bar-entry, [role="tab"], .tab-item, .tab, button')).map(e => e.innerText ? e.innerText.trim() : '').filter(t => t.length > 0);
            const visuals = document.querySelectorAll('.visualContainerHost, .visualContainer, visual-container, .visualContainerHostSection').length;
            const textboxes = document.querySelectorAll('.textbox, .visual-textbox').length;
            const titles = Array.from(document.querySelectorAll('.visualTitle, h2, h3, .card')).map(e => e.innerText ? e.innerText.trim() : '');
            const bodySnippet = document.body.innerText.substring(0, 1000);
            return {
                title: document.title,
                tabs: tabs.filter(t => ['The Night', 'The Comeback, Measured', 'Texas Deep-Dive', 'Why This One Was Different', 'The Midterm Pattern', 'What Changes Now', 'State Detail', 'Page 1'].includes(t) || t.includes('Night') || t.includes('Texas')),
                visualCount: visuals,
                textboxCount: textboxes,
                titles: titles.filter(t => t.length > 0).slice(0, 20),
                bodySnippet: bodySnippet
            };
        })()
        """
        await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": eval_script, "returnByValue": True}}))
        res = json.loads(await ws.recv())
        print("DOM State:\n", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

asyncio.run(inspect())
