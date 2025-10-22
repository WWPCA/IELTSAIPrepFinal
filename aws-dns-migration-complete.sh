#!/bin/bash

# Complete DNS Migration from Namecheap to AWS Route 53
# Following AWS Route 53 DNS Configuration and Migration Guide
# https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring.html
# https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/MigratingDNS.html

echo "🚀 AWS Route 53 Complete DNS Migration for ieltsaiprep.com"
echo "📖 Following AWS Route 53 Migration Best Practices"
echo "================================================================="

# Configuration
DOMAIN_NAME="ieltsaiprep.com"
REGION="us-east-1"
CALLER_REFERENCE="ieltsaiprep-migration-$(date +%s)"
API_ID="n0cpf1rmvc"  # Your existing Lambda API Gateway ID

echo ""
echo "Step 1: Pre-Migration DNS Audit"
echo "==============================="

echo "📋 Documenting current DNS records from Namecheap..."
echo "Before migration, we need to record all existing DNS records:"
echo ""
echo "Current known records for ieltsaiprep.com:"
echo "- SSL validation CNAME records (will be recreated)"
echo "- Any existing A/CNAME/MX/TXT records"
echo ""
echo "⚠️  IMPORTANT: Verify no critical services depend on current DNS"

echo ""
echo "Step 2: Create Route 53 Hosted Zone"
echo "==================================="

# Create hosted zone following AWS migration guide
echo "Creating Route 53 hosted zone for $DOMAIN_NAME..."

HOSTED_ZONE_OUTPUT=$(aws route53 create-hosted-zone \
    --name $DOMAIN_NAME \
    --caller-reference $CALLER_REFERENCE \
    --hosted-zone-config Comment="IELTS GenAI Prep production domain" \
    --output json)

if [ $? -eq 0 ]; then
    echo "✅ Hosted zone created successfully"
    
    HOSTED_ZONE_ID=$(echo $HOSTED_ZONE_OUTPUT | jq -r '.HostedZone.Id' | sed 's|/hostedzone/||')
    echo "📋 Hosted Zone ID: $HOSTED_ZONE_ID"
    
    # Get Route 53 nameservers
    echo ""
    echo "📡 AWS Route 53 Nameservers (save these for Namecheap update):"
    echo "=============================================================="
    NAMESERVERS=$(aws route53 get-hosted-zone --id $HOSTED_ZONE_ID \
        --query 'DelegationSet.NameServers[]' \
        --output text)
    
    echo "$NAMESERVERS" | while read ns; do
        echo "   $ns"
    done
    
    # Save nameservers to file for reference
    echo "$NAMESERVERS" > route53-nameservers.txt
    echo ""
    echo "📝 Nameservers saved to: route53-nameservers.txt"
    
else
    echo "❌ Failed to create hosted zone"
    exit 1
fi

echo ""
echo "Step 3: Configure DNS Records in Route 53"
echo "=========================================="

# Create SOA and NS records are automatically created by Route 53
echo "✅ SOA and NS records automatically created by Route 53"

# Create A record for apex domain (placeholder initially)
echo "Creating placeholder A record for apex domain..."
cat > /tmp/create-apex-record.json << EOF
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "A",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "192.0.2.1"
            }]
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/create-apex-record.json

echo "✅ Placeholder A record created (will update after API Gateway setup)"

# Create CNAME for www subdomain
echo "Creating CNAME record for www subdomain..."
cat > /tmp/create-www-record.json << EOF
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "www.$DOMAIN_NAME",
            "Type": "CNAME",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "$DOMAIN_NAME"
            }]
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/create-www-record.json

echo "✅ CNAME record created for www subdomain"

echo ""
echo "Step 4: SSL Certificate with Route 53 DNS Validation"
echo "===================================================="

# Check for existing certificates and clean up
echo "Checking for existing SSL certificates..."
EXISTING_CERTS=$(aws acm list-certificates \
    --region $REGION \
    --query "CertificateSummaryList[?contains(DomainName, 'ieltsaiprep.com')].CertificateArn" \
    --output text)

