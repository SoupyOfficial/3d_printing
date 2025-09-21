# Bed Leveling Map - Ender 3 Pro

This document records bed leveling measurements and adjustments to maintain consistent first layer quality.

## Bed Leveling Grid

Standard 4-point leveling positions (measured from front-left corner):

```
Rear Left        Rear Right
(30, 190)        (190, 190)
    [C]             [D]
     
     
    [E] Center (110, 110)
     
     
    [A]             [B]  
(30, 30)         (190, 30)
Front Left       Front Right
```

## Current Bed Level Status

**Last Leveled**: [Date]  
**Method**: Paper drag test (0.1mm standard copy paper)  
**Bed Temperature**: 60°C  
**Nozzle Temperature**: Room temperature  

### Corner Measurements

| Position | Z-Offset | Screw Turns | Paper Drag | Notes |
|----------|----------|-------------|------------|-------|
| A (Front Left) | 0.00mm | Baseline | Slight drag | Reference corner |
| B (Front Right) | +0.05mm | 1/4 turn CCW | Slight drag | Slightly high |
| C (Rear Left) | -0.02mm | 1/8 turn CW | Slight drag | Slightly low |
| D (Rear Right) | +0.03mm | 1/8 turn CCW | Slight drag | Slightly high |
| E (Center) | +0.01mm | N/A | Slight drag | Good center |

**Deviation Range**: 0.07mm (Acceptable: <0.1mm)

## Bed Warping Analysis

### Height Map (relative to front-left corner)

```
   0    50   100  150  200 (X-axis, mm)
0  0.00 +0.01 +0.02 +0.03 +0.05  200
50 -0.01 +0.00 +0.01 +0.02 +0.04  150
100-0.02 -0.01 +0.01 +0.02 +0.03  100 (Y-axis)
150-0.02 -0.01 +0.00 +0.02 +0.03   50
200-0.02 +0.00 +0.01 +0.02 +0.03    0
```

**Warping Pattern**: Slight bow with center slightly low, right side consistently high

## BLTouch/Auto Leveling Data

*Note: Fill this section if BLTouch or similar auto-leveling sensor is installed*

### Mesh Bed Leveling Results
**Date**: [When mesh was generated]  
**Grid Size**: 3x3 / 5x5 / 9x9  
**Probe Points**: [Number of measurement points]

```
Mesh Level Results (example format):
    0     1     2     3     4
0  +0.12 +0.08 +0.05 +0.08 +0.12
1  +0.05 +0.02 -0.01 +0.02 +0.05
2  -0.02 -0.05 -0.08 -0.05 -0.02
3  +0.05 +0.02 -0.01 +0.02 +0.05
4  +0.12 +0.08 +0.05 +0.08 +0.12
```

**Standard Deviation**: [Value]mm  
**Max Deviation**: [Value]mm  
**Mesh Active**: Yes/No

## Leveling History

### Recent Adjustments

| Date | Reason | Method | Adjustments Made | Result |
|------|--------|--------|------------------|--------|
| 2024-09-21 | Initial setup | Paper test | Baseline leveling | Good first layers |
| | | | | |
| | | | | |

### Bed Surface Condition

**Surface Type**: Magnetic PEI spring steel  
**Condition**: Good / Fair / Poor  
**Cleaning Method**: IPA wipes  
**Wear Areas**: [Note any worn spots]  
**Replacement Date**: [When surface was last replaced]

## Environmental Factors

### Temperature Effects
- **Thermal Expansion**: Bed expands ~0.1mm per 50°C temperature rise
- **Ambient Temperature**: Note room temperature during leveling
- **Seasonal Variation**: Document any seasonal drift patterns

### Mechanical Factors
- **Frame Settlement**: New printers may settle in first months
- **Transport**: Re-level after moving printer
- **Maintenance**: Level after any bed or Z-axis work

## Troubleshooting Notes

### Common Issues and Solutions

**Poor First Layer Adhesion**:
- Check: Corner level accuracy, bed cleanliness, Z-offset
- Solution: Re-level affected corners, clean with IPA, adjust Z-offset

**First Layer Too Thick/Thin**:
- Check: Global Z-offset, nozzle height consistency
- Solution: Adjust Z-offset globally, verify nozzle condition

**Layer Height Variation Across Bed**:
- Check: Bed warping, loose bed screws, frame squareness
- Solution: Shim bed if warped, tighten hardware, square frame

**Inconsistent Between Sessions**:
- Check: Bed screw tightness, thermal expansion effects
- Solution: Lock nuts on adjustment screws, consistent temperatures

## Maintenance Schedule

### Weekly (Active Use)
- [ ] **Quick Level Check**: Test all 4 corners with paper
- [ ] **Center Point Check**: Verify center height consistency
- [ ] **Visual Inspection**: Check for bed surface damage

### Monthly
- [ ] **Full Re-level**: Complete 4-corner adjustment procedure
- [ ] **Mesh Update**: Regenerate auto-leveling mesh if equipped
- [ ] **Hardware Check**: Tighten bed adjustment screws

### As Needed
- [ ] **After Transport**: Always re-level after moving printer
- [ ] **After Maintenance**: Re-level after any Z-axis or bed work
- [ ] **Surface Replacement**: Full re-calibration with new print surface

## Tools Required

### Basic Leveling
- Standard copy paper (0.1mm thickness)
- Flashlight or good lighting
- Patience and steady hands

### Advanced Leveling  
- Feeler gauges (0.05-0.2mm range)
- Dial indicator with magnetic base
- BLTouch or similar probe (if installed)
- Digital calipers for verification

## Success Criteria

**Well-Leveled Bed Indicators**:
- [ ] Paper drag consistent across all 4 corners
- [ ] First layer lines uniform width and height
- [ ] No gaps or over-squashing in first layer
- [ ] Good adhesion without excessive force to remove prints
- [ ] Center point within 0.05mm of corners

**Warning Signs**:
- [ ] Paper drag varies significantly between corners
- [ ] First layer shows thickness variation
- [ ] Poor adhesion in specific areas
- [ ] Difficulty removing prints in some areas
- [ ] Nozzle strikes bed surface during printing

## Notes and Observations

**Bed Characteristics**:
- This bed tends to run slightly high on the right side
- Center point typically measures 0.01-0.02mm high relative to corners
- Thermal expansion is minimal with PEI surface
- Surface requires IPA cleaning every 5-10 prints for optimal adhesion

**Filament-Specific Notes**:
- PLA: Works well with current level settings
- PLA+: May need slightly closer first layer (-0.01mm Z-offset)
- PETG: Requires backing off Z-offset (+0.05mm) to prevent surface damage

---

*Update this document whenever bed leveling is performed. Consistent documentation helps identify trends and predict maintenance needs.*