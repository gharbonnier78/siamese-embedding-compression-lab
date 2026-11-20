// Fixed wall appliance - P0 dimensional study, NOT verified enclosure/fit/IP.
$fn = 48;
part = "assembly"; // "body", "lid", "bracket", "dock", "assembly", "exploded"
W=100; H=150; D=30; // aspirational head only, mm
wall=2.8; rear=3.2; lid_t=3.0; gap=0.6; seal_w=2.3;
lens_d=16; nir_emitter_d=11; pir_d=8;

module body() {
    difference() {
      cube([W,H,D-lid_t]);
      translate([wall,wall,rear])
          cube([W-2*wall,H-2*wall,D-rear-lid_t+0.2]);
      translate([W/2-7,-0.2,9]) cube([14,wall+0.6,12]); // unsealed cable aperture TBD
    }
    // External ridges (NO through-slots); thermal conductivity unverified
    for (x=[14:12:86]) translate([x,12,-1.5]) cube([3,H-24,1.5]);
}
module lid() {
   difference() {
      cube([W,H,lid_t]);
      for(x=[31,69]) translate([x,H-31,-0.2]) cylinder(d=lens_d,h=lid_t+0.5);
      translate([W/2,H-64,-0.2]) cylinder(d=nir_emitter_d,h=lid_t+0.5);
      translate([W/2,H-92,-0.2]) cylinder(d=pir_d,h=lid_t+0.5);
      // illustrative square gasket groove. Compression/method unknown.
      difference() {
         translate([wall+gap,wall+gap,-0.2])
             cube([W-2*(wall+gap),H-2*(wall+gap),0.9]);
         translate([wall+gap+seal_w,wall+gap+seal_w,-0.3])
             cube([W-2*(wall+gap+seal_w),H-2*(wall+gap+seal_w),1.1]);
      }
   }
}
module bracket() {
   difference() {
      cube([W-18,H-22,3]);
      for(x=[20,W-38],y=[23,H-45])
         translate([x,y,-0.2]) cylinder(d=5,h=3.5);
   }
}
module dock() { // Optional protected commercial battery/PoE dock: OUTSIDE head target
   difference(){
      cube([84,90,32]);
      translate([3,3,4]) cube([78,84,29]);
   }
}
if (part=="body") body();
else if (part=="lid") lid();
else if (part=="bracket") bracket();
else if (part=="dock") dock();
else if(part=="exploded") {
    color("DimGray") body();
    color("Black") translate([0,0,D+20]) lid();
    color("Silver") translate([9,11,-15]) bracket();
    color("LightGray") translate([W+20,0,0]) dock();
} else {
    color("DimGray") body();
    color("Black") translate([0,0,D-lid_t]) lid();
    color("Silver") translate([9,11,-6]) bracket();
}
