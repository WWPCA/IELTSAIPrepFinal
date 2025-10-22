#!/bin/bash

# Get current CloudFront distribution configuration
aws cloudfront get-distribution-config --id E1EPXAU67877FR --region us-east-1 > distribution-config-raw.json

# Extract ETag for update
ETAG=$(grep '"ETag"' distribution-config-raw.json | cut -d'"' -f4)

# Create updated configuration with all HTTP methods
cat > updated-distribution-config.json << 'EOF'
{
  "CallerReference": "ielts-genai-prep-2025-06-20",
  "Aliases": {
    "Quantity": 2,
    "Items": [
      "ieltsaiprep.com",
      "www.ieltsaiprep.com"
    ]
  },
  "DefaultRootObject": "",
  "Comment": "IELTS GenAI Prep Production Distribution",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "ielts-api-gateway-origin",
        "DomainName": "n0cpf1rmvc.execute-api.us-east-1.amazonaws.com",
        "OriginPath": "/prod",
        "CustomOriginConfig": {
          "HTTPPort": 443,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only",
          "OriginSslProtocols": {
            "Quantity": 1,
            "Items": ["TLSv1.2"]
          }
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "ielts-api-gateway-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {
        "Forward": "all"
      },
      "Headers": {
        "Quantity": 8,
        "Items": [
          "Authorization",
          "Content-Type",
          "Origin",
          "Referer",
          "User-Agent",
          "Host",
          "Accept",
          "Accept-Language"
        ]
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 0,
    "MaxTTL": 31536000,
    "Compress": true
  },
  "CacheBehaviors": {
    "Quantity": 2,
    "Items": [
      {
        "PathPattern": "/api/*",
        "TargetOriginId": "ielts-api-gateway-origin",
        "ViewerProtocolPolicy": "https-only",
        "AllowedMethods": {
          "Quantity": 7,
          "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
          "CachedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
          }
        },
        "ForwardedValues": {
          "QueryString": true,
          "Cookies": {
            "Forward": "all"
          },
          "Headers": {
            "Quantity": 10,
            "Items": [
              "Authorization",
              "Content-Type",
              "Origin",
              "Referer",
              "User-Agent",
              "Host",
              "Accept",
              "Accept-Language",
              "X-Forwarded-For",
              "X-Forwarded-Proto"
            ]
          }
        },
        "MinTTL": 0,
        "DefaultTTL": 0,
        "MaxTTL": 0,
        "Compress": false
      },
      {
        "PathPattern": "/assessment/*",
        "TargetOriginId": "ielts-api-gateway-origin",
        "ViewerProtocolPolicy": "https-only",
        "AllowedMethods": {
          "Quantity": 7,
          "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
          "CachedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"]
          }
        },
        "ForwardedValues": {
          "QueryString": true,
          "Cookies": {
            "Forward": "all"
          },
          "Headers": {
            "Quantity": 12,
            "Items": [
              "Authorization",
              "Content-Type",
              "Origin",
              "Referer",
              "User-Agent",
              "Host",
              "Accept",
              "Accept-Language",
              "Cache-Control",
              "Pragma",
              "X-Forwarded-For",
              "X-Forwarded-Proto"
            ]
          }
        },
        "MinTTL": 0,
        "DefaultTTL": 0,
        "MaxTTL": 0,
        "Compress": false
      }
    ]
  },
  "PriceClass": "PriceClass_All",
  "ViewerCertificate": {
    "ACMCertificateArn": "arn:aws:acm:us-east-1:116981806044:certificate/7ddc9aad-f9f3-4b19-bfd6-09bd0e478799",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "WebACLId": "",
  "HttpVersion": "http2",
  "IsIPV6Enabled": true,
  "Logging": {
    "Enabled": false,
    "IncludeCookies": false,
    "Bucket": "",
    "Prefix": ""
  }
}
EOF

echo "CloudFront distribution configuration updated to support all HTTP methods"