#!/bin/bash

# Production AWS Route 53 Migration for ieltsaiprep.com
# Following AWS Route 53 best practices for inactive domain migration
# References:
# - https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/migrate-dns-domain-inactive.html
# - https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html
# - https://docs.aws.amazon.com/Route53/latest/APIReference/Welcome.html
# - https://docs.aws.amazon.com/cli/latest/reference/route53/

set -e  # Exit on any error

echo "AWS Route 53 Production Migration for ieltsaiprep.com"
echo "Following AWS Route 53 Migration Best Practices"
echo "=================================================="

# Configuration
DOMAIN_NAME="ieltsaiprep.com"
REGION="us-east-1"
CALLER_REFERENCE="ieltsaiprep-prod-$(date +%s)"
API_ID="n0cpf1rmvc"
STAGE="prod"

# Validate AWS CLI configuration
echo "Validating AWS CLI configuration..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "ERROR: AWS CLI not configured. Run 'aws configure' first."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"
echo "Target Region: $REGION"

echo ""
echo "Phase 1: Pre-Migration Assessment"
echo "================================="

# Check if domain already has a hosted zone
echo "Checking for existing hosted zones..."
EXISTING_ZONES=$(aws route53 list-hosted-zones \
    --query "HostedZones[?Name=='${DOMAIN_NAME}.'].Id" \
    --output text)

if [ ! -z "$EXISTING_ZONES" ]; then
    echo "WARNING: Existing hosted zone found for $DOMAIN_NAME"
    echo "Hosted Zone IDs: $EXISTING_ZONES"
    read -p "Delete existing hosted zones and continue? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "Migration cancelled."
        exit 1
    fi
    
    # Delete existing hosted zones
    for zone_id in $EXISTING_ZONES; do
        clean_zone_id=$(echo $zone_id | sed 's|/hostedzone/||')
        echo "Deleting existing hosted zone: $clean_zone_id"
        
        # Delete all records except SOA and NS
        aws route53 list-resource-record-sets \
            --hosted-zone-id $clean_zone_id \
            --query 'ResourceRecordSets[?Type!=`SOA` && Type!=`NS`]' \
            --output json > /tmp/records_to_delete.json
        
        if [ -s /tmp/records_to_delete.json ] && [ "$(cat /tmp/records_to_delete.json)" != "[]" ]; then
            # Create delete batch
            echo '{"Changes": []}' | jq '.Changes = [.ResourceRecordSets[] | {Action: "DELETE", ResourceRecordSet: .}]' /tmp/records_to_delete.json > /tmp/delete_batch.json
            
            aws route53 change-resource-record-sets \
                --hosted-zone-id $clean_zone_id \
                --change-batch file:///tmp/delete_batch.json
        fi
        
        aws route53 delete-hosted-zone --id $clean_zone_id
        echo "Deleted hosted zone: $clean_zone_id"
    done
fi

echo ""
echo "Phase 2: Create Route 53 Hosted Zone"
echo "===================================="

echo "Creating hosted zone for $DOMAIN_NAME..."
HOSTED_ZONE_RESPONSE=$(aws route53 create-hosted-zone \
    --name $DOMAIN_NAME \
    --caller-reference $CALLER_REFERENCE \
    --hosted-zone-config Comment="IELTS GenAI Prep production domain - migrated from Namecheap" \
    --output json)

HOSTED_ZONE_ID=$(echo $HOSTED_ZONE_RESPONSE | jq -r '.HostedZone.Id' | sed 's|/hostedzone/||')
echo "Hosted Zone ID: $HOSTED_ZONE_ID"

# Get Route 53 nameservers
echo "Retrieving Route 53 nameservers..."
NAMESERVERS=$(aws route53 get-hosted-zone \
    --id $HOSTED_ZONE_ID \
    --query 'DelegationSet.NameServers' \
    --output json)

echo "Route 53 Nameservers:"
echo $NAMESERVERS | jq -r '.[]' | while read ns; do
    echo "  $ns"
done

