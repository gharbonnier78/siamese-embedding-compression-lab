# Test Bench Bill of Materials

**Independent equipment, never installed inside the product.** No purchase, price or stock verified. Named models are candidates, not qualified configurations.

| ID | Quantity | Equipment/source | Verification |
|---|---:|---|---|
| BN-01 | 1 | Existing PC or workstation, replay/ingestion scripts and dashboard | Timestamped throughput, reproducibility and storage for authorized data only |
| BN-02 | 1 | [Keysight N6705C](https://www.keysight.com/us/en/product/N6705C/dc-power-analyzer-modular-600-w-4-slots.html) mainframe, source/measurement module TBD; passive independent DC analyzer alternative | Ranges, insertion drop, pulse capture and calibration; distinguish PSU measurements from backup operation |
| BN-03 | 1 + probes | [Keysight DAQ970A](https://www.keysight.com/us/en/product/DAQ970A/data-acquisition-system.html), thermocouple configuration/accessories TBD; calibrated standalone logger alternative | Channels, cold-junction compensation, certificates, placement and uncertainty |
| BN-04 | 1 | Approved lab DC supply and electronic load, unselected | Peak current, protection and transient response |
| BN-05 | 1 set | Oscilloscope, differential probe, sync generator/marker, shunts and cables | Bandwidth, isolation and clock drift |
| BN-06 | 1 set | Lux meter/radiometer, visible/NIR targets and controlled source | Spectral band, calibration and specialist NIR evaluation |
| BN-07 | Lab access | Climate chamber, controlled driven rain, irradiation/wind and mechanical/motion fixtures | Severities and instrumentation set by mission; external lab if needed |
| BN-08 | Optional | Thermography and ground-truth video excluding personal data | Emissivity, time markers and authorized data only |
| BN-09 | 1 set | Electrical measurement harness and reference probes, pack test protection | Verified connections, Kelvin method, limits and stop procedure |
| BN-10 | 1 set | Calibration-only tripod, rigid wall mockup, targets and removable markers | Geometry repeatability and repositioning evidence |
| BN-11 | 1 set | PoE source and DC interruption instruments, load and PD power measurement; candidate UPS and protected reserve fixtures as needed | Class/drop with representative cable; separate data and energy loss; measure transfer/recovery and final-cable failure |

The bench may power and instrument the prototype in the lab. Prove autonomous operation without a PC or network access, on regulated DC or PoE without network service, using independent instruments that do not control the product. An energy interruption is a separate test.
