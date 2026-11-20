# Environmental Test Matrix

**Proposed plan; no tests passed.** Methods references: IEC 60068 (environment), [IEC 60529](https://webstore.iec.ch/en/publication/2452) (ingress), IEC 62471 (photobiology), [ISO/IEC 30107-1](https://www.iso.org/standard/83828.html) (PAD framework). Set severities, dwell times and criteria before testing from mission, drawings and vendor limits. Start with inert/synthetic targets; only use consenting participants after specific authorization. No real lists, street trials or protected datasets. Study 0 remains negative.

| Test | Method and controls | Evidence/review criterion |
|---|---|---|
| Direct sun, backlight, rapid shade | Measure angle, irradiance and lux; reproducible control scene | RGB/NIR saturation, exposure recovery, capture yield and temperature; thresholds TBD |
| Night and reflections | Moving inert targets and reflective surfaces; measure lux, NIR current and duration | Fault interlock, approved exposure before human trials, energy and capture yield |
| Rain, water film and ingress | Directed rain, dry/wet windows, inspection before and after, complete closed assembly | Continuity, no harmful penetration, occlusion and no-decision rate; exploratory test does not establish IP rating |
| Cold and wet transition | Cold start, wet–cold–warm cycle, discharge within pack limits | Wake, usable Wh, BMS cutoff and fog recovery; no charging outside permitted range |
| Heat + sun + bursts | Closed enclosure, radiative loading and sustained workload | Junction/shell/pack/optics temperatures, throttling and safe shutdown; margins to verified limits |
| Humidity and condensation | Cycle humidity and temperature; compare with dry control | Quality, recovery time and inspection for water/corrosion |
| Moving pedestrians, stationary device | Fixed wall mockup; tripod for calibration only; clustered and occluded passages, ~1,000/hour over 10 hours/day × 5 days; separate structural vibration | Blur, RGB/NIR skew, duplicates, loss, sustained p95/p99, J/event, false alerts/hour and operator workload |
| Offline mission | Disconnect data path and disable radios while maintaining supply; no PC | Target 100% local pipeline continuity, stale-policy notification and later export without silent loss |
| PoE/DC loss, recovery and backup comparison | Separate data from supply loss; test at peak load and lowest admissible backup state. Compare local module, upstream UPS and dual packs if safely qualified for testing. Test final cable loss separately. | Within agreed interval: no reset/corruption, rail above minimum. Beyond it: safe shutdown. Capture dips, inrush, temperature and recharge. For dual hot-swap, test both removal directions at peak load after safety review. |
| Update, faults and saturation | Interrupt update at multiple stages; invalid package, full disk, tamper | Reject invalid signature, full rollback, intact logs or signaled loss, never enter unsafe mode |

Compare with bench controls in repeated blocks. Record versions, units, references, calibration, conditions and exclusions before analysis. Report W, Wh/day, J/event, J/query, peak current, p50/p95/p99, throttling, temperatures, loss and backlog. Separate acquisition/processing failures (FTA/FTC), quality, PAD, 1:1 FMR/FNMR and 1:N FPIR/FNIR; give denominators, uncertainty intervals and per-condition results. Fix performance thresholds before observing results.
