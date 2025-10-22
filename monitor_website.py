#!/usr/bin/env python3
"""
Monitor the IELTS GenAI Prep website for correct pricing display
Run this periodically to ensure the website maintains correct $36 pricing
"""
import requests
import time
import datetime

def check_website_pricing():
    """Check if website displays correct $36 pricing"""
    try:
        response = requests.get('https://www.ieltsaiprep.com/', timeout=10)
        
        if response.status_code != 200:
            print(f"ERROR: Website returned status {response.status_code}")
            return False
        
        content = response.text
        pricing_count = content.count('$36')
        
        print(f"Pricing check: Found {pricing_count} instances of $36")
        
        if pricing_count >= 4:
            print("SUCCESS: Website pricing is correct")
            return True
        else:
            print(f"ERROR: Expected at least 4 instances of $36, found {pricing_count}")
            print("RECOMMENDATION: Run emergency_redeploy.py to fix")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not check website: {e}")
        return False

def continuous_monitor(check_interval_minutes=60):
    """Continuously monitor the website"""
    print(f"Starting continuous monitoring (checking every {check_interval_minutes} minutes)")
    
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Checking website...")
        
        check_website_pricing()
        
        print(f"Next check in {check_interval_minutes} minutes")
        time.sleep(check_interval_minutes * 60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        continuous_monitor()
    else:
        check_website_pricing()
