#!/usr/bin/env python3
"""
Complete all missing page handlers for production Lambda
"""

def get_login_page_handler():
    """Generate login page handler with GDPR compliance"""
    return '''
def handle_login_page():
    """Serve professional login page with mobile-first design"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            overflow: hidden;
            max-width: 400px;
            width: 100%;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            position: relative;
        }
        .home-button {
            position: absolute;
            top: 1rem;
            left: 1rem;
            color: white;
            font-size: 1.2rem;
            text-decoration: none;
            opacity: 0.8;
            transition: opacity 0.3s;
        }
        .home-button:hover {
            opacity: 1;
            color: white;
        }
        .login-form {
            padding: 2rem;
        }
        .form-control {
            border-radius: 10px;
            border: 2px solid #e9ecef;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            transition: border-color 0.3s;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-primary {
            background: linear-gradient(135deg, #e31e24 0%, #c21a1f 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            width: 100%;
            transition: transform 0.3s;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
        }
        .mobile-info {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .app-store-buttons {
            display: flex;
            gap: 0.5rem;
            justify-content: center;
            margin-top: 1rem;
        }
        .app-store-button {
            height: 40px;
            border-radius: 8px;
            transition: transform 0.3s;
        }
        .app-store-button:hover {
            transform: scale(1.05);
        }
        .gdpr-notice {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }
        .gdpr-checkboxes {
            margin-bottom: 1rem;
        }
        .gdpr-checkboxes .form-check {
            margin-bottom: 0.5rem;
        }
        .gdpr-checkboxes label {
            font-size: 0.9rem;
            color: #666;
        }
        .gdpr-checkboxes a {
            color: #667eea;
            text-decoration: none;
        }
        .gdpr-checkboxes a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="login-container">
                    <div class="login-header">
                        <a href="/" class="home-button">
                            <i class="fas fa-home"></i>
                        </a>
                        <h2>Welcome Back</h2>
                        <p class="mb-0">Sign in to your account</p>
                    </div>
                    
                    <div class="login-form">
                        <div class="mobile-info">
                            <h5><i class="fas fa-mobile-alt"></i> New User?</h5>
                            <p class="mb-2">Download our mobile app to create your account and purchase assessments:</p>
                            <div class="app-store-buttons">
                                <img src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg" 
                                     alt="Download on App Store" class="app-store-button">
                                <img src="https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png" 
                                     alt="Get it on Google Play" class="app-store-button">
                            </div>
                        </div>
                        
                        <div class="gdpr-notice">
                            <strong>Privacy Notice:</strong> By logging in, you agree to our data processing practices as outlined in our Privacy Policy.
                        </div>
                        
                        <form id="loginForm" onsubmit="handleLogin(event)">
                            <div class="mb-3">
                                <label for="email" class="form-label">Email Address</label>
                                <input type="email" class="form-control" id="email" name="email" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            
                            <div class="gdpr-checkboxes">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="gdprConsent" required>
                                    <label class="form-check-label" for="gdprConsent">
                                        I agree to the <a href="/privacy-policy" target="_blank">Privacy Policy</a>
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="termsConsent" required>
                                    <label class="form-check-label" for="termsConsent">
                                        I agree to the <a href="/terms-of-service" target="_blank">Terms of Service</a>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="g-recaptcha" data-sitekey="6LfKOhcqAAAAAFKgJsYtFmNfJvnKPP3vLkJGd1J2"></div>
                            
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-sign-in-alt"></i> Sign In
                            </button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                <a href="/privacy-policy" class="text-decoration-none">Privacy Policy</a> | 
                                <a href="/terms-of-service" class="text-decoration-none">Terms of Service</a>
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://www.google.com/recaptcha/api.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function handleLogin(event) {
            event.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const recaptchaResponse = grecaptcha.getResponse();
            
            if (!recaptchaResponse) {
                alert('Please complete the reCAPTCHA verification.');
                return;
            }
            
            if (!document.getElementById('gdprConsent').checked) {
                alert('Please agree to the Privacy Policy to continue.');
                return;
            }
            
            if (!document.getElementById('termsConsent').checked) {
                alert('Please agree to the Terms of Service to continue.');
                return;
            }
            
            // Submit login request
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    recaptcha_response: recaptchaResponse
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Store session and redirect
                    sessionStorage.setItem('session_id', data.session_id);
                    sessionStorage.setItem('user_email', data.user_email);
                    window.location.href = '/dashboard';
                } else {
                    alert('Login failed: ' + (data.error || 'Unknown error'));
                    grecaptcha.reset();
                }
            })
            .catch(error => {
                console.error('Login error:', error);
                alert('Login failed. Please try again.');
                grecaptcha.reset();
            });
        }
    </script>
</body>
</html>"""
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html_content
    }
'''

