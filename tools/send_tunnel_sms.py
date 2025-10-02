#!/usr/bin/env python3
# send_tunnel_sms.py -- Send current tunnel URL via SMS
# Run: python send_tunnel_sms.py [custom_url]

import sys
import smtplib
import time
from email.message import EmailMessage
from pathlib import Path

# Setup dual logging (console + file)
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
logs_dir = project_root / "logs"
logs_dir.mkdir(exist_ok=True)
sms_log_file = logs_dir / "sms_notifications.log"

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
        with open(sms_log_file, "a", encoding="utf-8") as f:
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
    """Send SMS with tunnel URL and verbose logging"""
    env = load_env()
    
    if "GOOGLE_APP_PASS" not in env:
        dual_log("GOOGLE_APP_PASS not found in .env file", "ERROR")
        return False
    
    gmail_user = "soupsterx@gmail.com"
    sms_addr = "3216981359@vtext.com"
    email_addr = "soupsterx@gmail.com"
    
    # Create message based on type - Using compact format to avoid truncation
    if message_type == "current":
        subject = "Fluidd URL"
        body = f"Fluidd: {url} ({time.strftime('%H:%M')})"
    elif message_type == "restart":
        subject = "Fluidd Restart"
        body = f"Fluidd Restarted: {url} ({time.strftime('%H:%M')})"
    else:
        subject = "Fluidd"
        body = f"Fluidd: {url} ({time.strftime('%H:%M')})"
    
    dual_log("Preparing to send notification...")
    dual_log(f"URL: {url}")
    dual_log(f"Subject: {subject}")
    dual_log(f"Message: {body}")
    dual_log(f"Message length: {len(body)} characters")
    dual_log(f"SMS target: {sms_addr}")
    dual_log(f"Email target: {email_addr}")
    
    # Results tracking
    sms_success = False
    email_success = False
    
    try:
        dual_log("Connecting to Gmail SMTP...")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            dual_log("Starting TLS encryption...")
            s.ehlo()
            s.starttls()
            
            dual_log(f"Authenticating as {gmail_user}...")
            s.login(gmail_user, env["GOOGLE_APP_PASS"])
            dual_log("SMTP authentication successful")
            
            # Send SMS via email-to-SMS gateway
            dual_log(f"Sending SMS to {sms_addr}...")
            sms_msg = EmailMessage()
            sms_msg.set_content(body)
            sms_msg["Subject"] = subject
            sms_msg["From"] = gmail_user
            sms_msg["To"] = sms_addr
            
            dual_log("SMS message headers:")
            dual_log(f"   From: {sms_msg['From']}")
            dual_log(f"   To: {sms_msg['To']}")
            dual_log(f"   Subject: {sms_msg['Subject']}")
            dual_log(f"   Content-Length: {len(body)} chars")
            
            s.send_message(sms_msg)
            sms_success = True
            dual_log("SMS sent successfully via email-to-SMS gateway!")
            
            # Send backup email
            dual_log(f"Sending backup email to {email_addr}...")
            email_msg = EmailMessage()
            email_body = f"Fluidd Tunnel Notification\n\nURL: {url}\nTime: {time.strftime('%Y-%m-%d %H:%M:%S')}\nStatus: {message_type}\n\nThis is a backup delivery in case SMS fails."
            email_msg.set_content(email_body)
            email_msg["Subject"] = f"[Backup] {subject}"
            email_msg["From"] = gmail_user
            email_msg["To"] = email_addr
            
            s.send_message(email_msg)
            email_success = True
            dual_log("Backup email sent successfully!")

    except smtplib.SMTPAuthenticationError as e:
        dual_log(f"SMTP Authentication failed: {e}", "ERROR")
        dual_log("Check GOOGLE_APP_PASS in .env file", "ERROR")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        dual_log(f"Recipients refused: {e}", "ERROR")
        return False
    except smtplib.SMTPServerDisconnected as e:
        dual_log(f"SMTP server disconnected: {e}", "ERROR")
        return False
    except Exception as e:
        dual_log(f"Unexpected error: {e}", "ERROR")
        dual_log(f"Error type: {type(e).__name__}", "ERROR")
        return False
    
    # Summary
    dual_log("Delivery Summary:")
    dual_log(f"   SMS: {'Success' if sms_success else 'Failed'}")
    dual_log(f"   Email: {'Success' if email_success else 'Failed'}")
    
    return sms_success or email_success

def main():
    dual_log("Fluidd Tunnel SMS Sender")
    dual_log("=" * 40)
    
    # Get URL from command line or current logs
    if len(sys.argv) > 1:
        url = sys.argv[1]
        message_type = "custom"
        dual_log(f"Using provided URL: {url}")
    else:
        url = get_current_url()
        message_type = "current"
        if url:
            dual_log(f"Found current URL: {url}")
        else:
            dual_log("No current tunnel URL found in logs", "ERROR")
            dual_log("Start a tunnel first or provide URL as argument:")
            dual_log("   python send_tunnel_sms.py https://your-tunnel.trycloudflare.com")
            return 1
    
    dual_log("")
    success = send_sms(url, message_type)
    
    if success:
        dual_log("SMS notification sent successfully!")
    else:
        dual_log("Failed to send SMS notification", "ERROR")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
