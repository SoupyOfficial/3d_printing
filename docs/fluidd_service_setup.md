# Fluidd Tunnel Service Setup Guide

This guide explains how to set up the Fluidd cloudflared tunnel as a Windows service that starts automatically and restarts on crashes.

## Quick Setup

### 1. Install Required Dependencies

```bash
pip install psutil pywin32
```

### 2. Install the Service (as Administrator)

**Option A: Using PowerShell (Recommended)**
```powershell
# Run PowerShell as Administrator
cd tools
.\install_service.ps1 install
```

**Option B: Using Python**
```bash
# Run Command Prompt as Administrator
cd tools
python service_manager.py install
```

### 3. Start the Service

```bash
python service_manager.py start
```

## VS Code Integration

Use the VS Code Command Palette (`Ctrl+Shift+P`) and run these tasks:

- **Install Service**: `Tasks: Run Task` → `service:install`
- **Start Service**: `Tasks: Run Task` → `service:start`
- **Stop Service**: `Tasks: Run Task` → `service:stop`
- **Restart Service**: `Tasks: Run Task` → `service:restart`
- **Check Status**: `Tasks: Run Task` → `service:status`
- **View Logs**: `Tasks: Run Task` → `service:view-logs`
- **Uninstall Service**: `Tasks: Run Task` → `service:uninstall`

## Service Features

✅ **Auto-start on boot**: Service starts automatically when Windows starts  
✅ **Auto-restart on crash**: Service restarts if cloudflared crashes  
✅ **Process cleanup**: Stops existing cloudflared before starting new ones  
✅ **SMS notifications**: Sends tunnel URL via SMS (if configured)  
✅ **Detailed logging**: Logs to `logs/cloudflared_service.log`  
✅ **URL tracking**: Saves current URL to `logs/cloudflared_url.txt`  

## Configuration

The service uses the same `.env` file as the standalone scripts:

```
GOOGLE_APP_PASS=your_gmail_app_password
CLOUD_FLARED_PATH=C:\path\to\cloudflared.exe  # Optional
```

## Service Management Commands

### PowerShell Script (requires Admin)
```powershell
.\install_service.ps1 [install|start|stop|restart|status|uninstall]
```

### Python Script
```bash
python service_manager.py [install|start|stop|restart|status|uninstall]
```

### Windows Service Manager
```bash
# View in Services app
services.msc

# Command line management
sc start FluiddTunnel
sc stop FluiddTunnel
sc query FluiddTunnel
```

## Logs and Monitoring

- **Service logs**: `logs/cloudflared_service.log`
- **Current URL**: `logs/cloudflared_url.txt`
- **Windows Event Log**: Look for "Fluidd Tunnel Service" entries

## Troubleshooting

### Service won't install
- Run PowerShell/Command Prompt as Administrator
- Ensure Python and pip are in PATH
- Install dependencies: `pip install psutil pywin32`

### Service won't start
- Check `logs/cloudflared_service.log` for errors
- Verify `.env` file exists and is readable
- Ensure cloudflared.exe path is correct

### No SMS notifications
- Verify `GOOGLE_APP_PASS` is set in `.env`
- Check Gmail app password is valid
- Review service logs for SMS errors

### Service crashes repeatedly
- Check Windows Event Viewer
- Review service logs
- Ensure cloudflared.exe is not corrupted
- Verify network connectivity

## Migration from Standalone Scripts

If you were using the standalone Python/PowerShell scripts:

1. Stop any running scripts (`Ctrl+C`)
2. Install the service as described above
3. The service will handle everything automatically
4. Use VS Code tasks or command-line tools to manage

## Uninstalling

To completely remove the service:

```bash
# Stop and remove service
python service_manager.py uninstall

# Or using PowerShell (as Admin)
.\install_service.ps1 uninstall
```

The service files and logs will remain for manual cleanup if needed.