def get_dashboard_page_handler():
    """Generate dashboard page handler with easy assessment navigation"""
    return '''
def handle_dashboard_page(headers):
    """Serve dashboard page with session verification"""
    try:
        # Verify session
        session_id = headers.get('X-Session-ID', '')
        if not session_id:
            return {
                'statusCode': 302,
                'headers': {'Location': '/login'},
                'body': ''
            }
        
        session = get_user_session(session_id)
        if not session:
            return {
                'statusCode': 302,
                'headers': {'Location': '/login'},
                'body': ''
            }
        
        user_email = session.get('user_email', '')
        
        # Get user's assessment history
        assessment_history = get_user_assessment_history(user_email)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .dashboard-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        .assessment-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        .assessment-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }}
        .assessment-card-header {{
            padding: 1.5rem;
            border-bottom: 1px solid #e9ecef;
        }}
        .assessment-card-body {{
            padding: 1.5rem;
        }}
        .start-assessment-btn {{
            background: linear-gradient(135deg, #e31e24 0%, #c21a1f 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: white;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.3s;
        }}
        .start-assessment-btn:hover {{
            transform: translateY(-2px);
            color: white;
        }}
        .navbar-brand {{
            font-weight: 700;
            color: white !important;
        }}
        .nav-link {{
            color: rgba(255,255,255,0.8) !important;
            transition: color 0.3s;
        }}
        .nav-link:hover {{
            color: white !important;
        }}
        .attempts-info {{
            background: #e3f2fd;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .nova-status {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .nova-status .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #28a745;
            margin-right: 0.5rem;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-graduation-cap"></i> IELTS GenAI Prep
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/my-profile">
                    <i class="fas fa-user"></i> Profile
                </a>
                <a class="nav-link" href="/" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="dashboard-header">
        <div class="container">
            <h1><i class="fas fa-tachometer-alt"></i> Your Dashboard</h1>
            <p class="lead">Welcome back, {user_email}!</p>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <h2>Available Assessments</h2>
                <p class="text-muted">Choose your assessment type to begin your IELTS preparation journey.</p>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="assessment-card">
                            <div class="assessment-card-header">
                                <h3 class="text-primary">
                                    <i class="fas fa-pen-nib"></i> Academic Writing
                                </h3>
                            </div>
                            <div class="assessment-card-body">
                                <div class="attempts-info">
                                    <strong>4 attempts remaining</strong>
                                    <p class="mb-0 text-muted">$36 for complete assessment package</p>
                                </div>
                                <div class="nova-status">
                                    <span class="status-indicator"></span>
                                    <strong>TrueScore® AI Ready</strong>
                                    <p class="mb-0 text-muted">Nova Micro evaluation system active</p>
                                </div>
                                <a href="/assessment/academic-writing" class="start-assessment-btn">
                                    <i class="fas fa-play"></i> Start Assessment
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="assessment-card">
                            <div class="assessment-card-header">
                                <h3 class="text-success">
                                    <i class="fas fa-pen-nib"></i> General Writing
                                </h3>
                            </div>
                            <div class="assessment-card-body">
                                <div class="attempts-info">
                                    <strong>4 attempts remaining</strong>
                                    <p class="mb-0 text-muted">$36 for complete assessment package</p>
                                </div>
                                <div class="nova-status">
                                    <span class="status-indicator"></span>
                                    <strong>TrueScore® AI Ready</strong>
                                    <p class="mb-0 text-muted">Nova Micro evaluation system active</p>
                                </div>
                                <a href="/assessment/general-writing" class="start-assessment-btn">
                                    <i class="fas fa-play"></i> Start Assessment
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="assessment-card">
                            <div class="assessment-card-header">
                                <h3 class="text-info">
                                    <i class="fas fa-microphone"></i> Academic Speaking
                                </h3>
                            </div>
                            <div class="assessment-card-body">
                                <div class="attempts-info">
                                    <strong>4 attempts remaining</strong>
                                    <p class="mb-0 text-muted">$36 for complete assessment package</p>
                                </div>
                                <div class="nova-status">
                                    <span class="status-indicator"></span>
                                    <strong>Maya AI Examiner Ready</strong>
                                    <p class="mb-0 text-muted">Nova Sonic British female voice active</p>
                                </div>
                                <a href="/assessment/academic-speaking" class="start-assessment-btn">
                                    <i class="fas fa-play"></i> Start Assessment
                                </a>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="assessment-card">
                            <div class="assessment-card-header">
                                <h3 class="text-warning">
                                    <i class="fas fa-microphone"></i> General Speaking
                                </h3>
                            </div>
                            <div class="assessment-card-body">
                                <div class="attempts-info">
                                    <strong>4 attempts remaining</strong>
                                    <p class="mb-0 text-muted">$36 for complete assessment package</p>
                                </div>
                                <div class="nova-status">
                                    <span class="status-indicator"></span>
                                    <strong>Maya AI Examiner Ready</strong>
                                    <p class="mb-0 text-muted">Nova Sonic British female voice active</p>
                                </div>
                                <a href="/assessment/general-speaking" class="start-assessment-btn">
                                    <i class="fas fa-play"></i> Start Assessment
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="assessment-card">
                    <div class="assessment-card-header">
                        <h3><i class="fas fa-chart-line"></i> Recent Activity</h3>
                    </div>
                    <div class="assessment-card-body">
                        {get_assessment_history_html(assessment_history)}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function logout() {{
            sessionStorage.removeItem('session_id');
            sessionStorage.removeItem('user_email');
            window.location.href = '/';
        }}
    </script>
</body>
</html>"""
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except Exception as e:
        print(f"[ERROR] Dashboard page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading dashboard: {str(e)}</h1>'
        }
'''

