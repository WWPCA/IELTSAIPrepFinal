#!/usr/bin/env python3
"""
Remove SSL validation CNAME records from Route 53 (no longer needed)
"""
import boto3

def remove_ssl_validation_records():
    """Remove SSL certificate validation CNAME records"""
    
    route53 = boto3.client('route53')
    hosted_zone_id = 'Z01451123MAROFMSZLXBI'
    
    # SSL validation records to remove
    records_to_remove = [
        {
            'Name': '_ac240725bce173c01adef0958d2a1d4c.ieltsaiprep.com.',
            'Type': 'CNAME',
            'TTL': 300,
            'ResourceRecords': [{'Value': '_2708eb3cfcc0efd2475eb8f51eaca121.xlfgrmvvlj.acm-validations.aws'}]
        },
        {
            'Name': '_3d1dd3b857c6f4ef303f9db8b3c32d64.www.ieltsaiprep.com.',
            'Type': 'CNAME', 
            'TTL': 300,
            'ResourceRecords': [{'Value': '_7b2288190e8b52918acf5428e80c6763.xlfgrmvvlj.acm-validations.aws'}]
        }
    ]
    
    changes = []
    for record in records_to_remove:
        changes.append({
            'Action': 'DELETE',
            'ResourceRecordSet': record
        })
    
    try:
        change_batch = {
            'Comment': 'Remove SSL validation CNAME records - certificates already validated',
            'Changes': changes
        }
        
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=change_batch
        )
        
        change_id = response['ChangeInfo']['Id']
        status = response['ChangeInfo']['Status']
        
        print(f"DNS cleanup initiated successfully!")
        print(f"Change ID: {change_id}")
        print(f"Status: {status}")
        print("\nRemoved SSL validation records:")
        print("  _ac240725bce173c01adef0958d2a1d4c.ieltsaiprep.com")
        print("  _3d1dd3b857c6f4ef303f9db8b3c32d64.www.ieltsaiprep.com")
        print("\nRemaining essential records:")
        print("  ieltsaiprep.com (NS) - Domain delegation")
        print("  ieltsaiprep.com (SOA) - Zone authority")
        print("  www.ieltsaiprep.com (A) - Your website")
        
        return True
        
    except Exception as e:
        print(f"Error removing SSL validation records: {e}")
        return False

if __name__ == "__main__":
    print("Cleaning up SSL validation CNAME records...")
    
    if remove_ssl_validation_records():
        print("\nDNS cleanup completed successfully!")
        print("Your Route 53 zone now contains only essential records.")
    else:
        print("DNS cleanup failed")