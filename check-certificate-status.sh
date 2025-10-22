#!/bin/bash

# Check SSL Certificate Validation Status
echo "Checking SSL certificate validation status..."

CERT_ARN="arn:aws:acm:us-east-1:116981806044:certificate/7ddc9aad-f9f3-4b19-bfd6-09bd0e478799"

aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region us-east-1 \
  --query 'Certificate.{Status:Status,DomainValidations:DomainValidationOptions[*].[DomainName,ValidationStatus]}' \
  --output table

echo ""
echo "Certificate Status Legend:"
echo "- PENDING_VALIDATION: Waiting for DNS validation"
echo "- SUCCESS: Domain validated successfully"
echo "- ISSUED: Certificate is ready for use"
echo ""
echo "Once all domains show SUCCESS and certificate shows ISSUED,"
echo "we can create the API Gateway custom domain mapping."