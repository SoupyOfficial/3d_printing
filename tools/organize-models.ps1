#Requires -Version 5.1
<#
.SYNOPSIS
  Organize 3D printing assets into the canonical models/ structure and process new archives.

.DESCRIPTION
  This script enforces a file-type-first layout in the models folder and automates archive processing.
  It moves files by extension to:
    - models/model_files/(test|prod)/...  -> .stl, .3mf, .obj
    - models/gcode/(test|prod)/...        -> .gcode
    - models/sources/prod/(openscad|fusion360|other)/... -> .scad, .f3d, others
  Non-model extras extracted from archives are NOT kept (policy): they remain stored inside the ZIPs only.

  Archives are expected under models/archives/prod. If any .zip are found elsewhere under models/, they
  will be moved to models/archives/prod.

  The script is idempotent and can be safely re-run. It uses per-zip sentinel files in
  models/archives/prod/.processed to avoid reprocessing the same ZIP unless -Reprocess is specified.

.PARAMETER Root
  Path to the repository root (folder that contains models/). Defaults to script directory's parent.

.PARAMETER All
  Run both archive processing and sanitization. Default when no specific mode switch is provided.

.PARAMETER ProcessArchives
  Only process ZIP archives under models/archives/prod (and move stray zips under models/ there first).

.PARAMETER Sanitize
  Only sanitize existing trees (move stray files by type, purge non-model extras in model_files/gcode, prune empties).

.PARAMETER Reprocess
  Reprocess all ZIPs ignoring existing sentinel files.

.PARAMETER DryRun
  Print intended actions without changing files.

.PARAMETER SeedSentinels
  Mark all current ZIPs under models/archives/prod as processed without extracting or moving files.
  Useful to adopt this script in a repository that has already been organized manually.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools/organize-models.ps1 -All

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools/organize-models.ps1 -ProcessArchives -DryRun

.NOTES
  Policy reminders:
    - Keep meshes together (.stl/.3mf/.obj) under model_files.
    - Keep .gcode under gcode only.
    - Keep sources (.scad/.f3d) under sources/prod/{openscad|fusion360}.
    - Do not retain extracted non-model extras; leave them inside the zip.
#>

