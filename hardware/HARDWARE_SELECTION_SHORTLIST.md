# Initial board + instrumentation shortlist — source-grounded, not purchase approved

## SBC candidate — Radxa ROCK 5B (8GB or more RAM candidate)

- Official board reference: https://docs.radxa.com/en/rock5/rock5b/getting-started/introduction
- Official board envelope: 100 x 75 mm (applies to 5B/5B+ form-factor; validate revision).
- RK3588 NPU claims up to 6 TOPS, **not a measured AdaFace real-world throughput**.
- Vendor documents camera CSI availability; confirm the exact chosen revision, ribbon routing, Linux/NPU model export/runtime and suitable NIR camera support **before purchase**.
- Power supply reference: https://docs.radxa.com/en/rock5/rock5b/getting-started/power-supply — manufacturer recommends official 30W PD adapter; neither 30W rating nor marketing TOPS is measured energy consumption.
- Do not buy until verified model-inference compatibility (including AdaFace IR101/R100 preprocessing/ops) and firmware support on target runtime.

## Power instrumentation

- Choose a precision external DC power meter / logging power analyzer with verified resolution, bandwidth, calibration traceability and time-sync capability. An INA228 breakout is an inexpensive secondary rail monitor candidate, **not automatically a calibrated absolute measurement reference**. Verify shunt, input voltage range, telemetry sampling limits and electrical isolation where applicable.
- Avoid relying solely on a consumer USB-C voltage display for energy-per-transaction or high-frequency peak characterization.

## Physical configuration recommendation

**Stage A:** bench powered by manufacturer-approved adapter, board plus Ethernet + RGB sensor, no battery, no enclosure, external precision power meter, thermocouples, standalone load generator; start with non-biometric synthetic workloads.

**Stage B:** add NIR, PIR/wake interrupt, passive heatsink and preliminary printed enclosure *only* once camera interfaces, mounting and safe heat paths validated.

**Stage C:** introduce a certified commercial battery + compatible power electronics if mission demand and measured duty cycle justify it. Do not hand-assemble loose lithium cells.

## Procurement gates

For each ordered line record vendor, manufacturer part number, version/revision, unit cost including VAT/shipping, availability, alternatives, datasheet, dimensions, return policy, license and acceptance tests. The historical roughly EUR 700 figure is **not** a current bill of materials or qualified estimate.
