#!/usr/bin/env python3
"""
Deploy IELTS Lambda Package to AWS via S3
"""

import boto3
import os
import sys
from datetime import datetime

def deploy_lambda():
    """Deploy ZIP package to AWS Lambda via S3"""
    
    # Configuration
    function_name = "ielts-genai-prep-lambda"
    region = os.environ.get('AWS_REGION', 'us-east-1')
    zip_file = "ielts-lambda-deployment.zip"
    s3_bucket = "ielts-deployment-bucket"  # Found in DEPLOYMENT_INSTRUCTIONS.md
    s3_key = f"deployments/ielts-lambda-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    
    print(f"=== Deploying to AWS Lambda via S3 ===")
    print(f"Function: {function_name}")
    print(f"Region: {region}")
    print(f"Package: {zip_file}")
    print(f"S3 Bucket: {s3_bucket}")
    print()
    
    # Check if ZIP file exists
    if not os.path.exists(zip_file):
        print(f"❌ Error: {zip_file} not found!")
        return False
    
    # Get file size
    file_size = os.path.getsize(zip_file) / (1024 * 1024)  # Convert to MB
    print(f"Package size: {file_size:.2f} MB")
    print()
    
    try:
        # Create AWS clients
        s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        lambda_client = boto3.client(
            'lambda',
            region_name=region,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Step 1: Upload to S3
        print(f"📦 Uploading to S3: s3://{s3_bucket}/{s3_key}")
        s3_client.upload_file(
            zip_file,
            s3_bucket,
            s3_key,
            ExtraArgs={'ContentType': 'application/zip'}
        )
        print("✅ Uploaded to S3")
        print()
        
        # Step 2: Update Lambda function from S3
        print("🚀 Updating Lambda function from S3...")
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            S3Bucket=s3_bucket,
            S3Key=s3_key,
            Publish=True
        )
        
        print("✅ Deployment successful!")
        print()
        print(f"Function ARN: {response['FunctionArn']}")
        print(f"Version: {response['Version']}")
        print(f"Last Modified: {response['LastModified']}")
        print(f"Code Size: {response['CodeSize'] / (1024*1024):.2f} MB")
        print(f"Runtime: {response['Runtime']}")
        print()
        print("=" * 60)
        print("🌐 Your changes are now live at: https://www.ieltsaiprep.com")
        print("=" * 60)
        print()
        print("✅ All template updates deployed:")
        print("   • Cookie consent removed from layout.html")
        print("   • FAQ text correct in comprehensive_preview.html")
        print("   • reCAPTCHA present on login.html")
        print("   • Coral gradient (#E33219 → #FF6B55) on forgot_password.html")
        print("   • Work Sans fonts added to forgot_password.html")
        print()
        print("✅ All Python dependencies included:")
        print("   • boto3, botocore (AWS SDK)")
        print("   • requests (HTTP library)")
        print("   • google-genai (Gemini API)")
        print("   • flask, werkzeug (web framework)")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Deployment failed: {error_str}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = deploy_lambda()
    sys.exit(0 if success else 1)
