"""Deterministic PC-only mock experiment with separate physical and simulated evidence.

No camera, instrument or real face data; results are ASSUMED watts and temperatures,
not measured accuracy, autonomy or any power claim.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random

ASSUMED_WATTS = {
    "sleep": 0.18, "idle": 1.8, "detect": 5.5, "search": 9.5,
    "transmit": 3.2, "maintenance": 4.0,
}

def simulate(seed: int, repetitions: int, interval_s: float = 0.5) -> list[dict]:
    if repetitions < 1 or interval_s <= 0:
        raise ValueError("positive repetitions and interval required")
    rng = random.Random(seed)
    out=[]
    wh=0.0
    clock=0.0
    kinds=list(ASSUMED_WATTS)
    for n in range(repetitions):
        mode=kinds[n%len(kinds)]
        base_w=ASSUMED_WATTS[mode]
        # Reproducible jitter is a hypothesis, not instrument noise calibration.
        power_w=round(base_w*(0.97 + 0.06*rng.random()),6)
        ambient_c=round(18 + 15*rng.random(),5)
        case_c=round(ambient_c+power_w*0.7,5)
        wh+=power_w*interval_s/3600
        out.append({
            "sample":n, "clock_s":round(clock,3),
            "mode":mode, "power_w_ASSUMED":power_w,
            "ambient_c_ASSUMED":ambient_c, "case_c_ASSUMED":case_c,
            "energy_wh_ASSUMED":round(wh,8), "source":"SYNTHETIC",
            "seed":seed
        })
        clock+=interval_s
    return out

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=7)
    p.add_argument("--samples",type=int,default=120)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    rows=simulate(a.seed,a.samples)
    a.output.mkdir(parents=True,exist_ok=True)
    path=a.output/"synthetic_bench.csv"
    with path.open("w",newline="",encoding="utf8") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    blob=path.read_bytes()
    manifest={"evidence_type":"SIMULATION_ONLY_NOT_METROLOGY","seed":a.seed,
              "samples":len(rows),"csv_sha256":hashlib.sha256(blob).hexdigest(),
              "instrument_calibration_id":None,"real_world_claim":False}
    (a.output/"run_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf8")
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":
    main()
