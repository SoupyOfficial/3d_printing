# service_manager.py -- Simple service management script
# Run: python service_manager.py [install|start|stop|restart|status|uninstall]

import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} successful")
            if result.stdout.strip():
                print(result.stdout.strip())
            return True
        else:
            print(f"✗ {description} failed")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"✗ {description} failed: {e}")
        return False

def check_admin():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def install_requirements():
    """Install required Python packages"""
    packages = ["psutil", "pywin32"]
    for package in packages:
        print(f"Checking {package}...")
        result = subprocess.run([sys.executable, "-c", f"import {package}"], 
                              capture_output=True)
        if result.returncode != 0:
            print(f"Installing {package}...")
            if not run_command(f"{sys.executable} -m pip install {package}", 
                             f"Install {package}"):
                return False
        else:
            print(f"✓ {package} is available")
    return True

def main():
    script_dir = Path(__file__).resolve().parent
    service_script = script_dir / "fluidd_service.py"
    
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    
    print("Fluidd Tunnel Service Manager")
    print(f"Service script: {service_script}")
    print(f"Action: {action}")
    print()
    
    if not service_script.exists():
        print(f"✗ Service script not found: {service_script}")
        return 1
    
    if action in ["install", "start", "stop", "restart"]:
        if not check_admin():
            print("✗ Administrator privileges required for this action")
            print("Run PowerShell as Administrator or use 'Run as administrator'")
            return 1
    
    if action == "install":
        print("Installing service requirements...")
        if not install_requirements():
            print("✗ Failed to install requirements")
            return 1
        
        if run_command(f'"{sys.executable}" "{service_script}" install', 
                      "Install service"):
            run_command("sc config FluiddTunnel start=auto", 
                       "Configure auto-start")
            run_command("sc failure FluiddTunnel reset=300 actions=restart/5000/restart/10000/restart/30000", 
                       "Configure restart on failure")
            print("\n✓ Service installed and configured!")
            print("To start: python service_manager.py start")
        
    elif action == "start":
        run_command(f'"{sys.executable}" "{service_script}" start', "Start service")
        
    elif action == "stop":
        run_command(f'"{sys.executable}" "{service_script}" stop', "Stop service")
        
    elif action == "restart":
        run_command(f'"{sys.executable}" "{service_script}" stop', "Stop service")
        time.sleep(2)
        run_command(f'"{sys.executable}" "{service_script}" start', "Start service")
        
    elif action == "uninstall":
        run_command(f'"{sys.executable}" "{service_script}" stop', "Stop service")
        run_command(f'"{sys.executable}" "{service_script}" remove', "Remove service")
        
    elif action == "status":
        # Check service status
        result = subprocess.run("sc query FluiddTunnel", shell=True, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Service Status:")
            print(result.stdout)
        else:
            print("✗ Service not found or not accessible")
        
        # Check for cloudflared processes
        result = subprocess.run("tasklist /FI \"IMAGENAME eq cloudflared.exe\"", 
                              shell=True, capture_output=True, text=True)
        if "cloudflared.exe" in result.stdout:
            print("\nRunning cloudflared processes:")
            print(result.stdout)
        else:
            print("\n✗ No cloudflared processes running")
        
        # Check log files
        logs_dir = script_dir.parent / "logs"
        log_file = logs_dir / "cloudflared_service.log"
        url_file = logs_dir / "cloudflared_url.txt"
        
        if log_file.exists():
            print(f"\nLog file: {log_file} ({log_file.stat().st_size} bytes)")
        else:
            print(f"\n✗ Log file not found: {log_file}")
            
        if url_file.exists():
            print(f"URL file: {url_file}")
            try:
                url_content = url_file.read_text().strip()
                print(f"Current URL:\n{url_content}")
            except Exception as e:
                print(f"✗ Could not read URL file: {e}")
        else:
            print(f"✗ URL file not found: {url_file}")
    
    else:
        print(f"Unknown action: {action}")
        print("Valid actions: install, start, stop, restart, status, uninstall")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())