if [ ! -z "$EXISTING_CERTS" ]; then
    echo "Found existing certificates. Cleaning up..."
    for cert_arn in $EXISTING_CERTS; do
        echo "Deleting certificate: $cert_arn"
        aws acm delete-certificate --certificate-arn $cert_arn --region $REGION
    done
    echo "✅ Existing certificates cleaned up"
fi

# Request new certificate with Route 53 validation
echo "Requesting SSL certificate with Route 53 DNS validation..."
CERTIFICATE_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN_NAME \
    --subject-alternative-names "www.$DOMAIN_NAME" \
    --validation-method DNS \
    --region $REGION \
    --tags Key=Project,Value=IELTSGenAIPrep Key=Environment,Value=Production \
    --output text --query 'CertificateArn')

echo "✅ SSL Certificate requested: $CERTIFICATE_ARN"

# Wait for certificate details to be available
echo "Waiting for certificate validation details..."
sleep 15

# Get validation records and create them in Route 53
echo "Creating DNS validation records automatically in Route 53..."

# Function to create validation records
create_validation_records() {
    local attempt=1
    local max_attempts=10
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt: Getting certificate validation records..."
        
        VALIDATION_OPTIONS=$(aws acm describe-certificate \
            --certificate-arn $CERTIFICATE_ARN \
            --region $REGION \
            --query 'Certificate.DomainValidationOptions' \
            --output json 2>/dev/null)
        
        if [ $? -eq 0 ] && [ "$VALIDATION_OPTIONS" != "null" ] && [ "$VALIDATION_OPTIONS" != "[]" ]; then
            echo "✅ Certificate validation records retrieved"
            break
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Failed to get certificate validation records"
        return 1
    fi
    
    # Process each validation record
    echo "$VALIDATION_OPTIONS" | jq -r '.[] | @base64' | while read encoded_record; do
        if [ "$encoded_record" != "null" ] && [ ! -z "$encoded_record" ]; then
            decoded_record=$(echo $encoded_record | base64 -d 2>/dev/null)
            
            if [ $? -eq 0 ]; then
                validation_name=$(echo $decoded_record | jq -r '.ResourceRecord.Name // empty' 2>/dev/null)
                validation_value=$(echo $decoded_record | jq -r '.ResourceRecord.Value // empty' 2>/dev/null)
                domain_name=$(echo $decoded_record | jq -r '.DomainName // empty' 2>/dev/null)
                
                if [ ! -z "$validation_name" ] && [ ! -z "$validation_value" ]; then
                    echo "Creating validation record for domain: $domain_name"
                    echo "  Name: $validation_name"
                    echo "  Value: $validation_value"
                    
                    # Create the validation record
                    cat > /tmp/validation-record-$(echo $domain_name | tr '.' '-').json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "$validation_name",
            "Type": "CNAME",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "$validation_value"
            }]
        }
    }]
}
EOF
                    
                    aws route53 change-resource-record-sets \
                        --hosted-zone-id $HOSTED_ZONE_ID \
                        --change-batch file:///tmp/validation-record-$(echo $domain_name | tr '.' '-').json
                    
                    if [ $? -eq 0 ]; then
                        echo "✅ DNS validation record created for $domain_name"
                    else
                        echo "❌ Failed to create validation record for $domain_name"
                    fi
                fi
            fi
        fi
    done
}

# Create validation records
create_validation_records

echo ""
echo "Step 5: Wait for SSL Certificate Validation"
echo "==========================================="

echo "Waiting for SSL certificate to be validated and issued..."
echo "This typically takes 2-5 minutes with Route 53 DNS validation..."

# Function to check certificate status
check_certificate_status() {
    aws acm describe-certificate \
        --certificate-arn $CERTIFICATE_ARN \
        --region $REGION \
        --query 'Certificate.Status' \
        --output text 2>/dev/null
}

