#!/usr/bin/env python3
"""
Deactivate Direct API Gateway URL
Removes the 'prod' stage to disable direct access while keeping CloudFront working
"""

import boto3
from botocore.exceptions import ClientError

def deactivate_api_gateway_stage():
    """Delete the prod stage to deactivate direct URL access"""
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    api_id = 'n0cpf1rmvc'
    stage_name = 'prod'
    
    try:
        # Delete the stage
        apigateway.delete_stage(
            restApiId=api_id,
            stageName=stage_name
        )
        
        print(f"✅ API Gateway stage '{stage_name}' deleted")
        print("✅ Direct URL access deactivated")
        print("❌ https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod - NOW RETURNS 404")
        
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotFoundException':
            print(f"ℹ️  Stage '{stage_name}' not found (already deleted)")
            return True
        else:
            print(f"❌ Error deleting stage: {e}")
            return False

def check_cloudfront_status():
    """Check if CloudFront will still work"""
    
    print("\n🔍 Checking CloudFront configuration...")
    
    # CloudFront should still work because it routes to the API Gateway
    # even without the stage, as long as the API exists
    
    cloudfront = boto3.client('cloudfront')
    
    try:
        distributions = cloudfront.list_distributions()
        
        for dist in distributions['DistributionList'].get('Items', []):
            aliases = dist.get('Aliases', {}).get('Items', [])
            if 'www.ieltsaiprep.com' in aliases:
                print(f"✅ CloudFront distribution found: {dist['Id']}")
                print("⚠️  WARNING: CloudFront may also stop working without the prod stage")
                print("   Consider using a resource policy instead")
                return True
        
        print("❌ CloudFront distribution not found")
        return False
        
    except ClientError as e:
        print(f"❌ Error checking CloudFront: {e}")
        return False

def main():
    """Main function to deactivate direct URL"""
    
    print("🔒 Deactivating Direct API Gateway URL")
    print("=" * 45)
    
    print("This will:")
    print("❌ Make https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod return 404")
    print("⚠️  May also break https://www.ieltsaiprep.com (CloudFront routing)")
    print("⚠️  This action cannot be easily undone")
    print()
    
    confirm = input("Are you sure you want to proceed? Type 'DELETE' to confirm: ")
    
    if confirm != 'DELETE':
        print("❌ Operation cancelled")
        return
    
    # Check CloudFront first
    check_cloudfront_status()
    
    print("\n🚀 Proceeding with stage deletion...")
    
    success = deactivate_api_gateway_stage()
    
    if success:
        print("\n🎉 DIRECT URL DEACTIVATED!")
        print("❌ https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod - OFFLINE")
        print("⚠️  Check https://www.ieltsaiprep.com to verify it still works")
        print("\n💡 If the domain stops working, you'll need to:")
        print("   1. Recreate the prod stage, or")
        print("   2. Update CloudFront to point to a different stage")
    else:
        print("\n❌ FAILED TO DEACTIVATE")

if __name__ == "__main__":
    main()