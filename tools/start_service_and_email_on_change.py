#!/usr/bin/env python3
# start_service_and_email_on_change.py
# Starts cloudflared tunnel directly as a Python subprocess and sends an EMAIL only when the tunnel URL changes.
# Usage:
#   python tools/start_service_and_email_on_change.py            # start tunnel and monitor
#   python tools/start_service_and_email_on_change.py --dry-run  # no email sent, logs only
#   python tools/start_service_and_email_on_change.py --no-start # just monitor, don't start tunnel
#   python tools/start_service_and_email_on_change.py --email-to someone@example.com

import argparse
import os
import re
import smtplib
import subprocess
import sys
import time
import threading
from email.message import EmailMessage
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOGS_DIR = PROJECT_ROOT / "logs"
ENV_FILE = PROJECT_ROOT / ".env"
URL_FILE = LOGS_DIR / "cloudflared_url.txt"
STATE_FILE = LOGS_DIR / "last_sent_url.txt"
MONITOR_LOG = LOGS_DIR / "url_change_monitor.log"

LOGS_DIR.mkdir(exist_ok=True)


def log(msg: str):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    try:
        print(line)
        sys.stdout.flush()
    finally:
        try:
            with open(MONITOR_LOG, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass


def load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for raw in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def read_current_url() -> str | None:
    if not URL_FILE.exists():
        return None
    try:
        content = URL_FILE.read_text(encoding="utf-8", errors="ignore").strip()
        first = content.splitlines()[0].strip() if content else ""
        # Validate looks like a trycloudflare URL
        m = re.match(r"https://[A-Za-z0-9\-]+\.trycloudflare\.com/?", first)
        return m.group(0) if m else None
    except Exception:
        return None


def read_last_sent_url() -> str | None:
    if not STATE_FILE.exists():
        return None
    try:
        return STATE_FILE.read_text(encoding="utf-8", errors="ignore").strip() or None
    except Exception:
        return None


def write_last_sent_url(url: str) -> None:
    try:
        STATE_FILE.write_text(url + "\n", encoding="utf-8")
    except Exception as e:
        log(f"Failed to write state file: {e}")


def send_email(gmail_user: str, app_pass: str, to_addr: str, subject: str, body: str, dry_run: bool) -> bool:
    log(f"Preparing email -> To: {to_addr} | Subject: {subject}")
    log(f"Email body length: {len(body)} chars")
    if dry_run:
        log("Dry-run: email not sent")
        return True
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = to_addr

        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.ehlo()
            s.starttls()
            s.login(gmail_user, app_pass)
            s.send_message(msg)
        log("Email sent successfully")
        return True
    except smtplib.SMTPAuthenticationError as e:
        log(f"Email auth failed: {e}")
        return False
    except Exception as e:
        log(f"Email send failed: {type(e).__name__}: {e}")
        return False


def stop_existing_cloudflared():
    """Stop any existing cloudflared processes"""
    try:
        import psutil
        stopped_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                    log(f"Found existing cloudflared process (PID: {proc.info['pid']})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                        stopped_count += 1
                    except psutil.TimeoutExpired:
                        proc.kill()
                        stopped_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if stopped_count > 0:
            log(f"Stopped {stopped_count} existing cloudflared process(es)")
            time.sleep(2)
        return stopped_count
    except ImportError:
        # Fall back to taskkill on Windows
        try:
            result = subprocess.run(['taskkill', '/F', '/IM', 'cloudflared.exe'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                log("Stopped existing cloudflared processes using taskkill")
                time.sleep(2)
                return 1
            return 0
        except Exception:
            return 0


def start_cloudflared_tunnel(env: dict) -> subprocess.Popen | None:
    """Start cloudflared tunnel as subprocess and return the process"""
    cloudflared_path = env.get("CLOUD_FLARED_PATH")
    if not cloudflared_path:
        cloudflared_path = str(Path.home() / "Downloads" / "cloudflared.exe")
    
    if not Path(cloudflared_path).exists():
        log(f"cloudflared not found at {cloudflared_path}")
        return None
    
    log(f"Starting cloudflared tunnel from {cloudflared_path}")
    
    try:
        proc = subprocess.Popen(
            [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:4408"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            bufsize=1
        )
        log(f"Started cloudflared process (PID: {proc.pid})")
        return proc
    except Exception as e:
        log(f"Failed to start cloudflared: {e}")
        return None


def monitor_cloudflared_output(proc: subprocess.Popen):
    """Monitor cloudflared output in a separate thread and log to file"""
    tunnel_log = LOGS_DIR / "cloudflared_tunnel.log"
    
    def output_reader():
        try:
            with open(tunnel_log, "w", encoding="utf-8") as logfile:
                logfile.write(f"Cloudflared tunnel started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                logfile.write("-" * 50 + "\n")
                logfile.flush()
                
                while True:
                    if proc.stdout is None:
                        break
                    line = proc.stdout.readline()
                    if not line:
                        if proc.poll() is not None:
                            break
                        time.sleep(0.1)
                        continue
                    
                    line = line.strip()
                    if line:
                        log(f"cloudflared: {line}")
                        logfile.write(f"{line}\n")
                        logfile.flush()
                        
                        # Check for tunnel URL and save it
                        m = re.search(r"https://[A-Za-z0-9\-]+\.trycloudflare\.com", line)
                        if m:
                            url = m.group(0)
                            try:
                                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                                URL_FILE.write_text(f"{url}\nGenerated at: {timestamp}\n", encoding="utf-8")
                                log(f"Saved tunnel URL to {URL_FILE}")
                            except Exception as e:
                                log(f"Failed to write URL file: {e}")
        except Exception as e:
            log(f"Error monitoring cloudflared output: {e}")
    
    thread = threading.Thread(target=output_reader, daemon=True)
    thread.start()
    return thread


def wait_for_url(timeout_sec: int = 120) -> str | None:
    log(f"Waiting for tunnel URL (timeout {timeout_sec}s)…")
    start = time.time()
    last_size = -1
    while time.time() - start < timeout_sec:
        url = read_current_url()
        if url:
            log(f"Detected tunnel URL: {url}")
            return url
        # If file exists but empty, wait a bit longer
        if URL_FILE.exists():
            try:
                s = URL_FILE.stat().st_size
                if s != last_size:
                    last_size = s
                    log(f"URL file present (size {s} bytes), waiting for content…")
            except Exception:
                pass
        time.sleep(2)
    log("Timeout waiting for tunnel URL")
    return None


def monitor_loop(gmail_user: str, app_pass: str, to_addr: str, dry_run: bool, poll_sec: int = 10, tunnel_proc: subprocess.Popen | None = None):
    last_sent = read_last_sent_url()
    if last_sent:
        log(f"Last sent URL from state: {last_sent}")
    else:
        log("No previously sent URL recorded")

    # Try to ensure we have an initial URL
    current = read_current_url() or wait_for_url(timeout_sec=180)
    if current:
        log(f"Current URL at start: {current}")
        if current != last_sent:
            subject = "Fluidd URL Changed"
            body = (
                f"Fluidd tunnel URL has changed.\n\n"
                f"New URL: {current}\n"
                f"Previous: {last_sent or 'None recorded'}\n"
                f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            if send_email(gmail_user, app_pass, to_addr, subject, body, dry_run):
                write_last_sent_url(current)
                last_sent = current
        else:
            log("Initial URL matches last sent; no email sent")
    else:
        log("Proceeding without initial URL; will continue monitoring…")

    log("Monitoring for URL changes… Press Ctrl+C to stop.")
    try:
        last_seen = current
        while True:
            # Check if tunnel process is still running
            if tunnel_proc and tunnel_proc.poll() is not None:
                log(f"Tunnel process exited with code {tunnel_proc.returncode}")
                break
                
            time.sleep(poll_sec)
            new_url = read_current_url()
            if not new_url:
                continue
            if new_url != last_seen:
                log(f"URL file changed: {last_seen} -> {new_url}")
                if new_url != last_sent:
                    subject = "Fluidd URL Changed"
                    body = (
                        f"Fluidd tunnel URL has changed.\n\n"
                        f"New URL: {new_url}\n"
                        f"Previous: {last_sent or 'None recorded'}\n"
                        f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    if send_email(gmail_user, app_pass, to_addr, subject, body, dry_run):
                        write_last_sent_url(new_url)
                        last_sent = new_url
                else:
                    log("URL change matches last sent; suppressing duplicate email")
                last_seen = new_url
    except KeyboardInterrupt:
        log("Stopping monitor (Ctrl+C)")
        if tunnel_proc:
            log("Terminating tunnel process...")
            tunnel_proc.terminate()
            try:
                tunnel_proc.wait(timeout=5)
                log("Tunnel process terminated cleanly")
            except subprocess.TimeoutExpired:
                log("Force killing tunnel process...")
                tunnel_proc.kill()


def main():
    parser = argparse.ArgumentParser(description="Start cloudflared tunnel and email only when URL changes")
    parser.add_argument("--no-start", action="store_true", help="Do not attempt to start the tunnel; just monitor")
    parser.add_argument("--dry-run", action="store_true", help="Do not send email; log actions only")
    parser.add_argument("--email-to", default=None, help="Override destination email address")
    parser.add_argument("--poll", type=int, default=10, help="Polling interval in seconds (default: 10)")
    args = parser.parse_args()

    log("URL change monitor starting…")
    log(f"Project root: {PROJECT_ROOT}")
    env = load_env()

    gmail_user = env.get("GMAIL_USER", "soupsterx@gmail.com")
    app_pass = env.get("GOOGLE_APP_PASS")
    to_addr = args.email_to or env.get("ALERT_EMAIL") or gmail_user

    if not app_pass:
        log("GOOGLE_APP_PASS not set in .env; cannot send emails")
        if not args.dry_run:
            log("Hint: add GOOGLE_APP_PASS to .env or run with --dry-run for testing")
            return 1

    tunnel_proc = None
    
    if not args.no_start:
        # Stop any existing cloudflared processes
        stop_existing_cloudflared()
        
        # Start our own cloudflared tunnel
        tunnel_proc = start_cloudflared_tunnel(env)
        if tunnel_proc:
            # Start monitoring thread for cloudflared output
            monitor_thread = monitor_cloudflared_output(tunnel_proc)
            log("Tunnel started successfully, monitoring output...")
        else:
            log("Failed to start tunnel. Continuing to monitor anyway…")

    monitor_loop(gmail_user, app_pass or "", to_addr, args.dry_run, poll_sec=args.poll, tunnel_proc=tunnel_proc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
