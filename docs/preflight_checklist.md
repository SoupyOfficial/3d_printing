# Preflight Checklist - Ender 3 Pro

Complete this checklist before every print session to ensure consistent results and prevent failed prints.

## Pre-Power Checklist (Physical Inspection)

### Frame and Bed
- [ ] **Bed surface clean** - No dust, fingerprints, or residue
- [ ] **Print removal tools ready** - Scraper, flush cutters available
- [ ] **Build area clear** - No obstructions around printer
- [ ] **Spool mounted securely** - Filament feeds smoothly without tangling
- [ ] **Filament end secured** - No loose end that could cause tangles

### Mechanical Systems
- [ ] **All axes move freely** - Manually test X, Y, Z movement
- [ ] **No visible damage** - Belts, rods, cables intact
- [ ] **Bowden tube seated** - Both ends fully inserted in fittings
- [ ] **Nozzle clear** - No visible buildup or partial clogs

## Power-On Sequence

### System Startup
- [ ] **Power on printer** - Allow electronics to boot completely
- [ ] **Check display function** - Screen responsive, no error messages
- [ ] **Listen for unusual sounds** - Fans running normally, no grinding
- [ ] **Verify temperatures** - Room temp readings for nozzle and bed (~20-25°C)

### Home and Movement Test
- [ ] **Home all axes (G28)** - Smooth homing without binding
- [ ] **Test X-axis travel** - Full range, no belt skipping
- [ ] **Test Y-axis travel** - Bed moves smoothly through full range  
- [ ] **Test Z-axis travel** - No binding, consistent layer height capability
- [ ] **Return to home position** - Verify accuracy of homing

## Bed Leveling (Paper Method)

### Four-Corner Level
- [ ] **Heat bed to printing temperature** (60°C for PLA)
- [ ] **Position nozzle at front-left corner** - 2-3mm from bed edge
- [ ] **Lower Z until paper drags** - Standard copy paper (0.1mm)
- [ ] **Adjust bed corner screw** - Until paper has slight drag
- [ ] **Repeat for all four corners** - Front-left, front-right, rear-right, rear-left
- [ ] **Re-check all corners** - Bed leveling affects adjacent corners
- [ ] **Test center point** - Verify level extends to middle of bed

### Z-Offset Fine Tuning
- [ ] **Load test G-code** - Use first_layer_test.gcode
- [ ] **Start test print** - Observe first few lines
- [ ] **Adjust Z-offset during print** - Use LCD controls if available
  - Lines too thin/gaps → Lower Z-offset (more squish)
  - Lines too thick/blobby → Raise Z-offset (less squish)
- [ ] **Cancel test when satisfied** - Save Z-offset setting

## Filament Preparation

### Filament Quality Check
- [ ] **Inspect filament end** - Cut clean 45° angle if needed
- [ ] **Check for moisture** - PLA should snap cleanly, not bend
- [ ] **Verify diameter consistency** - Measure at several points (~1.75mm)
- [ ] **Test bend flexibility** - Should be flexible but not brittle

### Loading and Priming
- [ ] **Heat hotend to printing temperature** (205°C for PLA+)
- [ ] **Purge old filament** - Extrude until new color/material appears
- [ ] **Load new filament** - Feed through Bowden tube until visible
- [ ] **Manual extrusion test** - Extrude 50mm, check consistency
- [ ] **Check extrusion color** - Clean color without contamination

## Calibration Verification

### Quick Function Tests
- [ ] **Extrusion multiplier check** - 100mm requested should extrude ~100mm
- [ ] **Temperature stability** - Hotend holds target temp ±2°C
- [ ] **Bed temperature stability** - Bed holds target temp ±3°C  
- [ ] **Fan operation** - Part cooling fan responds to commands

### Print Settings Review
- [ ] **Verify slicer profile loaded** - Correct material and quality settings
- [ ] **Check layer height** - Matches calibration (typically 0.2mm)
- [ ] **Confirm temperatures** - Nozzle and bed match filament requirements
- [ ] **Validate retraction settings** - Distance and speed appropriate for setup

## Final Pre-Print

### File Preparation
- [ ] **G-code file verified** - Recent slice, correct settings
- [ ] **Print time estimated** - Reasonable duration for current session
- [ ] **First layer preview** - Check slicer simulation for issues
- [ ] **Support/adhesion settings** - Appropriate for model geometry

### Environment Check
- [ ] **Room temperature stable** - Avoid drafts, temperature swings
- [ ] **Adequate lighting** - Ability to monitor first few layers
- [ ] **Emergency access** - Power switch and pause controls accessible
- [ ] **First layer monitoring plan** - Stay nearby for first 5-10 layers

## Start Print Sequence

### Launch Protocol
- [ ] **Send G-code to printer** - Via SD card or direct connection
- [ ] **Monitor homing sequence** - Verify normal startup routine
- [ ] **Observe heating phase** - Temperatures rise smoothly to targets
- [ ] **Watch purge line** - Clean extrusion, proper flow
- [ ] **Monitor first layer closely** - Adjust if needed in first 2-3 layers

### Early Print Monitoring  
- [ ] **First layer adhesion** - Lines stick without lifting
- [ ] **Layer consistency** - Even extrusion, no gaps or over-extrusion
- [ ] **Part cooling activation** - Fan starts at appropriate layer
- [ ] **No stringing on travels** - Clean movement between features

## Abort Conditions

### Stop Print Immediately If:
- **Poor bed adhesion** - Lines not sticking or lifting
- **Nozzle clogging** - Under-extrusion or no extrusion
- **Layer shifting** - Misalignment between layers
- **Thermal issues** - Temperature fluctuations or runaway
- **Mechanical binding** - Unusual sounds or jerky movement
- **Filament jam** - Grinding or skipping in extruder

## Troubleshooting Quick Reference

### First Layer Issues
- **Not sticking**: Lower Z-offset, increase bed temp, clean bed
- **Too squished**: Raise Z-offset, check bed level
- **Uneven**: Re-level bed, check for warped surface

### Extrusion Problems
- **Under-extrusion**: Check nozzle clog, increase temperature, verify flow rate
- **Over-extrusion**: Decrease temperature, reduce flow rate, check retraction

### Movement Issues  
- **Skipping**: Check belt tension, reduce acceleration, verify wiring
- **Binding**: Lubricate rods, check eccentric nuts, inspect for debris

## Success Criteria

Print is ready to continue unmonitored when:
- First 10 layers completed successfully
- Layer adhesion confirmed strong
- No mechanical issues observed
- Part cooling working properly
- Estimated time remaining reasonable for session

## Documentation

Record preflight results in `/logs/print_log.csv`:
- Date/time of preflight check
- Any adjustments made
- Calibration verification results
- Environmental conditions
- File being printed