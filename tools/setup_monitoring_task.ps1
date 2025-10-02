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
    Write-Host "`nInstalling health monitoring task..." -ForegroundColor Yellow
    
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
        # Create the scheduled task
        $action = New-ScheduledTaskAction -Execute "python" -Argument "`"$HealthScript`"" -WorkingDirectory $ProjectRoot
        
        # Create triggers for:
        # 1. Daily at 8:00 AM for status report
        # 2. Every 30 minutes for health checks
        $dailyTrigger = New-ScheduledTaskTrigger -Daily -At "08:00"
        $healthTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)
        
        # Task settings
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
        
        # Principal (run as SYSTEM for reliability)
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        # Register the task
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($dailyTrigger, $healthTrigger) -Settings $settings -Principal $principal -Description "Monitors Fluidd tunnel health and sends daily status reports"
        
        Write-Host "✅ Health monitoring task installed successfully" -ForegroundColor Green
        Write-Host "Task will run:" -ForegroundColor Cyan
        Write-Host "  - Daily at 8:00 AM for status reports" -ForegroundColor White
        Write-Host "  - Every 30 minutes for health checks" -ForegroundColor White
        
        return $true
    }
    catch {
        Write-Error "Error installing task: $($_.Exception.Message)"
        return $false
    }
}

function Uninstall-MonitoringTask {
    Write-Host "`nUninstalling health monitoring task..." -ForegroundColor Yellow
    
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Health monitoring task uninstalled successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Error uninstalling task: $($_.Exception.Message)"
        return $false
    }
}

function Get-TaskStatus {
    Write-Host "`nHealth Monitoring Task Status:" -ForegroundColor Cyan
    
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "Task Name: $($task.TaskName)"
            Write-Host "State: $($task.State)"
            Write-Host "Description: $($task.Description)"
            
            # Get last run info
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            Write-Host "Last Run Time: $($taskInfo.LastRunTime)"
            Write-Host "Last Result: $($taskInfo.LastTaskResult)"
            Write-Host "Next Run Time: $($taskInfo.NextRunTime)"
            
            # Show triggers
            Write-Host "`nTriggers:"
            foreach ($trigger in $task.Triggers) {
                Write-Host "  - $($trigger.TriggerType): $($trigger.StartBoundary)"
                if ($trigger.Repetition.Interval) {
                    Write-Host "    Repeats every: $($trigger.Repetition.Interval)"
                }
            }
            
        } else {
            Write-Host "Task not found" -ForegroundColor Red
        }
    }
    catch {
        Write-Error "Error getting task status: $($_.Exception.Message)"
    }
}

# Main execution
switch ($Action.ToLower()) {
    "install" {
        if (Install-MonitoringTask) {
            Write-Host "`n🎉 Health monitoring setup completed!" -ForegroundColor Green
            Write-Host "The system will now automatically:" -ForegroundColor Cyan
            Write-Host "  - Send daily status reports at 8 AM" -ForegroundColor White
            Write-Host "  - Perform health checks every 30 minutes" -ForegroundColor White
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