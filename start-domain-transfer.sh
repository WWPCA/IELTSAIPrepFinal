#!/bin/bash

echo "=== ieltsaiprep.com Domain Transfer to AWS Route 53 ==="
echo ""
echo "Current Status:"
echo "✅ Domain unlock requested from Namecheap"
echo "✅ CloudFront distribution: d2ehqyfqw00g6j.cloudfront.net"
echo "✅ Current Route 53 hosted zone exists"
echo ""

echo "IMPORTANT: Before starting the transfer, you need to:"
echo "1. Get the EPP/Authorization code from Namecheap"
echo "2. Ensure domain is unlocked at Namecheap"
echo "3. Disable WHOIS privacy protection temporarily"
echo ""

read -p "Do you have the EPP/Authorization code from Namecheap? (y/n): " has_code

if [ "$has_code" != "y" ]; then
    echo ""
    echo "Please complete these steps in Namecheap first:"
    echo "1. Log into your Namecheap account"
    echo "2. Go to Domain List → ieltsaiprep.com"
    echo "3. Click 'Manage' → 'Advanced DNS' or 'Transfer'"
    echo "4. Get the EPP/Authorization code"
    echo "5. Ensure domain is unlocked"
    echo "6. Disable WHOIS privacy protection"
    echo ""
    echo "Then run this script again."
    exit 1
fi

read -p "Enter the EPP/Authorization code: " auth_code

if [ -z "$auth_code" ]; then
    echo "Authorization code is required"
    exit 1
fi

echo ""
echo "Starting domain transfer process..."
echo ""

# Run the Python transfer script
python3 transfer-domain-to-route53.py << EOF
$auth_code
EOF

echo ""
echo "=== Next Steps ==="
echo "1. Check your email for transfer approval requests"
echo "2. Approve the transfer from both Namecheap and AWS"
echo "3. Monitor transfer status (typically 5-7 days)"
echo "4. Test website functionality after transfer"
echo ""
echo "Cost: ~$12-14 for transfer + $0.50/month for Route 53 hosted zone"
echo ""
echo "To check transfer status later, run:"
echo "aws route53domains get-operation-detail --operation-id <operation-id>"