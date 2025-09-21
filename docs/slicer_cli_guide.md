# Slicer CLI Guide - Command Line Slicing

This guide provides command-line workflows for both PrusaSlicer/SuperSlicer/OrcaSlicer and CuraEngine, enabling automated slicing and consistent results.

## PrusaSlicer/SuperSlicer/OrcaSlicer CLI

### Installation and Setup

#### Windows Installation Paths
- **PrusaSlicer**: `C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe`
- **SuperSlicer**: `C:\Program Files\SuperSlicer\superslicer.exe`  
- **OrcaSlicer**: `C:\Program Files\OrcaSlicer\OrcaSlicer.exe`

#### Add to System PATH
```cmd
# Add to Windows PATH environment variable
set PATH=%PATH%;C:\Program Files\Prusa3D\PrusaSlicer
```

### Basic CLI Commands

#### Slice with Profile
```cmd
# Basic slicing command
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_pla_0.2mm.gcode

# With verbose output
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_pla_0.2mm.gcode --loglevel info
```

#### Override Specific Settings
```cmd
# Change temperature on command line
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --temperature 210 --bed-temperature 65 --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_210C.gcode

# Change layer height
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --layer-height 0.15 --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_015mm.gcode

# Multiple overrides
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --infill-density 20 --perimeters 4 --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_strong.gcode
```

#### Batch Processing
```cmd
# Slice multiple files with same profile
for %%f in (models\*.stl) do (
    prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --export-gcode "%%f" -o "gcode/production/%%~nf_pla_0.2mm.gcode"
)
```

### Advanced PrusaSlicer Options

#### Configuration Export/Import
```cmd
# Export current configuration
prusa-slicer.exe --export-config slicer/profiles/current_config.ini

# Use multiple configuration files  
prusa-slicer.exe --load slicer/profiles/printer_settings.ini --load slicer/profiles/material_pla.ini --load slicer/profiles/quality_0.2mm.ini --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie.gcode
```

#### Custom G-code Integration
```cmd
# Add custom start/end G-code
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --start-gcode "G28\nG92 E0\nG1 E5 F300" --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_custom.gcode
```

## CuraEngine CLI

### Installation and Setup

#### CuraEngine Installation
```cmd
# Download CuraEngine from Ultimaker GitHub
# Extract to C:\Program Files\CuraEngine\
set PATH=%PATH%;C:\Program Files\CuraEngine
```

### Basic CuraEngine Commands

#### Slice with JSON Profile  
```cmd
# Basic CuraEngine slicing
CuraEngine.exe slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -o gcode/production/bow_tie_cura.gcode -l models/bow_tie_reference.stl

# With progress output
CuraEngine.exe slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -o gcode/production/bow_tie_cura.gcode -l models/bow_tie_reference.stl -p
```

#### Override Settings
```cmd
# Override specific settings
CuraEngine.exe slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -s material_print_temperature=210 -s material_bed_temperature=65 -o gcode/production/bow_tie_210C.gcode -l models/bow_tie_reference.stl

# Multiple setting overrides
CuraEngine.exe slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -s infill_sparse_density=20 -s wall_line_count=4 -s speed_print=40 -o gcode/production/bow_tie_strong.gcode -l models/bow_tie_reference.stl
```

### Profile Management

#### Create Reusable Batch Files

**slice_bow_tie_prusa.cmd**:
```cmd
@echo off
set INPUT=%1
set OUTPUT=%2
set TEMP=%3

if "%INPUT%"=="" set INPUT=models/bow_tie_reference.stl
if "%OUTPUT%"=="" set OUTPUT=gcode/production/bow_tie_pla_0.2mm.gcode  
if "%TEMP%"=="" set TEMP=205

echo Slicing %INPUT% at %TEMP%C...
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --temperature %TEMP% --export-gcode "%INPUT%" -o "%OUTPUT%"

echo Slicing complete: %OUTPUT%
```

**slice_bow_tie_cura.cmd**:
```cmd
@echo off
set INPUT=%1
set OUTPUT=%2  
set TEMP=%3

if "%INPUT%"=="" set INPUT=models/bow_tie_reference.stl
if "%OUTPUT%"=="" set OUTPUT=gcode/production/bow_tie_cura.gcode
if "%TEMP%"=="" set TEMP=205

echo Slicing %INPUT% with CuraEngine at %TEMP%C...
CuraEngine.exe slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -s material_print_temperature=%TEMP% -o "%OUTPUT%" -l "%INPUT%"

echo Slicing complete: %OUTPUT%
```

### Usage Examples

