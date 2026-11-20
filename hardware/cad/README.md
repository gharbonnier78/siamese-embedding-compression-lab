# CAD and manufacturing readiness

We have **not recovered verified STL/STEP/Fusion/FreeCAD files or fabrication drawings** from prior chat/repository. Do not present this directory as a production-ready CAD package.

Before modeling any detailed enclosure, freeze:
- actual SBC model/revision and PCB board outline, standoffs, height envelope and thermal placement;
- RGB/NIR module package dimensions, optical axes, NIR-compatible window and emitter eye-safety data;
- PoE/Ethernet power-in, antenna layout, connector service loops and cable bend radii;
- mounting choice, ingress protection, cooling (passive vs active), surface-temperature limits;
- legally/commercially compliant battery module, protection and charger layout if needed;
- tolerance and material properties with supplier/printer and assembly plan.

Deliverables required for G3:
1. Native editable CAD source (parametric FreeCAD/OpenSCAD/STEP when appropriate).
2. Dimensioned assembly drawings and exploded view.
3. Validated STL/3MF for printing and clearance/tolerance coupons.
4. Versioned mechanical and electronics BOM (supplier refs; alternates).
5. Build instructions, wiring diagram, test points, photo evidence.
6. Revision-controlled calibration and metrology harness.

Manufacturing sequence: source and measure real board/cameras -> 2D layout -> CAD with connector/optical envelopes -> coupon print -> first enclosure print -> fit/thermal verification -> revise. No parts purchase or build has been represented as completed.
