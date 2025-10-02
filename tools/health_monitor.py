#!/usr/bin/env python3
# health_monitor.py -- Standalone health monitoring for Fluidd tunnel
# Run: python health_monitor.py [--status-report | --health-check]

import json
import time
import smtplib
import urllib.request
import urllib.error
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from email.message import EmailMessage

# Setup dual logging (console + file)
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)
health_log_file = logs_dir / "health_monitor.log"

def dual_log(message, prefix="INFO"):
    """Log to both console and file"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {prefix}: {message}"
    
    # Console output
    try:
        print(log_line)
        sys.stdout.flush()
    except Exception:
        pass
    
    # File output
    try:
        with open(health_log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        pass

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
    """Send SMS message with verbose logging and email backup"""
    env = load_env()
    
    if "GOOGLE_APP_PASS" not in env:
        dual_log("GOOGLE_APP_PASS not found in .env file", "ERROR")
        return False
    
    gmail_user = "soupsterx@gmail.com"
    sms_addr = "3216981359@vtext.com"
    email_addr = "soupsterx@gmail.com"
    
    dual_log("Preparing notification...")
    dual_log(f"Subject: {subject}")
    dual_log(f"Message: {message}")
    dual_log(f"Message length: {len(message)} characters")
    dual_log(f"SMS target: {sms_addr}")
    dual_log(f"Email target: {email_addr}")
    
    sms_success = False
    email_success = False
    
    try:
        dual_log("Connecting to Gmail SMTP...")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            dual_log("Starting TLS encryption...")
            s.ehlo()
            s.starttls()
            
            dual_log("Authenticating...")
            s.login(gmail_user, env["GOOGLE_APP_PASS"])
            dual_log("SMTP authentication successful")
            
            # Send SMS
            dual_log("Sending SMS...")
            sms_msg = EmailMessage()
            sms_msg.set_content(message)
            sms_msg["Subject"] = subject
            sms_msg["From"] = gmail_user
            sms_msg["To"] = sms_addr
            
            s.send_message(sms_msg)
            sms_success = True
            dual_log("SMS sent successfully!")
            
            # Send backup email
            dual_log("Sending backup email...")
            email_msg = EmailMessage()
            email_body = f"Health Monitor Notification\n\nSubject: {subject}\nMessage: {message}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis is a backup delivery."
            email_msg.set_content(email_body)
            email_msg["Subject"] = f"[Health Monitor Backup] {subject}"
            email_msg["From"] = gmail_user
            email_msg["To"] = email_addr
            
            s.send_message(email_msg)
            email_success = True
            dual_log("Backup email sent successfully!")
        
        dual_log("Delivery Summary:")
        dual_log(f"SMS: {'Success' if sms_success else 'Failed'}")
        dual_log(f"Email: {'Success' if email_success else 'Failed'}")
        
        return sms_success or email_success
        
    except smtplib.SMTPAuthenticationError as e:
        dual_log(f"SMTP Authentication failed: {e}", "ERROR")
        dual_log("Check GOOGLE_APP_PASS in .env file", "ERROR")
        return False
    except Exception as e:
        dual_log(f"Notification failed: {type(e).__name__}: {e}", "ERROR")
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
    dual_log("Generating daily status report...")
    
    # Get current status
    current_url = get_current_url()
    service_running = get_service_status()
    process_info = get_process_info()
    url_healthy = check_url_health(current_url) if current_url else False
    
    # Calculate uptime
    status = load_status()
    last_start = status.get('last_start')
    uptime_str = "Unknown"
    if last_start:
        try:
            start_time = datetime.fromisoformat(last_start)
            uptime = datetime.now() - start_time
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            uptime_str = f"{int(hours)}:{int(minutes):02d}"
        except Exception:
            uptime_str = "Unknown"
    
    now = datetime.now()
    
    # Create compact status message to avoid SMS truncation
    health_icon = "OK" if (url_healthy and service_running) else "ISSUE"
    url_short = current_url.replace("https://", "") if current_url else "None"
    
    status_msg = f"Fluidd Status {now.strftime('%H:%M')}: {health_icon} | URL: {url_short} | Uptime: {uptime_str}"

    # Send SMS with compact format
    if send_sms("Fluidd Status", status_msg):
        dual_log("Daily status report sent successfully")
        
        # Update status with report timestamp
        status["last_report"] = now.isoformat()
        status["last_health_check"] = now.isoformat()
        save_status(status)
        
        return True
    else:
        dual_log("Failed to send daily status report", "ERROR")
        return False

def perform_health_check():
    """Perform immediate health check (silent - no SMS unless there's an issue)"""
    print("🔍 Performing silent health check...")
    
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
        
        # Only send alert if this is a new issue (hasn't been down for a while)
        last_check = status.get("last_health_check")
        url_was_healthy = status.get("url_healthy", True)
        
        # Send alert only if tunnel was previously healthy
        if url_was_healthy:
            alert_msg = f"⚠️ Fluidd tunnel health check failed at {datetime.now().strftime('%H:%M:%S')}.\n\nURL: {current_url}\n\nThe tunnel may be down or unreachable."
            send_sms("Fluidd Health Alert", alert_msg)
            print("📱 Alert SMS sent")
        else:
            print("ℹ️ Tunnel still down - no alert sent to avoid spam")
    
    # Update status
    status["last_health_check"] = datetime.now().isoformat()
    status["url_healthy"] = is_healthy
    save_status(status)
    
    return is_healthy

def main():
    parser = argparse.ArgumentParser(description='Fluidd Tunnel Health Monitor')
    parser.add_argument('--status-report', action='store_true', 
                       help='Send status report (used by scheduled task)')
    parser.add_argument('--health-check', action='store_true',
                       help='Perform silent health check only')
    
    args = parser.parse_args()
    
    print("🔧 Fluidd Tunnel Health Monitor")
    print("=" * 40)
    
    if args.status_report:
        print("📅 Sending scheduled status report...")
        success = send_daily_status_report()
        if success:
            print("✅ Status report sent successfully!")
        else:
            print("❌ Failed to send status report")
        return
    
    elif args.health_check:
        print("🔍 Performing scheduled health check...")
        is_healthy = perform_health_check()
        print(f"Health status: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
        return
    
    else:
        # Default behavior - legacy mode
        print("ℹ️ Running in legacy mode...")
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