"""Loopback-only experimental supervisor for simulated telemetry and operator alerts.

Not secure network management. It intentionally refuses non-loopback connections
and stores no imagery, biometric templates or real watchlists. Run only with
synthetic demonstration data. Replace with mTLS, RBAC, audit and isolated storage
before any real device or private/identifying information is used.
"""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
from urllib.parse import urlparse

MAX_POST_BYTES = 2_000_000
SENSITIVE_KEYS = ("candidate_ref", "lab_subject", "face", "embedding", "image", "person")
dashboard = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Siamese Embedded — synthetic supervisor</title>
<style>
:root{font:14px system-ui,sans-serif;color:#e5ecf1;background:#0c151c}
main{max-width:1100px;margin:25px auto;padding:0 14px}h1{font-size:27px;margin-bottom:3px}
small{color:#9cb6c5}.warning{padding:10px;background:#3a2b21;color:#ffdeab;border-radius:8px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px;margin:20px 0}
.card{border:1px solid #304654;background:#162730;border-radius:12px;padding:15px}
.metric{font-size:26px;font-weight:650;margin:5px 0}table{width:100%;border-collapse:collapse}
td,th{border-bottom:1px solid #35505e;padding:9px;text-align:left}
th{color:#a4c3d1;font-size:12px}section{margin:22px 0}code{font-size:12px}
</style></head><body><main><h1>SIAMESE EMBEDDED / PC SUPERVISOR</h1>
<small>External bench · simulated Ethernet and security dispatch feed</small>
<p class="warning">SYNTHETIC EXERCISE ONLY — not real camera images, biometric accuracy, measured watts, radio coverage or a production security console.</p>
<div class="cards" id="cards"></div>
<section><h2>Operational probe timeline</h2><table><thead><tr><th>t (s)</th><th>Mode</th><th>Power (ASSUMED W)</th><th>Case (ASSUMED °C)</th><th>SoC (ASSUMED %)</th></tr></thead><tbody id="probes"></tbody></table></section>
<section><h2>Short security events</h2><table><thead><tr><th>Event</th><th>Zone</th><th>Type</th><th>RF receipt</th><th>Human ACK</th></tr></thead><tbody id="alerts"></tbody></table></section>
<script>
function el(name,value){const e=document.createElement(name);e.textContent=String(value);return e}
function row(parent,values){const t=el('tr','');for(const x of values)t.appendChild(el('td',x));parent.appendChild(t)}
async function refresh(){
 const r=await fetch('/api/latest',{cache:'no-store'});
 const result=await r.json();const m=result.manifest||{};
 const cards=document.getElementById('cards');cards.replaceChildren();
 for(const [label,value] of [['Mode','Synthetic only'],['Active embedding',m.active_dimension?m.active_dimension+'D':'—'],['Probe samples',(result.probes||[]).length],['Security alerts',(result.security_alerts||[]).length],['Ethernet',m.ethernet_up?'UP':'DOWN/QUEUE'],['RF',m.alert_radio_up?'UP':'DOWN/QUEUE']]){
   const d=el('div','');d.className='card';d.appendChild(el('small',label));const n=el('div',value);n.className='metric';d.appendChild(n);cards.appendChild(d);
 }
 const p=document.getElementById('probes');p.replaceChildren();
 for(const x of (result.probes||[]).slice(-15))row(p,[x.timestamp_s,x.mode,x.input_power_w_ASSUMED,x.case_temp_c_ASSUMED,x.battery_soc_pct_ASSUMED]);
 const a=document.getElementById('alerts');a.replaceChildren();
 for(const x of (result.security_alerts||[]))row(a,[x.event_id,x.zone_id,x.type,x.rf_receipt,x.operator_ack]);
}
refresh();setInterval(refresh,2500);
</script></main></body></html>"""

def check_sanitized(body: dict) -> None:
    if not isinstance(body, dict):
        raise ValueError("payload is not an object")
    if set(body) != {"manifest", "probes", "ethernet_telemetry", "security_alerts"}:
        raise ValueError("only sanitized simulated telemetry accepted")
    if body["manifest"].get("source") != "SIMULATED_NOT_MEASURED":
        raise ValueError("simulator console rejects non-synthetic payload")
    def walk(item):
        if isinstance(item, dict):
            for k,v in item.items():
                if any(term in k.lower() for term in SENSITIVE_KEYS):
                    raise ValueError("sensitive field not permitted in console")
                walk(v)
        elif isinstance(item, list):
            for v in item:
                walk(v)
    walk(body)
    if len(body["probes"]) > 10000 or len(body["security_alerts"]) > 1000:
        raise ValueError("demo resource limit")

class LocalConsole(ThreadingHTTPServer):
    def __init__(self, port: int, token: str):
        super().__init__(("127.0.0.1", port), Handler)
        self.token = token
        self.latest: dict = {}
        self.lock = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    server: LocalConsole

    def log_message(self, fmt, *args):
        # Never log tokens or raw request body.
        pass

    def reply(self, code: int, content: bytes, media_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        path=urlparse(self.path).path
        if path == "/":
            self.reply(200,dashboard.encode(),"text/html; charset=utf-8")
        elif path == "/api/latest":
            with self.server.lock:
                data=json.dumps(self.server.latest).encode()
            self.reply(200,data,"application/json")
        else:
            self.reply(404,b"not found","text/plain")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/ingest":
            return self.reply(404,b"not found","text/plain")
        if self.headers.get("Authorization","") != "Bearer "+self.server.token:
            return self.reply(401,b"unauthorized","text/plain")
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0 < length <= MAX_POST_BYTES:
                raise ValueError("payload too large")
            data=json.loads(self.rfile.read(length))
            check_sanitized(data)
        except (ValueError,KeyError,TypeError,json.JSONDecodeError):
            return self.reply(400,b"invalid synthetic payload","text/plain")
        with self.server.lock:
            self.server.latest=data
        self.reply(200,b'{"status":"accepted_demo"}',"application/json")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--token-env",default="SIAMESE_DEMO_CONSOLE_TOKEN")
    a=p.parse_args()
    token=os.environ.get(a.token_env,"")
    if len(token) < 16:
        raise SystemExit("set a random token (>=16 chars) in environment; demo local only")
    print(f"Synthetic supervisor at http://127.0.0.1:{a.port} (loopback-only)",flush=True)
    with LocalConsole(a.port,token) as srv:
        srv.serve_forever()

if __name__=="__main__":
    main()