[CmdletBinding()]
param(
  [Parameter()]
  [string]$Root,

  [switch]$All,
  [switch]$ProcessArchives,
  [switch]$Sanitize,
  [switch]$Reprocess,
  [switch]$DryRun,
  [switch]$SeedSentinels,
  [switch]$OnlyPending
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info([string]$msg) { Write-Host "[INFO ] $msg" -ForegroundColor Cyan }
function Write-Warn([string]$msg) { Write-Host "[WARN ] $msg" -ForegroundColor Yellow }
function Write-Err ([string]$msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Dry([string]$msg) { Write-Host "[DRYRN] $msg" -ForegroundColor DarkGray }

function MkDirSafe([string]$path) {
  if (-not [string]::IsNullOrWhiteSpace($path) -and -not (Test-Path -LiteralPath $path)) {
    if ($DryRun) { Write-Dry "mkdir $path" } else { New-Item -ItemType Directory -Path $path -Force | Out-Null }
  }
}

function Move-Safe([string]$src, [string]$dstDir) {
  MkDirSafe $dstDir
  $dest = Join-Path $dstDir (Split-Path -Leaf $src)
  if ($DryRun) {
    Write-Dry "move '$src' -> '$dest'"
  }
  else {
    if (Test-Path -LiteralPath $src) {
      Move-Item -LiteralPath $src -Destination $dest -Force
    }
  }
}

function Remove-Safe([string]$path) {
  if (-not (Test-Path -LiteralPath $path)) { return }
  if ($DryRun) { Write-Dry "remove '$path'" } else { Remove-Item -LiteralPath $path -Force -Recurse }
}

function Remove-EmptyDirs([string]$base) {
  if (-not (Test-Path -LiteralPath $base)) { return }
  # Post-order so deeper directories get removed first
  $dirs = Get-ChildItem -LiteralPath $base -Recurse -Directory | Sort-Object FullName -Descending
  foreach ($d in $dirs) {
    try {
      $hasFiles = Get-ChildItem -LiteralPath $d.FullName -Force | Where-Object { -not $_.PSIsContainer }
      $hasDirs  = Get-ChildItem -LiteralPath $d.FullName -Force | Where-Object { $_.PSIsContainer }
      if (-not $hasFiles -and -not $hasDirs) {
        if ($DryRun) { Write-Dry "rmdir '$($d.FullName)'" } else { Remove-Item -LiteralPath $d.FullName -Force }
      }
    } catch { }
  }
}

function Initialize-CanonicalStructure([string]$modelsRoot) {
  $paths = @(
    'model_files/prod',
    'model_files/test',
    'gcode/prod',
    'gcode/test',
    'sources/prod/openscad',
    'sources/prod/fusion360',
    'sources/prod/other',
    'archives/prod',
    'media/prod',
    'media/test'
  ) | ForEach-Object { Join-Path $modelsRoot $_ }
  foreach ($p in $paths) { MkDirSafe $p }
}

function ConvertTo-ProjectName([string]$name) {
  # Strip common suffixes like -model_files, -print_files, -gcode, -models
  $n = $name
  $suffixes = @('model_files','print_files','gcode','models','stl','files')
  foreach ($s in $suffixes) {
    $n = $n -replace ("[-_\. ]{0,1}$s$"), ''
  }
  # Collapse whitespace and punctuation to underscore
  $n = ($n -replace "[^A-Za-z0-9]+", '_').Trim('_')
  if ([string]::IsNullOrWhiteSpace($n)) { $n = 'project' }
  return $n.ToLowerInvariant()
}

function Get-ProjectName([string]$zipPath) {
  $base = [IO.Path]::GetFileNameWithoutExtension($zipPath)
  return (ConvertTo-ProjectName $base)
}

function Get-ProcessedSentinel([string]$archivesProd, [string]$zipPath) {
  $processedDir = Join-Path $archivesProd '.processed'
  MkDirSafe $processedDir
  $zipName = Split-Path -Leaf $zipPath
  return Join-Path $processedDir ("$zipName.done")
}

function Move-FilesByExtension([IO.FileInfo[]]$files, [string]$dstRoot, [string]$subDir) {
  foreach ($f in $files) {
    Move-Safe $f.FullName (Join-Path $dstRoot $subDir)
  }
}

function Invoke-ArchiveProcessing([string]$modelsRoot, [switch]$Reprocess, [switch]$SeedSentinels, [switch]$OnlyPending) {
  $archivesRoot = Join-Path $modelsRoot 'archives'
  $archivesProd = Join-Path $archivesRoot 'prod'
  $archivesPending = Join-Path $archivesRoot 'pending-processing'
  MkDirSafe $archivesProd

  # Prefer explicit pending-processing intake if present
  $pendingMoved = @()
  if (Test-Path -LiteralPath $archivesPending) {
    $pendingZips = Get-ChildItem -LiteralPath $archivesPending -File -Filter *.zip -ErrorAction SilentlyContinue
    foreach ($pz in $pendingZips) {
      Write-Info "Intake pending ZIP -> archives/prod: $($pz.FullName)"
      $destPath = Join-Path $archivesProd (Split-Path -Leaf $pz.FullName)
      if ($DryRun) {
        Write-Dry "move '$($pz.FullName)' -> '$destPath'"
        # Synthesize a file-like object for downstream processing
        $pendingMoved += [pscustomobject]@{
          FullName     = $destPath
          Name         = (Split-Path -Leaf $destPath)
          Extension    = '.zip'
          DirectoryName= (Split-Path -Parent $destPath)
        }
      } else {
        Move-Item -LiteralPath $pz.FullName -Destination $destPath -Force
        # Track as FileInfo in prod for targeted processing
        $pendingMoved += (Get-Item -LiteralPath $destPath)
      }
    }
  }

  # Move other stray zips under models/ into archives/prod (unless OnlyPending is set and we already have pendingMoved)
  if (-not $OnlyPending) {
    $strayZips = Get-ChildItem -Path (Join-Path $modelsRoot '*') -Recurse -File -ErrorAction SilentlyContinue |
                  Where-Object { ($_.Extension -and $_.Extension.ToLowerInvariant() -eq '.zip') -and ($_.DirectoryName -ne $archivesProd) -and ($_.DirectoryName -ne $archivesPending) }
    foreach ($z in $strayZips) {
      Write-Info "Moving stray ZIP to archives/prod: $($z.FullName)"
      Move-Safe $z.FullName $archivesProd
    }
  }

  $zips = @()
  if ($OnlyPending -and $pendingMoved.Count -gt 0) {
    $zips = $pendingMoved
  } else {
    $zips = Get-ChildItem -LiteralPath $archivesProd -File -Filter *.zip -ErrorAction SilentlyContinue
  }
  if (-not $zips) { Write-Info 'No ZIP archives to process.'; return }

  foreach ($zip in $zips) {
    $sentinel = Get-ProcessedSentinel $archivesProd $zip.FullName
    if ((-not $Reprocess) -and (Test-Path -LiteralPath $sentinel)) {
      Write-Info "Already processed, skipping: $($zip.Name)"
      continue
    }

    if ($SeedSentinels -and (-not $OnlyPending)) {
      Write-Info "Seeding sentinel (no extract): $($zip.Name)"
      if ($DryRun) {
        Write-Dry "new-sentinel '$sentinel'"
      } else {
        Set-Content -LiteralPath $sentinel -Value (Get-Date).ToString('s') -Force
      }
      continue
    }

  $project = Get-ProjectName $zip.FullName
    Write-Info "Processing: $($zip.Name) -> project '$project'"

    # Extract to temp directory
    $tempBase = Join-Path ([IO.Path]::GetTempPath()) ("models_extract_" + [Guid]::NewGuid().ToString('N'))
    MkDirSafe $tempBase
    if ($DryRun) {
      Write-Dry "Expand-Archive -LiteralPath '$($zip.FullName)' -DestinationPath '$tempBase' -Force"
    }
    else {
      try {
        Expand-Archive -LiteralPath $zip.FullName -DestinationPath $tempBase -Force
      } catch {
        Write-Warn "Failed to expand archive: $($zip.FullName). Skipping. Error: $($_.Exception.Message)"
        Remove-Safe $tempBase
        continue
      }
    }

    # Gather files by extension
    $all = @()
    if (Test-Path -LiteralPath $tempBase) {
      $all = Get-ChildItem -LiteralPath $tempBase -Recurse -File -ErrorAction SilentlyContinue
    }

    $modelExts  = @('.stl','.3mf','.obj')
    $gcodeExts  = @('.gcode')
    $scadExts   = @('.scad')
    $f3dExts    = @('.f3d')

    $modelFiles = $all | Where-Object { $modelExts -contains $_.Extension.ToLowerInvariant() }
    $gcodeFiles = $all | Where-Object { $gcodeExts -contains $_.Extension.ToLowerInvariant() }
    $scadFiles  = $all | Where-Object { $scadExts -contains $_.Extension.ToLowerInvariant() }
    $f3dFiles   = $all | Where-Object { $f3dExts -contains $_.Extension.ToLowerInvariant() }
    $otherSrc   = $all | Where-Object { $_.Extension -and ($_.Extension.ToLowerInvariant() -in @('.step','.stp','.igs','.iges','.sldprt','.sldasm','.x_t','.x_b')) }

    Move-FilesByExtension $modelFiles $modelsRoot (Join-Path 'model_files\prod' ("_uncategorized\$project"))
    Move-FilesByExtension $gcodeFiles $modelsRoot (Join-Path 'gcode\prod'       ("_uncategorized\$project"))
    Move-FilesByExtension $scadFiles  $modelsRoot (Join-Path 'sources\prod\openscad'  $project)
    Move-FilesByExtension $f3dFiles   $modelsRoot (Join-Path 'sources\prod\fusion360' $project)
    Move-FilesByExtension $otherSrc   $modelsRoot (Join-Path 'sources\prod\other'     $project)

    # Cleanup temp extract and create sentinel
    Remove-Safe $tempBase
    if ($DryRun) {
      Write-Dry "new-sentinel '$sentinel'"
    } else {
      Set-Content -LiteralPath $sentinel -Value (Get-Date).ToString('s') -Force
    }
  }
}

## removed duplicate old Sanitize-Trees function (superseded by Invoke-TreeSanitization)
function Invoke-TreeSanitization([string]$modelsRoot) {
  $modelRoot = Join-Path $modelsRoot 'model_files\prod'
  $gcodeRoot = Join-Path $modelsRoot 'gcode\prod'
  $srcRoot   = Join-Path $modelsRoot 'sources\prod'

  MkDirSafe $modelRoot; MkDirSafe $gcodeRoot; MkDirSafe $srcRoot

  # 1) Move any .gcode found under model_files -> gcode
  $gcodeInModels = Get-ChildItem -LiteralPath $modelRoot -Recurse -File -Filter *.gcode -ErrorAction SilentlyContinue
  foreach ($f in $gcodeInModels) {
    # Determine project as top-level directory under model_files/prod
    $rel = $f.FullName.Substring($modelRoot.Length).TrimStart([IO.Path]::DirectorySeparatorChar)
    $project = ($rel.Split([IO.Path]::DirectorySeparatorChar))[0]
    if ([string]::IsNullOrWhiteSpace($project)) { $project = '_uncategorized' }
    $dst = Join-Path $gcodeRoot $project
    Move-Safe $f.FullName $dst
  }

  # 2) Move any meshes found under gcode -> model_files
  $meshExts = @('.stl','.3mf','.obj')
  $meshesInGcode = Get-ChildItem -LiteralPath $gcodeRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $meshExts -contains $_.Extension.ToLowerInvariant() }
  foreach ($f in $meshesInGcode) {
    $rel = $f.FullName.Substring($gcodeRoot.Length).TrimStart([IO.Path]::DirectorySeparatorChar)
    $project = ($rel.Split([IO.Path]::DirectorySeparatorChar))[0]
    if ([string]::IsNullOrWhiteSpace($project)) { $project = '_uncategorized' }
    $dst = Join-Path $modelRoot $project
    Move-Safe $f.FullName $dst
  }

  # 3) Move sources anywhere under model_files/gcode into sources
  $sourceMoves = @()
  $sourceMoves += Get-ChildItem -LiteralPath $modelRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension.ToLowerInvariant() -in @('.scad','.f3d','.step','.stp','.igs','.iges','.sldprt','.sldasm','.x_t','.x_b') }
  $sourceMoves += Get-ChildItem -LiteralPath $gcodeRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension.ToLowerInvariant() -in @('.scad','.f3d','.step','.stp','.igs','.iges','.sldprt','.sldasm','.x_t','.x_b') }
  foreach ($f in $sourceMoves) {
    $ext = $f.Extension.ToLowerInvariant()
    $targetSub = switch ($ext) {
      '.scad' { 'openscad' }
      '.f3d'  { 'fusion360' }
      default { 'other' }
    }
    # project inferred by nearest top-level folder under model_files/prod or gcode/prod
    $anchor = if ($f.FullName.StartsWith($modelRoot)) { $modelRoot } else { $gcodeRoot }
    $rel = $f.FullName.Substring($anchor.Length).TrimStart([IO.Path]::DirectorySeparatorChar)
    $project = ($rel.Split([IO.Path]::DirectorySeparatorChar))[0]
    if ([string]::IsNullOrWhiteSpace($project)) { $project = '_uncategorized' }
    $dst = Join-Path $srcRoot (Join-Path $targetSub $project)
    Move-Safe $f.FullName $dst
  }

  # 4) Remove non-model extras from model_files and gcode
  $extras = @('.pdf','.txt','.rtf','.doc','.docx','.xlsx','.csv','.png','.jpg','.jpeg','.gif','.bmp','.webp','.svg','.zip','.7z','.rar')
  $toRemove = @()
  $toRemove += Get-ChildItem -LiteralPath $modelRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $extras -contains $_.Extension.ToLowerInvariant() }
  $toRemove += Get-ChildItem -LiteralPath $gcodeRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $extras -contains $_.Extension.ToLowerInvariant() }
  foreach ($f in $toRemove) { Remove-Safe $f.FullName }

  # 5) Prune empty directories
  Remove-EmptyDirs $modelRoot
  Remove-EmptyDirs $gcodeRoot
}

