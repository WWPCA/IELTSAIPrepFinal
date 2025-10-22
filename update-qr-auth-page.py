#!/usr/bin/env python3
"""
Update QR auth page to match comprehensive design template
"""
import boto3
import zipfile

def create_enhanced_qr_auth_lambda():
    """Create Lambda with comprehensive QR auth page matching home page design"""
    
    # Read the comprehensive home page for styling reference
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # Create comprehensive QR auth page template
    qr_auth_page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Access IELTS GenAI Prep - Download Mobile App">
    <title>Access Portal - IELTS GenAI Prep</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .navbar {
            background-color: #fff !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .navbar-brand {
            font-weight: bold;
            color: #4361ee !important;
        }
        
        .access-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-top: 100px;
            padding: 50px;
        }
        
        .download-banner {
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            margin-bottom: 40px;
        }
        
        .step-card {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        
        .step-card:hover {
            transform: translateY(-2px);
            border-color: #4361ee;
        }
        
        .step-number {
            background: #4361ee;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .feature-highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 30px;
            text-align: center;
            margin-top: 30px;
        }
        
        .app-store-badges {
            text-align: center;
            margin: 30px 0;
        }
        
        .app-store-badges img {
            height: 60px;
            margin: 0 10px;
        }
        
        .cross-platform-note {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .price-highlight {
            color: #28a745;
            font-weight: bold;
            font-size: 1.1em;
        }
    </style>
</head>

<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-graduation-cap me-2"></i>IELTS GenAI Prep
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <div class="access-container">
                    <!-- Header -->
                    <div class="text-center mb-4">
                        <h1 class="display-5 fw-bold mb-3">Access IELTS GenAI Prep</h1>
                        <p class="lead">World's ONLY GenAI Assessment Platform for IELTS Test Preparation</p>
                    </div>

                    <!-- Download Banner -->
                    <div class="download-banner">
                        <h2><i class="fas fa-mobile-alt me-2"></i>Download Our Mobile App First</h2>
                        <p class="mb-0">To access our GenAI assessment platform</p>
                    </div>

                    <!-- Steps -->
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <div class="step-card h-100">
                                <div class="d-flex align-items-start">
                                    <div class="step-number">1</div>
                                    <div>
                                        <h5><strong>Download</strong></h5>
                                        <p class="mb-0">Get IELTS GenAI Prep from the App Store or Google Play</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4 mb-3">
                            <div class="step-card h-100">
                                <div class="d-flex align-items-start">
                                    <div class="step-number">2</div>
                                    <div>
                                        <h5><strong>Purchase</strong></h5>
                                        <p class="mb-0">Register and purchase assessment packages <span class="price-highlight">($36.00 each)</span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4 mb-3">
                            <div class="step-card h-100">
                                <div class="d-flex align-items-start">
                                    <div class="step-number">3</div>
                                    <div>
                                        <h5><strong>Access</strong></h5>
                                        <p class="mb-0">Login on this website using your mobile app credentials</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- App Store Badges -->
                    <div class="app-store-badges">
                        <h5 class="mb-3">Download IELTS GenAI Prep:</h5>
                        <div class="d-flex justify-content-center flex-wrap">
                            <div class="badge bg-dark text-light me-3 mb-2 p-3">
                                <i class="fab fa-apple me-2"></i>Available on App Store
                            </div>
                            <div class="badge bg-success text-light mb-2 p-3">
                                <i class="fab fa-google-play me-2"></i>Get it on Google Play
                            </div>
                        </div>
                    </div>

                    <!-- Feature Highlight -->
                    <div class="feature-highlight">
                        <h4><i class="fas fa-star me-2"></i>What You Get</h4>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <p><i class="fas fa-check me-2"></i><strong>TrueScore® Writing Assessment</strong></p>
                                <p><i class="fas fa-check me-2"></i><strong>ClearScore® Speaking Assessment</strong></p>
                            </div>
                            <div class="col-md-6">
                                <p><i class="fas fa-check me-2"></i>4 Unique Assessments per Package</p>
                                <p><i class="fas fa-check me-2"></i>Academic & General Training Options</p>
                            </div>
                        </div>
                    </div>

                    <!-- Cross-Platform Access -->
                    <div class="cross-platform-note">
                        <div class="row align-items-center">
                            <div class="col-md-2 text-center">
                                <i class="fas fa-shield-alt fa-2x text-success"></i>
                            </div>
                            <div class="col-md-10">
                                <h5 class="mb-2"><i class="fas fa-sync-alt me-2 text-success"></i>Secure Cross-Platform Access</h5>
                                <p class="mb-0">One account works on both mobile and web platforms! After purchasing in the mobile app, use the same login credentials to access assessments on desktop/laptop through this website.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Login Button -->
                    <div class="text-center mt-4">
                        <p class="mb-3">Already have an account?</p>
                        <a href="/login" class="btn btn-primary btn-lg px-5">
                            <i class="fas fa-sign-in-alt me-2"></i>Login to Your Account
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="py-4 mt-5">
        <div class="container">
            <div class="row">
                <div class="col-12 text-center text-white">
                    <p>&copy; 2024 IELTS GenAI Prep. All rights reserved.</p>
                    <div>
                        <a href="/privacy-policy" class="text-white me-3">Privacy Policy</a>
                        <a href="/terms-of-service" class="text-white">Terms of Service</a>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

    # Create Lambda function code with enhanced QR auth page
    lambda_code = f'''import json

def lambda_handler(event, context):
    """Lambda handler with comprehensive pages"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    print(f"Processing {{method}} {{path}}")
    
    # Comprehensive home page HTML content
    home_html = """{home_content.replace('\\', '\\\\').replace('"', '\\"')}"""
    
    # Enhanced QR auth page
    qr_auth_html = """{qr_auth_page.replace('\\', '\\\\').replace('"', '\\"')}"""
    
    if path == '/' or path == '/index.html':
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            }},
            'body': home_html
        }}
    
    elif path == '/qr-auth':
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            }},
            'body': qr_auth_html
        }}
    
    elif path == '/login':
        login_html = """<!DOCTYPE html>
<html>
<head>
    <title>Login - IELTS GenAI Prep</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
        }}
        .login-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-top: 100px;
            padding: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <div class="text-center mb-4">
                        <h1 class="fw-bold mb-3"><i class="fas fa-graduation-cap me-2 text-primary"></i>IELTS GenAI Prep</h1>
                        <h2>Login to Your Account</h2>
                    </div>
                    <div class="alert alert-info">
                        <h5><i class="fas fa-info-circle me-2"></i>Mobile-First Access Required</h5>
                        <p class="mb-3">To access assessments, please:</p>
                        <ol>
                            <li>Download our mobile app from App Store or Google Play</li>
                            <li>Create account and purchase assessment packages ($36 each)</li>
                            <li>Return here and login with your mobile app credentials</li>
                        </ol>
                        <div class="text-center mt-3">
                            <a href="/qr-auth" class="btn btn-primary">
                                <i class="fas fa-mobile-alt me-2"></i>Get Mobile App
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': login_html
        }}
    
    elif path == '/privacy-policy':
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '<!DOCTYPE html><html><head><title>Privacy Policy - IELTS GenAI Prep</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h1>Privacy Policy</h1><p>IELTS GenAI Prep Privacy Policy - Coming Soon</p></div></body></html>'
        }}
    
    elif path == '/terms-of-service':
        return {{
            'statusCode': 200,
            'headers': {{'Content-Type': 'text/html'}},
            'body': '<!DOCTYPE html><html><head><title>Terms of Service - IELTS GenAI Prep</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h1>Terms of Service</h1><p>IELTS GenAI Prep Terms of Service - Coming Soon</p></div></body></html>'
        }}
    
    else:
        return {{
            'statusCode': 302,
            'headers': {{'Location': '/'}},
            'body': ''
        }}
'''
    
    # Create deployment package
    with zipfile.ZipFile('enhanced-qr-auth-lambda.zip', 'w') as zip_file:
        zip_file.writestr('simple_lambda.py', lambda_code)
    
    print("Enhanced QR auth Lambda package created successfully")
    return True

def deploy_enhanced_lambda():
    """Deploy the enhanced Lambda function with comprehensive QR auth page"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        with open('enhanced-qr-auth-lambda.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.update_function_code(
            FunctionName='ielts-genai-prep-api',
            ZipFile=zip_content
        )
        
        print(f"Lambda function updated successfully!")
        print(f"Function ARN: {response['FunctionArn']}")
        
        return True
        
    except Exception as e:
        print(f"Error updating Lambda function: {e}")
        return False

if __name__ == "__main__":
    print("Creating enhanced QR auth page...")
    if create_enhanced_qr_auth_lambda():
        print("Deploying enhanced Lambda with comprehensive QR auth page...")
        if deploy_enhanced_lambda():
            print("Enhanced QR auth page deployment completed successfully!")
            print("QR auth page now matches comprehensive design template")
        else:
            print("Deployment failed")
    else:
        print("Package creation failed")