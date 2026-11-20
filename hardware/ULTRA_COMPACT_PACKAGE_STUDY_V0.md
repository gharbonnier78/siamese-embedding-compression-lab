> **Environmental/design-for-manufacturing update (2026-11-20):** See [staged outdoor-upgradable prototype plan](STAGED_ENVIRONMENTAL_PROTOTYPING_AND_DFM_V0.md). A-v2 is a sealed-capable chassis **without through vents**, gasket/window/cable interface allowances and a thermally conductive exterior; IP/tropicalization is *not* a P0/P1 acceptance condition or a validated property. Keep the 100×150×30 mm goal aspirational and assess full installed volume with optional backup dock.

# Ultra-compact wall appliance — recovered dimensions, candidate modules and CAD brief

**Date:** 2026-11-20  
**Scope:** design challenge and preliminary packaging study, **not a verified production assembly or completed CAD**.  
**Source of dimensional challenge:** earlier 2026-08-20 "Projection Siamois 19 08 26" conversation. **This more specific compactness requirement supersedes generic enclosure assumptions** in the 165×120×55 mm prior exploratory SCAD and 2026-11-20 Flux Phase 0.

## Recovered original design intent and constraints

- **Hard compactness challenge: 100 mm wide × 150 mm high × 30 mm deep (0.45 litre geometric envelope).** This is a target to falsify, not a proven feasible assembly.
- **Earlier less compact baseline for comparison:** ~120×68×138 mm = ~1.13 litres (different orientation; compare volume, not mounting geometry).
- **Installation:** temporarily rigidly fastened to an event wall/support, stationary cameras facing people moving through defined field of view. It is not a body-worn or walking device.
- **Front:** EO/RGB and NIR cameras coplanar (near one another), pulsed eye-safe NIR emitter, ultralow-power passage/presence PIR or optional radar. Concealed antenna(s), no unnecessary external projections.
- **Back:** conductive enclosure heat spreader/heat sink integrated into wall mounting, thermal path from AI SoM, tamper/rear retention bracket, sealed cable gland and PoE/DC.
- **Compute/data:** local onboard model, encrypted 1:N gallery and exact/ANN index, separate authorized allow/watchlist policy, no runtime PC. Supervisory MCU sensor acquisition and optional LoRa alert RF integrated on a compact auxiliary carrier.
- **Power:** PoE or regulated DC preferred for fixed event operation; protected backup and uninterrupted battery replacement remain *to-be-validated requirements*; don't claim two smart packs fit in 30 mm. **Compare 30 mm head with separate wall-mounted power/backup dock versus thicker all-in-one**, preserving safety and continuity when required.
- **Earlier components mentioned conceptually:** RK3588-class SoM, Intel AX210 Wi-Fi, Quectel RM500Q-GL 5G fallback, NXP SE050 secure element, about 20Wh demonstration backup. These were concepts, not a verified mechanical BOM or circuit.
- **NO silent feature removal** to meet enclosure dimensions: explicitly report the feasibility tradeoffs for 5G antenna, backup batteries, NIR emitter safety, fanless heat sinking and high-FOV lens depth.

## Source-grounded compact shortlist (module dimensions only)

| Function | Module candidate | Vendor dimensions / source | Engineering qualification blocker |
|---|---|---|---|
| Edge AI SoM A | Radxa CM5 RK3588S with NPU | Official product lists 56×41 mm (some documentation calls 55×40 mm), https://radxa.com/products/cm/cm5/ | Actual SKU/module revision, installed height, carrier PoE, 2 CSI camera streams, AdaFace model conversion, steady power and heat dissipation |
| Edge AI SoM B | Raspberry Pi Compute Module 5 | 55×40×4.7 mm, https://www.raspberrypi.com/products/compute-module-5/ | No independent high-TOPS NPU on module; CPU and optional external accelerator latency/heat/board space must be tested |
| Higher power alternative | NVIDIA Jetson Orin NX | 69.6×45 mm, vendor data sheet | Bigger module and heat solution; select only if required model, no unqualified GPU inference claims |
| RGB global shutter candidate | Arducam OV9782 color MIPI module | 24×25 mm, https://www.arducam.com/arducam-1mp-ov9782-global-shutter-color-mipi-camera-module-22pin-for-depthai-oak-dm1090ffc.html | 1 MP may be inadequate for intended face pixel density at event standoff; verify format/CSI compatibility, frame synchronization and lens total depth |
| NIR mono candidate | Arducam OV9281 global shutter | 25×24 mm, https://www.arducam.com/blog/product/mini-ov9281-mono-global-shutter-for-pi/ | Choose no-IR-cut variant, matched optics/FOV, NIR emitter safety, measurable recognition quality |
| Short alert radio | Murata Type 1SJ LoRaWAN module | 10×8×1.6 mm, https://www.murata.com/en-global/products/connectivitymodule/lpwa/overview/lineup/type-1sj-296 | RF antenna footprint, gateway coverage and secure operator ACK workflow; radio module size ≠ complete antenna or RF design |
| LoRa+MCU alternative | RAK3172 / RAK3172-SiP | 15×15.5×3.5 mm or SiP 12×12×1.22 mm, https://docs.rakwireless.com/product-categories/wisduo/rak3172-sip/overview/ | Consider reuse as alert MCU but check real sensor buses, security stack, memory and power instead of assuming functional equivalence |
| PIR wake | Panasonic EKMB series | Standby sensor options 1/2/6 µA, https://na.industrial.panasonic.com/products/sensors/sensors-automotive-industrial-applications/lineup/pir-motion-sensor-papirs/series/149462 | Lens window thickness, temperature dependence, trigger FOV and false wakes in crowds |
| Crypto secure element | NXP EdgeLock SE050 | 3×3×0.33 mm chip, https://www.nxp.com/pages/edgelock-se050-plug-and-trust-secure-element-family-enhanced-iot-security-with-high-flexibility%3ASE050 | Board routing, genuine secure boot/OTA chain integration |
| Wi-Fi option | Intel AX210 M.2 2230 | 22×30 mm standard card, https://www.intel.fr/content/www/fr/fr/products/docs/wireless/wi-fi-6e-ax210-module-brief.html | Connector, antennas, extra energy and platform driver integration |
| Cellular fallback | Quectel RM500Q-GL | 52×30×2.3 mm, manufacturer's official documentation | Antenna/battery/thermal and modem power may dominate the slim 30 mm packaging; compare *optional adjacent dock* or omission only by approved tradeoff |
 
