# install_service.ps1 -- Install and manage Fluidd Tunnel Windows Service
# Run as Administrator: powershell -ExecutionPolicy Bypass -File install_service.ps1

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("install", "uninstall", "start", "stop", "restart", "status")]
    [string]$Action = "install"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ServiceScript = Join-Path $ScriptDir "fluidd_service.py"
$LogsDir = Join-Path $ProjectRoot "logs"

Write-Host "Fluidd Tunnel Service Management" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host "Service script: $ServiceScript"
Write-Host "Action: $Action" -ForegroundColor Yellow

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Error "This script must be run as Administrator"
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Ensure logs directory exists
if (-not (Test-Path $LogsDir)) { 
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null 
    Write-Host "Created logs directory: $LogsDir"
}

# Check Python and required packages
function Test-PythonRequirements {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python: $pythonVersion"
        
        # Check for required packages
        $packages = @("psutil", "pywin32")
        $missing = @()
        
        foreach ($package in $packages) {
            try {
                python -c "import $package" 2>$null
                Write-Host "✓ $package is installed" -ForegroundColor Green
            }
            catch {
                Write-Host "✗ $package is missing" -ForegroundColor Red
                $missing += $package
            }
        }
        
        if ($missing.Count -gt 0) {
            Write-Host "`nInstalling missing packages..." -ForegroundColor Yellow
            foreach ($package in $missing) {
                Write-Host "Installing $package..."
                python -m pip install $package
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓ $package installed successfully" -ForegroundColor Green
                } else {
                    Write-Error "Failed to install $package"
                    return $false
                }
            }
        }
        
        return $true
    }
    catch {
        Write-Error "Python is not available or not in PATH"
        return $false
    }
}

function Install-Service {
    Write-Host "`nInstalling Fluidd Tunnel Service..." -ForegroundColor Yellow
    
    if (-not (Test-PythonRequirements)) {
        Write-Error "Python requirements not met"
        return $false
    }
    
    if (-not (Test-Path $ServiceScript)) {
        Write-Error "Service script not found: $ServiceScript"
        return $false
    }
    
    try {
        # Install the service
        python $ServiceScript install
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Service installed successfully" -ForegroundColor Green
            
            # Configure service for automatic startup and restart on failure
            sc.exe config FluiddTunnel start=auto
            sc.exe failure FluiddTunnel reset=300 actions=restart/5000/restart/10000/restart/30000
            
            Write-Host "✓ Service configured for automatic startup" -ForegroundColor Green
            Write-Host "✓ Service configured to restart on failure" -ForegroundColor Green
            
            return $true
        } else {
            Write-Error "Failed to install service"
            return $false
        }
    }
    catch {
        Write-Error "Error installing service: $($_.Exception.Message)"
        return $false
    }
}

function Uninstall-Service {
    Write-Host "`nUninstalling Fluidd Tunnel Service..." -ForegroundColor Yellow
    
    try {
        # Stop service first
        Stop-Service -Name "FluiddTunnel" -ErrorAction SilentlyContinue
        
        # Remove the service
        python $ServiceScript remove
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Service uninstalled successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Error "Failed to uninstall service"
            return $false
        }
    }
    catch {
        Write-Error "Error uninstalling service: $($_.Exception.Message)"
        return $false
    }
}

function Start-TunnelService {
    Write-Host "`nStarting Fluidd Tunnel Service..." -ForegroundColor Yellow
    
    try {
        Start-Service -Name "FluiddTunnel"
        Write-Host "✓ Service started successfully" -ForegroundColor Green
        
        # Wait a moment and check status
        Start-Sleep -Seconds 2
        $service = Get-Service -Name "FluiddTunnel" -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Write-Host "✓ Service is running" -ForegroundColor Green
        } else {
            Write-Warning "Service may not have started properly"
        }
        
        return $true
    }
    catch {
        Write-Error "Error starting service: $($_.Exception.Message)"
        return $false
    }
}

function Stop-TunnelService {
    Write-Host "`nStopping Fluidd Tunnel Service..." -ForegroundColor Yellow
    
    try {
        Stop-Service -Name "FluiddTunnel" -Force
        Write-Host "✓ Service stopped successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Error stopping service: $($_.Exception.Message)"
        return $false
    }
}

function Restart-TunnelService {
    Write-Host "`nRestarting Fluidd Tunnel Service..." -ForegroundColor Yellow
    
    if (Stop-TunnelService) {
        Start-Sleep -Seconds 2
        return Start-TunnelService
    }
    return $false
}

function Get-ServiceStatus {
    Write-Host "`nFluidd Tunnel Service Status:" -ForegroundColor Cyan
    
    try {
        $service = Get-Service -Name "FluiddTunnel" -ErrorAction SilentlyContinue
        if ($service) {
            Write-Host "Service Name: $($service.Name)"
            Write-Host "Display Name: $($service.DisplayName)"
            Write-Host "Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
            Write-Host "Start Type: $($service.StartType)"
            
            # Check log files
            $logFile = Join-Path $LogsDir "cloudflared_service.log"
            $urlFile = Join-Path $LogsDir "cloudflared_url.txt"
            
            if (Test-Path $logFile) {
                $logSize = (Get-Item $logFile).Length
                Write-Host "Log file: $logFile ($logSize bytes)"
            } else {
                Write-Host "Log file: Not found"
            }
            
            if (Test-Path $urlFile) {
                Write-Host "URL file: $urlFile"
                $urlContent = Get-Content $urlFile -Raw
                Write-Host "Current URL:" -ForegroundColor Yellow
                Write-Host $urlContent
            } else {
                Write-Host "URL file: Not found"
            }
            
        } else {
            Write-Host "Service not installed" -ForegroundColor Red
        }
        
        # Check for running cloudflared processes
        $cloudflaredProcs = Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue
        if ($cloudflaredProcs) {
            Write-Host "`nRunning cloudflared processes:"
            $cloudflaredProcs | ForEach-Object {
                Write-Host "  PID: $($_.Id), Started: $($_.StartTime)"
            }
        } else {
            Write-Host "`nNo cloudflared processes running" -ForegroundColor Yellow
        }
        
    }
    catch {
        Write-Error "Error getting service status: $($_.Exception.Message)"
    }
}

# Main execution
switch ($Action.ToLower()) {
    "install" {
        if (Install-Service) {
            Write-Host "`nService installation completed successfully!" -ForegroundColor Green
            Write-Host "To start the service, run: .\install_service.ps1 start" -ForegroundColor Cyan
        }
    }
    "uninstall" {
        if (Uninstall-Service) {
            Write-Host "`nService uninstallation completed successfully!" -ForegroundColor Green
        }
    }
    "start" {
        Start-TunnelService
    }
    "stop" {
        Stop-TunnelService
    }
    "restart" {
        Restart-TunnelService
    }
    "status" {
        Get-ServiceStatus
    }
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "Valid actions: install, uninstall, start, stop, restart, status"
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan