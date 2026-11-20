# Physical Concept

**Temporary fixed installation; no final dimensions or enclosure selection.** Use an authorized wall or rigid structure, such as a pole or truss with a qualified adapter. A tripod is for calibration and controlled tests only. People move; the device does not. Verify all dimensions, loads and hardware on site.

```text
Elevation: fixed support ║ plate + retention → [RGB | NIR | emitter]
                         ║                     axis tilted toward capture zone
                        secured cable ↓ / drip loop (mounting height H TBD)
Side: wall ║ standoff → lockable yaw/tilt → optical axes ↘ near-to-far zone
     protected cable exit
Plan: support ■ ── RGB ∩ NIR zone ── calibration markers
                 → pedestrian flow / occlusions / reflective surfaces
```

**Mount:** Site-approved wall plate or structural adapter, lockable adjustment plate, angle/repositioning marks, independent secondary retention if required after review, tamper-resistant hardware and opening detection, strain relief and drip loop clear of passage. Check static load, cable torque, wind/vibration, clearance and service access. Do not install in public before validating support, fasteners, retention and clearance. Separate backup access from electronics if necessary, and do not assume ingress protection with a door open.

**Optics:** Rigidly couple RGB and NIR cameras; separate the emitter to reduce internal reflections. Provide a sunshade and measure window transmission. Survey height, yaw/tilt, near/far distance, passage width/direction, trigger line, lighting, reflective surfaces and occlusions. Qualify common FOV and target pixel density at multiple heights. First approximation for frontoparallel width: 2d·tan(horizontal FOV/2); verify on site because obliquity, distortion and overlap invalidate simple extrapolation. Set criteria before capture. Relate PIR-to-first-frame delay, walking speed, exposure and blur; measure RGB/NIR exposure skew. Test NIR with inert targets, hardware fault inhibit and photobiological evaluation before human exposure. No final NIR power or optical geometry is assumed.

**Enclosure:** Evaluate passive conduction from compute and NIR through chassis to shell, away from the backup. Outdoors: drainage, seals, cleanable window and assembled-unit condensation, cold, rain and solar tests; no IP rating claimed. Indoors: check reflections, transitions, artificial light, ventilation and public access.

**Commissioning:** (1) Approve site and survey geometry. (2) Install, retain and inspect mount/cables. (3) Measure alignment, common FOV, pixel density, timing and optical safety using inert markers. (4) Verify signatures and versions of model/index/policy, clock, timestamps and local health. (5) Test offline with power maintained, then source loss/return, retention and recovery. (6) Archive the site profile and acceptance evidence. Recalibrate and recheck after relocation, impact or a changed view.