**No supplier, cost, inventory, actual sensor compatibility or full product dimensions have been verified in this study.** All above are *component-level* candidate measurements.

## Two package architectures to compare, not silently drop requirements

### **PKG-A: ultra-slim sensor+AI head**
Target 100×150×30 mm including enclosure (0.45L), rigid wall mount, RGB/NIR optical front, ultra-low-power PIR, RF antenna inside RF-transparent zone, CPU/NPU SoM + carrier and eMMC, PoE/DC cable, passive rear aluminium thermal spreader. An **external but still wall-fixed managed backup/power dock** may be necessary for safe hot-swap, PoE/DC conversion, high peak power, extra 5G modem, and battery pack service. **Label separate power dock as increasing total system volume and cost; do not use head volume to claim the complete installed system is 0.45L.**

### **PKG-B: integrated all-in-one**
Preserve dual protected swappable battery requirement and internal modem/antennas if site wants it. Dimension is **not yet bounded**; expect depth to need increasing and let CAD/thermal/electrical studies determine it. Same electronics/optical head and separate rear modular battery cassette for service. Do not invent 40-50mm as an achieved minimum.

## Engineering drawing / sketch request

Create a **single industrial sketch sheet** with:
1. Primary 3/4 front orthographic of very thin wall-mounted housing approx H150×W100×D30 mm *TARGET ONLY*, exposed RGB+NIR protected windows side by side, adjacent pulsed NIR window and PIR, minimal status LED, no huge dome cameras.
2. Rear semi-exploded internal pack layout: 56×41mm SoM, camera modules 24×25 each, compact supervisor/RF/PoE PCB, copper spreader and rear aluminium heat path, concealed antenna window; clear wall bracket, cable going down.
3. Small right-edge **section view** dimensioned 30mm target and distinct optional external power/battery dock as **NOT INCLUDED IN 30mm head**.
4. Clean industrial aesthetic, dark brushed aluminium or graphite, flush glass/IR windows, gentle chamfers, tamper resistant service slot, weather seals. Explicitly technical concept illustration **not fabricated/verified**; no proprietary commercial product likeness.

## Hard acceptance questions before selecting mechanical design

- What is the actual paired camera FOV and face pixel density (especially the candidate 1MP modules), at entrance distances derived from site survey?
- Can RGB/NIR CSI channels and fixed trigger operate in same selected SoM/OS, at requested frame rate and capture timing?
- What is the **true 3D z-stack** including optical lenses, adhesive/windows, sensor boards, mounting screws, CSI ribbons, board-to-board connectors, SoM, thermal interface, heat spreader, environmental sealing, rear wall bracket, cable bend radii and connector backshells?
- Will the high-power SoM and NIR LED cause unsafe hotspots inside a 30 mm sealed unit in full sun? Demonstrate *measured* surface/SoC/pack temperature after solar soak.
- Does a complete dual-hot-swap solution and protected 5G fall back fit in the target size with safety and service access? If not, show modular adjacent dock with actual total dimensions and TCO, or request approval to relax the target.
- Show weight, total occupied volume including external dock, installation time and manufacturing cost for **both** packages PKG-A/B.
- Preserve low-power radio alert-to-organizer receiver, acknowledged messages and no exposed biometric data.
- No claim of real-life facial watchlist legality or match accuracy without separate approved context.

**Original scientific design principle:** do not degrade algorithmic accuracy/energy benchmarking to make the enclosure look good. The device is for controlled synthetic / consented research with independent analysis PC and evidence.
