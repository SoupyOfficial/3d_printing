#!/usr/bin/env python3
# health_monitor.py -- Standalone health monitoring for Fluidd tunnel
# Run: python health_monitor.py

import json
import time
import smtplib
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from email.message import EmailMessage

def load_env():
    """Load environment variables from .env file"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"): 
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def get_current_url():
    """Get current tunnel URL"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    url_file = project_root / "logs" / "cloudflared_url.txt"
    
    if url_file.exists():
        try:
            content = url_file.read_text().strip()
            lines = content.split('\n')
            return lines[0] if lines else None
        except Exception:
            return None
    return None

def load_status():
    """Load service status from JSON file"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    status_file = project_root / "logs" / "service_status.json"
    
    try:
        if status_file.exists():
            with open(status_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load status: {e}")
    return {}

def save_status(status_data):
    """Save service status to JSON file"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    status_file = project_root / "logs" / "service_status.json"
    
    try:
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2, default=str)
    except Exception as e:
        print(f"Failed to save status: {e}")

def check_url_health(url, timeout=10):
    """Check if tunnel URL is accessible"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Fluidd-Health-Monitor/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.getcode() == 200
    except Exception as e:
        print(f"Health check failed for {url}: {e}")
        return False

def should_send_daily_report(last_report_str):
    """Check if it's time to send daily status report (8 AM)"""
    now = datetime.now()
    target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # If we've passed 8 AM today and haven't sent report yet
    if now >= target_time:
        # Check if we already sent today's report
        if last_report_str:
            try:
                last_report_date = datetime.fromisoformat(last_report_str).date()
                if last_report_date >= now.date():
                    return False  # Already sent today
            except ValueError:
                pass  # Invalid date format, send report
        return True
    
    return False

def send_sms(subject, message):
    """Send SMS message"""
    env = load_env()
    
    if "GOOGLE_APP_PASS" not in env:
        print("❌ GOOGLE_APP_PASS not found in .env file")
        return False
    
    gmail_user = "soupsterx@gmail.com"
    sms_addr = "3216981359@vtext.com"
    
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = sms_addr

        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.ehlo()
            s.starttls()
            s.login(gmail_user, env["GOOGLE_APP_PASS"])
            s.send_message(msg)
        
        return True
    except Exception as e:
        print(f"SMS failed: {e}")
        return False

def get_service_status():
    """Check if the Windows service is running"""
    try:
        import subprocess
        result = subprocess.run("sc query FluiddTunnel", shell=True, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return "RUNNING" in result.stdout
        return False
    except Exception:
        return False

def get_process_info():
    """Get cloudflared process information"""
    try:
        import subprocess
        result = subprocess.run("tasklist /FI \"IMAGENAME eq cloudflared.exe\"", 
                              shell=True, capture_output=True, text=True)
        if "cloudflared.exe" in result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "cloudflared.exe" in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return {"pid": parts[1], "status": "Running"}
        return {"status": "Not running"}
    except Exception:
        return {"status": "Unknown"}

def send_daily_status_report():
    """Send comprehensive daily status report"""
    print("📊 Generating daily status report...")
    
    # Get current status
    current_url = get_current_url()
    status = load_status()
    
    # Check health
    url_healthy = check_url_health(current_url) if current_url else False
    service_running = get_service_status()
    process_info = get_process_info()
    
    # Calculate uptime
    uptime_str = "Unknown"
    if status.get("tunnel_start_time"):
        try:
            start_time = datetime.fromisoformat(status["tunnel_start_time"])
            uptime = datetime.now() - start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        except ValueError:
            pass
    
    # Build status message
    now = datetime.now()
    status_msg = f"""🌅 Fluidd Daily Status Report

🕐 Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
🔗 Current URL: {current_url or 'None'}
🌐 URL Health: {'✅ Accessible' if url_healthy else '❌ Not accessible' if current_url else '❓ No URL'}
⚙️ Service: {'✅ Running' if service_running else '❌ Not running'}
🖥️ Process: {process_info.get('status', 'Unknown')}
⏱️ Uptime: {uptime_str}
🔄 Restarts: {status.get('restart_count', 0)}
📊 Overall: {'✅ Healthy' if (url_healthy and service_running) else '⚠️ Issues detected'}

Daily 8 AM status check complete."""

    # Send SMS
    if send_sms("Fluidd Daily Status", status_msg):
        print("✅ Daily status report sent successfully")
        
        # Update status with report timestamp
        status["last_report"] = now.isoformat()
        status["last_health_check"] = now.isoformat()
        save_status(status)
        
        return True
    else:
        print("❌ Failed to send daily status report")
        return False

def perform_health_check():
    """Perform immediate health check"""
    print("🔍 Performing health check...")
    
    current_url = get_current_url()
    status = load_status()
    
    if not current_url:
        print("❌ No tunnel URL found")
        return False
    
    print(f"🔗 Checking URL: {current_url}")
    
    # Test accessibility
    is_healthy = check_url_health(current_url)
    
    if is_healthy:
        print("✅ Tunnel is accessible and healthy")
    else:
        print("❌ Tunnel is not accessible")
        
        # Send alert if this is a new issue
        alert_msg = f"⚠️ Fluidd tunnel health check failed at {datetime.now().strftime('%H:%M:%S')}.\n\nURL: {current_url}\n\nThe tunnel may be down or unreachable."
        send_sms("Fluidd Health Alert", alert_msg)
    
    # Update status
    status["last_health_check"] = datetime.now().isoformat()
    status["url_healthy"] = is_healthy
    save_status(status)
    
    return is_healthy

def main():
    print("🔧 Fluidd Tunnel Health Monitor")
    print("=" * 40)
    
    # Load current status
    status = load_status()
    
    # Check if daily report should be sent
    if should_send_daily_report(status.get("last_report")):
        print("📅 Time for daily status report...")
        send_daily_status_report()
    else:
        print("📅 Daily report already sent or not time yet")
        
        # Perform regular health check
        perform_health_check()
    
    print("\n✅ Health monitoring complete!")

if __name__ == "__main__":
    main()