# Save nameservers for reference
echo $NAMESERVERS | jq -r '.[]' > route53-nameservers.txt

echo ""
echo "Phase 3: Configure DNS Records"
echo "============================="

# Create health check for the API Gateway endpoint (optional but recommended)
echo "Creating health check for API Gateway endpoint..."
HEALTH_CHECK_RESPONSE=$(aws route53 create-health-check \
    --caller-reference "ieltsaiprep-health-$(date +%s)" \
    --health-check-config Type=HTTPS,ResourcePath=/,FullyQualifiedDomainName=${API_ID}.execute-api.${REGION}.amazonaws.com,Port=443,RequestInterval=30,FailureThreshold=3 \
    --output json 2>/dev/null || echo '{"HealthCheck":{"Id":"skipped"}}')

HEALTH_CHECK_ID=$(echo $HEALTH_CHECK_RESPONSE | jq -r '.HealthCheck.Id')
if [ "$HEALTH_CHECK_ID" != "null" ] && [ "$HEALTH_CHECK_ID" != "skipped" ]; then
    echo "Health Check ID: $HEALTH_CHECK_ID"
    
    # Tag the health check
    aws route53 change-tags-for-resource \
        --resource-type healthcheck \
        --resource-id $HEALTH_CHECK_ID \
        --add-tags Key=Project,Value=IELTSGenAIPrep Key=Environment,Value=Production
fi

# Create initial A record (placeholder)
echo "Creating placeholder A record..."
cat > /tmp/create-placeholder-a-record.json << EOF
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
    --change-batch file:///tmp/create-placeholder-a-record.json

