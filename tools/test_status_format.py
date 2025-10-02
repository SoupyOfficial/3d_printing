#!/usr/bin/env python3
# test_status_format.py -- Test the new status message format

import time
from datetime import datetime

def test_status_format():
    now = datetime.now()
    current_url = "https://fees-nano-personalized-florists.trycloudflare.com"
    url_healthy = True
    service_running = True
    uptime_str = "2h 15m"
    
    health_icon = "OK" if (url_healthy and service_running) else "ISSUE"
    url_short = current_url.replace("https://", "") if current_url else "None"
    
    status_msg = f"Fluidd Status {now.strftime('%H:%M')}: {health_icon} | URL: {url_short} | Uptime: {uptime_str}"
    
    print("New Status Message Format:")
    print("=" * 50)
    print(f"Length: {len(status_msg)} characters")
    print(f"Message: {status_msg}")
    print()
    
    # Test with issue
    health_icon = "ISSUE"
    status_msg2 = f"Fluidd Status {now.strftime('%H:%M')}: {health_icon} | URL: {url_short} | Uptime: {uptime_str}"
    print(f"With Issue - Length: {len(status_msg2)} characters")
    print(f"Message: {status_msg2}")

if __name__ == "__main__":
    test_status_format()