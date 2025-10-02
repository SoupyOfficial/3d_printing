# README: Fluidd Tunnel Service

## What is this?

This service automatically manages a cloudflared tunnel for your Fluidd 3D printer interface, ensuring it's always available and restarts if it crashes.

## Quick Start

### 1. One-time Setup (requires Administrator)

```bash
# Open PowerShell as Administrator
cd tools
.\install_service.ps1 install
```

### 2. Start the Service

```bash
python service_manager.py start
```

### 3. Check if it's working

```bash
python service_manager.py status
```

The tunnel URL will be automatically sent to your phone via SMS (if configured) and saved to `logs/cloudflared_url.txt`.

## VS Code Integration

Use `Ctrl+Shift+P` and search for these tasks:

- `service:install` - Install as Windows service
- `service:start` - Start the service  
- `service:stop` - Stop the service
- `service:status` - Check status and view URL
- `service:view-logs` - Open logs in VS Code

## Features

✅ **Starts automatically** when Windows boots  
✅ **Restarts automatically** if cloudflared crashes  
✅ **SMS notifications** with tunnel URL  
✅ **Clean process management** - stops existing tunnels before starting  
✅ **Detailed logging** in `logs/cloudflared_service.log`  
✅ **URL tracking** in `logs/cloudflared_url.txt`  

## Configuration

Edit `.env` in the project root:

```
GOOGLE_APP_PASS=your_gmail_app_password_here
CLOUD_FLARED_PATH=C:\path\to\cloudflared.exe  # Optional, defaults to Downloads
```

## Troubleshooting

**Service won't install?**
- Run PowerShell as Administrator
- Install dependencies: `pip install --user psutil pywin32`

**No SMS notifications?**
- Set `GOOGLE_APP_PASS` in `.env` file
- Use Gmail app password (not regular password)

**Service crashes?**
- Check `logs/cloudflared_service.log`
- Verify cloudflared.exe is in Downloads folder or set `CLOUD_FLARED_PATH`

**Need to uninstall?**
```bash
.\install_service.ps1 uninstall
```