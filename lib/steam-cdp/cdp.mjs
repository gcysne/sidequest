// Evaluate a JS file in a Steam CEF target (Steam must expose devtools on 127.0.0.1:8080).
// usage: node cdp.mjs "<target title, e.g. SharedJSContext>" file.js   -> prints the (awaited) result
import fs from 'fs';
const [title, file] = process.argv.slice(2);
const targets = await (await fetch('http://127.0.0.1:8080/json')).json();
const t = targets.find(x => x.title === title);
if (!t) { console.error('no target', title); process.exit(1); }
const ws = new WebSocket(t.webSocketDebuggerUrl);
ws.onopen = () => ws.send(JSON.stringify({id: 1, method: 'Runtime.evaluate',
  params: {expression: fs.readFileSync(file, 'utf8'), returnByValue: true, awaitPromise: true}}));
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id !== 1) return; const r = m.result;
  console.log(r.exceptionDetails ? 'EXC: ' + JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails)
    : (typeof r.result.value === 'string' ? r.result.value : JSON.stringify(r.result.value, null, 1)));
  ws.close(); };