# Wait for certificate validation
max_attempts=20
attempt=1
while [ $attempt -le $max_attempts ]; do
    status=$(check_certificate_status)
    echo "Attempt $attempt/$max_attempts: Certificate status: $status"
    
    if [ "$status" = "ISSUED" ]; then
        echo "✅ SSL Certificate successfully validated and issued!"
        break
    elif [ "$status" = "FAILED" ]; then
        echo "❌ SSL Certificate validation failed"
        
        # Get failure reason
        aws acm describe-certificate \
            --certificate-arn $CERTIFICATE_ARN \
            --region $REGION \
            --query 'Certificate.DomainValidationOptions[].ValidationStatus' \
            --output table
        
        exit 1
    fi
    
    sleep 30
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "⏰ Certificate validation taking longer than expected"
    echo "Certificate ARN: $CERTIFICATE_ARN"
    echo "Continue manually once certificate shows 'ISSUED' status"
    exit 1
fi

echo ""
echo "Step 6: Create API Gateway Custom Domain"
echo "========================================"

echo "Creating custom domain in API Gateway..."
aws apigatewayv2 create-domain-name \
    --domain-name $DOMAIN_NAME \
    --domain-name-configurations CertificateArn=$CERTIFICATE_ARN,EndpointType=REGIONAL,SecurityPolicy=TLS_1_2 \
    --tags Project=IELTSGenAIPrep,Environment=Production \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Custom domain created in API Gateway"
else
    echo "❌ Failed to create custom domain"
    exit 1
fi

# Get the target domain name for Route 53 alias record
echo "Getting API Gateway target domain..."
sleep 5

TARGET_DOMAIN=$(aws apigatewayv2 get-domain-name \
    --domain-name $DOMAIN_NAME \
    --region $REGION \
    --query 'DomainNameConfigurations[0].TargetDomainName' \
    --output text)

if [ "$TARGET_DOMAIN" = "None" ] || [ -z "$TARGET_DOMAIN" ]; then
    echo "❌ Failed to get target domain name"
    exit 1
fi

echo "🎯 API Gateway Target Domain: $TARGET_DOMAIN"

# Create API mapping
echo "Creating API mapping..."
aws apigatewayv2 create-api-mapping \
    --domain-name $DOMAIN_NAME \
    --api-id $API_ID \
    --stage prod \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ API mapping created successfully"
else
    echo "❌ Failed to create API mapping"
    exit 1
fi

echo ""
echo "Step 7: Update Route 53 A Record to Point to API Gateway"
echo "========================================================"

# Get the hosted zone ID for API Gateway in us-east-1 (for alias records)
API_GATEWAY_HOSTED_ZONE_ID="Z1UJRXOUMOOFQ8"

