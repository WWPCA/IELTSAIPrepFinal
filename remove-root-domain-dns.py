#!/usr/bin/env python3
"""
Remove DNS A record for ieltsaiprep.com, keeping only www.ieltsaiprep.com
"""
import boto3
import json

def remove_root_domain_dns():
    """Remove A record for ieltsaiprep.com from Route 53"""
    
    route53 = boto3.client('route53')
    hosted_zone_id = 'Z01451123MAROFMSZLXBI'
    
    try:
        # Create change batch to delete the A record for ieltsaiprep.com
        change_batch = {
            'Comment': 'Remove A record for ieltsaiprep.com - serving only www.ieltsaiprep.com',
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': 'ieltsaiprep.com.',
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': 'Z2FDTNDATAQYW2',
                            'DNSName': 'd2ehqyfqw00g6j.cloudfront.net.',
                            'EvaluateTargetHealth': False
                        }
                    }
                }
            ]
        }
        
        # Apply the DNS change
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        
        change_id = response['ChangeInfo']['Id']
        status = response['ChangeInfo']['Status']
        
        print(f"DNS change initiated successfully!")
        print(f"Change ID: {change_id}")
        print(f"Status: {status}")
        print(f"Removed A record for: ieltsaiprep.com")
        print(f"Keeping A record for: www.ieltsaiprep.com")
        print("\nDNS propagation will take 5-10 minutes globally.")
        print("After propagation:")
        print("✓ www.ieltsaiprep.com will continue working")
        print("✗ ieltsaiprep.com will no longer resolve to your site")
        
        return True
        
    except Exception as e:
        print(f"Error removing DNS record: {e}")
        return False

def verify_current_dns():
    """Verify current DNS configuration"""
    
    route53 = boto3.client('route53')
    hosted_zone_id = 'Z01451123MAROFMSZLXBI'
    
    try:
        response = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        
        print("Current DNS records:")
        for record in response['ResourceRecordSets']:
            if record['Type'] == 'A' and 'ieltsaiprep.com' in record['Name']:
                print(f"  {record['Name']} -> {record.get('AliasTarget', {}).get('DNSName', 'N/A')}")
        
    except Exception as e:
        print(f"Error checking DNS records: {e}")

if __name__ == "__main__":
    print("Current DNS configuration:")
    verify_current_dns()
    print("\nRemoving root domain DNS record...")
    
    if remove_root_domain_dns():
        print("\nDNS update completed successfully!")
        print("Only www.ieltsaiprep.com will be served after propagation.")
    else:
        print("DNS update failed")