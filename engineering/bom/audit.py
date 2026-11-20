"""Audit only: count provisional BOMs and fail-closed on manufacturing readiness."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

BOMS = [
    "hardware/BOM_PRODUCT_FIELD_DEVICE_V0.csv",
    "hardware/BOM_EVENT_SECURITY_ALERT_RECEIVER_V0.csv",
    "hardware/BOM_EXTERNAL_TEST_BENCH_V0.csv",
]
MATERIALS = "engineering/mechanical/MATERIALS_AND_PROCESS_V0.csv"

def evaluate(root: Path) -> dict:
    findings=[]
    for relative in BOMS + [MATERIALS]:
        path=root/relative
        if not path.is_file():
            findings.append({"path":relative,"present":False,"items":0,
                             "unverified":None,"fabrication_ready":False})
            continue
        with path.open(newline="",encoding="utf8") as stream:
            rows=list(csv.DictReader(stream))
        missing=0
        for row in rows:
            # Only full sourced MPNs may support procurement, never inferred prices.
            if "bom" not in relative.lower():
                if str(row.get("status","")).upper() != "RELEASED":
                    missing+=1
            elif not row.get("manufacturer_part_number", "").strip() or \
                row.get("manufacturer_part_number","").strip().upper() in ("TBD","NONE","UNKNOWN"):
                missing+=1
        findings.append({"path":relative,"present":True,"items":len(rows),
                         "unverified":missing,"fabrication_ready":False})
    return {"audit_kind":"SUPPLIER_BOM_CHECK_ONLY","report_status":"HOLD_FABRICATION",
            "reason":"No reviewed/electrically complete design or sourcing evidence",
            "findings":findings,"manufacturing_release":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("."))
    parser.add_argument("--output",type=Path)
    a=parser.parse_args()
    report=evaluate(a.root)
    body=json.dumps(report,indent=2,sort_keys=True)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(body+"\n",encoding="utf8")
    print(body)

if __name__=="__main__":
    main()
