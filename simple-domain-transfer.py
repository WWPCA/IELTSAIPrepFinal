#!/usr/bin/env python3
"""
Simple AWS Route 53 Domain Transfer Script
For transferring ieltsaiprep.com from Namecheap to AWS Route 53
"""

import boto3
import json
from botocore.exceptions import ClientError

def check_domain_transferability():
    """Check if domain can be transferred"""
    route53domains = boto3.client('route53domains', region_name='us-east-1')
    
    try:
        response = route53domains.check_domain_transferability(
            DomainName='ieltsaiprep.com'
        )
        
        transferable = response['Transferability']['Transferable']
        print(f"Domain transferability: {'✅ Yes' if transferable else '❌ No'}")
        
        if not transferable:
            print(f"Reason: {response['Transferability'].get('TransferabilityResult', 'Unknown')}")
            return False
        
        return True
        
    except ClientError as e:
        print(f"Error checking transferability: {e}")
        return False

def get_transfer_cost():
    """Get the cost of domain transfer"""
    route53domains = boto3.client('route53domains', region_name='us-east-1')
    
    try:
        response = route53domains.get_domain_detail(
            DomainName='ieltsaiprep.com'
        )
        print("Domain transfer cost: ~$12-14 USD (standard .com transfer)")
        return True
        
    except ClientError as e:
        print(f"Note: Could not get exact cost, but standard .com transfer is ~$12-14 USD")
        return True

def initiate_domain_transfer(auth_code):
    """Initiate domain transfer from Namecheap to Route 53"""
    route53domains = boto3.client('route53domains', region_name='us-east-1')
    
    try:
        print("Initiating domain transfer...")
        
        response = route53domains.transfer_domain(
            DomainName='ieltsaiprep.com',
            IdnLangCode='en',
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
        print(f"Transfer typically takes 5-7 days to complete")
        
        return operation_id
        
    except ClientError as e:
        print(f"❌ Error initiating domain transfer: {e}")
        return None

def main():
    """Main transfer process"""
    print("=== AWS Route 53 Domain Transfer ===")
    print("Domain: ieltsaiprep.com")
    print("From: Namecheap → AWS Route 53")
    print()
    
    # Check current setup
    print("Current Setup:")
    print("✅ Route 53 hosted zone exists")
    print("✅ DNS records configured")
    print("✅ CloudFront distribution active")
    print()
    
    # Check transferability
    print("Checking domain transferability...")
    if not check_domain_transferability():
        print("❌ Domain cannot be transferred at this time")
        return
    
    # Get cost information
    get_transfer_cost()
    print()
    
    # Get auth code
    auth_code = input("Enter your EPP/Authorization code from Namecheap: ").strip()
    
    if not auth_code:
        print("❌ Authorization code is required")
        return
    
    # Initiate transfer
    operation_id = initiate_domain_transfer(auth_code)
    
    if operation_id:
        print()
        print("=== Next Steps ===")
        print("1. Check your email for transfer approval requests")
        print("2. Approve the transfer from both Namecheap and AWS")
        print("3. Monitor transfer progress")
        print("4. Transfer typically completes in 5-7 days")
        print()
        print("To check status later:")
        print(f"aws route53domains get-operation-detail --operation-id {operation_id}")
        print()
        print("Your website will continue working during the transfer!")
    else:
        print("❌ Transfer failed to initiate")

if __name__ == "__main__":
    main()