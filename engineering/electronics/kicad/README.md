# KiCad board study — NO electrical schematic or production PCB

edge_probe_carrier_PLACEHOLDER.kicad_pcb is a **mechanical outline only**, with zero footprints, copper, electronics, nets or routing. It is not yet a complete PCB design, and MUST NOT be sent for fabrication. Separate generic I/O requirements are in ../PROBE_INTERFACE_CONTRACT.csv.

Next steps before KiCad schematic generation: select MCU, shunt ADC with true ranges, PoE PD/DC safe supply, BMS interface, RF certified module, camera sync, connector pinout, voltage levels, optics safety. Then use actual datasheet pins/footprints, native .kicad_sch, ngspice protected power path, ERC/DRC, human review; after G3 issue Gerber/Excellon/BOM/CPL.

This file can be opened as an outline concept in KiCad. It is NOT an electrical design.
