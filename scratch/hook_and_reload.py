import asyncio
import json
import urllib.request
import websockets

async def hook_and_reload():
    req = urllib.request.urlopen("http://localhost:9222/json")
    targets = json.loads(req.read().decode())
    target = next((t for t in targets if "reportView" in t.get("url", "")), None)
    if not target:
        print("No reportView target")
        return

    print("Connecting to reportView target...")
    async with websockets.connect(target["webSocketDebuggerUrl"], max_size=100*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws.send(json.dumps({"id": 2, "method": "Page.enable"}))
        await ws.send(json.dumps({"id": 3, "method": "Log.enable"}))

        # Script to inject before any scripts execute on page reload
        preload_script = """
        (() => {
            console.log("=== PRELOAD HOOK INSTALLED ===");
            window.__HOOK_LOGS = [];
            
            // Listen to all unhandled rejections and errors
            window.addEventListener('unhandledrejection', (e) => {
                const reason = e.reason ? (e.reason.stack || e.reason.message || String(e.reason)) : 'unknown';
                console.error("[PRELOAD] UnhandledRejection:", reason);
                try { sessionStorage.setItem('LAST_REJECTION', reason); } catch(err){}
            });
            window.addEventListener('error', (e) => {
                const err = e.error ? (e.error.stack || e.error.message || String(e.error)) : e.message;
                console.error("[PRELOAD] WindowError:", err);
                try { sessionStorage.setItem('LAST_WINDOW_ERROR', err); } catch(err){}
            });

            // Intercept webpack chunk loading
            let wc = window.webpackChunkdesktop || [];
            let origPush = wc.push ? wc.push.bind(wc) : null;

            function hookModules(chunk) {
                try {
                    const modules = chunk[1];
                    if (modules) {
                        for (let modId in modules) {
                            const origMod = modules[modId];
                            const modStr = origMod.toString();
                            if (modStr.includes('DesignerContainer_FailedToLoadReport') || modStr.includes('DesktopExplorationComponent')) {
                                console.log('[PRELOAD] Found DesktopExplorationComponent in module ' + modId + ', hooking...');
                                modules[modId] = function(module, exports, require) {
                                    origMod.apply(this, arguments);
                                    // Let's hook ErrorService or explore proxy if possible
                                };
                            }
                        }
                    }
                } catch(e) {
                    console.error('[PRELOAD] hookModules error:', e);
                }
            }

            // Hook ErrorService when created
            let checkInterval = setInterval(() => {
                if (window.webpackChunkdesktop) {
                    let wpRequire = null;
                    try {
                        window.webpackChunkdesktop.push([[Math.random()], {}, (req) => { wpRequire = req; }]);
                        if (wpRequire) {
                            const vp = wpRequire(677053);
                            if (vp && vp.iE) {
                                const globalObj = vp.iE();
                                if (globalObj && globalObj.errorService && !globalObj.errorService.__hooked) {
                                    globalObj.errorService.__hooked = true;
                                    const es = globalObj.errorService;
                                    const origError = es.error.bind(es);
                                    es.error = function(title, msg, details) {
                                        console.error(">>> ERROR_SERVICE.ERROR CALLED! <<<");
                                        console.error("Title:", title);
                                        console.error("Msg:", msg);
                                        console.error("Details:", JSON.stringify(details));
                                        if (details && details.stackTrace) {
                                            console.error("STACK TRACE:\n", details.stackTrace);
                                        }
                                        try {
                                            sessionStorage.setItem('CAPTURED_ERROR_SERVICE', JSON.stringify({
                                                title: title,
                                                msg: msg,
                                                details: details,
                                                stack: details ? details.stackTrace : null
                                            }));
                                        } catch(e){}
                                        return origError.apply(this, arguments);
                                    };
                                    console.log("[PRELOAD] errorService.error successfully hooked!");
                                    clearInterval(checkInterval);
                                }
                            }
                        }
                    } catch(e){}
                }
            }, 10);
        })()
        """

        await ws.send(json.dumps({
            "id": 4,
            "method": "Page.addScriptToEvaluateOnNewDocument",
            "params": {"source": preload_script}
        }))
        res = json.loads(await ws.recv())
        print("Hook registered:", res)

        print("Reloading reportView...")
        await ws.send(json.dumps({"id": 5, "method": "Page.reload"}))

        # Listen for 15 seconds
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 15:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=1)
                msg = json.loads(raw)
                m = msg.get("method")
                if m == "Runtime.consoleAPICalled":
                    args = msg.get("params", {}).get("args", [])
                    t = msg.get("params", {}).get("type")
                    vals = [a.get("value", a.get("description", "")) for a in args]
                    val_str = " ".join(str(v) for v in vals)
                    print(f"[{t}] {val_str}")
            except asyncio.TimeoutError:
                continue

asyncio.run(hook_and_reload())
