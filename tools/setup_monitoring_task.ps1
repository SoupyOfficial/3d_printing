# setup_monitoring_task.ps1 -- Setup Windows Task Scheduler for health monitoring
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup_monitoring_task.ps1

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("install", "uninstall", "status")]
    [string]$Action = "install"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$HealthScript = Join-Path $ScriptDir "health_monitor.py"
$TaskName = "FluiddTunnelHealthMonitor"

Write-Host "Fluidd Tunnel Health Monitoring Setup" -ForegroundColor Cyan
Write-Host "Action: $Action" -ForegroundColor Yellow

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

function Install-MonitoringTask {
    Write-Host "`nInstalling health monitoring tasks..." -ForegroundColor Yellow
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python: $pythonVersion"
    }
    catch {
        Write-Error "Python is not available or not in PATH"
        return $false
    }
    
    # Check if health monitor script exists
    if (-not (Test-Path $HealthScript)) {
        Write-Error "Health monitor script not found: $HealthScript"
        return $false
    }
    
    try {
        # Task settings (shared)
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        # 1. Status Reports Task - 4 times daily (8 AM, 12 PM, 4 PM, 8 PM)
        $statusAction = New-ScheduledTaskAction -Execute "python" -Argument "`"$HealthScript`" --status-report" -WorkingDirectory $ProjectRoot
        $statusTrigger1 = New-ScheduledTaskTrigger -Daily -At "08:00"
        $statusTrigger2 = New-ScheduledTaskTrigger -Daily -At "12:00"
        $statusTrigger3 = New-ScheduledTaskTrigger -Daily -At "16:00"
        $statusTrigger4 = New-ScheduledTaskTrigger -Daily -At "20:00"
        $statusTriggers = @($statusTrigger1, $statusTrigger2, $statusTrigger3, $statusTrigger4)
        
        Register-ScheduledTask -TaskName "FluiddStatusReports" -Action $statusAction -Trigger $statusTriggers -Settings $settings -Principal $principal -Description "Sends Fluidd tunnel status reports 4 times daily (8AM, 12PM, 4PM, 8PM)"
        
        # 2. Health Monitoring Task - Every 2 hours for basic health checks (no SMS)
        $healthAction = New-ScheduledTaskAction -Execute "python" -Argument "`"$HealthScript`" --health-check" -WorkingDirectory $ProjectRoot
        $healthTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Days 365)
        
        Register-ScheduledTask -TaskName "FluiddHealthCheck" -Action $healthAction -Trigger $healthTrigger -Settings $settings -Principal $principal -Description "Performs Fluidd tunnel health checks every 2 hours (silent monitoring)"
        
        Write-Host "✅ Health monitoring tasks installed successfully" -ForegroundColor Green
        Write-Host "Tasks configured:" -ForegroundColor Cyan
        Write-Host "  - Status Reports: 8 AM, 12 PM, 4 PM, 8 PM (with SMS)" -ForegroundColor White
        Write-Host "  - Health Checks: Every 2 hours (silent monitoring)" -ForegroundColor White
        
        return $true
    }
    catch {
        Write-Error "Error installing tasks: $($_.Exception.Message)"
        return $false
    }
}

function Uninstall-MonitoringTask {
    Write-Host "`nUninstalling health monitoring tasks..." -ForegroundColor Yellow
    
    try {
        # Remove both tasks
        $tasks = @("FluiddStatusReports", "FluiddHealthCheck", $TaskName)
        foreach ($task in $tasks) {
            try {
                Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction SilentlyContinue
                Write-Host "Removed task: $task" -ForegroundColor Green
            }
            catch {
                # Ignore if task doesn't exist
            }
        }
        Write-Host "✅ Health monitoring tasks uninstalled successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Error uninstalling tasks: $($_.Exception.Message)"
        return $false
    }
}

function Get-TaskStatus {
    Write-Host "`nHealth Monitoring Tasks Status:" -ForegroundColor Cyan
    
    $taskNames = @("FluiddStatusReports", "FluiddHealthCheck", $TaskName)
    
    foreach ($taskName in $taskNames) {
        try {
            $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
            if ($task) {
                Write-Host "`n--- $taskName ---" -ForegroundColor Yellow
                Write-Host "State: $($task.State)"
                Write-Host "Description: $($task.Description)"
                
                # Get last run info
                $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
                Write-Host "Last Run Time: $($taskInfo.LastRunTime)"
                Write-Host "Last Result: $($taskInfo.LastTaskResult)"
                Write-Host "Next Run Time: $($taskInfo.NextRunTime)"
                
                # Show triggers
                Write-Host "Triggers:"
                foreach ($trigger in $task.Triggers) {
                    Write-Host "  - $($trigger.TriggerType): $($trigger.StartBoundary)"
                    if ($trigger.Repetition.Interval) {
                        Write-Host "    Repeats every: $($trigger.Repetition.Interval)"
                    }
                }
            }
        }
        catch {
            # Ignore missing tasks
        }
    }
}

# Main execution
switch ($Action.ToLower()) {
    "install" {
        if (Install-MonitoringTask) {
            Write-Host "`n🎉 Health monitoring setup completed!" -ForegroundColor Green
            Write-Host "The system will now automatically:" -ForegroundColor Cyan
            Write-Host "  - Send status reports at 8 AM, 12 PM, 4 PM, and 8 PM" -ForegroundColor White
            Write-Host "  - Perform silent health checks every 2 hours" -ForegroundColor White
            Write-Host "  - Alert you if the tunnel becomes unreachable" -ForegroundColor White
        }
    }
    "uninstall" {
        Uninstall-MonitoringTask
    }
    "status" {
        Get-TaskStatus
    }
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "Valid actions: install, uninstall, status"
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan