# 3D Printing Workspace - Ender 3 Pro Bow Tie Project

A complete, reproducible 3D printing workspace for designing, slicing, and producing two-color bow ties on a Creality Ender 3 Pro. Includes parametric models, calibrated profiles, automated workflows, and comprehensive documentation.

## 🎯 Quick Start

### Prerequisites
1. **Ender 3 Pro** with stock 0.4mm nozzle
2. **PLA+ filament** (two colors)
3. **Windows 11** (with optional WSL2 support)

### Get Printing in 5 Steps
1. **Run first layer test**: `calibration/first_layer_test.gcode`
2. **Run temperature tower**: `calibration/temp_tower_pla_195-220C.gcode` 
3. **Update profile with optimal temperature**
4. **Slice bow tie**: Use VS Code Task `slice:prusa`
5. **Add color swap**: Use VS Code Task `post:color-swap-m600`

## 🛠️ Required Tools

### Essential Software
- **[OpenSCAD](https://openscad.org/downloads.html)** - Parametric model editing
- **[PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/)** - Primary slicer (or SuperSlicer/OrcaSlicer)
- **[Python 3.12+](https://www.python.org/downloads/)** - Automation scripts
- **[VS Code](https://code.visualstudio.com/)** - Development environment (recommended)

### Python Dependencies
```bash
pip install pyyaml
```

### Optional Tools
- **[CuraEngine](https://github.com/Ultimaker/CuraEngine)** - Alternative slicer
- **[Git LFS](https://git-lfs.github.io/)** - Large file version control
- **Creality Filament Dryer** - Moisture control

### Installation Checklist
- [ ] Add OpenSCAD to Windows PATH
- [ ] Add PrusaSlicer to Windows PATH  
- [ ] Install Python and verify with `python --version`
- [ ] Install PyYAML with `pip install pyyaml`
- [ ] Clone/download this repository

## 📁 Repository Structure

```
3d_printing/
├─ README.md                    # This file
├─ .gitignore                   # Git exclusions
├─ .gitattributes              # Git LFS configuration
├─ docs/                       # Comprehensive documentation
│  ├─ maintenance_checklist.md
│  ├─ preflight_checklist.md
│  ├─ extruder_clicking_troubleshooting.md
│  ├─ color_swap_guide.md
│  └─ slicer_cli_guide.md
├─ models/                     # Parametric design files
│  ├─ bow_tie_parametric.scad  # Fully parameterized model
│  └─ bow_tie_reference.stl    # Default export
├─ slicer/                     # Slicing configuration
│  ├─ profiles/                # Calibrated printer profiles
│  ├─ project/                 # 3MF project files
│  └─ postprocess/             # Automation scripts
├─ calibration/                # Ready-to-print test files
│  ├─ first_layer_test.gcode
│  ├─ temp_tower_pla_195-220C.gcode
│  ├─ retraction_tower.gcode
│  ├─ flow_cube_100pct.gcode
│  ├─ xyz_calibration_cube.gcode
│  └─ notes.md                 # Calibration instructions
├─ printer/                    # Printer-specific config
│  ├─ printer_profile.md       # Hardware documentation
│  └─ bed_leveling_map.md      # Leveling records
├─ gcode/                      # Generated print files
│  ├─ tests/                   # Calibration outputs
│  └─ production/              # Final print files
├─ logs/                       # Print history and results
│  └─ print_log.csv           # Structured logging
├─ tools/                      # VS Code integration
│  └─ tasks.json              # Automated workflows
└─ manifests/                  # Build metadata
   └─ bow_tie.slice.yml       # Print specifications
```

## 🎮 VS Code Integration

This workspace includes pre-configured VS Code tasks for automated workflows:

### Available Tasks (`Ctrl+Shift+P` → "Tasks: Run Task")

**Build Tasks**:
- `build:model` - Export STL from OpenSCAD
- `slice:prusa` - Slice with PrusaSlicer 
- `slice:cura` - Slice with CuraEngine
- `build:complete-pipeline` - Full automated build

**Post-Processing**:
- `post:color-swap-m600` - Add M600 filament change
- `post:color-swap-pause` - Add manual pause

**Utilities**:
- `calibration:all` - Show calibration sequence
- `validate:profiles` - Check configuration files
- `package:release` - Create deployment package
- `workspace:setup-tools` - Show installation requirements

## 🔧 One-Page Workflow

### 1️⃣ Prep Phase (After Long Break)
- [ ] **Clean printer**: Bed surface, extruder gear, filament path
- [ ] **Check belts**: Proper tension, no fraying
- [ ] **Verify mechanics**: Smooth X/Y/Z movement
- [ ] **Load filament**: Dry PLA+, check for moisture

### 2️⃣ Calibrate Phase  
- [ ] **First layer**: `calibration/first_layer_test.gcode`
- [ ] **Temperature**: `calibration/temp_tower_pla_195-220C.gcode`
- [ ] **Retraction**: `calibration/retraction_tower.gcode` (if needed)
- [ ] **Flow rate**: `calibration/flow_cube_100pct.gcode` (if needed)
- [ ] **Update profiles**: Record optimal settings

### 3️⃣ Slice Phase
```bash
# Option A: VS Code Tasks (Recommended)
Ctrl+Shift+P → "Tasks: Run Task" → "build:complete-pipeline"

# Option B: Command Line
python tools/slice_and_process.py --temp 210 --layer 5
```

### 4️⃣ Color Swap Configuration
- [ ] **Choose method**: M600 (auto) or Pause (manual)
- [ ] **Set layer**: Layer 5 (1.0mm) recommended for bow tie
- [ ] **Prepare colors**: Have both filaments ready
- [ ] **Test purge amount**: 50-100mm typically needed

### 5️⃣ Print Phase
- [ ] **Run preflight**: `docs/preflight_checklist.md`
- [ ] **Load G-code**: `gcode/production/bow_tie_*_swap_L5.gcode`
- [ ] **Monitor first layer**: Stay nearby for 5-10 minutes
- [ ] **Handle color swap**: Follow prompts at layer 5
- [ ] **Complete print**: Wait for cool-down

### 6️⃣ Log Results
Update `logs/print_log.csv` with:
- Print outcome (success/failure)
- Settings used (temperature, layer height, etc.)
- Issues encountered
- Quality notes
- Time to completion

## 🎨 Parametric Model Customization

Edit `models/bow_tie_parametric.scad` parameters:

```scad
// Main dimensions
bow_width_mm = 110;        // Conservative width
bow_height_mm = 55;        // Standard height  
bow_thickness_mm = 3.0;    // Comfortable thickness

// Strap accommodation
strap_slot_width_mm = 22;  // 20mm strap + tolerance
strap_slot_height_mm = 2.5; // Standard strap thickness
```

**Re-export after changes**:
```bash
# Command line export
openscad -o models/bow_tie_reference.stl models/bow_tie_parametric.scad

# Or use VS Code task: build:model
```

## 🌈 Color Swap Methods

### Method 1: M600 (Firmware Change)
**Best for**: Printers with M600 support
```bash
python slicer/postprocess/insert_color_swap.py \
  --input bow_tie.gcode \
  --by layer --value 5 \
  --mode m600
```

### Method 2: Manual Pause  
**Best for**: Universal compatibility
```bash
python slicer/postprocess/insert_color_swap.py \
  --input bow_tie.gcode \
  --by height --value 1.0 \
  --mode pause
```

**Color swap timing**:
- **Layer 3**: Minimal base, maximum secondary color
- **Layer 5**: Balanced split (recommended)
- **Layer 8**: More base color, accent secondary

## 📊 Quality Control

### Success Criteria
- [ ] **Dimensional accuracy**: ±0.1mm on all measurements
- [ ] **Layer adhesion**: No delamination at color change
- [ ] **Surface finish**: Smooth, consistent texture
- [ ] **Color separation**: Clean boundary, no bleeding
- [ ] **Fit and function**: Strap slides easily through slot

### Common Issues and Solutions
| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Poor first layer | Bed leveling | Run `first_layer_test.gcode`, adjust Z-offset |
| Stringing | Temperature/retraction | Run `temp_tower` and `retraction_tower` |
| Under-extrusion | Flow rate/clog | Run `flow_cube`, check nozzle |
| Color bleeding | Insufficient purge | Increase purge amount, clean nozzle |
| Layer shift | Belt tension | Check X/Y belt tightness |

## 🔄 Update and Maintenance

### Manifests and Logging
- **Before each print**: Update `manifests/bow_tie.slice.yml` with current settings
- **After each print**: Log results in `logs/print_log.csv`
- **Weekly**: Review logs for trends and optimization opportunities

### Version Control (Optional)
```bash
# Initialize Git repository
git init
git lfs track "*.stl" "*.gcode" "*.3mf" "*.png" "*.jpg"
git add .
git commit -m "Initial 3D printing workspace setup"

# Tag successful configurations
git tag -a v1.0 -m "Working PLA+ profile, Layer 5 color swap"
```

### Seasonal Maintenance
- **Every 3 months**: Run complete calibration sequence
- **Filament changes**: Re-run temperature tower for new brands
- **After modifications**: Full recalibration cycle

## 🆘 Troubleshooting

### Quick Diagnostic Commands
```bash
# Validate workspace integrity
python -c "import os; print('✓ Workspace valid' if all(os.path.exists(d) for d in ['models', 'slicer', 'gcode']) else '✗ Missing directories')"

# Check tool availability  
openscad --version && prusa-slicer --help && python --version

# Verify profiles
python tools/validate_profiles.py
```

### Emergency Contacts
- **Extruder clicking**: See `docs/extruder_clicking_troubleshooting.md`
- **Print failure**: Follow `docs/preflight_checklist.md`
- **Color swap issues**: Reference `docs/color_swap_guide.md`

## 📚 Documentation Deep Dive

- **[Maintenance Checklist](docs/maintenance_checklist.md)** - Regular printer upkeep
- **[Preflight Checklist](docs/preflight_checklist.md)** - Pre-print validation  
- **[Color Swap Guide](docs/color_swap_guide.md)** - Detailed two-color printing
- **[Slicer CLI Guide](docs/slicer_cli_guide.md)** - Command-line workflows
- **[Troubleshooting Guide](docs/extruder_clicking_troubleshooting.md)** - Problem solving

## 🧹 Organize models automation

To enforce the canonical models/ layout and process ZIP archives safely, use the PowerShell organizer:

- Script: `tools/organize-models.ps1`
- Docs: `docs/organize_models_script.md`

Quick usage (Windows PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\organize-models.ps1 -All -DryRun
```

Remove `-DryRun` to apply changes. If running from outside the repo, add `-Root "C:\path\to\3d_printing"`.

## 🎯 Next Steps

### Immediate Actions (First Use)

1. **Install required tools** using the checklist above
2. **Run `first_layer_test.gcode`** to verify bed leveling
3. **Run `temp_tower_pla_195-220C.gcode`** to find optimal temperature
4. **Update profiles** with calibrated settings
5. **Test complete workflow** with a bow tie print

### Future Enhancements

- [ ] **Multi-material support**: Upgrade to MMU or dual extruder
- [ ] **Advanced profiles**: PETG, TPU, wood-fill materials
- [ ] **Custom models**: Adapt workspace for other two-color projects
- [ ] **Remote monitoring**: Add OctoPrint or similar for remote control
- [ ] **Quality automation**: Automated first-layer inspection

## 🤝 Contributing

This workspace is designed to be adapted and improved:

1. **Document changes**: Update manifests and logs with modifications
2. **Share successes**: Contribute successful profiles and settings
3. **Report issues**: Use detailed troubleshooting guides to diagnose problems
4. **Extend functionality**: Add new models, profiles, or automation scripts

---

**Happy Printing!** 🎉

*This workspace represents a complete, production-ready 3D printing environment. Follow the workflows, maintain the documentation, and iterate based on your results for consistent, high-quality two-color prints.*
