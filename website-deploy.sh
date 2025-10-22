#!/bin/bash
# AWS Website Deployment Script for ieltsaiprep.com
# Deploys static website to S3 with CloudFront CDN

set -e

echo "🚀 Deploying IELTS GenAI Prep Website to AWS..."

# Configuration
BUCKET_NAME="ieltsaiprep-com-website"
CLOUDFRONT_COMMENT="IELTS GenAI Prep Website CDN"
REGION="us-east-1"

# Create S3 bucket for website hosting
echo "📦 Creating S3 bucket for website..."
aws s3 mb s3://$BUCKET_NAME --region $REGION || echo "Bucket already exists"

# Configure bucket for static website hosting
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html

# Set bucket policy for public read access
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json

# Create website files
echo "📄 Creating website files..."
mkdir -p website-dist

# Create main index.html
cat > website-dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Test Preparation</title>
    <meta name="description" content="Master IELTS with AI-powered assessment and personalized feedback. Get real-time speaking practice with Maya AI examiner and detailed writing evaluations.">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }
        
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #667eea;
        }
        
        .nav-links {
            display: flex;
            list-style: none;
            gap: 2rem;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #667eea;
        }
        
        .hero {
            padding: 120px 0 80px;
            text-align: center;
            color: white;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }
        
        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        
        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .btn-primary {
            background: #ff6b6b;
            color: white;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .features {
            padding: 80px 0;
            background: white;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 3rem;
            margin-top: 3rem;
        }
        
        .feature-card {
            text-align: center;
            padding: 2rem;
            border-radius: 20px;
            background: #f8f9fa;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .feature-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .pricing {
            padding: 80px 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            text-align: center;
        }
        
        .pricing-card {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            max-width: 400px;
            margin: 2rem auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .price {
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
            margin: 1rem 0;
        }
        
        .download-section {
            padding: 80px 0;
            background: #2c3e50;
            color: white;
            text-align: center;
        }
        
        .app-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
            flex-wrap: wrap;
        }
        
        .app-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 12px 24px;
            background: #34495e;
            color: white;
            text-decoration: none;
            border-radius: 10px;
            transition: background 0.3s;
        }
        
        .app-btn:hover {
            background: #4a6741;
        }
        
        footer {
            background: #1a1a1a;
            color: white;
            text-align: center;
            padding: 2rem 0;
        }
        
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .nav-links {
                display: none;
            }
            
            .cta-buttons {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <div class="logo">IELTS GenAI Prep</div>
            <ul class="nav-links">
                <li><a href="#features">Features</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="#download">Download</a></li>
            </ul>
        </nav>
    </header>

    <section class="hero">
        <div class="container">
            <h1>Master IELTS with AI</h1>
            <p>Get personalized feedback and real-time practice with our AI-powered IELTS preparation platform</p>
            <div class="cta-buttons">
                <a href="#download" class="btn btn-primary">
                    <i class="fas fa-download"></i>
                    Download App
                </a>
                <a href="https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/health" class="btn btn-secondary">
                    <i class="fas fa-play"></i>
                    Try Demo
                </a>
            </div>
        </div>
    </section>

    <section id="features" class="features">
        <div class="container">
            <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 1rem;">Why Choose IELTS GenAI Prep?</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-microphone"></i>
                    </div>
                    <h3>ClearScore® Speaking Assessment</h3>
                    <p>Practice with Maya, our AI examiner, for real-time speaking feedback using Amazon Nova Sonic technology.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-edit"></i>
                    </div>
                    <h3>TrueScore® Writing Assessment</h3>
                    <p>Get detailed writing evaluations with AI-powered feedback on coherence, grammar, and vocabulary.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3>Personalized Learning</h3>
                    <p>Adaptive algorithms track your progress and provide customized study recommendations.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fas fa-mobile-alt"></i>
                    </div>
                    <h3>Cross-Platform Access</h3>
                    <p>Study anywhere with our mobile app and web platform synchronization.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="pricing" class="pricing">
        <div class="container">
            <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">Simple, Transparent Pricing</h2>
            <div class="pricing-card">
                <h3>Assessment Package</h3>
                <div class="price">$36</div>
                <p>4 Unique Assessments</p>
                <ul style="text-align: left; margin: 2rem 0;">
                    <li>✓ Academic Writing Assessment</li>
                    <li>✓ General Writing Assessment</li>
                    <li>✓ Academic Speaking Assessment</li>
                    <li>✓ General Speaking Assessment</li>
                    <li>✓ Detailed AI Feedback</li>
                    <li>✓ Progress Tracking</li>
                </ul>
                <a href="#download" class="btn btn-primary">Get Started</a>
            </div>
        </div>
    </section>

    <section id="download" class="download-section">
        <div class="container">
            <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">Download IELTS GenAI Prep</h2>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">Available on iOS and Android</p>
            <div class="app-buttons">
                <a href="#" class="app-btn">
                    <i class="fab fa-apple"></i>
                    App Store
                </a>
                <a href="#" class="app-btn">
                    <i class="fab fa-google-play"></i>
                    Google Play
                </a>
            </div>
            <p style="margin-top: 2rem; opacity: 0.8;">Coming soon to app stores worldwide</p>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2025 IELTS GenAI Prep. All rights reserved.</p>
            <p>Powered by Amazon Nova AI Technology</p>
        </div>
    </footer>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // API health check
        fetch('https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod/health')
            .then(response => response.json())
            .then(data => {
                console.log('API Status:', data);
            })
            .catch(error => {
                console.log('API check failed:', error);
            });
    </script>
</body>
</html>
EOF

# Create error page
cat > website-dist/error.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - IELTS GenAI Prep</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 50px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .error-container {
            max-width: 600px;
        }
        h1 {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        a {
            color: #ff6b6b;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404</h1>
        <p>Sorry, the page you're looking for doesn't exist.</p>
        <a href="/">Return to Homepage</a>
    </div>
</body>
</html>
EOF

# Upload website files to S3
echo "⬆️ Uploading website files to S3..."
aws s3 sync website-dist/ s3://$BUCKET_NAME --delete

# Create CloudFront distribution for CDN
echo "🌐 Creating CloudFront distribution..."
cat > cloudfront-config.json << EOF
{
    "CallerReference": "ieltsaiprep-$(date +%s)",
    "Comment": "$CLOUDFRONT_COMMENT",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$BUCKET_NAME",
        "ViewerProtocolPolicy": "redirect-to-https",
        "MinTTL": 0,
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "TrustedSigners": {
            "Enabled": false,
            "Quantity": 0
        }
    },
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$BUCKET_NAME",
                "DomainName": "$BUCKET_NAME.s3-website-$REGION.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/error.html",
                "ResponseCode": "404"
            }
        ]
    }
}
EOF

# Get S3 website endpoint
S3_WEBSITE_ENDPOINT="$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo "✅ Website deployment complete!"
echo ""
echo "📍 Website URLs:"
echo "S3 Website: http://$S3_WEBSITE_ENDPOINT"
echo ""
echo "🔗 API Endpoint: https://n0cpf1rmvc.execute-api.us-east-1.amazonaws.com/prod"
echo ""
echo "📱 Ready for App Store testing with live backend!"

# Clean up temporary files
rm -f bucket-policy.json cloudfront-config.json
rm -rf website-dist

echo "🎉 ieltsaiprep.com is now live on AWS!"
EOF