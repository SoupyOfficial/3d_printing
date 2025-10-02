#!/usr/bin/env python3
# send_tunnel_sms.py -- Send current tunnel URL via SMS
# Run: python send_tunnel_sms.py [custom_url]

import sys
import smtplib
import time
from email.message import EmailMessage
from pathlib import Path

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
    """Get current tunnel URL from logs"""
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

def send_sms(url, message_type="current"):
    """Send SMS with tunnel URL"""
    env = load_env()
    
    if "GOOGLE_APP_PASS" not in env:
        print("❌ GOOGLE_APP_PASS not found in .env file")
        return False
    
    gmail_user = "soupsterx@gmail.com"
    sms_addr = "3216981359@vtext.com"
    
    # Create message based on type
    if message_type == "current":
        subject = "Fluidd Tunnel URL"
        body = f"Fluidd tunnel is ready:\n{url}\n\nSent at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    elif message_type == "restart":
        subject = "Fluidd Tunnel Restarted"
        body = f"Fluidd tunnel has restarted:\n{url}\n\nRestarted at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        subject = "Fluidd Tunnel"
        body = f"Fluidd tunnel:\n{url}\n\nSent at: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        print(f"📤 Sending SMS to {sms_addr}...")
        
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = sms_addr

        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.ehlo()
            s.starttls()
            s.login(gmail_user, env["GOOGLE_APP_PASS"])
            s.send_message(msg)

        print(f"✅ SMS sent successfully!")
        print(f"📱 Message: {body}")
        return True
        
    except Exception as e:
        print(f"❌ SMS failed: {e}")
        return False

def main():
    print("📱 Fluidd Tunnel SMS Sender")
    print("=" * 40)
    
    # Get URL from command line or current logs
    if len(sys.argv) > 1:
        url = sys.argv[1]
        message_type = "custom"
        print(f"🔗 Using provided URL: {url}")
    else:
        url = get_current_url()
        message_type = "current"
        if url:
            print(f"🔗 Found current URL: {url}")
        else:
            print("❌ No current tunnel URL found in logs")
            print("💡 Start a tunnel first or provide URL as argument:")
            print("   python send_tunnel_sms.py https://your-tunnel.trycloudflare.com")
            return 1
    
    print()
    success = send_sms(url, message_type)
    
    if success:
        print("\n🎉 SMS notification sent successfully!")
    else:
        print("\n❌ Failed to send SMS notification")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())