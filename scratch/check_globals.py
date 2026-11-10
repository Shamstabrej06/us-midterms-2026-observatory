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
        except Exception as e:
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

async def check():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    client = CDPClient(target["webSocketDebuggerUrl"])
    await client.connect()

    await client.call("Runtime.enable")

    eval_script = """
    (() => {
        const keys = Object.keys(window).filter(k => 
            !k.startsWith('webkit') && !k.startsWith('on') && 
            !['window', 'self', 'document', 'location', 'top', 'parent'].includes(k)
        );
        return keys;
    })()
    """
    res = await client.call("Runtime.evaluate", {"expression": eval_script, "returnByValue": True})
    print("Window keys:", res.get("result", {}).get("result", {}).get("value"))

    # Also let's check for any Angular / React / Minerva components
    eval_minerva = """
    (() => {
        let res = {};
        if (window.minerva) res.minerva = Object.keys(window.minerva);
        if (window.powerbi) res.powerbi = Object.keys(window.powerbi);
        if (window.angular) res.angular = true;
        return res;
    })()
    """
    res2 = await client.call("Runtime.evaluate", {"expression": eval_minerva, "returnByValue": True})
    print("Minerva / PowerBI objects:", res2.get("result", {}).get("result", {}).get("value"))

    await client.close()

asyncio.run(check())
