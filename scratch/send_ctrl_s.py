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

async def trigger_save():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)

    client = CDPClient(target["webSocketDebuggerUrl"])
    await client.connect()

    await client.call("Runtime.enable")

    # Send Ctrl+S
    # modifiers: 2 = Control
    print("Sending Ctrl+S key event...")
    await client.call("Input.dispatchKeyEvent", {
        "type": "rawKeyDown",
        "modifiers": 2,
        "windowsVirtualKeyCode": 83,
        "code": "KeyS",
        "key": "s"
    })
    await client.call("Input.dispatchKeyEvent", {
        "type": "keyUp",
        "modifiers": 2,
        "windowsVirtualKeyCode": 83,
        "code": "KeyS",
        "key": "s"
    })

    print("Sent Ctrl+S! Waiting 3 seconds...")
    await asyncio.sleep(3)
    await client.close()

asyncio.run(trigger_save())
