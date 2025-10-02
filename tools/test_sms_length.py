#!/usr/bin/env python3
# test_sms_length.py -- Test SMS message lengths and formats

import time

def test_message_formats():
    url = "https://fees-nano-personalized-florists.trycloudflare.com"
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    short_time = time.strftime('%H:%M')
    
    formats = {
        "Old Format": f"Fluidd tunnel is ready:\n{url}\n\nGenerated at: {timestamp}",
        "NEW Format": f"Fluidd: {url} ({short_time})",
        "Compact Format": f"Fluidd: {url}\nAt: {short_time}",
        "Ultra Compact": f"Fluidd:\n{url}",
        "Short URL Only": url,
        "With Domain": f"3D Printer:\n{url}",
    }
    
    print("SMS Message Length Analysis")
    print("=" * 50)
    print("SMS Standard Limit: 160 characters")
    print()
    
    for name, message in formats.items():
        length = len(message)
        status = "✅ OK" if length <= 160 else "❌ TOO LONG"
        print(f"{name}: {length} chars {status}")
        print(f"Message: {repr(message)}")
        print()

if __name__ == "__main__":
    test_message_formats()