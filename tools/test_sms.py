#!/usr/bin/env python3
# test_sms.py -- Test SMS functionality before installing service
# Run: python test_sms.py

import smtplib
import sys
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

def test_sms(test_url="https://test-tunnel-url.trycloudflare.com"):
    """Test SMS sending functionality"""
    print("Testing SMS functionality...")
    print("=" * 50)
    
    # Load environment
    env = load_env()
    
    if "GOOGLE_APP_PASS" not in env:
        print("❌ GOOGLE_APP_PASS not found in .env file")
        print("   Please add your Gmail app password to .env file:")
        print("   GOOGLE_APP_PASS=your_app_password_here")
        return False
    
    # SMS configuration (same as service)
    gmail_user = "soupsterx@gmail.com"
    sms_addr = "3216981359@vtext.com"
    gmail_pass = env["GOOGLE_APP_PASS"]
    
    print(f"📧 Gmail user: {gmail_user}")
    print(f"📱 SMS address: {sms_addr}")
    print(f"🔑 App password: {'*' * len(gmail_pass)}")
    print(f"🔗 Test URL: {test_url}")
    print()
    
    try:
        print("📨 Creating email message...")
        msg = EmailMessage()
        msg.set_content(f"🧪 Fluidd tunnel test message:\n{test_url}\n\nThis is a test from the 3D printing service setup.")
        msg["Subject"] = "Fluidd Tunnel Test"
        msg["From"] = gmail_user
        msg["To"] = sms_addr
        print("✅ Email message created")
        
        print("🌐 Connecting to Gmail SMTP...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            print("🔌 Connected to SMTP server")
            
            print("🤝 Starting TLS encryption...")
            server.ehlo()
            server.starttls()
            print("✅ TLS encryption started")
            
            print("🔐 Authenticating with Gmail...")
            server.login(gmail_user, gmail_pass)
            print("✅ Authentication successful")
            
            print("📤 Sending SMS...")
            server.send_message(msg)
            print("✅ SMS sent successfully!")
            
        print()
        print("🎉 SMS test completed successfully!")
        print(f"📱 Check your phone at {sms_addr.split('@')[0]} for the test message")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Possible solutions:")
        print("   1. Check that GOOGLE_APP_PASS is correct")
        print("   2. Ensure 2-factor authentication is enabled on Gmail")
        print("   3. Generate a new app password at: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        print("💡 Check your internet connection and Gmail settings")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Check the error details above")
        return False

def main():
    print("🔧 Fluidd Tunnel SMS Test")
    print("This script tests SMS functionality before installing the service")
    print()
    
    # Allow custom test URL
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://test-tunnel-url.trycloudflare.com"
    
    success = test_sms(test_url)
    
    print()
    if success:
        print("✅ SMS test successful! The service will be able to send notifications.")
        print("🚀 You can now proceed with service installation:")
        print("   python service_manager.py install")
    else:
        print("❌ SMS test failed. Please fix the configuration before installing the service.")
        print("🔧 Check the .env file and Gmail app password settings.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())