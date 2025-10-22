#!/usr/bin/env python3
"""
Update authentication pages for mobile-first username/password with reCAPTCHA
"""
import boto3
import zipfile

def create_mobile_first_auth_lambda():
    """Create Lambda with mobile-first authentication pages"""
    
    # Read the comprehensive home page
    with open('public_home.html', 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    # Create mobile app access page (replacing QR auth)
    mobile_access_page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Access IELTS GenAI Prep - Download Mobile App">
    <title>Mobile App Access - IELTS GenAI Prep</title>
    
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
                        <p class="mb-0">Create account and purchase assessments through our mobile app</p>
                    </div>

                    <!-- Steps -->
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <div class="step-card h-100">
                                <div class="d-flex align-items-start">
                                    <div class="step-number">1</div>
                                    <div>
                                        <h5><strong>Download Mobile App</strong></h5>
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
                                        <h5><strong>Purchase Assessment</strong></h5>
                                        <p class="mb-0">Create account and purchase assessment packages <span class="price-highlight">($36.00 each)</span> through secure app store billing</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4 mb-3">
                            <div class="step-card h-100">
                                <div class="d-flex align-items-start">
                                    <div class="step-number">3</div>
                                    <div>
                                        <h5><strong>Login Anywhere</strong></h5>
                                        <p class="mb-0">Use your mobile app credentials to login on this website for desktop access</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Feature Highlight -->
                    <div class="feature-highlight">
                        <h4><i class="fas fa-star me-2"></i>What You Get with Each Purchase</h4>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <p><i class="fas fa-check me-2"></i><strong>TrueScore® Writing Assessment</strong> (4 unique assessments)</p>
                                <p><i class="fas fa-check me-2"></i><strong>ClearScore® Speaking Assessment</strong> (4 unique assessments)</p>
                            </div>
                            <div class="col-md-6">
                                <p><i class="fas fa-check me-2"></i>Official IELTS criteria alignment</p>
                                <p><i class="fas fa-check me-2"></i>Academic & General Training options</p>
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
                                <p class="mb-0">One account works on both mobile and web platforms! After purchasing in the mobile app, use the same username and password to login on this website for desktop/laptop access.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Login Button -->
                    <div class="text-center mt-4">
                        <p class="mb-3">Already purchased through the mobile app?</p>
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

    # Create enhanced login page with reCAPTCHA
    login_page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Google reCAPTCHA -->
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
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
        
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-top: 100px;
            padding: 40px;
        }
        
        .form-control:focus {
            border-color: #4361ee;
            box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.25);
        }
        
        .btn-primary {
            background-color: #4361ee;
            border-color: #4361ee;
        }
        
        .btn-primary:hover {
            background-color: #3651d4;
            border-color: #3651d4;
        }
        
        .mobile-first-notice {
            background: #e7f3ff;
            border: 1px solid #b3d7ff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
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
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/">Home</a>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="login-container">
                    <div class="text-center mb-4">
                        <h1 class="fw-bold mb-3">
                            <i class="fas fa-graduation-cap me-2 text-primary"></i>
                            IELTS GenAI Prep
                        </h1>
                        <h2 class="h4 mb-0">Login to Your Account</h2>
                    </div>

                    <!-- Mobile-First Notice -->
                    <div class="mobile-first-notice">
                        <h5><i class="fas fa-info-circle me-2 text-primary"></i>First Time User?</h5>
                        <p class="mb-3">You must first download our mobile app to create an account and purchase assessments:</p>
                        <ol class="mb-3">
                            <li>Download IELTS GenAI Prep from App Store or Google Play</li>
                            <li>Create account and purchase assessment packages ($36 each)</li>
                            <li>Return here and login with the same credentials</li>
                        </ol>
                        <div class="text-center">
                            <a href="/mobile-access" class="btn btn-outline-primary btn-sm">
                                <i class="fas fa-mobile-alt me-2"></i>Get Mobile App
                            </a>
                        </div>
                    </div>

                    <!-- Login Form -->
                    <form id="loginForm">
                        <div class="mb-3">
                            <label for="username" class="form-label">
                                <i class="fas fa-user me-2"></i>Username or Email
                            </label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">
                                <i class="fas fa-lock me-2"></i>Password
                            </label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <!-- Google reCAPTCHA -->
                        <div class="mb-3">
                            <div class="g-recaptcha" data-sitekey="YOUR_RECAPTCHA_SITE_KEY"></div>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-sign-in-alt me-2"></i>Login
                            </button>
                        </div>
                    </form>

                    <!-- Cross-Platform Note -->
                    <div class="text-center mt-4 pt-3 border-top">
                        <small class="text-muted">
                            <i class="fas fa-shield-alt me-1"></i>
                            Secure cross-platform access: Use the same credentials from your mobile app
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get reCAPTCHA response
            const recaptchaResponse = grecaptcha.getResponse();
            
            if (!recaptchaResponse) {
                alert('Please complete the reCAPTCHA verification.');
                return;
            }
            
            // Here you would normally submit to your authentication endpoint
            alert('Login functionality will be implemented with backend authentication.');
        });
    </script>
</body>
</html>'''

    # Create Lambda function code
    lambda_code = f'''import json

def lambda_handler(event, context):
    """Lambda handler with mobile-first authentication pages"""
    
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    print(f"Processing {{method}} {{path}}")
    
    # Comprehensive home page HTML content
    home_html = """{home_content.replace('\\', '\\\\').replace('"', '\\"')}"""
    
    # Mobile access page (replacing QR auth)
    mobile_access_html = """{mobile_access_page.replace('\\', '\\\\').replace('"', '\\"')}"""
    
    # Enhanced login page with reCAPTCHA
    login_html = """{login_page.replace('\\', '\\\\').replace('"', '\\"')}"""
    
    if path == '/' or path == '/index.html':
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            }},
            'body': home_html
        }}
    
    elif path == '/mobile-access' or path == '/qr-auth':
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            }},
            'body': mobile_access_html
        }}
    
    elif path == '/login':
        return {{
            'statusCode': 200,
            'headers': {{
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-cache'
            }},
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
    with zipfile.ZipFile('mobile-first-auth-lambda.zip', 'w') as zip_file:
        zip_file.writestr('simple_lambda.py', lambda_code)
    
    print("Mobile-first authentication Lambda package created successfully")
    return True

def deploy_mobile_first_auth():
    """Deploy the Lambda function with mobile-first authentication"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        with open('mobile-first-auth-lambda.zip', 'rb') as zip_file:
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
    print("Creating mobile-first authentication pages...")
    if create_mobile_first_auth_lambda():
        print("Deploying Lambda with mobile-first authentication...")
        if deploy_mobile_first_auth():
            print("Mobile-first authentication deployment completed successfully!")
            print("Updated authentication flow: mobile app → username/password → reCAPTCHA")
        else:
            print("Deployment failed")
    else:
        print("Package creation failed")