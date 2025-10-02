#!/usr/bin/env python3
# monitoring_dashboard.py -- Real-time monitoring dashboard for Fluidd tunnel
# Run: python monitoring_dashboard.py

import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def load_status():
    """Load service status from JSON file"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    status_file = project_root / "logs" / "service_status.json"
    
    try:
        if status_file.exists():
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def get_current_url():
    """Get current tunnel URL"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    url_file = project_root / "logs" / "cloudflared_url.txt"
    
    if url_file.exists():
        try:
            content = url_file.read_text().strip()
            lines = content.split('\n')
            if lines:
                return lines[0], lines[1] if len(lines) > 1 else ""
        except Exception:
            pass
    return None, None

def get_service_status():
    """Check Windows service status"""
    try:
        result = subprocess.run("sc query FluiddTunnel", shell=True, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if "RUNNING" in result.stdout:
                return "🟢 Running"
            elif "STOPPED" in result.stdout:
                return "🔴 Stopped"
            else:
                return "🟡 Unknown"
        return "❌ Not installed"
    except Exception:
        return "❓ Error checking"

def get_process_info():
    """Get cloudflared process information"""
    try:
        result = subprocess.run("tasklist /FI \"IMAGENAME eq cloudflared.exe\"", 
                              shell=True, capture_output=True, text=True)
        if "cloudflared.exe" in result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "cloudflared.exe" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        return f"🟢 PID: {parts[1]}, Memory: {parts[4]}"
        return "🔴 Not running"
    except Exception:
        return "❓ Error checking"

def get_task_status():
    """Get scheduled task status"""
    try:
        result = subprocess.run("schtasks /query /tn FluiddTunnelHealthMonitor", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if "Ready" in result.stdout or "Running" in result.stdout:
                return "🟢 Active"
            else:
                return "🟡 Inactive"
        return "❌ Not installed"
    except Exception:
        return "❓ Error checking"

def get_log_tail():
    """Get last few lines from service log"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    log_file = project_root / "logs" / "cloudflared_service.log"
    
    try:
        if log_file.exists():
            content = log_file.read_text(encoding='utf-8')
            lines = content.strip().split('\n')
            return lines[-5:] if len(lines) >= 5 else lines
        return ["No log file found"]
    except Exception as e:
        return [f"Error reading log: {e}"]

def format_uptime(start_time_str):
    """Format uptime from start time string"""
    try:
        start_time = datetime.fromisoformat(start_time_str)
        uptime = datetime.now() - start_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except Exception:
        return "Unknown"

def display_dashboard():
    """Display the monitoring dashboard"""
    now = datetime.now()
    status = load_status()
    url, url_timestamp = get_current_url()
    
    print("🔧 FLUIDD TUNNEL MONITORING DASHBOARD")
    print("=" * 70)
    print(f"📅 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔄 Auto-refresh: Every 5 seconds (Ctrl+C to exit)")
    print()
    
    # Service Status Section
    print("📊 SERVICE STATUS")
    print("-" * 30)
    print(f"Windows Service: {get_service_status()}")
    print(f"CloudFlared Process: {get_process_info()}")
    print(f"Health Monitor Task: {get_task_status()}")
    print()
    
    # Tunnel Information
    print("🌐 TUNNEL INFORMATION")
    print("-" * 30)
    if url:
        print(f"Current URL: {url}")
        print(f"Generated: {url_timestamp}")
        
        # Health status
        last_health = status.get("last_health_check")
        if last_health:
            try:
                health_time = datetime.fromisoformat(last_health)
                health_age = now - health_time
                if health_age.total_seconds() < 600:  # Less than 10 minutes
                    health_status = "🟢 Recent" if status.get("url_healthy", False) else "🔴 Failed"
                else:
                    health_status = "🟡 Stale"
                print(f"Health Check: {health_status} ({health_age.total_seconds():.0f}s ago)")
            except Exception:
                print("Health Check: ❓ Unknown")
        else:
            print("Health Check: ❓ No data")
    else:
        print("Current URL: ❌ None available")
    print()
    
    # Uptime and Statistics
    print("📈 STATISTICS")
    print("-" * 30)
    tunnel_start = status.get("tunnel_start_time")
    if tunnel_start:
        print(f"Uptime: {format_uptime(tunnel_start)}")
    else:
        print("Uptime: Unknown")
    
    restart_count = status.get("restart_count", 0)
    print(f"Restarts Today: {restart_count}")
    
    last_report = status.get("last_report")
    if last_report:
        try:
            report_time = datetime.fromisoformat(last_report)
            report_age = now - report_time
            if report_age.days == 0:
                print(f"Last Daily Report: Today at {report_time.strftime('%H:%M')}")
            else:
                print(f"Last Daily Report: {report_age.days} days ago")
        except Exception:
            print("Last Daily Report: Invalid timestamp")
    else:
        print("Last Daily Report: None sent")
    print()
    
    # Recent Log Entries
    print("📋 RECENT LOG ENTRIES")
    print("-" * 30)
    log_lines = get_log_tail()
    for line in log_lines:
        # Truncate long lines for display
        display_line = line[:65] + "..." if len(line) > 65 else line
        print(f"  {display_line}")
    print()
    
    # System Health Summary
    print("🏥 SYSTEM HEALTH SUMMARY")
    print("-" * 30)
    
    # Determine overall health
    service_ok = "Running" in get_service_status()
    process_ok = "PID:" in get_process_info()
    url_ok = url is not None
    health_ok = status.get("url_healthy", False)
    
    health_items = [
        ("Service Running", service_ok),
        ("Process Active", process_ok),
        ("URL Available", url_ok),
        ("URL Accessible", health_ok)
    ]
    
    healthy_count = sum(1 for _, ok in health_items if ok)
    
    for item, ok in health_items:
        status_icon = "✅" if ok else "❌"
        print(f"  {status_icon} {item}")
    
    if healthy_count == len(health_items):
        overall_status = "🟢 EXCELLENT"
    elif healthy_count >= len(health_items) - 1:
        overall_status = "🟡 GOOD"
    elif healthy_count >= len(health_items) // 2:
        overall_status = "🟠 FAIR"
    else:
        overall_status = "🔴 POOR"
    
    print(f"\nOverall Health: {overall_status} ({healthy_count}/{len(health_items)})")

def main():
    """Main dashboard loop"""
    try:
        while True:
            clear_screen()
            display_dashboard()
            print("\nPress Ctrl+C to exit...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed. Have a great day!")

if __name__ == "__main__":
    main()