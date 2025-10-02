#!/usr/bin/env python3
# verify_service_setup.py -- Complete verification before service installation
# Run: python verify_service_setup.py

import os
import sys
import subprocess
import smtplib
from pathlib import Path
from email.message import EmailMessage

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_check(description, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {description}")
    if details:
        print(f"   {details}")
    return status

def check_python_packages():
    """Check if required Python packages are installed"""
    print_header("PYTHON PACKAGES")
    
    packages = {
        "psutil": "Process management",
        "win32serviceutil": "Windows service integration"
    }
    
    all_good = True
    for package, description in packages.items():
        try:
            result = subprocess.run([sys.executable, "-c", f"import {package}"], 
                                  capture_output=True, text=True)
            success = result.returncode == 0
            print_check(f"{package} ({description})", success)
            if not success:
                all_good = False
        except Exception as e:
            print_check(f"{package} ({description})", False, str(e))
            all_good = False
    
    return all_good

def check_env_file():
    """Check .env file configuration"""
    print_header("CONFIGURATION")
    
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    
    env_exists = print_check(".env file exists", env_file.exists(), str(env_file))
    
    if not env_exists:
        return False
    
    # Load environment
    env = {}
    try:
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"): 
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except Exception as e:
        print_check("Read .env file", False, str(e))
        return False
    
    google_pass = print_check("GOOGLE_APP_PASS configured", 
                            "GOOGLE_APP_PASS" in env and len(env.get("GOOGLE_APP_PASS", "")) > 0)
    
    cloudflared_path = env.get("CLOUD_FLARED_PATH", str(Path.home() / "Downloads" / "cloudflared.exe"))
    cloudflared_exists = print_check("cloudflared.exe found", 
                                    Path(cloudflared_path).exists(), 
                                    cloudflared_path)
    
    return google_pass and cloudflared_exists

def check_sms_functionality():
    """Test SMS sending"""
    print_header("SMS FUNCTIONALITY")
    
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    
    # Load environment
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"): 
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    
    if "GOOGLE_APP_PASS" not in env:
        print_check("SMS configuration", False, "GOOGLE_APP_PASS not set")
        return False
    
    gmail_user = "soupsterx@gmail.com"
    sms_addr = "3216981359@vtext.com"
    
    try:
        print("   Testing SMTP connection...")
        msg = EmailMessage()
        msg.set_content("Service verification test - ignore this message")
        msg["Subject"] = "Fluidd Service Test"
        msg["From"] = gmail_user
        msg["To"] = sms_addr

        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.ehlo()
            s.starttls()
            s.login(gmail_user, env["GOOGLE_APP_PASS"])
            # Don't actually send during verification
            # s.send_message(msg)

        print_check("SMS authentication", True, "Gmail login successful")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print_check("SMS authentication", False, "Invalid Gmail app password")
        return False
    except Exception as e:
        print_check("SMS connectivity", False, str(e))
        return False

def check_service_files():
    """Check if service files exist"""
    print_header("SERVICE FILES")
    
    script_dir = Path(__file__).resolve().parent
    
    files = {
        "fluidd_service.py": "Main service script",
        "service_manager.py": "Service management helper",
        "install_service.ps1": "PowerShell installer",
        "test_sms.py": "SMS testing script"
    }
    
    all_good = True
    for filename, description in files.items():
        file_path = script_dir / filename
        exists = print_check(f"{filename} ({description})", 
                           file_path.exists(), 
                           str(file_path))
        if not exists:
            all_good = False
    
    return all_good

def check_directories():
    """Check required directories"""
    print_header("DIRECTORIES")
    
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    dirs = {
        "logs": "Log files directory",
        "tools": "Tools and scripts directory"
    }
    
    all_good = True
    for dirname, description in dirs.items():
        dir_path = project_root / dirname
        exists = print_check(f"{dirname}/ ({description})", 
                           dir_path.exists(), 
                           str(dir_path))
        if not exists:
            # Create logs directory if missing
            if dirname == "logs":
                try:
                    dir_path.mkdir(exist_ok=True)
                    print_check(f"Created {dirname}/ directory", True)
                except Exception as e:
                    print_check(f"Create {dirname}/ directory", False, str(e))
                    all_good = False
            else:
                all_good = False
    
    return all_good

def check_admin_permissions():
    """Check if running as administrator"""
    print_header("PERMISSIONS")
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print_check("Administrator privileges", is_admin, 
                   "Required for service installation" if not is_admin else "Ready for service installation")
        return is_admin
    except Exception:
        print_check("Administrator check", False, "Unable to determine admin status")
        return False

def main():
    print("🔧 Fluidd Tunnel Service Verification")
    print("This script verifies all requirements are met before installing the service")
    
    # Run all checks
    checks = [
        ("Python packages", check_python_packages),
        ("Configuration", check_env_file),
        ("Service files", check_service_files),
        ("Directories", check_directories),
        ("SMS functionality", check_sms_functionality),
        ("Admin permissions", check_admin_permissions)
    ]
    
    results = {}
    for name, check_func in checks:
        results[name] = check_func()
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready to install service.")
        print("\nNext steps:")
        print("1. Install service: python service_manager.py install")
        print("2. Start service: python service_manager.py start")
        print("3. Check status: python service_manager.py status")
        return 0
    else:
        print(f"\n❌ {total - passed} checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install packages: pip install --user psutil pywin32")
        print("- Run as administrator for service installation")
        print("- Check .env file configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())