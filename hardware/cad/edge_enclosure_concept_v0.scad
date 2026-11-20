// Exploratory enclosure concept, NOT DIMENSIONALLY VERIFIED OR PRINT-READY.
// Radxa ROCK 5B board envelope is 100x75 mm according to official docs.
// All camera, mounting, cutout, thermal, wiring and battery details are TBD.
// Inspect with OpenSCAD (part="assembly") or preview "base"/"lid" separately.
// https://docs.radxa.com/en/rock5/rock5b/getting-started/introduction

$fn = 40;
part = "assembly";     // [assembly,base,lid]
show_board_envelope = true;

// Deliberately oversized discovery prototype (mm) -- NOT a final dimension.
outer_x = 165;
outer_y = 120;
outer_z = 55;
wall = 3;
floor_t = 4;
lid_t = 3;

board_x = 100;
board_y = 75;
board_z = 20;          // tentative component-height envelope; measure actual
board_base_z = 9;      // reference only, no mechanical mounts fabricated

rgb_opening = 13;      // nominal camera aperture, NOT optically qualified
nir_opening = 13;
opening_pitch = 36;
opening_height = 33;

assert(outer_x > board_x + 2*wall + 10, "X clearance too small");
assert(outer_y > board_y + 2*wall + 10, "Y clearance too small");
assert(outer_z > board_base_z + board_z + lid_t + 3, "Z clearance too small");
assert(wall >= 2 && floor_t >= 3, "Unsupported wall/floor sizing");

module camera_window(xpos) {
    translate([xpos-rgb_opening/2,-0.5,opening_height-rgb_opening/2])
        cube([rgb_opening,wall+1, rgb_opening]);
}

module base_shell() {
    difference() {
        cube([outer_x,outer_y,outer_z-lid_t]);
        translate([wall,wall,floor_t])
            cube([outer_x-2*wall,outer_y-2*wall,outer_z-floor_t-lid_t+0.2]);
        // Camera cutouts: actual camera location, NIR windows and safety TBD
        camera_window(outer_x/2-opening_pitch/2);
        camera_window(outer_x/2+opening_pitch/2);
        // Rear connector clearance is only a broad assembly placeholder.
        translate([outer_x/2-27,outer_y-wall-0.5,12])
            cube([54,wall+1,22]);
    }
}

module top_lid() {
    // Plain cap, no snaps, screws, weather seal or fitting lips.
    cube([outer_x,outer_y,lid_t]);
}

module placeholder_board() {
    color([0,0.5,0.2,0.45])
        translate([(outer_x-board_x)/2,(outer_y-board_y)/2,board_base_z])
        cube([board_x,board_y,board_z]);
}

if (part == "base") base_shell();
else if (part == "lid") top_lid();
else {
    color([0.85,0.85,0.88,0.35]) base_shell();
    color([0.65,0.65,0.75,0.45]) translate([0,0,outer_z-lid_t]) top_lid();
    if (show_board_envelope) placeholder_board();
}
