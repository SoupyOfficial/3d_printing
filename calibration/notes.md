# Calibration Test Notes - Ender 3 Pro

## Overview
This document explains each calibration test, what success looks like, and how to interpret results.

## First Layer Test
**File**: `first_layer_test.gcode`
**Purpose**: Verify bed leveling and Z-offset calibration

### Success Criteria
- **Even extrusion**: All lines should have consistent width
- **Proper adhesion**: Lines stick to bed without lifting at corners  
- **No gaps or overlaps**: Adjacent lines should barely touch without gaps
- **Surface finish**: Smooth top surface, not glossy (over-squished) or rough (under-squished)

### Measurements
- **Line width**: Should measure ~0.48mm with 0.4mm nozzle
- **Layer height**: Should measure 0.2mm when scraped with fingernail

### Troubleshooting
- **Lines too thin/gaps**: Lower Z-offset by 0.05mm increments
- **Lines too wide/squished**: Raise Z-offset by 0.05mm increments  
- **Poor adhesion**: Check bed temperature (60°C), clean with IPA
- **Uneven lines**: Re-level bed, check for warped bed

---

## Temperature Tower (195°C-220°C)
**File**: `temp_tower_pla_195-220C.gcode`
**Purpose**: Find optimal nozzle temperature for your specific PLA filament

### Success Criteria
Look for the temperature section with:
- **Best layer adhesion**: No layer separation or splitting
- **Minimal stringing**: Clean travels between sections
- **Good surface finish**: Smooth walls without over-extrusion blobs
- **Sharp corners**: Crisp geometry without rounding

### Measurements
Record the optimal temperature range where all criteria are met.

### Typical Results for PLA+
- **195°C**: May show layer adhesion issues, under-extrusion
- **200-210°C**: Usually optimal range for most PLA+
- **215-220°C**: May show stringing, over-extrusion, poor overhangs

### Recording Results
Log optimal temperature in `/logs/print_log.csv` and update slicer profiles.

---

## Retraction Tower (0.4mm-1.2mm)
**File**: `retraction_tower.gcode` 
**Purpose**: Optimize retraction distance for Bowden extruder

### Success Criteria
Find the retraction distance with:
- **Minimal stringing**: Clean travels with no plastic strings
- **No under-extrusion**: No gaps after retraction/unretraction
- **Good bridging**: Overhangs print cleanly

### Measurements
- **0.4-0.6mm**: Typical for direct drive (may show stringing on Bowden)
- **0.8-1.0mm**: Usually optimal for Bowden extruders like Ender 3 Pro
- **1.2mm+**: May cause excessive wear, grinding, or under-extrusion

### Recording Results
Update retraction settings in slicer profiles with optimal distance.

---

## Flow Rate Cube  
**File**: `flow_cube_100pct.gcode`
**Purpose**: Calibrate extrusion multiplier/flow rate

### Success Criteria
Measure wall thickness with calipers:
- **Target**: 0.40mm walls with 0.4mm nozzle
- **Acceptable range**: 0.38-0.42mm

### Calculations
Flow Rate Adjustment = (Target Thickness / Measured Thickness) × Current Flow Rate

**Example**: 
- Measured: 0.45mm walls
- Target: 0.40mm walls  
- Current flow: 100%
- New flow = (0.40 ÷ 0.45) × 100% = 89%

### Recording Results
Update extrusion multiplier in slicer profiles and log in print log.

---

## XYZ Calibration Cube
**File**: `xyz_calibration_cube.gcode`
**Purpose**: Verify dimensional accuracy

### Success Criteria
Measure with calipers - all dimensions should be 20.00mm ± 0.1mm:
- **X-axis**: Width measurement
- **Y-axis**: Depth measurement  
- **Z-axis**: Height measurement

### Troubleshooting
- **Undersized**: Check belt tension, increase flow rate slightly
- **Oversized**: Decrease flow rate, check for over-extrusion
- **Z-axis short**: Check layer height calibration, Z-steps
- **Corners rounded**: Lower temperature, increase cooling

### Recording Results
Document dimensional accuracy in print log. Consistent results indicate well-calibrated printer.

---

## General Calibration Workflow

1. **Start with first layer test** - Foundation for all other tests
2. **Run temperature tower** - Critical for layer adhesion and quality
3. **Test retraction** - Eliminates stringing issues  
4. **Calibrate flow rate** - Ensures accurate extrusion
5. **Verify with XYZ cube** - Confirms overall dimensional accuracy

## Success Documentation

Record all successful settings in:
- `/logs/print_log.csv` - Date, settings, results
- Update slicer profiles in `/slicer/profiles/`
- Note any filament-specific variations

## Re-calibration Triggers

Re-run calibration tests when:
- Switching filament brands/types
- After major maintenance (nozzle change, extruder work)
- Print quality issues appear
- After firmware updates
- Seasonal temperature changes affecting filament behavior