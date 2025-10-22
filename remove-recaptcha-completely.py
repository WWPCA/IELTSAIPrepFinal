#!/usr/bin/env python3
"""
Remove reCAPTCHA completely from login page for testing
"""
import boto3
import zipfile
import os

def create_no_recaptcha_package():
    """Create deployment package without reCAPTCHA"""
    
    # Read the working Lambda code
    with open('working-lambda.py', 'r') as f:
        lambda_code = f.read()
    
    # Create minimal login page without reCAPTCHA
    login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }
        .form-control:focus {
            border-color: #4361ee;
            box-shadow: 0 0 0 0.2rem rgba(67, 97, 238, 0.15);
        }
        .btn-primary {
            background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%);
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <div class="text-center mb-4">
                        <h2 class="text-primary">Welcome Back</h2>
                        <p class="text-muted">Sign in to your IELTS GenAI Prep account</p>
                    </div>
                    
                    <div class="alert alert-info">
                        <strong>New to IELTS GenAI Prep?</strong><br>
                        To get started, you need to:<br>
                        1. Download our mobile app (iOS/Android)<br>
                        2. Create an account and purchase assessments<br>
                        3. Return here to access your assessments on desktop
                    </div>
                    
                    <div id="login-message" class="alert" style="display: none;"></div>
                    
                    <form id="login-form">
                        <div class="mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" value="test@ieltsgenaiprep.com" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" value="testpassword123" required>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember">
                            <label class="form-check-label" for="remember">Remember me for 30 days</label>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary" id="login-btn">Sign In</button>
                        </div>
                        
                        <div class="text-center mt-3">
                            <a href="#" class="text-decoration-none">Forgot your password?</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const loginForm = document.getElementById('login-form');
        const loginBtn = document.getElementById('login-btn');
        const loginMessage = document.getElementById('login-message');
        
        function showMessage(message, type) {
            loginMessage.textContent = message;
            loginMessage.className = `alert alert-${type}`;
            loginMessage.style.display = 'block';
        }
        
        function hideMessage() {
            loginMessage.style.display = 'none';
        }
        
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            hideMessage();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                showMessage('Please fill in all fields', 'danger');
                return;
            }
            
            loginBtn.disabled = true;
            loginBtn.textContent = 'Logging in...';
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage('Login successful! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showMessage(result.message || 'Login failed', 'danger');
                }
            } catch (error) {
                console.error('Login error:', error);
                showMessage('Network error. Please try again.', 'danger');
            } finally {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Sign In';
            }
        });
    });
    </script>
</body>
</html>'''
    
    # Create simple dashboard
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .btn-primary { background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%); border: none; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body text-center">
                        <h1 class="text-primary mb-4">IELTS GenAI Prep Dashboard</h1>
                        <p class="lead">Welcome! Your assessments are ready.</p>
                        
                        <div class="row mt-4">
                            <div class="col-md-6 mb-3">
                                <div class="card border-primary">
                                    <div class="card-body">
                                        <h5 class="card-title">🎯 Academic Writing</h5>
                                        <p class="card-text">TrueScore® AI Assessment</p>
                                        <button class="btn btn-primary">Start Assessment</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card border-success">
                                    <div class="card-body">
                                        <h5 class="card-title">🗣️ Academic Speaking</h5>
                                        <p class="card-text">ClearScore® AI Assessment</p>
                                        <button class="btn btn-success">Start Assessment</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card border-warning">
                                    <div class="card-body">
                                        <h5 class="card-title">✍️ General Writing</h5>
                                        <p class="card-text">TrueScore® AI Assessment</p>
                                        <button class="btn btn-warning">Start Assessment</button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6 mb-3">
                                <div class="card border-info">
                                    <div class="card-body">
                                        <h5 class="card-title">🎤 General Speaking</h5>
                                        <p class="card-text">ClearScore® AI Assessment</p>
                                        <button class="btn btn-info">Start Assessment</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    # Create home page
    home_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IELTS GenAI Prep - AI-Powered IELTS Practice</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .hero { color: white; padding: 100px 0; text-align: center; }
        .btn-primary { background: linear-gradient(135deg, #4361ee 0%, #3651d4 100%); border: none; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1 class="display-4 mb-4">IELTS GenAI Prep</h1>
            <p class="lead mb-4">AI-Powered IELTS Practice with Nova Sonic & Nova Micro</p>
            <a href="/login" class="btn btn-primary btn-lg">Get Started</a>
        </div>
    </div>
</body>
</html>'''
    
    # Create deployment package
    with zipfile.ZipFile('lambda-no-recaptcha.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
        zip_file.writestr('login.html', login_html)
        zip_file.writestr('dashboard.html', dashboard_html)
        zip_file.writestr('public_home.html', home_html)
    
    print("Created Lambda package without reCAPTCHA")
    return 'lambda-no-recaptcha.zip'

def deploy_no_recaptcha():
    """Deploy Lambda without reCAPTCHA"""
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = 'ielts-genai-prep-api'
    
    try:
        zip_file_path = create_no_recaptcha_package()
        
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"Deploying Lambda without reCAPTCHA...")
        print(f"Package size: {len(zip_content)} bytes")
        
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print("Lambda function updated successfully!")
        
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=function_name)
        
        print("Deployment completed!")
        os.remove(zip_file_path)
        
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if deploy_no_recaptcha():
        print("reCAPTCHA removed from login page!")
        print("Website: https://www.ieltsaiprep.com/login")
        print("Test credentials: test@ieltsgenaiprep.com / testpassword123")
    else:
        print("Deployment failed")