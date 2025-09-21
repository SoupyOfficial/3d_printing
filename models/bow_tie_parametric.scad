// Parametric Bow Tie for Two-Color 3D Printing
// Designed for Ender 3 Pro with 0.4mm nozzle
// Conservative width design for reliable printing

// === MAIN PARAMETERS ===
bow_width_mm = 110;        // Conservative width for most bow ties
bow_height_mm = 55;        // Standard height
bow_thickness_mm = 3.0;    // Thick enough for structure, thin enough for comfort
center_knot_width_mm = 20; // Width of center knot band
strap_slot_width_mm = 22;  // Width of strap opening (allows 20mm strap + tolerance)
strap_slot_height_mm = 2.5; // Height of strap opening

// === DERIVED PARAMETERS ===
wing_width = (bow_width_mm - center_knot_width_mm) / 2;
wing_taper_start = bow_height_mm * 0.3;  // Where wings start tapering
wing_taper_end = bow_height_mm * 0.8;    // Where wings reach minimum width
min_wing_width = wing_width * 0.6;       // Minimum wing width at taper

// === RENDERING SETTINGS ===
$fn = 64;  // Smooth curves for final render

// === MAIN MODULE ===
module bow_tie() {
    difference() {
        union() {
            // Main bow wings with taper
            for (side = [-1, 1]) {
                translate([side * (center_knot_width_mm/2 + wing_width/2), 0, 0]) {
                    bow_wing();
                }
            }
            
            // Center knot band
            translate([0, 0, bow_thickness_mm/2])
                cube([center_knot_width_mm, bow_height_mm, bow_thickness_mm], center=true);
        }
        
        // Strap slot through center
        translate([0, 0, bow_thickness_mm/2])
            cube([strap_slot_width_mm, strap_slot_height_mm, bow_thickness_mm + 0.1], center=true);
    }
}

// === BOW WING MODULE ===
module bow_wing() {
    translate([0, 0, bow_thickness_mm/2]) {
        linear_extrude(height=bow_thickness_mm, center=true) {
            polygon(points=[
                // Bottom edge of wing (full width)
                [-wing_width/2, -bow_height_mm/2],
                [wing_width/2, -bow_height_mm/2],
                
                // Transition to taper start
                [wing_width/2, -wing_taper_start/2],
                
                // Taper to minimum width
                [min_wing_width/2, -wing_taper_end/2],
                [min_wing_width/2, wing_taper_end/2],
                
                // Taper back to full width
                [wing_width/2, wing_taper_start/2],
                
                // Top edge of wing (full width)  
                [wing_width/2, bow_height_mm/2],
                [-wing_width/2, bow_height_mm/2],
                
                // Repeat taper on left side
                [-wing_width/2, wing_taper_start/2],
                [-min_wing_width/2, wing_taper_end/2],
                [-min_wing_width/2, -wing_taper_end/2],
                [-wing_width/2, -wing_taper_start/2]
            ]);
        }
    }
}

// === HELPER MODULE FOR COLOR SWAP VISUALIZATION ===
module bow_tie_with_color_layers() {
    color("red") {
        intersection() {
            bow_tie();
            translate([0, 0, bow_thickness_mm * 0.33/2])
                cube([bow_width_mm + 10, bow_height_mm + 10, bow_thickness_mm * 0.33], center=true);
        }
    }
    
    color("blue") {
        difference() {
            bow_tie();
            translate([0, 0, bow_thickness_mm * 0.33/2])
                cube([bow_width_mm + 10, bow_height_mm + 10, bow_thickness_mm * 0.33], center=true);
        }
    }
}

// === MAIN RENDER ===
// Uncomment the version you want to render:

// Standard single-color version
bow_tie();

// Color visualization version (uncomment to see color split)
//bow_tie_with_color_layers();

// === INFORMATION OUTPUT ===
echo("=== BOW TIE PARAMETERS ===");
echo(str("Bow Width: ", bow_width_mm, "mm"));
echo(str("Bow Height: ", bow_height_mm, "mm"));  
echo(str("Thickness: ", bow_thickness_mm, "mm"));
echo(str("Center Knot Width: ", center_knot_width_mm, "mm"));
echo(str("Strap Slot: ", strap_slot_width_mm, "mm x ", strap_slot_height_mm, "mm"));
echo(str("Wing Width: ", wing_width, "mm"));
echo(str("Minimum Wing Width: ", min_wing_width, "mm"));

// Calculate approximate color swap layer
color_swap_height = bow_thickness_mm * 0.33;  // 33% through print
layer_height = 0.2;  // Assumed layer height
color_swap_layer = ceil(color_swap_height / layer_height);
echo(str("Suggested color swap at layer: ", color_swap_layer, " (", color_swap_height, "mm height)"));