#!/usr/bin/env python3
"""
AWS Route 53 Domain Transfer Script
Transfers ieltsaiprep.com from Namecheap to AWS Route 53
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_hosted_zone():
    """Create hosted zone for ieltsaiprep.com in Route 53"""
    route53 = boto3.client('route53')
    
    try:
        # Check if hosted zone already exists
        response = route53.list_hosted_zones_by_name(DNSName='ieltsaiprep.com')
        
        for zone in response['HostedZones']:
            if zone['Name'] == 'ieltsaiprep.com.':
                print(f"Hosted zone already exists: {zone['Id']}")
                return zone['Id']
        
        # Create new hosted zone
        response = route53.create_hosted_zone(
            Name='ieltsaiprep.com',
            CallerReference=str(int(time.time())),
            HostedZoneConfig={
                'Comment': 'IELTS GenAI Prep domain hosted zone',
                'PrivateZone': False
            }
        )
        
        zone_id = response['HostedZone']['Id']
        name_servers = response['DelegationSet']['NameServers']
        
        print(f"Created hosted zone: {zone_id}")
        print("Name servers:")
        for ns in name_servers:
            print(f"  - {ns}")
        
        return zone_id
        
    except ClientError as e:
        print(f"Error creating hosted zone: {e}")
        return None

def create_dns_records(zone_id):
    """Create DNS records for ieltsaiprep.com"""
    route53 = boto3.client('route53')
    
    # Current CloudFront distribution domain
    cloudfront_domain = "d2ehqyfqw00g6j.cloudfront.net"  # Your actual CloudFront domain
    
    records = [
        {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': 'www.ieltsaiprep.com',
                'Type': 'A',
                'AliasTarget': {
                    'DNSName': cloudfront_domain,
                    'EvaluateTargetHealth': False,
                    'HostedZoneId': 'Z2FDTNDATAQYW2'  # CloudFront hosted zone ID
                }
            }
        },
        {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': 'ieltsaiprep.com',
                'Type': 'A',
                'TTL': 300,
                'ResourceRecords': [
                    {'Value': '1.2.3.4'}  # Redirect to www
                ]
            }
        }
    ]
    
    try:
        response = route53.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                'Comment': 'Initial DNS records for ieltsaiprep.com',
                'Changes': records
            }
        )
        
        print(f"DNS records created successfully")
        print(f"Change ID: {response['ChangeInfo']['Id']}")
        
        return True
        
    except ClientError as e:
        print(f"Error creating DNS records: {e}")
        return False

def initiate_domain_transfer(auth_code):
    """Initiate domain transfer from Namecheap to Route 53"""
    route53domains = boto3.client('route53domains', region_name='us-east-1')
    
    try:
        # Check if domain is available for transfer
        response = route53domains.check_domain_transferability(
            DomainName='ieltsaiprep.com'
        )
        
        if not response['Transferability']['Transferable']:
            print("Domain is not transferable")
            print(f"Reason: {response['Transferability'].get('TransferabilityResult', 'Unknown')}")
            return False
        
        # Get domain transfer cost
        response = route53domains.get_domain_detail(
            DomainName='ieltsaiprep.com'
        )
        
        print("Domain transfer is available")
        print("Transfer cost will be displayed during the transfer process")
        
        # Initiate transfer
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
        
        print(f"Domain transfer initiated successfully")
        print(f"Operation ID: {response['OperationId']}")
        
        return True
        
    except ClientError as e:
        print(f"Error initiating domain transfer: {e}")
        return False

def check_transfer_status(operation_id):
    """Check the status of domain transfer"""
    route53domains = boto3.client('route53domains', region_name='us-east-1')
    
    try:
        response = route53domains.get_operation_detail(
            OperationId=operation_id
        )
        
        status = response['Status']
        print(f"Transfer status: {status}")
        
        if status == 'SUCCESSFUL':
            print("Domain transfer completed successfully!")
        elif status == 'FAILED':
            print(f"Domain transfer failed: {response.get('Message', 'Unknown error')}")
        elif status == 'IN_PROGRESS':
            print("Domain transfer is in progress...")
        
        return status
        
    except ClientError as e:
        print(f"Error checking transfer status: {e}")
        return None

def main():
    """Main transfer process"""
    print("=== AWS Route 53 Domain Transfer ===")
    print("Domain: ieltsaiprep.com")
    print("From: Namecheap")
    print("To: AWS Route 53")
    print()
    
    # Step 1: Create hosted zone
    print("Step 1: Creating hosted zone...")
    zone_id = create_hosted_zone()
    if not zone_id:
        print("Failed to create hosted zone")
        return
    
    # Step 2: Create DNS records
    print("\nStep 2: Creating DNS records...")
    if not create_dns_records(zone_id):
        print("Failed to create DNS records")
        return
    
    # Step 3: Get auth code from user
    print("\nStep 3: Domain transfer initiation")
    auth_code = input("Enter the EPP/Authorization code from Namecheap: ").strip()
    
    if not auth_code:
        print("Authorization code is required")
        return
    
    # Step 4: Initiate transfer
    print("\nStep 4: Initiating domain transfer...")
    if initiate_domain_transfer(auth_code):
        print("\nTransfer initiated successfully!")
        print("You will receive email notifications about the transfer progress.")
        print("The transfer typically takes 5-7 days to complete.")
    else:
        print("Failed to initiate domain transfer")

if __name__ == "__main__":
    main()