function Get-ModelsState([string]$modelsRoot) {
  $sections = @('model_files','gcode','sources','archives')
  foreach ($s in $sections) {
    $p = Join-Path $modelsRoot $s
    if (-not (Test-Path -LiteralPath $p)) { continue }
    Write-Host "--- $s ---" -ForegroundColor Green
    $files = Get-ChildItem -LiteralPath $p -Recurse -File -ErrorAction SilentlyContinue
    if ($files) {
      $groups = $files | Group-Object { $_.Extension.ToLowerInvariant() } | Sort-Object Name
      foreach ($g in $groups) {
        '{0,6} {1}' -f $g.Count, $g.Name | Write-Host
      }
      # show a few sample paths
      $sample = $files | Select-Object -First 5 | ForEach-Object { $_.FullName }
      if ($sample) {
        Write-Host 'samples:' -ForegroundColor DarkCyan
        $sample | ForEach-Object { Write-Host "  $_" }
      }
    } else {
      Write-Host '(no files)'
    }
  }

  # Show processed zips
  $processedDir = Join-Path (Join-Path $modelsRoot 'archives\prod') '.processed'
  if (Test-Path -LiteralPath $processedDir) {
    $done = Get-ChildItem -LiteralPath $processedDir -File -ErrorAction SilentlyContinue
    if ($done) {
      Write-Host '--- processed zips ---' -ForegroundColor Green
  $done | ForEach-Object { Write-Host ("  " + ($_.Name -replace '\.done$','')) }
    }
  }
}

# Entry point
try {
  if (-not $Root) {
    if ($PSScriptRoot) { $Root = (Split-Path -Parent $PSScriptRoot) }
    else { $Root = (Get-Location).Path }
  }

  $modelsRoot = Join-Path $Root 'models'
  if (-not (Test-Path -LiteralPath $modelsRoot)) { throw "models directory not found at: $modelsRoot" }

  Initialize-CanonicalStructure $modelsRoot

  $selected = @($All, $ProcessArchives, $Sanitize) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
  if ($selected -eq 0) { $All = $true }

  if ($All -or $ProcessArchives -or $SeedSentinels) { Invoke-ArchiveProcessing -modelsRoot $modelsRoot -Reprocess:$Reprocess -SeedSentinels:$SeedSentinels -OnlyPending:$OnlyPending }
  if ($All -or $Sanitize) { Invoke-TreeSanitization -modelsRoot $modelsRoot }

  Get-ModelsState -modelsRoot $modelsRoot

  Write-Info 'Done.'
} catch {
  Write-Err $_.Exception.Message
  if ($_.InvocationInfo.PositionMessage) { Write-Warn $_.InvocationInfo.PositionMessage }
  exit 1
}
