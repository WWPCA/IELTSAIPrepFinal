#!/usr/bin/env python3
"""
Simple Lambda Handler for IELTS GenAI Prep Website
Serves static HTML without Flask dependencies
"""

import json
import os
import base64
from datetime import datetime

def lambda_handler(event, context):
    """AWS Lambda handler that serves the IELTS GenAI Prep website"""
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', '/'))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        headers = event.get('headers', {})
        
        # Website content with TrueScore® and ClearScore® branding
        if path == '/' and method == 'GET':
            html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="IELTS GenAI Prep - Your comprehensive IELTS assessment preparation platform">
    <title>IELTS GenAI Prep</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome for icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 80px 0;
            text-align: center;
        }
        .feature-card {
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
            height: 100%;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .brand-section {
            background: #f8f9fa;
            padding: 60px 0;
        }
        .cta-section {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <div class="text-center mb-4">
                <h1 class="display-4 fw-bold mb-3">Master IELTS with GenAI-Powered Scoring</h1>
                <div class="p-2 mb-4" style="background-color: #3498db; color: white; border-radius: 4px; display: inline-block; max-width: 100%; font-size: 1rem; line-height: 1.4;">
                    The only AI-based IELTS platform with official band-aligned feedback
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-lg-10 mx-auto">
                    <p class="lead">As your personal GenAI IELTS Coach, our TrueScore® & ClearScore® technologies provide industry-leading standardized assessment with Maya AI examiner.</p>
                </div>
            </div>

            <div class="text-center mb-5">
                <div class="d-md-flex d-block justify-content-center gap-3">
                    <a href="/login" class="btn btn-primary btn-lg mb-2 mb-md-0">Get Started</a>
                    <a href="#how-it-works" class="btn btn-outline-light btn-lg">Learn More</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="brand-section">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="fw-bold">GenAI Assessed IELTS Modules</h2>
                <p class="lead">Advanced AI evaluation with authentic IELTS band descriptors</p>
            </div>
            
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-edit fa-3x text-primary"></i>
                            </div>
                            <h4 class="card-title">TrueScore® Writing Assessment</h4>
                            <p class="card-text">Advanced AI evaluation for both Academic and General Training writing tasks.</p>
                            <ul class="list-unstyled text-start">
                                <li><i class="fas fa-check text-success me-2"></i>Task Achievement evaluation</li>
                                <li><i class="fas fa-check text-success me-2"></i>Coherence & Cohesion analysis</li>
                                <li><i class="fas fa-check text-success me-2"></i>Lexical Resource assessment</li>
                                <li><i class="fas fa-check text-success me-2"></i>Grammar Range & Accuracy scoring</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-microphone fa-3x text-success"></i>
                            </div>
                            <h4 class="card-title">ClearScore® Speaking Assessment</h4>
                            <p class="card-text">Maya AI examiner provides authentic speaking assessment with real-time analysis.</p>
                            <ul class="list-unstyled text-start">
                                <li><i class="fas fa-check text-success me-2"></i>Fluency & Coherence evaluation</li>
                                <li><i class="fas fa-check text-success me-2"></i>Lexical Resource assessment</li>
                                <li><i class="fas fa-check text-success me-2"></i>Grammar Range & Accuracy scoring</li>
                                <li><i class="fas fa-check text-success me-2"></i>Pronunciation analysis</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- How it Works Section -->
    <section id="how-it-works" class="py-5">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="fw-bold">How to Get Started</h2>
                <p class="lead">Three simple steps to your IELTS success</p>
            </div>
            
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-mobile-alt fa-3x text-info"></i>
                            </div>
                            <h4 class="card-title">1. Download Mobile App</h4>
                            <p class="card-text">Get the IELTS GenAI Prep app from the App Store or Google Play Store.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-shopping-cart fa-3x text-warning"></i>
                            </div>
                            <h4 class="card-title">2. Purchase Assessment</h4>
                            <p class="card-text">Choose your assessment type for $36 and get 4 complete practice tests.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-laptop fa-3x text-primary"></i>
                            </div>
                            <h4 class="card-title">3. Access Anywhere</h4>
                            <p class="card-text">Login with your mobile credentials on any device. Progress syncs automatically.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Benefits Section -->
    <section class="brand-section">
        <div class="container">
            <div class="row g-4">
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-medal fa-3x text-warning"></i>
                            </div>
                            <h4 class="card-title">Official Band-Descriptive Feedback</h4>
                            <p class="card-text">Receive detailed feedback aligned with official IELTS band descriptors for accurate scoring.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-sync-alt fa-3x text-info"></i>
                            </div>
                            <h4 class="card-title">Mobile & Desktop Access</h4>
                            <p class="card-text">Complete assessments on any device with seamless synchronization across platforms.</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card feature-card">
                        <div class="card-body text-center p-4">
                            <div class="mb-3">
                                <i class="fas fa-target fa-3x text-success"></i>
                            </div>
                            <h4 class="card-title">Designed for Success</h4>
                            <p class="card-text">Comprehensive preparation tools designed to help you achieve your target IELTS band score.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
        <div class="container">
            <h2 class="fw-bold mb-3">Ready to Master IELTS?</h2>
            <p class="lead mb-4">Join thousands of students who've improved their IELTS scores with our GenAI platform</p>
            <a href="/login" class="btn btn-light btn-lg">Start Your Journey Today</a>
        </div>
    </section>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            """
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': html_content
            }
        
        elif path == '/login' and method == 'GET':
            login_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }
        .login-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-card p-4">
                    <div class="text-center mb-4">
                        <i class="fas fa-graduation-cap fa-3x text-primary mb-3"></i>
                        <h2>IELTS GenAI Prep</h2>
                        <p class="text-muted">Sign in to your account</p>
                    </div>
                    
                    <form>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" required>
                        </div>
                        
                        <div class="mb-3 form-check">
                            <input type="checkbox" class="form-check-input" id="remember">
                            <label class="form-check-label" for="remember">Remember me</label>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 mb-3">Sign In</button>
                        
                        <div class="text-center">
                            <a href="/register" class="text-decoration-none">Don't have an account? Register</a><br>
                            <a href="/forgot-password" class="text-decoration-none">Forgot password?</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
            """
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': login_content
            }
        
        elif path == '/api/health' and method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'IELTS GenAI Prep',
                    'version': '1.0.0',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        else:
            # 404 for unknown routes
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'text/html'},
                'body': '''
                <!DOCTYPE html>
                <html>
                <head><title>404 Not Found</title></head>
                <body>
                    <h1>Page Not Found</h1>
                    <p>The requested page could not be found.</p>
                    <a href="/">Go to Homepage</a>
                </body>
                </html>
                '''
            }
            
    except Exception as e:
        print(f"[ERROR] Lambda handler failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }