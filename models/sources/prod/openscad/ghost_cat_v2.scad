
// Ghost Cat v2 - corrected placements
// Export: F6 -> STL
// Units: mm

// ------------ Params -------------
ghost_height = 52;        // overall height
sheet_radius = 22;        // outer radius
sheet_round  = 6;         // dome cap radius
sheet_thickness = 1.8;    // wall thickness
ear_height = 8;
ear_base_w = 9;
ear_base_d = 6;
eye_radius = 2.2;
eye_up = 18;              // from base
eye_lr = 8.5;             // from center X
paw_radius = 4.5;
paw_height = 6;
toe_radius = 1.6;
tail_radius = 3.4;
tail_len = 24;
tail_up = 7;
lift = 0.2;

$fn = 96;

// ------------ Helpers -------------
module dome_cup(outer=true){
    // cylinder with a domed top - used for outer and inner shells
    r = sheet_radius - (outer?0:sheet_thickness);
    h = ghost_height - (outer?0:sheet_thickness);
    // body
    union(){
        translate([0,0,lift]) cylinder(h=h - sheet_round, r=r);
        // dome
        translate([0,0,lift + h - sheet_round])
            translate([0,0,0]) sphere(r=sheet_round);
    }
}

module ear(){
    minkowski(){
        linear_extrude(height=ear_height)
            polygon(points=[[ -ear_base_w/2, 0],
                            [  ear_base_w/2, 0],
                            [ 0, ear_base_d ]]);
        sphere(0.7);
    }
}

module paw(){
    union(){
        cylinder(h=paw_height, r=paw_radius);
        translate([ paw_radius*0.8, 0, paw_height-0.9]) sphere(r=toe_radius);
        translate([-paw_radius*0.8, 0, paw_height-0.9]) sphere(r=toe_radius);
        translate([0, paw_radius*0.8, paw_height-0.9]) sphere(r=toe_radius);
    }
}

module tail(){
    union(){
        rotate([0,90,0]) cylinder(h=tail_len*0.55, r=tail_radius);
        translate([tail_len*0.55,0,tail_up]) rotate([20,90,0])
            cylinder(h=tail_len*0.45, r1=tail_radius, r2=tail_radius*0.6);
    }
}

module sheet_shell(){
    difference(){
        dome_cup(true);
        dome_cup(false);
        // bottom opening
        translate([0,0,-ghost_height]) cylinder(h=ghost_height, r=sheet_radius*1.05);
        // eyes
        for(s=[-1,1])
            translate([s*eye_lr, sheet_radius+0.1, lift+eye_up])
                rotate([90,0,0]) cylinder(h=4, r=eye_radius);
    }
}

module ghost_cat(){
    union(){
        // sheet
        sheet_shell();

        // ears: sit on dome just outside the wall
        ear_z = lift + ghost_height - sheet_round + 1;
        translate([-10, 0, ear_z]) rotate([0,0,20]) ear();
        translate([ 10, 0, ear_z]) rotate([0,0,-20]) ear();

        // front paws: outside the sheet, touching ground
        translate([-9, -(sheet_radius + paw_radius - 0.6), 0]) paw();
        translate([ 9, -(sheet_radius + paw_radius - 0.6), 0]) paw();

        // tail: behind
        translate([0, sheet_radius + 0.6, 0]) tail();
    }
}

ghost_cat();
