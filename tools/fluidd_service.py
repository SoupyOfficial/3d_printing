# fluidd_service.py -- Windows service wrapper for cloudflared tunnel
# Install as service: python fluidd_service.py install
# Start service: python fluidd_service.py start
# Stop service: python fluidd_service.py stop
# Remove service: python fluidd_service.py remove

import os
import sys
import time
import threading
import subprocess
import re
import smtplib
import json
import hashlib
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path

# Try to import psutil and Windows service modules
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: pywin32 not installed. Install with: pip install pywin32")
    print("Service functionality requires pywin32")

class FluiddTunnelService(win32serviceutil.ServiceFramework):
    """Windows service for cloudflared tunnel"""
    
    _svc_name_ = "FluiddTunnel"
    _svc_display_name_ = "Fluidd Cloudflared Tunnel"
    _svc_description_ = "Maintains cloudflared tunnel for Fluidd 3D printer interface"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        
        # Setup paths
        script_dir = Path(__file__).resolve().parent
        self.project_root = script_dir.parent
        self.env_file = self.project_root / ".env"
        self.logs_dir = self.project_root / "logs"
        self.log_file = self.logs_dir / "cloudflared_service.log"
        self.url_file = self.logs_dir / "cloudflared_url.txt"
        self.status_file = self.logs_dir / "service_status.json"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load environment and initialize monitoring
        self.env = self._load_env()
        self.current_url = None
        self.tunnel_start_time = None
        self.last_status_report = None
        self.restart_count = 0
        self.health_check_interval = 30  # seconds
        self.status_report_time = "08:00"  # 8 AM daily report
        
    def _load_env(self):
        """Load environment variables from .env file"""
        env = {}
        if self.env_file.exists():
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"): 
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
        return env
    
    def _log(self, message):
        """Write to service log, console, and Windows event log"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        
        # Write to console (stdout) for real-time viewing
        try:
            print(log_line)
            sys.stdout.flush()
        except Exception:
            pass
        
        # Write to service log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception:
            pass
            
        # Also log to Windows event log
        try:
            servicemanager.LogInfoMsg(message)
        except Exception:
            pass
    
    def _stop_existing_cloudflared(self):
        """Stop any existing cloudflared processes"""
        stopped_count = 0
        
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                        self._log(f"Found existing cloudflared process (PID: {proc.info['pid']})")
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                            stopped_count += 1
                        except psutil.TimeoutExpired:
                            proc.kill()
                            stopped_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            try:
                result = subprocess.run(['taskkill', '/F', '/IM', 'cloudflared.exe'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    stopped_count = 1
            except Exception:
                pass
        
        if stopped_count > 0:
            self._log(f"Stopped {stopped_count} existing cloudflared process(es)")
            time.sleep(2)
        
        return stopped_count
    
    def _send_sms(self, url):
        """Send SMS notification with tunnel URL - with verbose logging and email backup"""
        if "GOOGLE_APP_PASS" not in self.env:
            self._log("SMS not configured - GOOGLE_APP_PASS not set")
            return False
            
        gmail_user = "soupsterx@gmail.com"
        sms_addr = "3216981359@vtext.com"
        email_addr = "soupsterx@gmail.com"
        max_retries = 3
        retry_delay = 2  # seconds
        
        # Create compact message
        body = f"Fluidd: {url} ({time.strftime('%H:%M')})"
        subject = "Fluidd URL"
        
        self._log(f"Preparing SMS notification:")
        self._log(f"  URL: {url}")
        self._log(f"  Message: {body}")
        self._log(f"  Length: {len(body)} characters")
        self._log(f"  SMS target: {sms_addr}")
        self._log(f"  Email backup: {email_addr}")
        
        sms_success = False
        email_success = False
        
        for attempt in range(1, max_retries + 1):
            try:
                self._log(f"SMS attempt {attempt}/{max_retries}")
                self._log("Connecting to Gmail SMTP...")
                
                with smtplib.SMTP("smtp.gmail.com", 587) as s:
                    s.ehlo()
                    s.starttls()
                    self._log("SMTP TLS connection established")
                    
                    s.login(gmail_user, self.env["GOOGLE_APP_PASS"])
                    self._log("SMTP authentication successful")
                    
                    # Send SMS
                    self._log(f"Sending SMS to {sms_addr}...")
                    sms_msg = EmailMessage()
                    sms_msg.set_content(body)
                    sms_msg["Subject"] = subject
                    sms_msg["From"] = gmail_user
                    sms_msg["To"] = sms_addr
                    
                    s.send_message(sms_msg)
                    sms_success = True
                    self._log(f"SMS sent successfully to {sms_addr} on attempt {attempt}")
                    
                    # Send backup email
                    self._log(f"Sending backup email to {email_addr}...")
                    email_msg = EmailMessage()
                    email_body = f"Fluidd Tunnel Notification\n\nURL: {url}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}\nMessage: {body}\n\nThis is a backup delivery."
                    email_msg.set_content(email_body)
                    email_msg["Subject"] = f"[Backup] {subject}"
                    email_msg["From"] = gmail_user
                    email_msg["To"] = email_addr
                    
                    s.send_message(email_msg)
                    email_success = True
                    self._log("Backup email sent successfully")
                    
                break  # Exit retry loop on success
                
            except smtplib.SMTPAuthenticationError as e:
                self._log(f"SMS authentication failed on attempt {attempt}: {e}")
                if attempt == max_retries:
                    self._log("SMS failed - check GOOGLE_APP_PASS in .env file")
                break  # Don't retry auth errors
                
            except Exception as e:
                self._log(f"SMS attempt {attempt} failed: {type(e).__name__}: {e}")
                if attempt < max_retries:
                    self._log(f"Retrying SMS in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    self._log("SMS failed after all retry attempts")
        
        # Log summary
        self._log(f"Notification delivery summary:")
        self._log(f"  SMS: {'Success' if sms_success else 'Failed'}")
        self._log(f"  Email: {'Success' if email_success else 'Failed'}")
        
        return sms_success or email_success  # Success if either method worked
    
    def _save_status(self, status_data):
        """Save service status to JSON file"""
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2, default=str)
        except Exception as e:
            self._log(f"Failed to save status: {e}")
    
    def _load_status(self):
        """Load service status from JSON file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self._log(f"Failed to load status: {e}")
        return {}
    
    def _check_url_health(self, url):
        """Check if tunnel URL is accessible"""
        try:
            import urllib.request
            import urllib.error
            import socket
            
            # Set timeout for health check
            socket.setdefaulttimeout(10)
            
            # Try to connect to the tunnel URL
            req = urllib.request.Request(url, headers={'User-Agent': 'Fluidd-Service-Monitor/1.0'})
            with urllib.request.urlopen(req) as response:
                return response.getcode() == 200
                
        except Exception as e:
            self._log(f"Health check failed for {url}: {e}")
            return False
    
    def _should_send_daily_report(self):
        """Check if it's time to send daily status report (8 AM)"""
        now = datetime.now()
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # If we've passed 8 AM today and haven't sent report yet
        if now >= target_time:
            # Check if we already sent today's report
            if self.last_status_report:
                last_report_date = datetime.fromisoformat(self.last_status_report).date()
                if last_report_date >= now.date():
                    return False  # Already sent today
            return True
        
        return False
    
    def _send_daily_status_report(self):
        """Send daily status report at 8 AM"""
        if not self._should_send_daily_report():
            return
            
        try:
            now = datetime.now()
            uptime = now - datetime.fromisoformat(self.tunnel_start_time) if self.tunnel_start_time else timedelta(0)
            
            # Health check current URL
            url_status = "✅ Accessible" if self._check_url_health(self.current_url) else "❌ Not accessible"
            
            # Get process info
            process_info = "Running" if self._get_cloudflared_process() else "Not running"
            
            status_msg = f"""🌅 Fluidd Daily Status Report
            
🕐 Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
🔗 Current URL: {self.current_url or 'None'}
🌐 URL Status: {url_status}
⚙️ Process: {process_info}
⏱️ Uptime: {str(uptime).split('.')[0]}
🔄 Restarts today: {self.restart_count}
📊 Service: Healthy

This is your daily 8 AM status check."""

            # Send status SMS
            if self._send_sms_raw("Fluidd Daily Status", status_msg):
                self.last_status_report = now.isoformat()
                self._log("Daily status report sent successfully")
                
                # Save status
                self._save_status({
                    "last_report": self.last_status_report,
                    "current_url": self.current_url,
                    "tunnel_start_time": self.tunnel_start_time,
                    "restart_count": self.restart_count,
                    "uptime_seconds": uptime.total_seconds()
                })
            else:
                self._log("Failed to send daily status report")
                
        except Exception as e:
            self._log(f"Error sending daily status report: {e}")
    
    def _get_cloudflared_process(self):
        """Get cloudflared process info"""
        if HAS_PSUTIL:
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                        return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        return None
    
    def _send_sms_raw(self, subject, message):
        """Send raw SMS message (used for status reports)"""
        if "GOOGLE_APP_PASS" not in self.env:
            return False
            
        try:
            gmail_user = "soupsterx@gmail.com"
            sms_addr = "3216981359@vtext.com"
            
            msg = EmailMessage()
            msg.set_content(message)
            msg["Subject"] = subject
            msg["From"] = gmail_user
            msg["To"] = sms_addr

            with smtplib.SMTP("smtp.gmail.com", 587) as s:
                s.ehlo()
                s.starttls()
                s.login(gmail_user, self.env["GOOGLE_APP_PASS"])
                s.send_message(msg)
            
            return True
        except Exception as e:
            self._log(f"Raw SMS failed: {e}")
            return False
    
    def _run_tunnel(self):
        """Run the cloudflared tunnel with monitoring"""
        # Get cloudflared path
        cloudflared_path = self.env.get("CLOUD_FLARED_PATH")
        if not cloudflared_path:
            cloudflared_path = str(Path.home() / "Downloads" / "cloudflared.exe")
        
        if not Path(cloudflared_path).exists():
            self._log(f"cloudflared not found at {cloudflared_path}")
            return None
            
        self._log(f"Starting cloudflared tunnel from {cloudflared_path}")
        
        # Start cloudflared process
        try:
            proc = subprocess.Popen(
                [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:4408"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1
            )
        except Exception as e:
            self._log(f"Failed to start cloudflared: {e}")
            return None
        
        # Monitor for URL
        url = None
        start_time = time.time()
        timeout = 30
        
        while time.time() - start_time < timeout and self.running:
            if proc.poll() is not None:
                self._log("cloudflared process exited unexpectedly")
                break
                
            try:
                line = proc.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                    
                line = line.strip()
                if line:
                    self._log(f"cloudflared: {line}")
                    
                    # Look for tunnel URL
                    m = re.search(r"https://[A-Za-z0-9\-]+\.trycloudflare\.com", line)
                    if m:
                        url = m.group(0)
                        break
                        
            except Exception as e:
                self._log(f"Error reading cloudflared output: {e}")
                break
        
        if url:
            self._log(f"Tunnel URL obtained: {url}")
            
            # Update service state
            self.current_url = url
            self.tunnel_start_time = datetime.now().isoformat()
            
            # Save URL to file
            try:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                self.url_file.write_text(f"{url}\nGenerated at: {timestamp}\n")
            except Exception as e:
                self._log(f"Failed to write URL file: {e}")
            
            # Send SMS notification
            self._send_sms(url)
            
            # Save initial status
            self._save_status({
                "current_url": self.current_url,
                "tunnel_start_time": self.tunnel_start_time,
                "restart_count": self.restart_count,
                "last_health_check": datetime.now().isoformat()
            })
            
            return proc
        else:
            self._log(f"No tunnel URL found within {timeout}s")
            try:
                proc.terminate()
            except Exception:
                pass
            return None
    
    def SvcStop(self):
        """Called when the service is asked to stop"""
        self._log("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
    
    def SvcDoRun(self):
        """Main service loop with monitoring and health checks"""
        self._log("Fluidd Tunnel Service starting")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        
        # Load previous status
        status = self._load_status()
        self.last_status_report = status.get("last_report")
        self.restart_count = 0  # Reset daily restart count
        
        retry_delay = 5  # seconds between restart attempts
        max_retry_delay = 300  # max 5 minutes
        last_health_check = time.time()
        health_check_interval = 300  # 5 minutes
        
        while self.running:
            try:
                # Check for daily status report
                self._send_daily_status_report()
                
                # Stop any existing cloudflared processes
                self._stop_existing_cloudflared()
                
                # Start new tunnel
                proc = self._run_tunnel()
                
                if proc is None:
                    self._log(f"Failed to start tunnel, retrying in {retry_delay}s")
                    if win32event.WaitForSingleObject(self.hWaitStop, retry_delay * 1000) == win32event.WAIT_OBJECT_0:
                        break
                    retry_delay = min(retry_delay * 2, max_retry_delay)
                    continue
                
                # Reset retry delay on successful start
                retry_delay = 5
                self._log("Tunnel started successfully, monitoring...")
                
                # Monitor the process with health checks
                while self.running and proc.poll() is None:
                    # Wait with timeout for health checking
                    if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                        break
                    
                    # Perform periodic health checks
                    current_time = time.time()
                    if current_time - last_health_check > health_check_interval:
                        self._log("Performing health check...")
                        
                        # Check if URL is still accessible
                        if self.current_url:
                            if self._check_url_health(self.current_url):
                                self._log("Health check passed - tunnel is accessible")
                            else:
                                self._log("Health check failed - tunnel may be unreachable")
                        
                        # Check for daily status report
                        self._send_daily_status_report()
                        
                        last_health_check = current_time
                
                # Process exited or service stopping
                if self.running:
                    self.restart_count += 1
                    self._log(f"Tunnel process exited unexpectedly (restart #{self.restart_count}), restarting...")
                    
                    # Send restart notification if this is frequent
                    if self.restart_count > 3:
                        restart_msg = f"⚠️ Fluidd tunnel has restarted {self.restart_count} times today. Service is still running but may need attention."
                        self._send_sms_raw("Fluidd Multiple Restarts", restart_msg)
                    
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                else:
                    self._log("Service stopping, terminating tunnel...")
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass
                
            except Exception as e:
                self._log(f"Service error: {e}")
                if win32event.WaitForSingleObject(self.hWaitStop, retry_delay * 1000) == win32event.WAIT_OBJECT_0:
                    break
                retry_delay = min(retry_delay * 2, max_retry_delay)
        
        self._log("Fluidd Tunnel Service stopped")


def main():
    if len(sys.argv) == 1:
        # Started by Windows Service Manager
        if HAS_WIN32:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(FluiddTunnelService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("Error: pywin32 not installed. Cannot run as service.")
            print("Install with: pip install pywin32")
            sys.exit(1)
    else:
        # Handle command line arguments
        if not HAS_WIN32:
            print("Error: pywin32 not installed. Cannot manage service.")
            print("Install with: pip install pywin32")
            sys.exit(1)
            
        win32serviceutil.HandleCommandLine(FluiddTunnelService)


if __name__ == '__main__':
    main()