# Create AAAA record for IPv6 support (optional)
echo "Creating IPv6 AAAA record..."
cat > /tmp/create-ipv6-record.json << EOF
{
    "Changes": [{
        "Action": "CREATE",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "AAAA",
            "TTL": 300,
            "ResourceRecords": [{
                "Value": "2001:db8::1"
            }]
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/create-ipv6-record.json

echo ""
echo "Phase 4: SSL Certificate Management"
echo "==================================="

# Clean up any existing certificates
echo "Cleaning up existing SSL certificates..."
EXISTING_CERTS=$(aws acm list-certificates \
    --region $REGION \
    --query "CertificateSummaryList[?DomainName=='$DOMAIN_NAME' || contains(SubjectAlternativeNameSummary, '$DOMAIN_NAME')].CertificateArn" \
    --output text)

for cert_arn in $EXISTING_CERTS; do
    if [ ! -z "$cert_arn" ]; then
        echo "Deleting existing certificate: $cert_arn"
        aws acm delete-certificate --certificate-arn $cert_arn --region $REGION
    fi
done

# Request new SSL certificate with Route 53 validation
echo "Requesting SSL certificate with Route 53 DNS validation..."
CERTIFICATE_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN_NAME \
    --subject-alternative-names "www.$DOMAIN_NAME" "api.$DOMAIN_NAME" "*.$DOMAIN_NAME" \
    --validation-method DNS \
    --key-algorithm RSA_2048 \
    --region $REGION \
    --tags Key=Project,Value=IELTSGenAIPrep Key=Environment,Value=Production Key=ManagedBy,Value=Route53 \
    --output text --query 'CertificateArn')

echo "SSL Certificate ARN: $CERTIFICATE_ARN"

# Wait for certificate validation options to be available
echo "Waiting for certificate validation options..."
sleep 20

# Create DNS validation records automatically
echo "Creating DNS validation records in Route 53..."
MAX_VALIDATION_ATTEMPTS=12
validation_attempt=1

while [ $validation_attempt -le $MAX_VALIDATION_ATTEMPTS ]; do
    echo "Validation attempt $validation_attempt/$MAX_VALIDATION_ATTEMPTS"
    
    # Get validation options
    VALIDATION_OPTIONS=$(aws acm describe-certificate \
        --certificate-arn $CERTIFICATE_ARN \
        --region $REGION \
        --query 'Certificate.DomainValidationOptions' \
        --output json)
    
    if [ "$VALIDATION_OPTIONS" != "null" ] && [ "$VALIDATION_OPTIONS" != "[]" ]; then
        echo "Processing validation records..."
        
        # Process each domain validation option
        echo $VALIDATION_OPTIONS | jq -c '.[]' | while read domain_validation; do
            domain_name=$(echo $domain_validation | jq -r '.DomainName')
            validation_name=$(echo $domain_validation | jq -r '.ResourceRecord.Name // empty')
            validation_value=$(echo $domain_validation | jq -r '.ResourceRecord.Value // empty')
            
            if [ ! -z "$validation_name" ] && [ ! -z "$validation_value" ]; then
                echo "Creating validation record for $domain_name"
                
                # Create validation record
                cat > /tmp/validation-${domain_name//[^a-zA-Z0-9]/-}.json << EOF
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
                    --change-batch file:///tmp/validation-${domain_name//[^a-zA-Z0-9]/-}.json
                
                echo "Validation record created for $domain_name"
            fi
        done
        
        break
    fi
    
    sleep 15
    validation_attempt=$((validation_attempt + 1))
done

# Wait for certificate to be issued
echo "Waiting for SSL certificate validation..."
MAX_CERT_ATTEMPTS=24
cert_attempt=1

while [ $cert_attempt -le $MAX_CERT_ATTEMPTS ]; do
    CERT_STATUS=$(aws acm describe-certificate \
        --certificate-arn $CERTIFICATE_ARN \
        --region $REGION \
        --query 'Certificate.Status' \
        --output text)
    
    echo "Certificate status ($cert_attempt/$MAX_CERT_ATTEMPTS): $CERT_STATUS"
    
    if [ "$CERT_STATUS" = "ISSUED" ]; then
        echo "SSL Certificate successfully issued!"
        break
    elif [ "$CERT_STATUS" = "FAILED" ]; then
        echo "ERROR: SSL Certificate validation failed"
        aws acm describe-certificate \
            --certificate-arn $CERTIFICATE_ARN \
            --region $REGION \
            --query 'Certificate.DomainValidationOptions'
        exit 1
    fi
    
    sleep 30
    cert_attempt=$((cert_attempt + 1))
done

if [ $cert_attempt -gt $MAX_CERT_ATTEMPTS ]; then
    echo "ERROR: Certificate validation timeout"
    exit 1
fi

echo ""
echo "Phase 5: API Gateway Custom Domain Configuration"
echo "==============================================="

# Create custom domain in API Gateway
echo "Creating custom domain in API Gateway..."
aws apigatewayv2 create-domain-name \
    --domain-name $DOMAIN_NAME \
    --domain-name-configurations CertificateArn=$CERTIFICATE_ARN,EndpointType=REGIONAL,SecurityPolicy=TLS_1_2 \
    --tags Project=IELTSGenAIPrep,Environment=Production,ManagedBy=Route53 \
    --region $REGION

# Wait for domain to be ready
sleep 10

# Get target domain name
TARGET_DOMAIN=$(aws apigatewayv2 get-domain-name \
    --domain-name $DOMAIN_NAME \
    --region $REGION \
    --query 'DomainNameConfigurations[0].TargetDomainName' \
    --output text)

echo "API Gateway Target Domain: $TARGET_DOMAIN"

# Create API mapping
echo "Creating API mapping..."
aws apigatewayv2 create-api-mapping \
    --domain-name $DOMAIN_NAME \
    --api-id $API_ID \
    --stage $STAGE \
    --region $REGION

echo ""
echo "Phase 6: Update Route 53 Records to Point to API Gateway"
echo "========================================================"

# Get the correct hosted zone ID for API Gateway in us-east-1
API_GATEWAY_HOSTED_ZONE_ID="Z1UJRXOUMOOFQ8"

# Update A record to point to API Gateway (alias record)
echo "Updating A record to point to API Gateway..."
cat > /tmp/update-a-record-alias.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "A",
            "AliasTarget": {
                "DNSName": "$TARGET_DOMAIN",
                "EvaluateTargetHealth": true,
                "HostedZoneId": "$API_GATEWAY_HOSTED_ZONE_ID"
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/update-a-record-alias.json

# Update AAAA record for IPv6 (alias record)
echo "Updating AAAA record to point to API Gateway..."
cat > /tmp/update-aaaa-record-alias.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "$DOMAIN_NAME",
            "Type": "AAAA",
            "AliasTarget": {
                "DNSName": "$TARGET_DOMAIN",
                "EvaluateTargetHealth": true,
                "HostedZoneId": "$API_GATEWAY_HOSTED_ZONE_ID"
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/update-aaaa-record-alias.json

# Create www subdomain alias
echo "Creating www subdomain alias..."
cat > /tmp/create-www-alias.json << EOF
{
    "Changes": [{
        "Action": "UPSERT",
        "ResourceRecordSet": {
            "Name": "www.$DOMAIN_NAME",
            "Type": "A",
            "AliasTarget": {
                "DNSName": "$TARGET_DOMAIN",
                "EvaluateTargetHealth": true,
                "HostedZoneId": "$API_GATEWAY_HOSTED_ZONE_ID"
            }
        }
    }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $HOSTED_ZONE_ID \
    --change-batch file:///tmp/create-www-alias.json

echo ""
echo "Phase 7: Application Configuration Update"
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

# Update mobile app configuration
echo "Updating mobile app configuration..."
cat > mobile-app-config.js << EOF
// IELTS GenAI Prep - Production Configuration
// Route 53 managed custom domain

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

echo ""
echo "Phase 8: Migration Summary and Next Steps"
echo "========================================"

# Create migration summary
cat > route53-migration-summary.json << EOF
{
  "domain": "$DOMAIN_NAME",
  "migrationDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "awsAccount": "$ACCOUNT_ID",
  "hostedZoneId": "$HOSTED_ZONE_ID",
  "certificateArn": "$CERTIFICATE_ARN",
  "healthCheckId": "$HEALTH_CHECK_ID",
  "apiGatewayTarget": "$TARGET_DOMAIN",
  "nameservers": $(cat route53-nameservers.txt | jq -R . | jq -s .),
  "status": "ready-for-nameserver-update"
}
EOF

echo "Migration Summary:"
echo "=================="
echo "Domain: $DOMAIN_NAME"
echo "Hosted Zone ID: $HOSTED_ZONE_ID"
echo "SSL Certificate: $CERTIFICATE_ARN"
echo "Health Check: $HEALTH_CHECK_ID"
echo "API Gateway Target: $TARGET_DOMAIN"
echo ""
echo "CRITICAL NEXT STEP - Update Nameservers at Namecheap:"
echo "====================================================="
echo ""
echo "1. Login to Namecheap account"
echo "2. Go to Domain List → ieltsaiprep.com → Manage"
echo "3. Change nameservers to Custom DNS"
echo "4. Enter these Route 53 nameservers:"
echo ""

cat route53-nameservers.txt | while read ns; do
    echo "   $ns"
done

echo ""
echo "5. Save changes and wait 24-48 hours for DNS propagation"
echo ""
echo "Testing Commands (after DNS propagation):"
echo "========================================="
echo "dig $DOMAIN_NAME"
echo "dig www.$DOMAIN_NAME"
echo "curl -I https://$DOMAIN_NAME"
echo "curl -I https://www.$DOMAIN_NAME"
echo ""
echo "Files Created:"
echo "============="
echo "- route53-nameservers.txt (nameservers for Namecheap)"
echo "- route53-migration-summary.json (complete migration details)"
echo "- capacitor.config.json (updated mobile app config)"
echo "- mobile-app-config.js (updated API endpoints)"
echo ""

# Cleanup temporary files
rm -f /tmp/*.json

echo "AWS Route 53 Migration Completed Successfully!"
echo "Update nameservers at Namecheap to complete the migration."