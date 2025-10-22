#!/usr/bin/env python3
"""
Check current CloudFront distribution configuration
Get the correct domain name for DNS records
"""

import boto3
import json
from botocore.exceptions import ClientError

def get_cloudfront_distributions():
    """Get all CloudFront distributions"""
    cloudfront = boto3.client('cloudfront')
    
    try:
        response = cloudfront.list_distributions()
        
        if 'DistributionList' not in response or 'Items' not in response['DistributionList']:
            print("No CloudFront distributions found")
            return []
        
        distributions = response['DistributionList']['Items']
        
        for dist in distributions:
            dist_id = dist['Id']
            domain_name = dist['DomainName']
            status = dist['Status']
            
            print(f"Distribution ID: {dist_id}")
            print(f"Domain Name: {domain_name}")
            print(f"Status: {status}")
            
            # Check if this distribution serves ieltsaiprep.com
            if 'Aliases' in dist and dist['Aliases']['Quantity'] > 0:
                aliases = dist['Aliases']['Items']
                print(f"Aliases: {', '.join(aliases)}")
                
                if 'ieltsaiprep.com' in aliases or 'www.ieltsaiprep.com' in aliases:
                    print("✅ This distribution serves ieltsaiprep.com")
                    return {
                        'id': dist_id,
                        'domain': domain_name,
                        'aliases': aliases,
                        'status': status
                    }
            else:
                print("No aliases configured")
            
            print("-" * 50)
        
        return distributions
        
    except ClientError as e:
        print(f"Error getting CloudFront distributions: {e}")
        return []

def get_current_dns_records():
    """Get current DNS records for ieltsaiprep.com from Route 53"""
    route53 = boto3.client('route53')
    
    try:
        # List hosted zones
        response = route53.list_hosted_zones_by_name(DNSName='ieltsaiprep.com')
        
        for zone in response['HostedZones']:
            if zone['Name'] == 'ieltsaiprep.com.':
                zone_id = zone['Id']
                print(f"Found hosted zone: {zone_id}")
                
                # Get DNS records
                records_response = route53.list_resource_record_sets(
                    HostedZoneId=zone_id
                )
                
                print("\nCurrent DNS Records:")
                for record in records_response['ResourceRecordSets']:
                    record_name = record['Name']
                    record_type = record['Type']
                    
                    if record_type in ['A', 'AAAA', 'CNAME']:
                        print(f"  {record_name} ({record_type})")
                        
                        if 'AliasTarget' in record:
                            print(f"    → {record['AliasTarget']['DNSName']}")
                        elif 'ResourceRecords' in record:
                            values = [r['Value'] for r in record['ResourceRecords']]
                            print(f"    → {', '.join(values)}")
                
                return True
        
        print("No hosted zone found for ieltsaiprep.com")
        return False
        
    except ClientError as e:
        print(f"Error getting DNS records: {e}")
        return False

def main():
    """Main function to check current configuration"""
    print("=== Current AWS Configuration Check ===")
    print()
    
    print("1. CloudFront Distributions:")
    print("-" * 30)
    cloudfront_config = get_cloudfront_distributions()
    
    print("\n2. Current DNS Records:")
    print("-" * 30)
    get_current_dns_records()
    
    if cloudfront_config:
        print(f"\n3. Domain Transfer Configuration:")
        print("-" * 30)
        print(f"CloudFront Domain: {cloudfront_config['domain']}")
        print(f"Use this domain in the DNS A record for www.ieltsaiprep.com")
        print(f"CloudFront Hosted Zone ID: Z2FDTNDATAQYW2")

if __name__ == "__main__":
    main()