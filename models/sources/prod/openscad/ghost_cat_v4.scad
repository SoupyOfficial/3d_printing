
// Ghost Cat v4 – scalloped drape, correct placements, OpenSCAD-safe geometry
// Export: F6 -> STL
// Axes: +Z up, FRONT = -Y

// ---------------- Params ----------------
ghost_h        = 50;
r_top          = 15;
r_bot          = 23;
hem_round      = 7;
wall_thick     = 1.8;

scallops_n     = 8;
scallop_rad    = 7;
scallop_h      = 8;

eye_bump_r     = 2.6;
eye_h          = 22;
eye_lr         = 8.5;

ear_h          = 8;
ear_base_w     = 10;
ear_base_d     = 6;

paw_r          = 4.6;
paw_h          = 6;
paw_lr         = 9.5;
paw_fwd        = 1.0;

toe_r          = 1.5;

tail_r         = 3.6;
tail_len       = 26;
tail_lift      = 8;

lift_z         = 0.2;

$fn = 96;

// --------------- Helpers ----------------
module top_dome_frustum(h, r1, r2, round_r){
    union(){
        translate([0,0,lift_z])
            cylinder(h=h - round_r, r1=r1, r2=r2);
        translate([0,0,lift_z + h - round_r])
            sphere(r=round_r);
    }
}

module scallop_cutter(r_at_base, bite_r, bite_h, n){
    for(i=[0:n-1]){
        rotate([0,0,i*360/n])
            translate([r_at_base,0,-1])
                cylinder(h=bite_h+2, r=bite_r);
    }
}

module sheet_shell(){
    difference(){
        // OUTER with scallops
        difference(){
            top_dome_frustum(ghost_h, r_top, r_bot, hem_round);
            scallop_cutter(r_bot-0.4, scallop_rad, scallop_h, scallops_n);
        }
        // INNER (hollow) with matching scallops
        translate([0,0,wall_thick])
            difference(){
                top_dome_frustum(ghost_h,
                                 max(1,r_top-wall_thick),
                                 max(1,r_bot-wall_thick),
                                 max(0.1, hem_round-wall_thick));
                scallop_cutter(max(1,r_bot-wall_thick)-0.4,
                               max(1,scallop_rad-wall_thick*0.9),
                               max(1,scallop_h-1.0),
                               scallops_n);
            }
        // open bottom
        translate([0,0,-ghost_h]) cylinder(h=ghost_h, r=r_bot*1.2);
    }
}

module ear(){
    minkowski(){
        linear_extrude(height=ear_h)
            polygon(points=[[ -ear_base_w/2, 0],
                            [  ear_base_w/2, 0],
                            [ 0, ear_base_d ]]);
        sphere(0.7);
    }
}

module paw(){
    union(){
        cylinder(h=paw_h, r=paw_r);
        translate([ paw_r*0.8, 0, paw_h-0.8]) sphere(r=toe_r);
        translate([-paw_r*0.8, 0, paw_h-0.8]) sphere(r=toe_r);
        translate([0, paw_r*0.8, paw_h-0.8]) sphere(r=toe_r);
    }
}

module tail(){
    union(){
        rotate([0,90,0]) cylinder(h=tail_len*0.55, r=tail_r);
        translate([tail_len*0.55,0,tail_lift]) rotate([18,90,0])
            cylinder(h=tail_len*0.45, r1=tail_r, r2=tail_r*0.6);
    }
}

// --------------- Assembly ----------------
module ghost_cat(){
    // sheet
    sheet_shell();

    // eye bumps on the FRONT (-Y)
    for(s=[-1,1])
        translate([s*eye_lr, -(r_bot-0.6), lift_z+eye_h])
            sphere(r=eye_bump_r);

    // ears leaning forward
    ear_z = lift_z + ghost_h - hem_round + 0.8;
    translate([-10, -2, ear_z]) rotate([0,0,20]) ear();
    translate([ 10, -2, ear_z]) rotate([0,0,-20]) ear();

    // paws in front
    translate([-paw_lr, -(r_bot + paw_r*0.2) - paw_fwd, 0]) paw();
    translate([ paw_lr, -(r_bot + paw_r*0.2) - paw_fwd, 0]) paw();

    // tail behind
    translate([0, r_bot + 0.8, 0]) tail();
}

ghost_cat();
