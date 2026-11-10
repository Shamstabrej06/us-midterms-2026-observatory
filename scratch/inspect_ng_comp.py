import asyncio
import json
import urllib.request
import websockets

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0
        self.pending = {}
        self.listener_task = None

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=100*1024*1024)
        self.listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                mid = msg.get("id")
                if mid in self.pending:
                    self.pending[mid].set_result(msg)
        except asyncio.CancelledError:
            pass

    async def call(self, method, params=None):
        self.msg_id += 1
        mid = self.msg_id
        fut = asyncio.get_event_loop().create_future()
        self.pending[mid] = fut
        req = {"id": mid, "method": method}
        if params:
            req["params"] = params
        await self.ws.send(json.dumps(req))
        res = await fut
        del self.pending[mid]
        return res

    async def close(self):
        if self.listener_task:
            self.listener_task.cancel()
        if self.ws:
            await self.ws.close()

async def inspect():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    client = CDPClient(target["webSocketDebuggerUrl"])
    await client.connect()

    await client.call("Runtime.enable")

    # In Angular, ng.getComponent(el) returns the component instance!
    eval_script = """
    (() => {
        let res = {};
        const el = document.querySelector('desktop-status-bar-report-section');
        if (window.ng && window.ng.getComponent && el) {
            let comp = window.ng.getComponent(el);
            if (comp) {
                res.compKeys = Object.keys(comp);
                for (let k of res.compKeys) {
                    try {
                        let v = comp[k];
                        if (typeof v !== 'function') res[k] = v;
                    } catch(e) {}
                }
            }
        }
        // Also check app-desktop-report-view component
        const appEl = document.querySelector('app-desktop-report-view');
        if (window.ng && window.ng.getComponent && appEl) {
            let appComp = window.ng.getComponent(appEl);
            if (appComp) {
                res.appKeys = Object.keys(appComp);
            }
        }
        return res;
    })()
    """
    res = await client.call("Runtime.evaluate", {"expression": eval_script, "returnByValue": True})
    print("Angular Component:\n", json.dumps(res.get("result", {}).get("result", {}).get("value"), indent=2))

    await client.close()

asyncio.run(inspect())
