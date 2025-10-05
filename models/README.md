# Models folder structure

This directory is organized by file type, then by environment (test vs prod), and finally by category.

## Top-level convention

- model_files/(test|prod)/{category}/...   → STL/3MF/OBJ model files
- gcode/(test|prod)/...                    → Printer-ready G-code
- sources/(test|prod)/{tool}/...           → Source files (e.g., OpenSCAD)
- archives/prod/...                        → ZIP and other downloadable bundles
- media/(test|prod)/...                    → Videos, screenshots, etc.

## Notes

- STL, 3MF, and OBJ live together under model_files.
- "test" = benchmarks and calibration; "prod" = real projects.
- Common categories: accessories, decorations, figurines, hardware, household, mounts, organizers, planters.

## Examples

- model_files/prod/mounts/camera/Nebula_Camera_Mount_for_Ender3V3_V2.stl
- model_files/test/benchmarks/3DBenchy.stl
- gcode/prod/Webcam Bed Mount.gcode
- gcode/test/simple_squares.gcode
- sources/prod/openscad/ghost_cat_v4.scad

## How to add new items

- New model (STL/3MF/OBJ):
  - Final design → model_files/prod/{category}/
  - Calibration/benchmark → model_files/test/benchmarks/
- New G-code:
  - Validated slice → gcode/prod/
  - Experimental → gcode/test/
- Source files (e.g., .scad): sources/prod/{tool}/ (e.g., sources/prod/openscad/)
- ZIP downloads and any non-model extras (images, licenses, readmes) should stay zipped in archives/prod/ (do not extract to repo)
- Media (videos/screenshots): media/prod/ (or media/test/)

## Naming guidelines

- Prefer descriptive names; keep printer/material details in G-code filenames.
- Avoid confusing characters (quotes, colons). Spaces work, but hyphens/underscores improve portability.