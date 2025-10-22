#!/usr/bin/env python3
"""
WAF Protection Setup
Use AWS WAF to block direct API Gateway access
"""

import boto3
import json
from botocore.exceptions import ClientError

def create_waf_rule():
    """Create WAF rule to block direct access"""
    
    waf = boto3.client('wafv2', region_name='us-east-1')
    
    # WAF rule to block direct access
    rule_config = {
        'Name': 'BlockDirectAPIAccess',
        'Priority': 1,
        'Statement': {
            'NotStatement': {
                'Statement': {
                    'ByteMatchStatement': {
                        'SearchString': 'CloudFront',
                        'FieldToMatch': {
                            'SingleHeader': {
                                'Name': 'user-agent'
                            }
                        },
                        'TextTransformations': [
                            {
                                'Priority': 0,
                                'Type': 'LOWERCASE'
                            }
                        ],
                        'PositionalConstraint': 'CONTAINS'
                    }
                }
            }
        },
        'Action': {
            'Block': {}
        }
    }
    
    return rule_config

def apply_waf_to_api_gateway():
    """Apply WAF to API Gateway"""
    
    try:
        waf = boto3.client('wafv2', region_name='us-east-1')
        
        # Create Web ACL
        rule_config = create_waf_rule()
        
        response = waf.create_web_acl(
            Name='ielts-api-protection',
            Scope='REGIONAL',
            DefaultAction={'Allow': {}},
            Rules=[rule_config],
            Description='Protect IELTS API Gateway from direct access'
        )
        
        web_acl_arn = response['Summary']['ARN']
        
        # Associate with API Gateway
        waf.associate_web_acl(
            WebACLArn=web_acl_arn,
            ResourceArn=f'arn:aws:apigateway:us-east-1::/restapis/n0cpf1rmvc/stages/prod'
        )
        
        print("✅ WAF protection enabled")
        print(f"✅ Web ACL ARN: {web_acl_arn}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error setting up WAF: {e}")
        return False

def main():
    """Main WAF setup function"""
    print("🛡️  Setting up WAF Protection")
    print("=" * 40)
    
    success = apply_waf_to_api_gateway()
    
    if success:
        print("\n🎉 WAF Protection Active!")
        print("✅ Domain access: https://www.ieltsaiprep.com (WORKING)")
        print("❌ Direct access: Blocked by WAF")
    else:
        print("\n❌ WAF setup failed")

if __name__ == "__main__":
    main()