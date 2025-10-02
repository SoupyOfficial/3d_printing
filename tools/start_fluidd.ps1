# start_fluidd.ps1 -- Start cloudflared tunnel for Fluidd and send URL via SMS

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$EnvFile = Join-Path $ProjectRoot ".env"
$LogsDir = Join-Path $ProjectRoot "logs"

Write-Host "Project root: $ProjectRoot"
Write-Host ".env file: $EnvFile"

# Ensure logs directory exists
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null }

if (-not (Test-Path $EnvFile)) { 
    Write-Error ".env not found at $EnvFile"
    exit 1 
}

# Stop any existing cloudflared processes
Write-Host "Checking for existing cloudflared processes..."
$existingProcs = Get-Process -Name cloudflared -ErrorAction SilentlyContinue
if ($existingProcs) {
    Write-Host "Found $($existingProcs.Count) existing cloudflared process(es)"
    $existingProcs | ForEach-Object {
        Write-Host "Stopping cloudflared process (PID: $($_.Id))"
        $_ | Stop-Process -Force
    }
    Start-Sleep -Seconds 2
    Write-Host "Stopped existing cloudflared processes"
}

# load .env simple parser
Get-Content $EnvFile | ForEach-Object {
  if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
    Set-Variable -Name ($matches[1].Trim()) -Value ($matches[2].Trim()) -Scope Script
  }
}

if (-not $script:GOOGLE_APP_PASS) { Write-Error "GOOGLE_APP_PASS not set in .env"; exit 1 }

# settings
$gmailUser = "soupsterx@gmail.com"
$toSms = "3216981359@vtext.com"
$cloudflaredPath = $script:CLOUD_FLARED_PATH
if (-not $cloudflaredPath) { $cloudflaredPath = Join-Path $env:USERPROFILE "Downloads\cloudflared.exe" }
if (-not (Test-Path $cloudflaredPath)) { 
    Write-Error "cloudflared not found at $cloudflaredPath"
    exit 1 
}

# Use proper log directory structure
$logFile = Join-Path $LogsDir "cloudflared_tunnel.log"
$urlFile = Join-Path $LogsDir "cloudflared_url.txt"

Write-Host "Logging to: $logFile"
Write-Host "URL will be saved to: $urlFile"

# Clean up old files
Remove-Item $logFile, $urlFile -ErrorAction SilentlyContinue

# start process and capture stdout
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $cloudflaredPath
$psi.Arguments = "tunnel --url http://127.0.0.1:4408"
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi

Write-Host "Starting cloudflared tunnel..."
$proc.Start() | Out-Null

# Initialize log file
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"Cloudflared tunnel started at $timestamp" | Out-File -FilePath $logFile -Encoding utf8
"Command: $cloudflaredPath tunnel --url http://127.0.0.1:4408" | Out-File -FilePath $logFile -Append -Encoding utf8
"-" * 50 | Out-File -FilePath $logFile -Append -Encoding utf8

$sw = [diagnostics.stopwatch]::StartNew()
$timeout = 30
$url = $null

while ($sw.Elapsed.TotalSeconds -lt $timeout -and -not $proc.HasExited) {
    if (-not $proc.StandardOutput.EndOfStream) {
        $line = $proc.StandardOutput.ReadLine()
        if ($line) { 
            $line | Out-File -FilePath $logFile -Append -Encoding utf8
            Write-Host "cloudflared: $line"
            
            $m = [regex]::Match($line, 'https://[A-Za-z0-9\-]+\.trycloudflare\.com')
            if ($m.Success) { 
                $url = $m.Value
                break 
            }
        }
    }
    Start-Sleep -Milliseconds 200
}

if (-not $url) {
    Write-Error "No trycloudflare URL found within ${timeout}s. Check $logFile"
    $proc.Kill()
    exit 1
}

# Save URL with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
@"
$url
Generated at: $timestamp
"@ | Out-File -FilePath $urlFile -Encoding utf8

Write-Host "Tunnel URL: $url"

# email via Gmail SMTP (use app password from .env)
try {
    $plainPass = $script:GOOGLE_APP_PASS
    $securePass = ConvertTo-SecureString $plainPass -AsPlainText -Force
    $cred = New-Object System.Management.Automation.PSCredential ($gmailUser, $securePass)

    $body = "Fluidd tunnel is ready:`n$url"
    Send-MailMessage -SmtpServer "smtp.gmail.com" -Port 587 -UseSsl `
        -Credential $cred -From $gmailUser -To $toSms -Subject "Fluidd Tunnel URL" -Body $body

    Write-Host "SMS sent to $toSms"
    
    # Log successful SMS
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "SMS sent successfully to $toSms at $timestamp" | Out-File -FilePath $logFile -Append -Encoding utf8
}
catch {
    Write-Warning "Failed to send SMS: $($_.Exception.Message)"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "SMS failed: $($_.Exception.Message) at $timestamp" | Out-File -FilePath $logFile -Append -Encoding utf8
}

Write-Host "`nTunnel is running. Press Ctrl+C to stop..."
try {
    while (-not $proc.HasExited) {
        Start-Sleep -Seconds 1
    }
}
finally {
    if (-not $proc.HasExited) {
        Write-Host "Shutting down tunnel..."
        $proc.Kill()
        $proc.WaitForExit()
        Write-Host "Tunnel stopped."
    }
}
# process remains running. To stop later:
# Get-Process -Name cloudflared -ErrorAction SilentlyContinue | Stop-Process
