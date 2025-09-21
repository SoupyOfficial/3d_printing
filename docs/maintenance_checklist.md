# Maintenance Checklist - Ender 3 Pro

Perform these maintenance tasks regularly to ensure consistent print quality and extend printer lifespan.

## Weekly Maintenance (Active Use)

### Bed and Build Surface
- [ ] **Clean print bed with IPA** - Remove fingerprints, residue, oils
- [ ] **Inspect bed surface** - Check for scratches, warping, wear spots
- [ ] **Test bed leveling** - Quick 4-corner check with paper method
- [ ] **Check bed temperature uniformity** - Verify consistent heating

### Extruder and Hotend
- [ ] **Visual inspection of nozzle** - Look for clogs, damage, wear
- [ ] **Check filament path** - Ensure smooth feeding from spool to hotend
- [ ] **Inspect Bowden tube** - Look for kinks, cuts, or excessive wear at fittings
- [ ] **Test extrusion consistency** - Manually extrude 100mm, measure actual output

### Frame and Motion
- [ ] **Check belt tension** - X and Y belts should be tight but not over-tensioned
- [ ] **Lubricate Z-axis lead screw** - Light machine oil on threaded rod
- [ ] **Clean linear bearings** - Remove dust/debris from smooth rods
- [ ] **Check all fasteners** - Tighten any loose screws, especially on carriage

## Monthly Maintenance

### Mechanical Systems
- [ ] **Eccentric nuts adjustment** - Ensure wheels roll smoothly without wobble
  - X-axis carriage wheels (right side)
  - Y-axis bed wheels (left side) 
  - Z-axis gantry wheels
- [ ] **Belt tension calibration** - Use phone app or tension gauge if available
- [ ] **Linear bearing lubrication** - Apply thin layer of bearing grease
- [ ] **Check frame squareness** - Measure diagonals, adjust if needed

### Electrical and Electronics
- [ ] **Inspect wiring** - Look for wear, kinks, loose connections
- [ ] **Clean stepper motor fans** - Remove dust buildup
- [ ] **Check thermistor connections** - Ensure secure hotend and bed sensors
- [ ] **Test emergency stop** - Verify firmware safety features work

### Hotend Deep Clean
- [ ] **Cold pull cleaning** - Use cleaning filament or nylon at 90°C
- [ ] **Nozzle removal and inspection** - Check for internal clogs or damage
- [ ] **PTFE tube inspection** - Replace if degraded or cut at hotend end
- [ ] **Extruder gear cleaning** - Remove filament dust from drive gear teeth

## Quarterly Maintenance (Every 3 Months)

### Major Mechanical Service
- [ ] **Complete belt replacement** - If showing wear or stretching
- [ ] **Linear bearing replacement** - If showing excessive play or roughness
- [ ] **Extruder calibration** - E-steps calibration with 100mm test
- [ ] **Bed leveling sensor calibration** - If using BLTouch or similar

### Electronics Service
- [ ] **Firmware backup** - Save current settings before any updates
- [ ] **SD card health check** - Test card, defragment if needed
- [ ] **Power supply inspection** - Check fan operation, loose connections
- [ ] **Stepper driver temperature check** - Ensure adequate cooling

### Deep Cleaning
- [ ] **Complete disassembly cleaning** - Remove all panels for thorough clean
- [ ] **Bearing race cleaning** - Deep clean all linear motion components
- [ ] **Electronics housing cleaning** - Remove dust from control box
- [ ] **Cable management review** - Reorganize/secure any loose wiring

## As-Needed Maintenance

### Filament-Related
- [ ] **Nozzle replacement** - When switching materials or showing wear
- [ ] **PTFE tube replacement** - Every 6-12 months or when degraded
- [ ] **Extruder tension adjustment** - If filament grinding occurs
- [ ] **Hot tightening of nozzle** - After temperature changes or leaks

### Calibration Events
- [ ] **Full re-calibration** - After any major maintenance
- [ ] **PID tuning** - When changing nozzles or thermistors
- [ ] **Z-offset recalibration** - After bed or nozzle changes
- [ ] **Flow rate recalibration** - When switching filament types

## Tools Required

### Basic Tools
- Hex keys: 1.5mm, 2mm, 2.5mm, 3mm, 4mm, 5mm
- Screwdrivers: Phillips #1, #2; Flathead small/medium
- Needle-nose pliers
- Wire cutters/strippers
- Digital calipers
- Feeler gauges or paper (0.1mm)

### Specialized Tools  
- Nozzle wrench (7mm)
- Tube cutter (for PTFE)
- Thread locker (blue)
- Super lube or bearing grease
- 99% isopropyl alcohol
- Lint-free cloths
- Compressed air or brush

## Maintenance Schedule Template

Create a schedule based on print volume:
- **Light use** (0-20 hours/week): Monthly checks, quarterly deep service
- **Moderate use** (20-40 hours/week): Bi-weekly checks, monthly deep service  
- **Heavy use** (40+ hours/week): Weekly checks, monthly full service

## Red Flags - Stop and Service Immediately

- **Grinding sounds** from extruder or axes
- **Visible smoke** or burning smells  
- **Loose bed or significant wobble** during printing
- **Inconsistent extrusion** or under-extrusion issues
- **Layer shifting** or positional accuracy problems
- **Thermal runaway errors** or temperature fluctuations

## Documentation

Record all maintenance in `/logs/print_log.csv`:
- Date and time of service
- Tasks completed  
- Parts replaced
- Settings changed
- Next service due date
- Any observations or concerns