#### Basic Usage
```cmd
# Use default settings
slice_bow_tie_prusa.cmd

# Specify temperature
slice_bow_tie_prusa.cmd models/bow_tie_reference.stl gcode/production/bow_tie_210C.gcode 210

# CuraEngine equivalent
slice_bow_tie_cura.cmd models/bow_tie_reference.stl gcode/production/bow_tie_cura_210C.gcode 210
```

#### Advanced Workflows

**Production Slicing Pipeline**:
```cmd
@echo off
echo === Bow Tie Production Slicing Pipeline ===

echo 1. Slicing with PrusaSlicer...
prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_prusa.gcode

echo 2. Slicing with CuraEngine for comparison...
CuraEngine.exe slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -o gcode/production/bow_tie_cura.gcode -l models/bow_tie_reference.stl

echo 3. Adding color swap to primary file...
python slicer/postprocess/insert_color_swap.py --input gcode/production/bow_tie_prusa.gcode --by layer --value 5 --mode m600 --output gcode/production/bow_tie_prusa_swap_L5.gcode

echo 4. Generating manifest...
python tools/generate_manifest.py --input gcode/production/bow_tie_prusa_swap_L5.gcode --output manifests/bow_tie.slice.yml

echo === Pipeline Complete ===
```

## Metadata and Manifest Generation

### Extracting Slice Information
Both slicers can embed metadata in G-code comments. Extract this for manifests:

```cmd
# Extract metadata from G-code comments
findstr /C:"; generated by" /C:"; printing time" /C:"; layer height" gcode/production/bow_tie.gcode > temp_metadata.txt
```

### Integration with Manifest System
Commands should update `/manifests/bow_tie.slice.yml` with:
- Slicer used and version
- Profile settings applied  
- Command line overrides
- Output file paths and sizes
- Estimated print time
- Material usage

## Cross-Platform Considerations

### Linux/macOS Equivalents
```bash
# PrusaSlicer on Linux
./PrusaSlicer --load slicer/profiles/ender3pro_pla_0.2mm.ini --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_pla_0.2mm.gcode

# CuraEngine on Linux  
./CuraEngine slice -j slicer/profiles/cura_ender3pro_pla_0.2mm.json -o gcode/production/bow_tie_cura.gcode -l models/bow_tie_reference.stl
```

### WSL2 Integration
```bash
# Access Windows files from WSL2
cd /mnt/c/Users/JSCam/OneDrive/Documents/Development/3d_printing

# Run Windows executables from WSL2
/mnt/c/Program\ Files/Prusa3D/PrusaSlicer/prusa-slicer.exe --load slicer/profiles/ender3pro_pla_0.2mm.ini --export-gcode models/bow_tie_reference.stl -o gcode/production/bow_tie_pla_0.2mm.gcode
```

## Quality Control and Validation

### Automated Checks
```cmd
# Verify G-code output
if not exist "%OUTPUT%" (
    echo ERROR: Slicing failed - no output file generated
    exit /b 1
)

# Check file size (should be reasonable for model complexity)
for %%A in ("%OUTPUT%") do if %%~zA LSS 10000 (
    echo WARNING: Output file suspiciously small - possible slicing error
)

# Verify G-code contains expected commands
findstr /C:"G1" /C:"M104" /C:"M140" "%OUTPUT%" > nul
if errorlevel 1 (
    echo ERROR: G-code appears malformed - missing basic commands
    exit /b 1
)
```

### Settings Validation
Create validation scripts to ensure profiles contain required settings:

```cmd
# Validate profile completeness
findstr /C:"layer_height" /C:"temperature" /C:"bed_temperature" slicer/profiles/ender3pro_pla_0.2mm.ini > nul
if errorlevel 1 (
    echo ERROR: Profile missing critical settings
    exit /b 1
)
```

## Integration with VS Code Tasks

These CLI commands integrate with the VS Code tasks in `/tools/tasks.json` to provide seamless workflow automation within the development environment.

## Troubleshooting CLI Issues

### Common Problems
- **Profile not found**: Verify path exists, use absolute paths
- **Permission errors**: Run as administrator, check file permissions  
- **Command not recognized**: Verify installation, PATH configuration
- **Malformed output**: Check input file validity, profile compatibility

### Debug Options
```cmd
# Enable verbose logging
prusa-slicer.exe --loglevel debug --export-gcode models/bow_tie_reference.stl

# CuraEngine verbose output
CuraEngine.exe slice -j profile.json -o output.gcode -l input.stl -v
```

This CLI approach enables consistent, repeatable slicing workflows and integrates seamlessly with automated build systems and version control.