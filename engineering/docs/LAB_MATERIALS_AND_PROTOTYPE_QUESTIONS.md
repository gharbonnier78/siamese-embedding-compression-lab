# Laboratory questions: miniaturized, rain-tolerant fixed RGB/NIR appliance

**Date:** 2026-11-20. **Purpose:** concise pre-visit question guide for an engineering/materials laboratory (e.g. Arkema materials innovation discussion scheduled 3 Dec 2026). No access to specific equipment, materials, prototype service or expertise is assumed; first ask what the lab can actually offer.

## Materials / housing questions

1. **Enclosure:** For a 100×150×30 mm aspirational wall head, which realistic materials/processes at 1, 5, 20 and 100 units: printed ASA/PETG; CNC 6061 aluminum; molded PC/ABS; hybrid metallic heat-spreader + RF-transparent optical front? Obtain real thickness, tolerances, cost/lead time and UV aging.
2. **Thermal:** Can a compact passively cooled sealed box with an RK3588-class SoM reject measured worst-case heat under direct sun, and what TIM, metal contacts, corrosion isolation and accessible surface temperature tests are appropriate? Which dimensions must be relaxed?
3. **Optics:** Which scratch-resistant, UV-stable, weatherable windows transmit the chosen visible **and near-infrared** spectra without unacceptable reflection or distortion, and allow gasket/adhesive replacement? Request optical transmittance curves, not aesthetics alone.
4. **Water ingress and condensation:** What gasket form, hardness, compression set, torque sequence, ePTFE equalization vent location, cable gland, drain/visor geometry, maintenance opening-cycle protocol and testing method is recommended? What is the actual feasibility of IP65 vs IP66 for the assembled prototype?
5. **Coatings:** When should conformal coating/tropicalization be used, and which traces, connectors, probe areas, optical components and thermal faces must be excluded? Can it be reworked after P1/P2 modifications?
6. **RF:** How should a LoRaWAN/EU868 antenna reside in a heat-dissipating metal shell with no attenuation or ingress risk? Does an RF-transparent insert compromise sealing, and how would the lab test it?
7. **Field service:** Could a detachable sealed optical cassette or protective window be made serviceable between events without destroying IP level; can droplet film, mud/grease and condensation be handled with simple maintenance rather than heater power?
8. **Sustainability:** What repair, modularity and end-of-life path is economical for shells, optics, electronics, coating, and backup dock?

## Test equipment and qualification questions

9. Can the lab conduct controlled immersion/nozzle ingress only at its qualified severity, water spray, thermal cycling/soak, 60068-2-30 humidity cycling, 60068-2-78 constant humidity and joint aging? Who owns test reports, traceability and measured acceptance?
10. Can we obtain independent calibrated **power and thermal instrumentation** or partner-lab access for J/capture, J/matching/search, peak current and NIR/SoM temperature?
11. Can we instrument the complete head **mounted on real wall/truss clearance**, not merely a free-standing open board, through day/night and hot humidity?
12. What must we deliver for a useful design-for-manufacturing review: 3D STEP, P1 electronics BOM, real camera/SoM mechanical models, TIM spec, gasket section drawing and service procedure?
13. At what prototype maturity does a materials or environmental test provide genuine falsifiable evidence without forcing expensive molds, IP certification, or production tooling?
14. What is the smallest and cheapest **one-week experimental design** that would falsify the assumption that a sealed 30mm enclosure can cool the chosen SoM?

## Explicit deliverables from any lab discussion

A written list of tests the lab can support, recommended materials/processing, samples needed and preparation, expected external partner if out of scope, responsible reviewer and numerical acceptance thresholds set *before* testing. No announcement of "IP66 qualified" or "tropicalized" prior to actual evidence.

See P1 purchase candidate CSV, Flux brief, mechanical material matrix and staged environmental prototyping plan.
