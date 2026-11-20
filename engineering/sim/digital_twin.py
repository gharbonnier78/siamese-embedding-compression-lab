"""Digital twin of a FIXED event appliance: synthetic descriptors/vectors only.

This file does NOT simulate actual RGB/NIR pixels, infer genuine face matches,
measure watts, or validate biometric detection/accuracy. It models control flow
and deterministic telemetry so the external PC supervisor can be developed
before manufacturing hardware. One active representation per run: 512 or 128.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import urllib.request

DEVICE_ID = "demo-fixed-zone-01"
SCHEMA_VERSION = "synthetic-edge-digital-twin-v1"
ALERT_TYPES = {"REVIEW_REQUIRED", "POWER_FAULT", "TAMPER"}
PSEUDO_IDENTITIES = ["lab-001", "lab-002", "lab-003", "lab-004"]
ALLOWLIST = {"lab-001", "lab-002"}
WATCHLIST = {"lab-003"}
# These are not real identities, faces, watchlists, or physical sample imagery.

def vector(label: str, dimension: int) -> list[float]:
    seed = int.from_bytes(hashlib.sha256(label.encode()).digest()[:8], "big")
    gen = random.Random(seed)
    values = [gen.gauss(0, 1) for _ in range(dimension)]
    norm = math.sqrt(sum(v * v for v in values)) or 1.
    return [v / norm for v in values]

def measured_quality_proxy(capture: dict) -> float:
    """Purely hypothetical signal-quality score, NOT image quality or biometrics."""
    yaw = abs(float(capture["yaw_degrees"]))
    blur = float(capture["motion_blur_px"])
    occluded = float(capture["occlusion_fraction"])
    light_penalty = 0.15 if capture["mode"] == "RGB" and capture["ambient_lux"] < 10 else 0.0
    return max(0., 1 - yaw / 115 - blur / 15 - occluded * 0.65 - light_penalty)

def simulate_capture(capture: dict, dimension: int, gallery: dict, seed: int) -> dict:
    if dimension not in (512, 128):
        raise ValueError("only 512 or 128 projection demo")
    quality = measured_quality_proxy(capture)
    result = {
        "capture_id": capture["capture_id"], "mode": capture["mode"],
        "yaw_degrees": capture["yaw_degrees"],
        "ambient_lux": capture["ambient_lux"],
        "synthetic_quality_proxy": round(quality, 5),
        "source": "SIMULATED_NOT_BIOMETRIC",
    }
    if quality < 0.53 or capture.get("face_present") is False:
        return {**result, "decision": "NO_DECISION", "score": None,
                "matched_policy": None, "candidate_ref": None}
    # Injection of a synthetic descriptor, not extraction from a photo.
    label = capture.get("lab_subject")
    if label in gallery:
        base = gallery[label]
        noise = 0.2 + 0.25 * (1 - quality)
        rnd = random.Random(seed + int.from_bytes(
            hashlib.sha256(capture["capture_id"].encode()).digest()[:4], "big"))
        observed = [v + rnd.gauss(0, noise / math.sqrt(dimension))
                    for v in base]
    else:
        observed = vector("unknown:" + capture["capture_id"], dimension)
    norm = math.sqrt(sum(v*v for v in observed)) or 1.
    observed = [v/norm for v in observed]
    scored = sorted(
        ((sum(a*b for a,b in zip(observed, v)), k) for k,v in gallery.items()),
        reverse=True,
    )
    score, candidate = scored[0]
    # This threshold is a control-flow DEMO parameter, not an operating point
    # for any face-recognition, safety or security deployment.
    if score < 0.78:
        decision, policy, candidate = "UNKNOWN", None, None
    elif candidate in WATCHLIST:
        decision, policy = "REVIEW_REQUIRED", "SIMULATED_WATCHLIST"
    elif candidate in ALLOWLIST:
        decision, policy = "ALLOWLIST_CANDIDATE", "SIMULATED_ALLOWLIST"
    else:
        decision, policy = "UNKNOWN", None
    return {**result, "decision": decision,
            "score": round(score, 5),
            "matched_policy": policy,
            "candidate_ref": candidate if policy else None}

def load_scenario(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("scenario must be a nonempty list")
    required = {"capture_id","mode","yaw_degrees","motion_blur_px",
                "occlusion_fraction","ambient_lux","ambient_c","lab_subject"}
    for item in data:
        if required - item.keys() or item["mode"] not in ("RGB","NIR"):
            raise ValueError(f"invalid synthetic scene: {item}")
    return data

def run(scenes: list[dict], dimension: int=128, seed: int=17,
        ethernet_up: bool=True, alert_radio_up: bool=True) -> dict:
    gallery = {label: vector(label, dimension) for label in PSEUDO_IDENTITIES}
    records, alarms, sensor_readings, ethernet = [], [], [], []
    for n, scene in enumerate(scenes):
        result=simulate_capture(scene, dimension, gallery, seed)
        records.append(result)
        # Simulated watts and Celsius values are NOT from the real SoM or shunts.
        assumed_w = 2.0 if result["decision"] == "NO_DECISION" else (
            8.5 if scene["mode"] == "NIR" else 6.8)
        sensor_readings.append({
            "index": n, "timestamp_s": n*2.0,
            "mode": "DETECT_SEARCH" if result["decision"] != "NO_DECISION" else "QUALITY_REJECT",
            "input_power_w_ASSUMED": assumed_w,
            "case_temp_c_ASSUMED": round(float(scene["ambient_c"]) + assumed_w * 0.65, 2),
            "ambient_temp_c_ASSUMED": scene["ambient_c"],
            "battery_soc_pct_ASSUMED": max(5., 95. - n*0.5),
            "PIR_wake": True,
            "probe_origin": "SIMULATED_NOT_CALIBRATED",
        })
        ethernet.append({"event_id":f"tel-{n+1:04d}","transport":"ETHERNET",
                         "status":"DELIVERED" if ethernet_up else "QUEUED_OFFLINE"})
        if result["decision"] == "REVIEW_REQUIRED":
            # DO NOT put candidate identity or score in RF alert payload.
            alarms.append({"event_id":f"alert-{n+1:04d}", "device_id":DEVICE_ID,
                           "zone_id":"demo-entry-A", "type":"REVIEW_REQUEST",
                           "capture_ref":f"restricted-local-{n+1:04d}",
                           "rf_receipt":"ACK" if alert_radio_up else "QUEUED",
                           "operator_ack":"PENDING", "human_action":"NONE"})
    manifest={
        "schema_version":SCHEMA_VERSION,"device_id":DEVICE_ID,
        "synthetic_seed":seed,"active_dimension":dimension,
        "model_id":f"SYNTHETIC-DEMO-{dimension}D-NOT-BIOMETRIC",
        "policy_revision":"DEMO-POLICY-NOT-LIVE",
        "gallery_size":len(gallery),"source":"SIMULATED_NOT_MEASURED",
        "no_real_images":True, "no_real_1toN_accuracy_claim":True,
        "ethernet_up":ethernet_up,"alert_radio_up":alert_radio_up,
    }
    return {"manifest":manifest,"captures":records,"probes":sensor_readings,
            "ethernet_telemetry":ethernet,"security_alerts":alarms}

def post_to_demo_console(report: dict, url: str, token: str) -> None:
    if not url.startswith("http://127.0.0.1:") and not url.startswith("http://localhost:"):
        raise ValueError("demo console only accepts loopback; not production TLS")
    # Non-biometric outputs only; no capture metadata or candidate_ref in POST.
    body=json.dumps({"manifest":report["manifest"],"probes":report["probes"],
                     "ethernet_telemetry":report["ethernet_telemetry"],
                     "security_alerts":report["security_alerts"]}).encode()
    req=urllib.request.Request(url.rstrip("/")+"/ingest", body, method="POST",
            headers={"Content-Type":"application/json","Authorization":"Bearer "+token})
    with urllib.request.urlopen(req,timeout=5) as response:
        if response.status != 200:
            raise RuntimeError("console did not accept data")

def write_report(report: dict, destination: Path) -> None:
    destination.mkdir(parents=True,exist_ok=True)
    path=destination/"synthetic_digital_twin.json"
    text=json.dumps(report,indent=2,sort_keys=True)
    path.write_text(text+"\n",encoding="utf8")
    with (destination/"synthetic_probes.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=list(report["probes"][0]))
        w.writeheader();w.writerows(report["probes"])
    (destination/"SIMULATION_NOT_REAL_DATA.txt").write_text(
        "All data are synthetic and results are modeled. This is NOT a real "
        "RGB/NIR vision analysis, 1:N biometric accuracy assessment, or calibrated "
        "power/thermal trace. No claims of field deployment or legal authorization.\n",encoding="utf8")

def main() -> None:
    p=argparse.ArgumentParser(description="Synthetic fixed-site EO/NIR device demo")
    p.add_argument("--scenario",type=Path,default=Path(__file__).with_name("synthetic_scenes.json"))
    p.add_argument("--dim",type=int,choices=(128,512),default=128)
    p.add_argument("--seed",type=int,default=17)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--ethernet-down",action="store_true")
    p.add_argument("--rf-down",action="store_true")
    p.add_argument("--demo-console",default="")
    p.add_argument("--demo-token",default="",help="loopback demo token; never production credentials")
    a=p.parse_args()
    report=run(load_scenario(a.scenario),a.dim,a.seed,
               not a.ethernet_down,not a.rf_down)
    write_report(report,a.out)
    if a.demo_console:
        if not a.demo_token:
            raise ValueError("set --demo-token for local console")
        post_to_demo_console(report,a.demo_console,a.demo_token)
    print(json.dumps({"output":str(a.out),"mode":"SYNTHETIC",
                      "captures":len(report["captures"]),
                      "review_requests":len(report["security_alerts"]),
                      "active_dim":a.dim},sort_keys=True))

if __name__=="__main__":
    main()