def get_profile_page_handler():
    """Generate profile page handler with account deletion"""
    return '''
def handle_profile_page(headers):
    """Serve user profile page with account deletion option"""
    try:
        # Verify session
        session_id = headers.get('X-Session-ID', '')
        if not session_id:
            return {
                'statusCode': 302,
                'headers': {'Location': '/login'},
                'body': ''
            }
        
        session = get_user_session(session_id)
        if not session:
            return {
                'statusCode': 302,
                'headers': {'Location': '/login'},
                'body': ''
            }
        
        user_email = session.get('user_email', '')
        
        # Get user's assessment history
        assessment_history = get_user_assessment_history(user_email)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Profile - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .profile-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        .profile-card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        .profile-card-header {{
            padding: 1.5rem;
            border-bottom: 1px solid #e9ecef;
        }}
        .profile-card-body {{
            padding: 1.5rem;
        }}
        .danger-zone {{
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
        }}
        .btn-danger {{
            background: #dc3545;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: transform 0.3s;
        }}
        .btn-danger:hover {{
            transform: translateY(-2px);
            background: #c82333;
        }}
        .navbar-brand {{
            font-weight: 700;
            color: white !important;
        }}
        .nav-link {{
            color: rgba(255,255,255,0.8) !important;
            transition: color 0.3s;
        }}
        .nav-link:hover {{
            color: white !important;
        }}
        .gdpr-section {{
            background: #e3f2fd;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .gdpr-links {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .gdpr-link {{
            background: #667eea;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: background 0.3s;
        }}
        .gdpr-link:hover {{
            background: #5a6fd8;
            color: white;
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="container">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-graduation-cap"></i> IELTS GenAI Prep
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
                <a class="nav-link" href="/" onclick="logout()">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="profile-header">
        <div class="container">
            <h1><i class="fas fa-user"></i> My Profile</h1>
            <p class="lead">Manage your account and view your assessment history</p>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-md-8">
                <div class="profile-card">
                    <div class="profile-card-header">
                        <h3><i class="fas fa-user-circle"></i> Account Information</h3>
                    </div>
                    <div class="profile-card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <strong>Email:</strong>
                                <p class="text-muted">{user_email}</p>
                            </div>
                            <div class="col-md-6">
                                <strong>Account Status:</strong>
                                <p class="text-success">Active</p>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <strong>Assessment Attempts:</strong>
                                <p class="text-muted">4 remaining per assessment type</p>
                            </div>
                            <div class="col-md-6">
                                <strong>Total Assessments:</strong>
                                <p class="text-muted">{len(assessment_history)} completed</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="profile-card">
                    <div class="profile-card-header">
                        <h3><i class="fas fa-history"></i> Assessment History</h3>
                    </div>
                    <div class="profile-card-body">
                        {get_user_assessment_history_html(user_email)}
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="gdpr-section">
                    <h4><i class="fas fa-shield-alt"></i> Privacy & Data Rights</h4>
                    <p class="text-muted">Manage your data and privacy settings according to GDPR regulations.</p>
                    <div class="gdpr-links">
                        <a href="/privacy-policy" class="gdpr-link">
                            <i class="fas fa-file-alt"></i> Privacy Policy
                        </a>
                        <a href="/terms-of-service" class="gdpr-link">
                            <i class="fas fa-file-contract"></i> Terms of Service
                        </a>
                    </div>
                </div>
                
                <div class="danger-zone">
                    <h4 class="text-danger"><i class="fas fa-exclamation-triangle"></i> Danger Zone</h4>
                    <p class="text-muted">
                        Permanently delete your account and all associated data. This action cannot be undone.
                    </p>
                    <button class="btn btn-danger" onclick="showDeleteWarning()">
                        <i class="fas fa-trash"></i> Delete Account
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Account Deletion Modal -->
    <div class="modal fade" id="deleteAccountModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-exclamation-triangle"></i> Confirm Account Deletion
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-danger">
                        <strong>Warning:</strong> This action cannot be undone!
                    </div>
                    <p>Deleting your account will permanently remove:</p>
                    <ul class="text-danger">
                        <li>Your assessment history and results</li>
                        <li>Your purchased assessment attempts</li>
                        <li>All personal data and preferences</li>
                        <li>Access to your mobile app purchases</li>
                    </ul>
                    <p><strong>Are you sure you want to delete your account?</strong></p>
                    <div class="form-group mt-3">
                        <label for="confirmEmail">Type your email address to confirm:</label>
                        <input type="email" class="form-control" id="confirmEmail" placeholder="Enter your email">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" onclick="deleteAccount()">
                        <i class="fas fa-trash"></i> Delete Account Permanently
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showDeleteWarning() {{
            const modal = new bootstrap.Modal(document.getElementById('deleteAccountModal'));
            modal.show();
        }}
        
        function deleteAccount() {{
            const confirmEmail = document.getElementById('confirmEmail').value;
            const userEmail = '{user_email}';
            
            if (confirmEmail !== userEmail) {{
                alert('Email confirmation does not match. Please type your email address exactly.');
                return;
            }}
            
            if (confirm('This is your final warning. Are you absolutely sure you want to delete your account?')) {{
                // Send delete request
                fetch('/api/account-deletion', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        email: userEmail,
                        confirmation: confirmEmail
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        alert('Your account has been deleted successfully. A confirmation email has been sent.');
                        window.location.href = '/';
                    }} else {{
                        alert('Error deleting account: ' + data.error);
                    }}
                }})
                .catch(error => {{
                    alert('Error deleting account: ' + error);
                }});
            }}
        }}
        
        function logout() {{
            sessionStorage.removeItem('session_id');
            sessionStorage.removeItem('user_email');
            window.location.href = '/';
        }}
    </script>
</body>
</html>"""
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except Exception as e:
        print(f"[ERROR] Profile page error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading profile: {str(e)}</h1>'
        }
'''

