#!/usr/bin/env python3
"""
Backup and version control for the production Lambda template
Ensures the working template is preserved and can be redeployed
"""
import boto3
import json
import datetime
import zipfile
import base64

def backup_current_lambda():
    """Download and backup the current working Lambda function"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Get current function code
        response = lambda_client.get_function(FunctionName='ielts-genai-prep-api')
        code_url = response['Code']['Location']
        
        # Download the current deployment
        import requests
        code_response = requests.get(code_url)
        
        # Save as backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"production_backup_{timestamp}.zip"
        
        with open(backup_filename, 'wb') as f:
            f.write(code_response.content)
        
        print(f"Production Lambda backed up to: {backup_filename}")
        
        # Also save the working template separately
        with open('working_template.html', 'r') as f:
            template_content = f.read()
        
        backup_template_name = f"working_template_backup_{timestamp}.html"
        with open(backup_template_name, 'w') as f:
            f.write(template_content)
        
        print(f"Working template backed up to: {backup_template_name}")
        
        return backup_filename, backup_template_name
        
    except Exception as e:
        print(f"Backup failed: {e}")
        return None, None

def create_deployment_script():
    """Create a script to redeploy the working template"""
    script_content = '''#!/usr/bin/env python3
"""
Emergency redeployment script for the working IELTS GenAI Prep template
Run this if the production website ever shows incorrect pricing or content
"""
import boto3
import zipfile
import base64

def emergency_redeploy():
    """Redeploy the confirmed working template"""
    
    # Read the working template
    with open('working_template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Verify template has correct pricing
    if '$36' not in template_content:
        print("ERROR: Template does not contain correct $36 pricing!")
        return False
    
    pricing_count = template_content.count('$36')
    if pricing_count < 4:
        print(f"ERROR: Template only has {pricing_count} instances of $36, expected at least 4!")
        return False
    
    print(f"Template verified: Found {pricing_count} instances of $36 pricing")
    
    # Encode template
    template_b64 = base64.b64encode(template_content.encode('utf-8')).decode('ascii')
    
    # Create Lambda function
    lambda_code = f\'''
import json
import base64

def lambda_handler(event, context):
    path = event.get('path', '/')
    
    if path == '/':
        return serve_home_page()
    elif path == '/login':
        return serve_login_page()
    elif path == '/dashboard':
        return serve_dashboard_page()
    else:
        return serve_home_page()

def serve_home_page():
    template_b64 = "{template_b64}"
    html_content = base64.b64decode(template_b64.encode('ascii')).decode('utf-8')
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html; charset=utf-8'}},
        'body': html_content
    }}

def serve_login_page():
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """<!DOCTYPE html>
<html><head><title>Login - IELTS GenAI Prep</title></head>
<body style="padding: 40px;">
<h2>Login</h2>
<p>Test: test@ieltsgenaiprep.com / testpassword123</p>
<a href="/">← Back to Home</a>
</body></html>"""
    }}

def serve_dashboard_page():
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': """<!DOCTYPE html>
<html><head><title>Dashboard - IELTS GenAI Prep</title></head>
<body style="padding: 40px;">
<h2>Dashboard</h2>
<p>Your assessments are ready!</p>
<a href="/">← Back to Home</a>
</body></html>"""
    }}
\'''
    
    # Create deployment package
    with zipfile.ZipFile('emergency-redeploy.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Deploy to AWS Lambda
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('emergency-redeploy.zip', 'rb') as f:
        zip_content = f.read()
    
    print('Deploying working template...')
    lambda_client.update_function_code(
        FunctionName='ielts-genai-prep-api',
        ZipFile=zip_content
    )
    
    waiter = lambda_client.get_waiter('function_updated')
    waiter.wait(FunctionName='ielts-genai-prep-api')
    
    print('Emergency redeployment completed!')
    
    # Verify deployment
    import time
    time.sleep(5)  # Wait for deployment
    
    import requests
    try:
        response = requests.get('https://www.ieltsaiprep.com/')
        if '$36' in response.text and response.text.count('$36') >= 4:
            print('SUCCESS: Website verified with correct $36 pricing')
            return True
        else:
            print('ERROR: Website deployment may have failed')
            return False
    except Exception as e:
        print(f'Could not verify website: {e}')
        return False

if __name__ == "__main__":
    emergency_redeploy()
'''
    
    with open('emergency_redeploy.py', 'w') as f:
        f.write(script_content)
    
    print("Created emergency_redeploy.py - run this to restore the working template")

def create_monitoring_script():
    """Create a script to monitor the website and alert if pricing changes"""
    monitor_content = '''#!/usr/bin/env python3
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
        print(f"\\n[{timestamp}] Checking website...")
        
        check_website_pricing()
        
        print(f"Next check in {check_interval_minutes} minutes")
        time.sleep(check_interval_minutes * 60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        continuous_monitor()
    else:
        check_website_pricing()
'''
    
    with open('monitor_website.py', 'w') as f:
        f.write(monitor_content)
    
    print("Created monitor_website.py - run this to check website pricing")

if __name__ == "__main__":
    print("Creating permanent safeguards for the working template...")
    
    # Backup current deployment
    backup_zip, backup_template = backup_current_lambda()
    
    # Create emergency scripts
    create_deployment_script()
    create_monitoring_script()
    
    print("\\nSafeguards created:")
    print("1. Production backup saved")
    print("2. emergency_redeploy.py - restores working template")
    print("3. monitor_website.py - checks pricing is correct")
    print("\\nTo ensure permanent fix:")
    print("- Run monitor_website.py daily to verify pricing")
    print("- If website ever shows wrong pricing, run emergency_redeploy.py")
    print("- Keep working_template.html file protected")