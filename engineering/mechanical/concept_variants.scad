// Siamese Embedded A-v2 exploratory industrial geometry.
// Three distinct styles; no measured fit, ingress, gasket compression or heat.
// Fixed wall-mounted head. All dimensions in millimetres. OpenSCAD only.
$fn = 56;
style = "hull";   // hull | book | cassette
part = "assembly"; // assembly | back | front | bracket
W = 100;
H = 150;
D = 30;           // ASPIRATIONAL enclosure depth only
corner = 9;
wall = 3.0;
rear = 3.0;
optical_r = 10;
camera_y = 106;

module contour(x,y,r) {
    offset(r=r) square([x-2*r,y-2*r],center=true);
}
module enclosure_outline(z,height){
    translate([0,0,z]) linear_extrude(height=height) contour(W,H,corner);
}
module inside_volume(z,height){
    translate([0,0,z]) linear_extrude(height=height)
        contour(W-2*wall,H-2*wall,max(1,corner-wall));
}

module back() {
    difference() {
        enclosure_outline(0,D-3.0);
        inside_volume(rear,D-3.0-rear+0.2);
    }
    // External rear heat-transfer ribs only; NOT ventilation passages.
    for (x=[-33:11:33])
        translate([x,-52,-1.4]) cube([3,104,1.4],center=false);
    if(style=="book"){
        // Illustrative hinge-side geometry; seal compression is unknown.
        for (y=[-45,0,45]) translate([-W/2-3,y,9])
            rotate([90,0,0]) difference(){
                cylinder(r=5,h=13,center=true);
                cylinder(r=2.4,h=14,center=true);
            }
    }
    if(style=="cassette"){
        // Replaceable inner optical carrier shelf.
        translate([-36,22,D-5]) cube([72,46,2]);
    }
}
module optical_front() {
    difference() {
        enclosure_outline(D-3,3);
        for (x=[-19,19]) translate([x,camera_y-H/2,D-3.5])
            cylinder(r=optical_r,h=4);
        translate([0,12,D-3.5]) cylinder(r=6,h=4);
        translate([0,-24,D-3.5]) cylinder(r=6,h=4);
        // LED status aperture; seal design TODO.
        translate([-8,-48,D-3.5]) cube([16,3,4]);
    }
}
module front() {
    if(style=="cassette"){
        // Distinct removable service cassette around the optical apertures.
        color("DimGray") optical_front();
        color("Black") translate([0,27,D+0.1]) difference(){
            linear_extrude(height=2) contour(77,50,8);
            for(x=[-19,19]) translate([x,4,-0.3])
                cylinder(r=optical_r+1,h=3);
        }
    }else if(style=="book"){
        optical_front();
        // Book style seam rail and hinge labels, not functioning opening.
        translate([-W/2-1,0,D-1]) cube([2,H-20,2],center=true);
    }else {
        optical_front();
    }
}
module bracket() {
    color("Silver")
    difference(){
      translate([0,0,-6]) linear_extrude(height=3)
          contour(W-18,H-20,7);
      for(x=[-28,28], y=[-50,50])
          translate([x,y,-6.5]) cylinder(r=3.3,h=4);
    }
}
if(part=="back") back();
else if(part=="front") front();
else if(part=="bracket") bracket();
else {
    color(style=="book"?"SlateGray":style=="cassette"?"DimGray":"Gray") back();
    color("Black") front();
    bracket();
    // Optical windows and IR face are visually suggested ONLY.
    for(x=[-19,19])
      color([0.12,0.24,0.31]) translate([x,camera_y-H/2,D-2])
          cylinder(r=7,h=1);
}
