# start_fluidd.py -- Start cloudflared tunnel for Fluidd and send URL via SMS
# Run: python start_fluidd.py

import os, re, subprocess, smtplib, time
from email.message import EmailMessage
from pathlib import Path

# Try to import psutil, fall back to basic process handling if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    print("Warning: psutil not available. Install with: pip install psutil")
    print("Falling back to basic process handling...")
    HAS_PSUTIL = False

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
env_file = project_root / ".env"
logs_dir = project_root / "logs"

print("Project root:", project_root)
print(".env file:", env_file)

# Ensure logs directory exists
logs_dir.mkdir(exist_ok=True)

if not env_file.exists():
    raise SystemExit(f".env not found at {env_file}")

# Check for existing cloudflared processes and stop them
def stop_existing_cloudflared():
    """Stop any existing cloudflared processes"""
    stopped_count = 0
    
    if HAS_PSUTIL:
        # Use psutil for better process management
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                    print(f"Found existing cloudflared process (PID: {proc.info['pid']})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                        print(f"Stopped cloudflared process (PID: {proc.info['pid']})")
                        stopped_count += 1
                    except psutil.TimeoutExpired:
                        proc.kill()
                        print(f"Force killed cloudflared process (PID: {proc.info['pid']})")
                        stopped_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    else:
        # Fall back to taskkill on Windows
        try:
            result = subprocess.run(['taskkill', '/F', '/IM', 'cloudflared.exe'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("Stopped existing cloudflared processes using taskkill")
                stopped_count = 1
        except FileNotFoundError:
            print("taskkill not available - manual cleanup may be needed")
    
    if stopped_count > 0:
        print(f"Stopped {stopped_count} existing cloudflared process(es)")
        time.sleep(2)  # Wait for processes to fully terminate
    return stopped_count

print("Checking for existing cloudflared processes...")
stop_existing_cloudflared()

# simple .env parser
env = {}
for line in env_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"): continue
    if "=" in line:
        k,v = line.split("=",1)
        env[k.strip()] = v.strip()

if "GOOGLE_APP_PASS" not in env:
    raise SystemExit("GOOGLE_APP_PASS not set in .env")

GMAIL_USER = "soupsterx@gmail.com"
SMS_ADDR = "3216981359@vtext.com"
cloudflared_path = env.get("CLOUD_FLARED_PATH") or str(Path.home() / "Downloads" / "cloudflared.exe")
if not Path(cloudflared_path).exists():
    raise SystemExit(f"cloudflared not found at {cloudflared_path}")

# Use proper log directory structure
log_file = logs_dir / "cloudflared_tunnel.log"
url_file = logs_dir / "cloudflared_url.txt"

print(f"Logging to: {log_file}")
print(f"URL will be saved to: {url_file}")

# start cloudflared
proc = subprocess.Popen([cloudflared_path, "tunnel", "--url", "http://127.0.0.1:4408"],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
url = None
start = time.time()
timeout = 30

print("Starting cloudflared tunnel...")
with open(log_file, "w", encoding="utf-8") as log:
    log.write(f"Cloudflared tunnel started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write(f"Command: {cloudflared_path} tunnel --url http://127.0.0.1:4408\n")
    log.write("-" * 50 + "\n")
    log.flush()
    
    while time.time() - start < timeout:
        line = proc.stdout.readline() # type: ignore
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
            continue
        
        log.write(line)
        log.flush()
        print(f"cloudflared: {line.strip()}")
        
        m = re.search(r"https://[A-Za-z0-9\-]+\.trycloudflare\.com", line)
        if m:
            url = m.group(0)
            break

if not url:
    proc.terminate()
    raise SystemExit(f"No trycloudflare URL found within {timeout}s. Check {log_file}")

url_file.write_text(f"{url}\nGenerated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
print(f"Tunnel URL: {url}")

# send via Gmail SMTP using app password from .env
smtp_server = "smtp.gmail.com"
smtp_port = 587
user = GMAIL_USER
pwd = env["GOOGLE_APP_PASS"]

try:
    msg = EmailMessage()
    msg.set_content(f"Fluidd tunnel is ready:\n{url}")
    msg["Subject"] = "Fluidd Tunnel URL"
    msg["From"] = user
    msg["To"] = SMS_ADDR

    with smtplib.SMTP(smtp_server, smtp_port) as s:
        s.ehlo()
        s.starttls()
        s.login(user, pwd)
        s.send_message(msg)

    print(f"SMS sent to {SMS_ADDR}")
    
    # Log successful SMS
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"SMS sent successfully to {SMS_ADDR} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
except Exception as e:
    print(f"Failed to send SMS: {e}")
    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"SMS failed: {e} at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

print("\nTunnel is running. Press Ctrl+C to stop...")
try:
    while proc.poll() is None:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down tunnel...")
    proc.terminate()
    proc.wait()
    print("Tunnel stopped.")
# keep process running; Ctrl+C to stop both Python and cloudflared
