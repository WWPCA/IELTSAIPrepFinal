"""
Quick Test - Assessment Pages After CloudFront Fix
"""

import urllib.request
import urllib.error
import time
from datetime import datetime

def test_single_assessment_page():
    """Test one assessment page to check if fix is working"""
    
    url = "https://www.ieltsaiprep.com/assessment/academic-writing"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 CloudFront Test')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            if status_code == 200:
                if "Academic Writing Assessment" in content:
                    return True, "Assessment page loaded successfully"
                else:
                    return False, f"Page loaded but content may be incorrect"
            else:
                return False, f"HTTP {status_code}"
                
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False, "Still getting 403 - propagation not complete"
        else:
            return False, f"HTTP Error {e.code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main test function"""
    
    print("🧪 Testing Assessment Page After CloudFront Fix")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    is_working, message = test_single_assessment_page()
    
    if is_working:
        print("✅ WORKING: Assessment pages are now accessible!")
        print("🎉 CloudFront fix successful!")
        print("✅ Ready to test Nova AI functionality")
    else:
        print(f"⏳ NOT YET: {message}")
        print("💡 Changes may still be propagating globally")
        print("⏰ Try again in 5-10 minutes")
    
    return is_working

if __name__ == "__main__":
    main()