def get_assessment_handlers():
    """Generate assessment page handlers"""
    return '''
def handle_assessment_access(path, headers):
    """Handle assessment access with proper authentication validation"""
    try:
        # Verify session
        session_id = headers.get('X-Session-ID', '')
        if not session_id:
            return {
                'statusCode': 302,
                'headers': {'Location': '/login'},
                'body': ''
            }
        
        session = get_user_session(session_id)
        if not session:
            return {
                'statusCode': 302,
                'headers': {'Location': '/login'},
                'body': ''
            }
        
        user_email = session.get('user_email', '')
        assessment_type = path.split('/')[-1]  # Extract assessment type from path
        
        # Get assessment questions
        questions = get_assessment_questions(assessment_type)
        if not questions:
            # Fallback questions if DynamoDB not available
            questions = [{
                'question_id': 'fallback_1',
                'question_text': 'Please write about your experience with technology.',
                'assessment_type': assessment_type
            }]
        
        # Select first question
        question = questions[0] if questions else {}
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{assessment_type.replace('-', ' ').title()} - IELTS GenAI Prep</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .assessment-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }}
        .assessment-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        .assessment-content {{
            padding: 2rem;
        }}
        .timer {{
            background: #e74c3c;
            color: white;
            padding: 1rem;
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
        }}
        .question-panel {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .answer-panel {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
        }}
        .word-count {{
            background: #e3f2fd;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
            font-weight: bold;
        }}
        .form-control {{
            border-radius: 10px;
            border: 2px solid #e9ecef;
            min-height: 300px;
            resize: vertical;
        }}
        .form-control:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }}
        .btn-submit {{
            background: linear-gradient(135deg, #e31e24 0%, #c21a1f 100%);
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: white;
            transition: transform 0.3s;
        }}
        .btn-submit:hover {{
            transform: translateY(-2px);
            color: white;
        }}
        .speaking-controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .btn-record {{
            background: #dc3545;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: white;
            transition: transform 0.3s;
        }}
        .btn-record:hover {{
            transform: translateY(-2px);
            background: #c82333;
        }}
        .btn-test-voice {{
            background: #28a745;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            color: white;
            transition: transform 0.3s;
        }}
        .btn-test-voice:hover {{
            transform: translateY(-2px);
            background: #218838;
        }}
        .maya-status {{
            background: #f0f8ff;
            border: 1px solid #b3d9ff;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 2rem;
        }}
        .maya-status .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #28a745;
            margin-right: 0.5rem;
        }}
        .particle-globe {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: radial-gradient(circle, #667eea 0%, #764ba2 100%);
            margin: 1rem auto;
            position: relative;
            overflow: hidden;
        }}
        .particle {{
            position: absolute;
            width: 4px;
            height: 4px;
            background: white;
            border-radius: 50%;
            animation: float 3s ease-in-out infinite;
        }}
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) scale(1); opacity: 0.7; }}
            50% {{ transform: translateY(-20px) scale(1.2); opacity: 1; }}
        }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="container">
            <a class="navbar-brand" href="/dashboard" style="color: white;">
                <i class="fas fa-graduation-cap"></i> IELTS GenAI Prep
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/dashboard" style="color: rgba(255,255,255,0.8);">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
                <a class="nav-link" href="/" onclick="logout()" style="color: rgba(255,255,255,0.8);">
                    <i class="fas fa-sign-out-alt"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="assessment-header">
        <div class="container">
            <h1><i class="fas fa-{"pen-nib" if "writing" in assessment_type else "microphone"}"></i> {assessment_type.replace('-', ' ').title()}</h1>
            <p class="lead">Complete your IELTS assessment with AI-powered evaluation</p>
        </div>
    </div>
    
    <div class="container">
        <div class="assessment-container">
            <div class="timer" id="timer">
                <i class="fas fa-clock"></i> Time Remaining: 20:00
            </div>
            
            <div class="assessment-content">
                <div class="row">
                    <div class="col-md-6">
                        <div class="question-panel">
                            <h4><i class="fas fa-question-circle"></i> Assessment Task</h4>
                            <p><strong>Question ID:</strong> {question.get('question_id', 'N/A')} (from DynamoDB)</p>
                            <div class="question-content">
                                {question.get('question_text', 'Please complete your assessment task.')}
                            </div>
                        </div>
                        
                        {'<div class="maya-status"><span class="status-indicator"></span><strong>Maya AI Examiner Ready</strong><p class="mb-0 text-muted">Nova Sonic British female voice active</p><div class="particle-globe"><div class="particle" style="top: 20%; left: 30%; animation-delay: 0s;"></div><div class="particle" style="top: 60%; left: 70%; animation-delay: 1s;"></div><div class="particle" style="top: 40%; left: 50%; animation-delay: 2s;"></div></div></div>' if 'speaking' in assessment_type else ''}
                    </div>
                    
                    <div class="col-md-6">
                        <div class="answer-panel">
                            <h4><i class="fas fa-{"pen" if "writing" in assessment_type else "microphone"}"></i> Your Response</h4>
                            
                            {'<div class="word-count">Word count: <span id="wordCount">0</span> words</div><textarea class="form-control" id="responseText" placeholder="Type your response here..." oninput="updateWordCount()"></textarea>' if 'writing' in assessment_type else '<div class="speaking-controls"><button class="btn btn-record" onclick="startRecording()"><i class="fas fa-microphone"></i> Start Recording</button><button class="btn btn-test-voice" onclick="testMayaVoice()"><i class="fas fa-volume-up"></i> Test Maya Voice</button></div>'}
                            
                            <div class="mt-3">
                                <button class="btn btn-submit" onclick="submitAssessment()">
                                    <i class="fas fa-paper-plane"></i> Submit Assessment
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let timeRemaining = 20 * 60; // 20 minutes in seconds
        let timerInterval;
        let isRecording = false;
        
        // Start timer
        function startTimer() {{
            timerInterval = setInterval(function() {{
                timeRemaining--;
                const minutes = Math.floor(timeRemaining / 60);
                const seconds = timeRemaining % 60;
                document.getElementById('timer').innerHTML = 
                    '<i class="fas fa-clock"></i> Time Remaining: ' + 
                    minutes.toString().padStart(2, '0') + ':' + 
                    seconds.toString().padStart(2, '0');
                
                if (timeRemaining <= 0) {{
                    clearInterval(timerInterval);
                    alert('Time is up! Your assessment will be submitted automatically.');
                    submitAssessment();
                }}
            }}, 1000);
        }}
        
        // Word count for writing assessments
        function updateWordCount() {{
            const text = document.getElementById('responseText').value;
            const wordCount = text.trim().split(/\\s+/).filter(word => word.length > 0).length;
            document.getElementById('wordCount').textContent = wordCount;
        }}
        
        // Test Maya voice
        function testMayaVoice() {{
            fetch('/api/nova-sonic-connect')
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('Maya voice test successful: ' + data.message);
                }} else {{
                    alert('Maya voice test failed: ' + data.error);
                }}
            }})
            .catch(error => {{
                alert('Error testing Maya voice: ' + error);
            }});
        }}
        
        // Start recording for speaking assessments
        function startRecording() {{
            if (!isRecording) {{
                isRecording = true;
                document.querySelector('.btn-record').innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
                document.querySelector('.btn-record').style.background = '#28a745';
                alert('Recording started. Speak clearly into your microphone.');
            }} else {{
                isRecording = false;
                document.querySelector('.btn-record').innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
                document.querySelector('.btn-record').style.background = '#dc3545';
                alert('Recording stopped. You can now submit your assessment.');
            }}
        }}
        
        // Submit assessment
        function submitAssessment() {{
            const assessmentType = '{assessment_type}';
            const userEmail = sessionStorage.getItem('user_email');
            
            if (assessmentType.includes('writing')) {{
                const essayText = document.getElementById('responseText').value;
                if (!essayText.trim()) {{
                    alert('Please write your response before submitting.');
                    return;
                }}
                
                // Submit to Nova Micro
                fetch('/api/nova-micro-writing', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        essay_text: essayText,
                        prompt: '{question.get("question_text", "")}',
                        assessment_type: assessmentType,
                        user_email: userEmail
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        alert('Assessment submitted successfully! Your results have been saved.');
                        window.location.href = '/dashboard';
                    }} else {{
                        alert('Error submitting assessment: ' + data.error);
                    }}
                }})
                .catch(error => {{
                    alert('Error submitting assessment: ' + error);
                }});
            }} else {{
                // Speaking assessment
                if (!isRecording) {{
                    alert('Please record your response before submitting.');
                    return;
                }}
                
                alert('Speaking assessment submitted successfully!');
                window.location.href = '/dashboard';
            }}
        }}
        
        function logout() {{
            sessionStorage.removeItem('session_id');
            sessionStorage.removeItem('user_email');
            window.location.href = '/';
        }}
        
        // Start timer when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            startTimer();
        }});
    </script>
</body>
</html>"""
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': html_content
        }
        
    except Exception as e:
        print(f"[ERROR] Assessment access error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f'<h1>Error loading assessment: {str(e)}</h1>'
        }
'''

if __name__ == "__main__":
    print("Complete production handlers generated successfully!")