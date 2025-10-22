#!/usr/bin/env python3
"""
Update CloudFront distribution to serve only www.ieltsaiprep.com
"""
import boto3
import json

def update_cloudfront_www_only():
    """Update CloudFront to serve only www.ieltsaiprep.com"""
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    distribution_id = 'E1EPXAU67877FR'
    
    try:
        # Get current distribution config with ETag
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        print(f"Current aliases: {config['Aliases']['Items']}")
        
        # Update aliases to only include www.ieltsaiprep.com
        config['Aliases'] = {
            'Quantity': 1,
            'Items': ['www.ieltsaiprep.com']
        }
        
        # Update the distribution
        update_response = cloudfront.update_distribution(
            Id=distribution_id,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"CloudFront distribution updated successfully!")
        print(f"Distribution ID: {distribution_id}")
        print(f"New aliases: {config['Aliases']['Items']}")
        print(f"Status: {update_response['Distribution']['Status']}")
        print("\nThe distribution will propagate globally. This may take 15-20 minutes.")
        print("After propagation:")
        print("✓ www.ieltsaiprep.com will work normally")
        print("✗ ieltsaiprep.com will no longer be served by CloudFront")
        
        return True
        
    except Exception as e:
        print(f"Error updating CloudFront distribution: {e}")
        return False

def check_nameservers():
    """Check current DNS nameservers for ieltsaiprep.com"""
    
    import subprocess
    
    try:
        # Check nameservers
        result = subprocess.run(['dig', '+short', 'NS', 'ieltsaiprep.com'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            nameservers = result.stdout.strip().split('\n')
            print(f"\nCurrent nameservers for ieltsaiprep.com:")
            for ns in nameservers:
                if ns.strip():
                    print(f"  - {ns.strip()}")
                    
            # Check if using Route 53
            if any('awsdns' in ns for ns in nameservers):
                print("\n✓ Domain is using AWS Route 53 nameservers")
                print("You can configure DNS records in Route 53 to redirect ieltsaiprep.com to www.ieltsaiprep.com if needed")
            else:
                print("\n! Domain is using external nameservers")
                print("You may want to configure a redirect from ieltsaiprep.com to www.ieltsaiprep.com in your DNS provider")
        else:
            print("Could not check nameservers")
            
    except Exception as e:
        print(f"Error checking nameservers: {e}")

if __name__ == "__main__":
    print("Updating CloudFront distribution to serve only www.ieltsaiprep.com...")
    
    if update_cloudfront_www_only():
        print("\nCloudFront update initiated successfully!")
        check_nameservers()
    else:
        print("CloudFront update failed")