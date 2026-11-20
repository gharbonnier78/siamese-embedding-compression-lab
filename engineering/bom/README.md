# Bill of materials — do not procure from provisional tables

- **Product eBOM:** hardware/BOM_PRODUCT_FIELD_DEVICE_V0.csv
- **Event operator radio receiver:** hardware/BOM_EVENT_SECURITY_ALERT_RECEIVER_V0.csv
- **Separate PC and measurement bench:** hardware/BOM_EXTERNAL_TEST_BENCH_V0.csv
- **Mechanical materials/process study:** engineering/mechanical/MATERIALS_AND_PROCESS_V0.csv
- **Electrical interfaces:** engineering/electronics/PROBE_INTERFACE_CONTRACT.csv

Run \`python engineering/bom/audit.py --root . --output /tmp/bom-audit.json\`.

The auditor flags unverified lines but never authorizes fabrication. Complete procurement needs verified manufacturer/MPN, distributor and quote date, actual datasheets, assembled revisions, footprints, availability, alternatives, safety, exact board and optical mechanical envelopes and signed engineering approval.

No real eBOM/mBOM manufacturing pack exists yet; all BOMs contain candidates/placeholders. A passing CI pipeline is not a purchasing authorization.