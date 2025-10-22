#!/usr/bin/env python3
"""
Test AWS Route 53 domains service accessibility
"""

import boto3
from botocore.exceptions import ClientError

def test_domains_service():
    """Test if we can access Route 53 domains service"""
    try:
        # Route 53 domains must be accessed from us-east-1
        client = boto3.client('route53domains', region_name='us-east-1')
        
        # Try to list domains (this should work even if we have no domains)
        response = client.list_domains()
        print("✅ AWS Route 53 domains service accessible")
        print(f"Current domains: {len(response.get('Domains', []))}")
        
        # Test domain availability check
        response = client.check_domain_availability(
            DomainName='example12345.com'
        )
        print("✅ Domain availability check working")
        
        return True
        
    except ClientError as e:
        print(f"❌ AWS Route 53 domains service error: {e}")
        return False

def test_transferability():
    """Test domain transferability check"""
    try:
        client = boto3.client('route53domains', region_name='us-east-1')
        
        response = client.check_domain_transferability(
            DomainName='ieltsaiprep.com'
        )
        
        transferable = response['Transferability']['Transferable']
        print(f"Domain transferability: {'✅ Yes' if transferable else '❌ No'}")
        
        if not transferable:
            print(f"Reason: {response['Transferability'].get('TransferabilityResult', 'Unknown')}")
        
        return transferable
        
    except ClientError as e:
        print(f"❌ Error checking transferability: {e}")
        return False

def main():
    print("=== AWS Route 53 Domains Service Test ===")
    
    if not test_domains_service():
        print("Cannot access AWS Route 53 domains service")
        return
    
    if not test_transferability():
        print("Domain cannot be transferred")
        return
    
    print("\n✅ All tests passed - domain transfer should work")

if __name__ == "__main__":
    main()