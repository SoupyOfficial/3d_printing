# Organize models automation (PowerShell)

This repository includes a PowerShell script that enforces the canonical models/ structure and processes new archives safely.

Script: `tools/organize-models.ps1`

## What it does

- Creates/ensures the canonical folders:
  - `models/model_files/(test|prod)/`
  - `models/gcode/(test|prod)/`
  - `models/sources/prod/(openscad|fusion360|other)/`
  - `models/archives/prod/`
  - `models/media/(test|prod)/`
- Moves stray `.zip` files under `models/` into `models/archives/prod/`.
- Processes each ZIP in `models/archives/prod/`:
  - Extracts to a temp folder
  - Moves only relevant files by type:
    - `.stl/.3mf/.obj` → `models/model_files/prod/_uncategorized/<project>/`
    - `.gcode` → `models/gcode/prod/_uncategorized/<project>/`
    - `.scad` → `models/sources/prod/openscad/<project>/`
    - `.f3d` → `models/sources/prod/fusion360/<project>/`
    - common CAD formats (e.g., `.step/.stp/.igs/.iges/.sldprt/.sldasm/.x_t/.x_b`) → `models/sources/prod/other/<project>/`
  - Deletes the temp extraction (non-model extras stay only inside the ZIP)
  - Creates a sentinel file in `models/archives/prod/.processed/` to avoid reprocessing the same ZIP
- Sanitizes existing trees:
  - Moves `.gcode` out of `model_files` → `gcode`
  - Moves meshes out of `gcode` → `model_files`
  - Moves sources found anywhere into `sources/prod/...`
  - Removes non-model extras from `model_files` and `gcode` (images, docs, etc.)
  - Prunes empty directories

## Usage (Windows PowerShell)

Dry-run (show actions only):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\organize-models.ps1 -All -DryRun
```

Process only archives:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\organize-models.ps1 -ProcessArchives
```

Sanitize existing trees only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\organize-models.ps1 -Sanitize
```

Reprocess all ZIPs (ignore sentinels):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\organize-models.ps1 -ProcessArchives -Reprocess
```

Adopt the script without re-extracting prior ZIPs (seed sentinels only):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\organize-models.ps1 -ProcessArchives -SeedSentinels
```

Notes:
 
- If you run it from outside the repo root, add `-Root "C:\path\to\3d_printing"`.
- New extractions go to `_uncategorized/<project>`; you can later move them into a category under `model_files/prod/`.
- Non-model extras remain in the original ZIPs under `models/archives/prod/` per policy.

## Policy reminders

- Keep meshes together (`.stl/.3mf/.obj`) under `model_files`.
- Keep print files (`.gcode`) under `gcode` only.
- Keep sources under `sources/prod/{openscad|fusion360|other}`.
- Do not commit extracted non-model extras (images, PDFs, etc.)—they stay zipped in `archives/prod/`.
