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
        self.events = []

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=100*1024*1024)
        self.listener_task = asyncio.create_task(self._listen())

    async def _listen(self):
        try:
            async for raw in self.ws:
                msg = json.loads(raw)
                mid = msg.get("id")
                if mid and mid in self.pending:
                    self.pending[mid].set_result(msg)
                else:
                    self.events.append(msg)
                    if msg.get("method") == "Runtime.consoleAPICalled":
                        args = msg.get("params", {}).get("args", [])
                        t = msg.get("params", {}).get("type")
                        vals = [a.get("value", a.get("description", "")) for a in args]
                        print(f"[{t}] {' '.join(str(v) for v in vals)}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print("Listen exception:", e)

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

async def run():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    client = CDPClient(target["webSocketDebuggerUrl"])
    await client.connect()

    await client.call("Runtime.enable")
    await client.call("Page.enable")
    await client.call("Log.enable")

    preload = """
    console.log(">>> INJECTED HOOK RUNNING <<<");
    window.addEventListener('error', e => console.error("INJECTED ERROR:", e.message, e.error?.stack));
    window.addEventListener('unhandledrejection', e => console.error("INJECTED REJECTION:", e.reason?.message, e.reason?.stack));
    
    // Periodically check for errorService
    const iv = setInterval(() => {
        try {
            if (window.webpackChunkdesktop) {
                let req = null;
                window.webpackChunkdesktop.push([[Math.random()], {}, (r) => { req = r; }]);
                if (req) {
                    const vp = req(677053);
                    if (vp && vp.iE) {
                        const g = vp.iE();
                        if (g && g.errorService && !g.errorService.__hooked) {
                            g.errorService.__hooked = true;
                            const orig = g.errorService.error.bind(g.errorService);
                            g.errorService.error = function(t, m, d) {
                                console.error(">>> ERROR SERVICE INTERCEPTED <<<");
                                console.error("TITLE:", t);
                                console.error("MESSAGE:", m);
                                console.error("DETAILS:", JSON.stringify(d));
                                if (d && d.stackTrace) console.error("STACK:\n" + d.stackTrace);
                                return orig.apply(this, arguments);
                            };
                            console.log(">>> ERROR SERVICE HOOK ATTACHED <<<");
                            clearInterval(iv);
                        }
                    }
                }
            }
        } catch(e) {}
    }, 5);
    """
    res1 = await client.call("Page.addScriptToEvaluateOnNewDocument", {"source": preload})
    print("addScriptToEvaluateOnNewDocument response:", res1)

    print("Triggering Page.reload...")
    res2 = await client.call("Page.reload")
    print("Reload triggered:", res2)

    await asyncio.sleep(12)
    await client.close()

asyncio.run(run())