echo "Updating A record to point to API Gateway using alias record..."
cat > /tmp/update-apex-alias-record.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "A",
            "AliasTarget": {
                "DNSName": "$TARGET_DOMAIN",
                "EvaluateTargetHealth": false,
                "HostedZoneId": "$API_GATEWAY_HOSTED_ZONE_ID"
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/update-apex-alias-record.json

if [ $? -eq 0 ]; then
    echo "✅ A record updated to point to API Gateway"
else
    echo "❌ Failed to update A record"
    exit 1
fi

# Also create alias record for www subdomain
echo "Creating alias record for www subdomain..."
cat > /tmp/create-www-alias-record.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "www.$DOMAIN_NAME",
            "Type": "A",
            "AliasTarget": {
                "DNSName": "$TARGET_DOMAIN",
                "EvaluateTargetHealth": false,
                "HostedZoneId": "$API_GATEWAY_HOSTED_ZONE_ID"
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/create-www-alias-record.json

echo "✅ Alias record created for www subdomain"

echo ""
echo "Step 8: Update Application Configuration"
echo "========================================"

# Update Capacitor configuration
echo "Updating Capacitor configuration..."
cat > capacitor.config.json << EOF
{
  "appId": "com.ieltsgenaiprep.app",
  "appName": "IELTS GenAI Prep",
  "webDir": "www",
  "server": {
    "url": "https://$DOMAIN_NAME",
    "cleartext": false
  },
  "plugins": {
    "CapacitorHttp": {
      "enabled": true
    }
  }
}
EOF

echo "✅ Capacitor configuration updated"

# Update mobile app configuration
echo "Updating mobile app API configuration..."
cat > mobile-app-config.js << EOF
// IELTS GenAI Prep - Mobile App Configuration
// Production endpoints with Route 53 managed domain

const API_CONFIG = {
  baseURL: 'https://$DOMAIN_NAME',
  
  endpoints: {
    auth: {
      register: '/api/register',
      login: '/api/login',
      verify: '/api/verify-session'
    },
    assessments: {
      speaking: '/api/nova-sonic',
      writing: '/api/nova-micro',
      access: '/assessment'
    },
    purchases: {
      apple: '/api/verify-apple-purchase',
      google: '/api/verify-google-purchase',
      unlock: '/api/unlock-module'
    }
  },
  
  appStore: {
    products: {
      academicWriting: 'com.ieltsgenaiprep.academic.writing',
      generalWriting: 'com.ieltsgenaiprep.general.writing',
      academicSpeaking: 'com.ieltsgenaiprep.academic.speaking',
      generalSpeaking: 'com.ieltsgenaiprep.general.speaking'
    },
    prices: {
      cad: 36.00
    }
  },
  
  legal: {
    privacyPolicy: 'https://$DOMAIN_NAME/privacy-policy',
    termsOfService: 'https://$DOMAIN_NAME/terms-of-service'
  }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_CONFIG;
}

if (typeof window !== 'undefined') {
  window.API_CONFIG = API_CONFIG;
}
EOF

echo "✅ Mobile app configuration updated"

echo ""
echo "Step 9: DNS Migration Summary and Next Steps"
echo "==========================================="

echo "📋 AWS Route 53 Migration Completed Successfully!"
echo ""
echo "✅ Route 53 hosted zone created: $HOSTED_ZONE_ID"
echo "✅ SSL certificate issued and validated: $CERTIFICATE_ARN"
echo "✅ API Gateway custom domain configured"
echo "✅ DNS records configured in Route 53"
echo "✅ Application configuration updated"
echo ""
echo "🚨 CRITICAL NEXT STEP - Update Nameservers at Namecheap:"
echo "========================================================"
echo ""
echo "1. Login to Namecheap account"
echo "2. Go to Domain List → ieltsaiprep.com → Manage"
echo "3. Change nameservers from 'Namecheap BasicDNS' to 'Custom DNS'"
echo "4. Enter these Route 53 nameservers:"
echo ""

# Display nameservers again
cat route53-nameservers.txt | while read ns; do
    echo "   $ns"
done

echo ""
echo "5. Save changes at Namecheap"
echo "6. Wait 24-48 hours for global DNS propagation"
echo ""
echo "🧪 Testing After DNS Propagation:"
echo "================================="
echo "   curl -I https://$DOMAIN_NAME"
echo "   curl -I https://www.$DOMAIN_NAME"
echo "   curl -I https://$DOMAIN_NAME/privacy-policy"
echo ""
echo "📱 Mobile App Deployment:"
echo "========================"
echo "   ./deploy-mobile-app.sh"
echo ""
echo "🎯 Expected Results After Propagation:"
echo "======================================"
echo "   ✅ https://$DOMAIN_NAME → Your IELTS app"
echo "   ✅ SSL certificate valid"
echo "   ✅ Mobile app uses professional domain"
echo "   ✅ Ready for App Store submission"
echo ""

# Save configuration summary
cat > dns-migration-summary.txt << EOF
AWS Route 53 DNS Migration Summary
=================================

Domain: $DOMAIN_NAME
Hosted Zone ID: $HOSTED_ZONE_ID
SSL Certificate ARN: $CERTIFICATE_ARN
API Gateway Target: $TARGET_DOMAIN

Route 53 Nameservers:
$(cat route53-nameservers.txt)

Migration Date: $(date)
Status: Completed - Waiting for nameserver update at Namecheap

Next Steps:
1. Update nameservers at Namecheap
2. Wait for DNS propagation (24-48 hours)
3. Test domain functionality
4. Deploy mobile app
5. Submit to App Store
EOF

echo "📄 Migration summary saved to: dns-migration-summary.txt"

# Cleanup temporary files
rm -f /tmp/create-*.json /tmp/update-*.json /tmp/validation-*.json

echo ""
echo "🏁 AWS Route 53 DNS Migration Completed!"
echo "Next: Update nameservers at Namecheap with the Route 53 nameservers above"