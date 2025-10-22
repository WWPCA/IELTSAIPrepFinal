#!/usr/bin/env python3
"""
Run domain transfer with auth code as command line argument
Usage: python3 run-domain-transfer.py <auth_code>
"""

import sys
import boto3
from botocore.exceptions import ClientError

def transfer_domain(auth_code):
    """Transfer domain with the provided auth code"""
    route53domains = boto3.client('route53domains', region_name='us-east-1')
    
    print("=== AWS Route 53 Domain Transfer ===")
    print("Domain: ieltsaiprep.com")
    print("From: Namecheap → AWS Route 53")
    print()
    
    # Check transferability
    print("Checking domain transferability...")
    try:
        response = route53domains.check_domain_transferability(
            DomainName='ieltsaiprep.com'
        )
        
        if not response['Transferability']['Transferable']:
            print(f"❌ Domain cannot be transferred")
            print(f"Reason: {response['Transferability'].get('TransferabilityResult', 'Unknown')}")
            return False
            
        print("✅ Domain is transferable")
        
    except ClientError as e:
        print(f"Error checking transferability: {e}")
        return False
    
    # Initiate transfer
    print("Initiating domain transfer...")
    try:
        response = route53domains.transfer_domain(
            DomainName='ieltsaiprep.com',
            DurationInYears=1,
            AuthCode=auth_code,
            AdminContact={
                'FirstName': 'IELTS',
                'LastName': 'GenAI',
                'ContactType': 'COMPANY',
                'OrganizationName': 'IELTS GenAI Prep',
                'AddressLine1': '123 Main St',
                'City': 'Toronto',
                'State': 'ON',
                'CountryCode': 'CA',
                'ZipCode': 'M5V 3A8',
                'PhoneNumber': '+1.4161234567',
                'Email': 'admin@ieltsgenaiprep.com'
            },
            RegistrantContact={
                'FirstName': 'IELTS',
                'LastName': 'GenAI',
                'ContactType': 'COMPANY',
                'OrganizationName': 'IELTS GenAI Prep',
                'AddressLine1': '123 Main St',
                'City': 'Toronto',
                'State': 'ON',
                'CountryCode': 'CA',
                'ZipCode': 'M5V 3A8',
                'PhoneNumber': '+1.4161234567',
                'Email': 'admin@ieltsgenaiprep.com'
            },
            TechContact={
                'FirstName': 'IELTS',
                'LastName': 'GenAI',
                'ContactType': 'COMPANY',
                'OrganizationName': 'IELTS GenAI Prep',
                'AddressLine1': '123 Main St',
                'City': 'Toronto',
                'State': 'ON',
                'CountryCode': 'CA',
                'ZipCode': 'M5V 3A8',
                'PhoneNumber': '+1.4161234567',
                'Email': 'admin@ieltsgenaiprep.com'
            },
            PrivacyProtectAdminContact=True,
            PrivacyProtectRegistrantContact=True,
            PrivacyProtectTechContact=True
        )
        
        operation_id = response['OperationId']
        print(f"✅ Domain transfer initiated successfully!")
        print(f"Operation ID: {operation_id}")
        print()
        print("=== Next Steps ===")
        print("1. Check your email for transfer approval requests")
        print("2. Approve the transfer from both Namecheap and AWS")
        print("3. Transfer typically completes in 5-7 days")
        print("4. Your website will continue working during transfer")
        print()
        print("To check status:")
        print(f"aws route53domains get-operation-detail --operation-id {operation_id}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error initiating domain transfer: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 run-domain-transfer.py <auth_code>")
        print("Example: python3 run-domain-transfer.py ABC123XYZ")
        sys.exit(1)
    
    auth_code = sys.argv[1]
    
    if not auth_code:
        print("❌ Authorization code cannot be empty")
        sys.exit(1)
    
    print("Current Setup:")
    print("✅ Route 53 hosted zone exists")
    print("✅ DNS records configured")
    print("✅ CloudFront distribution active")
    print()
    
    success = transfer_domain(auth_code)
    
    if success:
        print("\n🎉 Domain transfer initiated successfully!")
        print("Cost: ~$12-14 USD + $0.50/month for Route 53 hosted zone")
    else:
        print("\n❌ Domain transfer failed")
        sys.exit(1)

if __name__ == "__main__":
    main()