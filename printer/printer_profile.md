# Printer Profile - Creality Ender 3 Pro

## Hardware Specifications

### Frame and Build Volume
- **Model**: Creality Ender 3 Pro
- **Build Volume**: 220 × 220 × 250 mm
- **Frame**: Aluminum extrusion with Y-axis upgrade (thicker base)
- **Assembly Date**: [Record when printer was assembled]
- **Firmware Version**: [Update with current firmware]

### Extruder System
- **Type**: Bowden extruder
- **Drive Gear**: Brass, dual-bearing design
- **Bowden Tube**: PTFE, ~42cm length
- **Nozzle**: E3D V6 compatible, 0.4mm standard
- **Nozzle Material**: Brass (stock)
- **Max Temperature**: 260°C (stock thermistor)
- **Filament Diameter**: 1.75mm

### Heated Bed
- **Type**: Magnetic flexible surface on aluminum base
- **Heating**: 12V silicone heater pad
- **Max Temperature**: 110°C (limited by PSU capacity)
- **Leveling**: Manual 4-point adjustment screws
- **Surface**: Textured PEI-coated spring steel (removable)

### Motion System
- **X-Axis**: Single rail with eccentric nuts
- **Y-Axis**: Dual rail system (Pro upgrade)
- **Z-Axis**: Dual Z-motors with lead screws
- **Stepper Motors**: NEMA 17, 1.8° step angle
- **Belts**: GT2, 6mm width
- **Linear Bearings**: V-wheel on aluminum extrusion

### Electronics
- **Mainboard**: Creality 4.2.7 (32-bit, silent drivers)
- **Stepper Drivers**: TMC2208 (silent operation)
- **Power Supply**: 24V, 350W Meanwell-style
- **Display**: LCD12864 with rotary encoder
- **SD Card**: MicroSD support for G-code files

## Calibrated Settings

### Motion Calibration
- **Steps per mm**:
  - X: 80.0
  - Y: 80.0  
  - Z: 400.0
  - E: 93.0 (stock extruder)
- **Max Feed Rates** (mm/min):
  - X: 500
  - Y: 500
  - Z: 5
  - E: 25
- **Acceleration** (mm/s²):
  - Print: 500
  - Travel: 1000
  - Retract: 500

### Temperature Calibration
- **PLA Optimal Range**: 200-215°C
- **PLA+ Optimal**: 205-220°C  
- **Bed Temperature**: 60-65°C for PLA/PLA+
- **First Layer**: Usually +5°C on bed
- **Ambient Compensation**: +5°C in winter, -5°C in summer

### Retraction (Bowden Optimized)
- **Distance**: 0.8-1.0mm (calibrated per filament)
- **Speed**: 35-45mm/s
- **Z-Hop**: 0.0mm (disabled to prevent Z-banding)
- **Minimum Travel**: 2.0mm before retract

## Modifications and Upgrades

### Completed Modifications
- [ ] **Yellow Bed Springs**: Upgraded from stock for better consistency
- [ ] **Metal Extruder**: Aluminum replacement for plastic stock unit
- [ ] **Capricorn PTFE Tube**: Higher temperature tolerance
- [ ] **BLTouch**: Auto bed leveling sensor
- [ ] **OctoPi**: Raspberry Pi with OctoPrint
- [ ] **LED Lighting**: Strip lights for better visibility
- [ ] **Enclosure**: For ABS printing and thermal stability

### Planned Upgrades
- [ ] **All-Metal Hotend**: For higher temperature materials
- [ ] **Direct Drive Conversion**: Reduce retraction needs
- [ ] **Linear Rails**: Replace V-wheels for precision
- [ ] **Dual Z-Motor**: Independent Z-axis control
- [ ] **Silent PSU Fan**: Replace with Noctua fan

## Maintenance Schedule

### Weekly (Active Use)
- [ ] **Bed Leveling Check**: 4-point paper test
- [ ] **Belt Tension**: Should be tight but not over-tensioned
- [ ] **Filament Path**: Inspect for wear, clogs, tangles
- [ ] **Print Surface**: Clean with IPA, check for damage

### Monthly
- [ ] **Eccentric Nuts**: Adjust wheel tension on all axes
- [ ] **Lubrication**: Z-axis lead screws with machine oil
- [ ] **Hot Tightening**: Re-tighten nozzle when hot
- [ ] **Wiring Inspection**: Check for wear, loose connections

### Quarterly  
- [ ] **PTFE Tube**: Replace Bowden tube
- [ ] **Belts**: Inspect for wear, replace if stretched
- [ ] **Nozzle**: Replace or clean thoroughly
- [ ] **Calibration**: Re-run full calibration sequence

## Known Issues and Solutions

### Common Problems
1. **First Layer Adhesion Issues**
   - Solution: Re-level bed, clean surface, adjust Z-offset
   - Prevention: Regular bed cleaning, proper storage of magnetic surface

2. **Extruder Clicking/Grinding**
   - Solution: Check nozzle temperature, clear partial clogs
   - Prevention: Quality filament storage, regular hot-end maintenance

3. **Layer Shifting**
   - Solution: Check belt tension, reduce print speeds
   - Prevention: Proper belt maintenance, avoid mechanical interference

4. **Z-Axis Binding**
   - Solution: Lubricate lead screws, check frame squareness
   - Prevention: Regular lubrication, avoid over-tightening

### Firmware-Specific Settings
Current firmware: **[Record current version]**
- **Thermal Runaway Protection**: Enabled
- **Mesh Bed Leveling**: [Enabled/Disabled]
- **Linear Advance**: [Enabled/Disabled, K-factor if used]
- **Junction Deviation**: [Value if using Marlin 2.x]

## Environmental Considerations

### Optimal Conditions
- **Temperature**: 20-25°C ambient
- **Humidity**: <50% RH for filament storage
- **Ventilation**: Adequate for fume extraction
- **Vibration**: Stable surface, minimal external vibration

### Seasonal Adjustments
- **Winter**: Increase bed temp by 5°C, watch for static
- **Summer**: Monitor overheating, increase cooling
- **High Humidity**: Use filament dryer more frequently

## Backup and Recovery

### Configuration Backup
- [ ] **Firmware Settings**: Export current configuration
- [ ] **Slicer Profiles**: Backup all calibrated profiles  
- [ ] **Calibration Results**: Document all successful settings
- [ ] **Modification Records**: Keep upgrade/repair history

### Emergency Procedures
- [ ] **Thermal Runaway**: Power switch location, emergency stop
- [ ] **Fire Safety**: Fire extinguisher nearby, never leave unattended
- [ ] **Power Loss Recovery**: UPS recommended for long prints
- [ ] **Mechanical Jam**: Emergency stop, safe disassembly procedure

## Contact Information

### Support Resources
- **Manual**: [Link to Creality manual]
- **Community**: r/ender3, Creality Facebook groups
- **Technical Support**: Creality official channels
- **Local Service**: [Record local technician if available]

### Parts Suppliers
- **Primary**: [Preferred supplier for replacement parts]
- **Emergency**: [Local supplier for urgent needs]  
- **Specialty**: [Supplier for upgrades/modifications]

## Change Log

| Date | Modification | Parts Used | Notes |
|------|--------------|------------|-------|
| 2024-09-21 | Initial setup | Stock configuration | Baseline documentation |
| | | | |
| | | | |

---

*Keep this profile updated with any changes, modifications, or calibration results. This serves as the definitive reference for this specific printer's configuration and performance characteristics.*