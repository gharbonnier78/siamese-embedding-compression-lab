# P1 minimal purchase decision — concrete SKUs, staged orders, no fake prices

**Date 2026-11-20; inventory and vendor quotes can change.** Order-candidate line items with source URLs and decision gates: [P1_PROCUREMENT_CANDIDATES_2026-11-20.csv](P1_PROCUREMENT_CANDIDATES_2026-11-20.csv).

## Minimal P1A order after compatibility review

1. One **Radxa ROCK 5B** RK3588 variant (8GB RAM if 1m index benchmark memory allows; 16GB if justified; NOT an assumed ROCK 5B+); official compliant 30W power supply, suitable tested heatsink and microSD/boot storage.
2. One **Arducam B0385 OV9782 1MP USB UVC RGB global-shutter camera** to start the Linux vision pipeline. Investigate exact sensor optics/driver behavior and triggering before buying a full camera set.
3. One **Raspberry Pi Pico 2** for supervision, **two Adafruit 5832 INA228** power-monitor breakout boards, **one Adafruit 5665 SHT45** temperature/RH breakout plus safe I2C and GPIO wiring.
4. Use an **existing PC** as the external simulator; use a **borrowed or rented calibrated DC power meter** as reference (INA228 is not the legal/engineering energy reference).
5. Simple 3D printed **dry-fit** fixture and standard CAT6 Ethernet patch cord. No PCB or enclosed battery at P1A.

**P1B, only after first bench evidence:** one **Arducam B0332 OV9281 USB mono global shutter** for real NIR-channel investigation, **Panasonic EKMB1301111K** PIR with proper sensor interface, **RAK3172-E EU868** LoRaWAN evaluation kit plus event-owned gateway only if there is a demonstrable dispatcher experiment; power backup later. No NIR illuminator without an eye-safety/driver review.

**Hold:** turnkey 5G, Li-ion custom battery board/hot-swap, certified IP enclosure, custom high-speed CSI/USB mainboard, standalone GPU, FPGA, custom LoRa antenna PCB and third-party biometric dataset licenses. A P1 COTS board may be much thicker than the envisioned 30 mm product and **does not validate packaging**.

## What must be verified before an order

Record exact manufacturer code and revision, lens FOV and effective face pixels at distance, USB UVC on selected ROCK OS, exposed trigger and required cable, RAM/flash sufficiency (1m×512×4B ≈2.05GB raw vector floats before index/OS), sustained NPU availability, peak power, thermal, supply compliance, support terms and shipping/returns in France. A search-result price is not a binding invoice.

**Important camera caveat:** a vendor statement of 'global shutter' is NOT proof of cross-camera synchronous capture. A recent user issue reported Linux trigger difficulties on B0385; obtain vendor confirmation or bench-test the actual version before building synchronisation-specific PCB.

## Sources

- Radxa 5B and power: https://radxa.com/products/rock5/5b/ ; https://docs.radxa.com/en/rock5/rock5b/getting-started/power-supply
- Arducam product list B0385/B0332: https://docs.arducam.com/UVC-Camera/USB2-UVC-Camera-Kit/Specs-and-Selection-Guide/
- Raspberry Pi Pico 2: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html
- Adafruit INA228 5832: https://www.adafruit.com/product/5832
- Adafruit SHT45 5665: https://www.adafruit.com/product/5665
- PIR Panasonic: https://na.industrial.panasonic.com/products/sensors/sensors-automotive-industrial-applications/lineup/pir-motion-sensor-papirs/series/149462/model/149532
- RAK 3172 EU868: https://docs.rakwireless.com/product-categories/wisduo/rak3172-evaluation-board/overview/
- Flux design/manufacturing exports: https://docs.flux.ai/reference/manufacturing
