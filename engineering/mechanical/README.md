# P0 enclosure, modular materials, mounting

**Three design variants added:** [Hull / Book / Cassette](VARIANT_COMPARISON.md), with editable parametric [concept_variants.scad](concept_variants.scad). Run `openscad -D 'style="hull"' -D 'part="assembly"' -o /tmp/hull.stl engineering/mechanical/concept_variants.scad` and repeat for `book` and `cassette`. Visual/envelope study only; structural joints are not qualified.


Source enclosure.scad generates BODY/LID/BRACKET and OPTIONAL DOCK as editable parameters; outputs STL for 3D viewing/dry fit only. The 100×150×30 mm head target is unverified. Lens holders, battery safety volume, screw bosses, sealed cable glands, thermal/radio parts and real component STEP models have NOT been physically fitted.

Example after installing OpenSCAD:
\`\`\`sh
openscad -D 'part="body"' -o /tmp/edge-body.stl engineering/mechanical/enclosure.scad
openscad -D 'part="lid"' -o /tmp/edge-lid.stl engineering/mechanical/enclosure.scad
openscad -D 'part="exploded"' -o /tmp/edge-exploded.stl engineering/mechanical/enclosure.scad
\`\`\`

These are geometry artifacts, NOT production STL. No full assembly STEP (part dimension/clearance verified) exists yet; STEP creation requires a reviewed solid-model CAD assembly in FreeCAD/CadQuery with actual vendor models. See materials list and RELEASE_GATES.md. IP66, tropicalization, condensation and thermal constraints are currently design goals, not evidence.
