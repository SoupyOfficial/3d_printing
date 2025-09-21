# Color Swap Guide - Two-Color Printing

This guide covers two methods for achieving two-color prints with a single extruder: firmware-based filament changes (M600) and manual pause-based swaps.

## Overview

Single-extruder color swaps work by pausing the print at a predetermined layer, allowing you to manually change filament, then resuming printing. The bow tie project is designed with a natural color split at ~33% height (layer 5 at 0.2mm).

## Method 1: Firmware Filament Change (M600)

**Best for**: Printers with M600 support and filament sensors
**Advantages**: Automated pause, position parking, resume prompts
**Requirements**: Marlin firmware with M600 enabled

### M600 Command Behavior
When M600 is encountered:
1. **Pause print** and save current position
2. **Park nozzle** at preset position (usually front-left)
3. **Retract filament** automatically  
4. **Wait for user** to change filament
5. **Purge and resume** when user confirms

### Implementation Steps

#### 1. Verify M600 Support
- [ ] **Check firmware**: Send `M600` via terminal/LCD
- [ ] **Expected response**: Nozzle parks, waits for filament change
- [ ] **If unsupported**: Use Method 2 (Manual Pause) instead

#### 2. Configure M600 Settings
Add to start G-code or configure in firmware:
```gcode
M603 L0 U0     ; Disable filament load/unload lengths (manual control)
M603 E50       ; Set extrusion amount for purge (50mm)
```

#### 3. Plan Color Split
For bow tie at 0.2mm layer height:
- **Layer 5** (1.0mm height) - Creates color split at knot area
- **Layer 8** (1.6mm height) - Alternative for more base color
- **Layer 3** (0.6mm height) - Minimum for adhesion strength

### Using insert_color_swap.py Script
```bash
python slicer/postprocess/insert_color_swap.py --input bow_tie.gcode --by layer --value 5 --mode m600 --output bow_tie_swap_L5.gcode
```

## Method 2: Manual Pause (M0/M25)

**Best for**: All printers, more universal compatibility
**Advantages**: Works with any firmware, simple implementation
**Requirements**: Manual intervention, timer optional

### Pause Command Options
- **M0**: Infinite pause until user presses resume
- **M25**: Pause with optional message display
- **M1**: Pause with user confirmation prompt

### Implementation Steps

#### 1. Insert Pause Commands
Add to G-code at desired layer:
```gcode
M0 Change to second color - Press resume when ready
```

#### 2. Manual Change Process
When pause occurs:
1. **Note position**: Printer stops mid-print
2. **Heat nozzle**: Maintain printing temperature
3. **Retract filament**: Manual or via LCD (10-15mm)
4. **Remove old filament**: Pull from extruder
5. **Load new filament**: Feed until visible at nozzle  
6. **Purge old color**: Extrude until clean color appears
7. **Resume print**: Press resume button

### Using insert_color_swap.py Script
```bash
python slicer/postprocess/insert_color_swap.py --input bow_tie.gcode --by layer --value 5 --mode pause --output bow_tie_swap_L5.gcode
```

## Color Swap Timing Strategies

### By Layer Count
**Advantages**: Precise layer control
**Use when**: Known layer heights, consistent settings

```bash
# Insert at specific layer
--by layer --value 5
```

### By Height (mm)
**Advantages**: Consistent results regardless of layer height
**Use when**: Variable layer heights or multiple profiles

```bash
# Insert at specific height  
--by height --value 1.0
```

## Filament Change Best Practices

### Pre-Change Preparation
- [ ] **Prepare new filament**: Cut clean 45° angle
- [ ] **Heat management**: Keep hotend at printing temperature
- [ ] **Tool access**: Have flush cutters and needle-nose pliers ready
- [ ] **Color planning**: Visualize final result before starting

### During Change Process
- [ ] **Work quickly**: Minimize cooling time
- [ ] **Adequate purge**: Ensure complete color change (usually 50-100mm)
- [ ] **Check flow**: Verify smooth extrusion before resume
- [ ] **Clean nozzle**: Remove any purged material strings

### Post-Change Quality Check
- [ ] **First layers**: Monitor initial layers after resume closely
- [ ] **Color purity**: Verify clean color transition
- [ ] **Layer adhesion**: Ensure good bonding between color layers
- [ ] **Alignment**: Check that resume position is accurate

## Troubleshooting Color Swaps

### Common Issues and Solutions

#### Poor Layer Adhesion at Color Change
**Causes**: Nozzle cooling, contamination, incorrect temperature
**Solutions**:
- Maintain consistent temperature throughout change
- Purge more material before resume
- Clean nozzle tip before resume
- Consider temperature bump (+5°C) during change

#### Color Bleeding/Mixing
**Causes**: Insufficient purging, residual material in nozzle
**Solutions**:
- Increase purge amount (75-150mm)
- Use transition tower in slicer
- Cold pull cleaning between materials
- Consider nozzle change for drastically different materials

#### Position Loss/Layer Shift
**Causes**: Stepper timeout, manual positioning errors
**Solutions**:
- Avoid touching printer axes during change
- Enable stepper hold during pause
- Use firmware pause commands vs manual intervention
- Mark reference points before pause

#### Stringing at Resume
**Causes**: Insufficient retraction before pause, oozing during change
**Solutions**:
- Add extra retraction before pause (5-10mm)
- Prime nozzle adequately after change
- Adjust retraction settings for new material
- Use purge tower for first few layers

## Advanced Techniques

### Multi-Color Planning
1. **Design consideration**: Plan color splits during model design
2. **Layer visualization**: Use slicer preview to identify optimal split points
3. **Support strategy**: Consider how color changes affect support material
4. **Post-processing**: Plan sanding/finishing around color boundaries

### Material Transitions
When changing material types (not just colors):
- **Temperature ramping**: Gradually adjust temperature between materials
- **Purge volume**: Increase purge amount for different material types
- **Retraction adjustment**: Different materials may need different retraction
- **Cooling changes**: Adjust fan settings for new material

### Batch Processing
For multiple color-swap prints:
1. **Script automation**: Use batch processing with insert_color_swap.py
2. **Profile consistency**: Maintain consistent slicer settings
3. **Filament prep**: Pre-cut and prepare all filament changes
4. **Documentation**: Log successful settings for repeat prints

## Quality Control

### Pre-Print Checklist
- [ ] **Color swap layer verified**: Correct layer/height calculated
- [ ] **G-code modified**: Pause commands properly inserted
- [ ] **Filament prepared**: Both colors ready and accessible
- [ ] **Tools ready**: Cutters, pliers, cleaning materials available

### Post-Print Evaluation
- [ ] **Color transition quality**: Sharp, clean color boundary
- [ ] **Layer adhesion**: No delamination at color change point
- [ ] **Dimensional accuracy**: No size changes due to pause/resume
- [ ] **Surface finish**: Consistent quality before and after swap

## Documentation Template

Record in `/logs/print_log.csv`:
- **Color swap layer/height**: Where change occurred
- **Filament types**: Both original and replacement materials  
- **Pause duration**: How long change took
- **Purge amount**: Material extruded for color clearing
- **Issues encountered**: Any problems during process
- **Quality result**: Success rating and notes

## Recommended Test Sequence

1. **Practice on simple geometry**: Test color swap on basic shapes first
2. **Calibrate purge amount**: Find minimum purge for clean color change
3. **Perfect timing**: Practice quick, efficient filament changes
4. **Document successful settings**: Record working configurations
5. **Scale to complex prints**: Apply learned techniques to detailed models

This systematic approach ensures reliable, high-quality two-color prints with minimal waste and maximum success rate.