
// Ghost Cat - parametric OpenSCAD
// Export: Design -> Render (F6), then File -> Export -> STL
// Units: millimeters

// ------------ Params -------------
ghost_height = 48;        // overall height
sheet_radius = 22;        // radius of the draped "sheet"
sheet_round = 4;          // fillet on sheet
sheet_thickness = 1.6;    // shell thickness
ear_height = 8;
ear_base = [8, 5];        // width x depth of ear base
eye_radius = 2.1;         // eye cutout radius
eye_offset = [8, 13];     // [left-right, up] from center
paw_radius = 4.2;
paw_height = 5;
toe_radius = 1.4;
tail_radius = 3.3;
tail_len = 22;
tail_up = 6;              // how high tail lifts from floor
lift = 0.4;               // Z-lift so it prints clean

$fn = 96;

// ------------ Modules -------------

module rounded_cylinder(h, r, fillet) {
    minkowski() {
        cylinder(h=h - 2*fillet, r=r - fillet, center=false);
        sphere(fillet);
    }
}

module ear() {
    // a rounded triangular prism ear
    rotate([0,0,0])
    minkowski() {
        linear_extrude(height=ear_height)
            polygon(points=[[ -ear_base[0]/2, 0],
                            [  ear_base[0]/2, 0],
                            [ 0, ear_base[1]] ]);
        sphere(0.8);
    }
}

module paw() {
    // single paw with 3 tiny toes
    union() {
        cylinder(h=paw_height, r=paw_radius, center=false);
        // toes
        translate([ paw_radius, 0, paw_height-0.8]) sphere(toe_radius);
        translate([-paw_radius, 0, paw_height-0.8]) sphere(toe_radius);
        translate([0, paw_radius, paw_height-0.8]) sphere(toe_radius);
    }
}

module tail() {
    // gentle S curve tail built from rotated cylinders
    union() {
        translate([0,0,0]) rotate([0,90,0]) cylinder(h=tail_len*0.55, r=tail_radius);
        translate([tail_len*0.55,0,tail_up]) rotate([20,90,0]) cylinder(h=tail_len*0.45, r1=tail_radius, r2=tail_radius*0.6);
    }
}

module sheet_shell() {
    // Outer rounded sheet
    difference() {
        translate([0,0,lift]) rounded_cylinder(h=ghost_height, r=sheet_radius, fillet=sheet_round);
        // hollow it
        translate([0,0,lift+sheet_thickness]) rounded_cylinder(h=ghost_height, r=sheet_radius - sheet_thickness, fillet=max(0.01, sheet_round - sheet_thickness));
        // bottom opening (bigger than paws)
        translate([0,0,-ghost_height]) cylinder(h=ghost_height, r=sheet_radius*1.05);
        // eye holes
        for (sx=[-1,1]) translate([sx*eye_offset[0], sheet_radius-2, lift+eye_offset[1]]) rotate([90,0,0]) cylinder(h=6, r=eye_radius);
    }
}

module ghost_cat() {
    union() {
        // sheet
        color("white") sheet_shell();
        // ears
        translate([ -10, 0, lift + ghost_height - ear_height*0.4]) rotate([0,0,25]) ear();
        translate([  10, 0, lift + ghost_height - ear_height*0.4]) rotate([0,0,-25]) ear();

        // paws front
        translate([-10, -sheet_radius+2, 0]) paw();
        translate([ 10, -sheet_radius+2, 0]) paw();

        // tail back
        translate([0, sheet_radius-2, 0]) tail();
    }
}

ghost_cat();
