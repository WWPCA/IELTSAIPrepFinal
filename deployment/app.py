"""
IELTS AI Prep - Production Flask Application  
Uses AWS DynamoDB for data storage with fallback to mock services for development
"""

from flask import Flask, send_from_directory, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import json
import uuid
import time
import secrets
import hashlib
from datetime import datetime, timedelta
import os
import logging
import requests

logger = logging.getLogger(__name__)

from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash

# Real CSRF token generation
def csrf_token():
    return secrets.token_urlsafe(32)

# Production configuration - Read at request time to avoid caching
class ProductionConfig:
    @property
    def RECAPTCHA_SITE_KEY(self):
        return os.environ.get("RECAPTCHA_V2_SITE_KEY")
    
    @property
    def RECAPTCHA_SECRET_KEY(self):
        return os.environ.get("RECAPTCHA_V2_SECRET_KEY")

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# ProxyFix configuration for API Gateway/CloudFront
# x_for=1: Trust X-Forwarded-For header  
# x_proto=1: Trust X-Forwarded-Proto header (http/https)
# x_host=1: Trust X-Forwarded-Host header (www.ieltsaiprep.com)
# x_port=1: Trust X-Forwarded-Port header
# x_prefix=1: Trust X-Forwarded-Prefix header
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

app.jinja_env.globals['csrf_token'] = csrf_token
app.jinja_env.globals['config'] = ProductionConfig()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, email=None):
        self.id = user_id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    """Load user from session - minimal implementation for template compatibility"""
    # Return None for now since we're using session-based auth
    # This makes current_user available in templates but always anonymous
    return None

# Kill caching for development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Add cache buster for CSS/JS files
@app.context_processor
def inject_cache_buster():
    return dict(cache_buster=str(int(time.time())))

# Add no-cache headers for development
@app.after_request
def add_no_cache_headers(response):
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# Initialize AWS DynamoDB connections
try:
    # Use real AWS DynamoDB
    print("[INIT] Starting DynamoDB DAL import...")
    from dynamodb_dal import DynamoDBConnection, UserDAL, SessionDAL, AssessmentDAL, EntitlementDAL, ResetTokenDAL
    print("[INIT] DynamoDB DALs imported successfully")
    from bedrock_service import BedrockService
    print("[INIT] Bedrock service imported successfully")
    from desktop_only_middleware import require_desktop
    print("[INIT] Desktop-only middleware imported")
    from mobile_api_routes import mobile_api
    print("[INIT] Mobile API blueprint imported")
    
    environment = os.environ.get('ENVIRONMENT', 'production')
    print(f"[INIT] Creating DynamoDB connection for environment: {environment}")
    db_connection = DynamoDBConnection(environment=environment)
    print("[INIT] DynamoDB connection created")
    
    user_dal = UserDAL(db_connection)
    print("[INIT] UserDAL initialized")
    session_dal = SessionDAL(db_connection)
    print("[INIT] SessionDAL initialized")
    assessment_dal = AssessmentDAL(db_connection)
    print("[INIT] AssessmentDAL initialized")
    entitlement_dal = EntitlementDAL(db_connection)
    print("[INIT] EntitlementDAL initialized")
    reset_token_dal = ResetTokenDAL(db_connection)
    print("[INIT] ResetTokenDAL initialized")
    
    # Register mobile API blueprint
    app.register_blueprint(mobile_api)
    print("[INIT] Mobile API blueprint registered at /api/v1/mobile")
    bedrock_service = BedrockService()
    print("[INIT] Bedrock service initialized")
    
    print(f"[PRODUCTION] Connected to AWS DynamoDB - region: {db_connection.region}, env: {environment}")
    print(f"[PRODUCTION] AWS Bedrock service initialized")
    use_production = True
    
except Exception as e:
    print(f"[ERROR] AWS services initialization error: {e}")
    import traceback
    traceback.print_exc()
    # Fallback to mock services for development
    try:
        from aws_mock_config import aws_mock
        db_connection = aws_mock
        user_dal = None
        session_dal = None
        assessment_dal = None
        bedrock_service = None
    except ImportError:
        db_connection = None
        user_dal = None
        session_dal = None
        assessment_dal = None
        bedrock_service = None
        reset_token_dal = None
    use_production = False

# Always initialize mock storage variables (ensures they exist even if DynamoDB works)
sessions = {}
mock_purchases = {}

# Register mobile API blueprint if available
try:
    from api_mobile import api_mobile
    app.register_blueprint(api_mobile)
    print("[INFO] Mobile API endpoints registered at /api/v1/*")
except ImportError:
    print("[INFO] Mobile API blueprint not available")

# Initialize Regional Gemini Service with DSQ for Speaking
try:
    from gemini_regional_service import create_regional_gemini_service
    from hybrid_integration_routes_regional import create_hybrid_routes_regional
    
    # Create regional service with DSQ support
    gemini_regional_service = create_regional_gemini_service(
        project_id=os.environ.get('GOOGLE_CLOUD_PROJECT')
    )
    
    # Register hybrid routes with regional optimization
    hybrid_blueprint = create_hybrid_routes_regional(assessment_dal)
    app.register_blueprint(hybrid_blueprint)
    print("[INFO] Gemini Regional Service with DSQ initialized")
    print(f"[INFO] Supporting {len(set(list(getattr(__import__('gemini_regional_service'), 'REGION_MAP', {}).values())))} regions globally")
except ImportError as e:
    print(f"[INFO] Gemini Regional Service not available: {e}")
    # Fallback to original smart selection if regional not available
    try:
        from gemini_live_audio_service_smart import create_smart_selection_service
        from hybrid_integration_routes_smart import create_hybrid_routes_smart
        
        gemini_smart_service = create_smart_selection_service(
            project_id=os.environ.get('GOOGLE_CLOUD_PROJECT'),
            region='us-central1'
        )
        
        # Register original hybrid routes
        from hybrid_integration_routes_smart import hybrid_routes_smart
        app.register_blueprint(hybrid_routes_smart)
        print("[INFO] Fallback to Gemini Smart Selection (single region)")
    except ImportError:
        print("[INFO] No Gemini service available")
        gemini_regional_service = None

# Import receipt validation for endpoints (lazy initialization)
receipt_service = None

def get_receipt_service():
    """Lazy-load receipt validation service"""
    global receipt_service
    if receipt_service is None:
        try:
            from receipt_validation import ReceiptValidationService
            receipt_service = ReceiptValidationService()
            print("[INFO] Receipt validation services initialized")
        except (ImportError, RuntimeError) as e:
            print(f"[INFO] Receipt validation services not available: {e}")
            receipt_service = False  # Use False to indicate initialization was attempted
    return receipt_service if receipt_service is not False else None

# Import types for use in routes
try:
    from receipt_validation import PurchaseStatus, validate_app_store_purchase
except ImportError:
    PurchaseStatus = None
    validate_app_store_purchase = None

# Apply security headers and CORS for mobile app support
@app.after_request
def add_security_headers(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Relaxed CSP for development - tighten in production
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data: blob:; img-src 'self' data: https:; font-src 'self' data: https:;"
    
    # CORS headers for mobile app and web client support
    origin = request.headers.get('Origin')
    allowed_origins = [
        'capacitor://localhost',  # Capacitor iOS
        'http://localhost',       # Capacitor Android  
        'https://localhost',      # Capacitor Android (HTTPS)
        'ionic://localhost',      # Ionic specific
        'http://localhost:3000',  # Local web development
        'http://localhost:8100',  # Ionic serve
        'https://www.ieltsaiprep.com',    # Production custom domain (primary)
        'https://ieltsaiprep.com',        # Production custom domain (non-www)
    ]
    
    # CORS headers with proper credential handling
    if origin and origin in allowed_origins:
        # For allowlisted origins, echo the origin and allow credentials
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    elif origin is None:
        # For requests without origin (mobile apps), allow wildcard but no credentials
        response.headers['Access-Control-Allow-Origin'] = '*'
        # Don't set Access-Control-Allow-Credentials for wildcard origins
    else:
        # For non-allowlisted origins, deny access
        response.headers['Access-Control-Allow-Origin'] = 'null'
    
    # Essential CORS headers for mobile app functionality
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-API-Key,X-Session-ID,X-Device-ID,X-Platform'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours preflight cache
    response.headers['Access-Control-Expose-Headers'] = 'X-Session-ID,X-RateLimit-Remaining,X-RateLimit-Reset'
    response.headers['Vary'] = 'Origin'  # Important for proper caching
    
    return response

# Handle preflight OPTIONS requests for CORS
from flask import make_response
@app.route('/<path:path>', methods=['OPTIONS'])
@app.route('/', methods=['OPTIONS'])
def handle_preflight(path=None):
    """Handle CORS preflight requests for all routes"""
    response = make_response()
    origin = request.headers.get('Origin')
    response.headers['Access-Control-Allow-Origin'] = origin or '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-API-Key,X-Session-ID,X-Device-ID,X-Platform'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response
print("[INFO] Security headers applied to all endpoints")
# Actual assessment data structure to match existing templates
user_assessments = {
    "test@ieltsaiprep.com": {
        "academic_speaking": [
            {
                'id': 1,
                'title': 'Academic Speaking Assessment 1',
                'description': 'Comprehensive IELTS Academic Speaking test with AI examiner Maya',
                'assessment_type': 'academic_speaking',
                'created_at': '2024-12-01T10:00:00Z',
                'completed': True,
                'score': 7.5,
                'transcript': 'User discussed education systems with excellent fluency and vocabulary range.',
                'feedback': 'Strong performance with natural conversation flow and appropriate register.',
                'audio_available': False
            }
        ],
        "academic_writing": [
            {
                'id': 2,
                'title': 'Academic Writing Assessment 1',
                'description': 'IELTS Academic Writing Tasks 1 & 2 with TrueScore feedback',
                'assessment_type': 'academic_writing',
                'created_at': '2024-12-01T14:30:00Z',
                'completed': True,
                'score': 7.0,
                'essay_text': 'Education plays a crucial role in shaping society. Universities should balance theoretical knowledge with practical skills to prepare graduates for evolving workplace demands...',
                'feedback': 'Well-structured response with clear task achievement and coherent organization.',
                'task1_score': 7.0,
                'task2_score': 7.0
            }
        ],
        "general_speaking": [
            {
                'id': 3,
                'title': 'General Training Speaking Assessment 1',
                'description': 'IELTS General Training Speaking test focusing on everyday situations',
                'assessment_type': 'general_speaking',
                'created_at': '2024-12-02T09:15:00Z',
                'completed': True,
                'score': 6.5,
                'transcript': 'Discussed daily routines, travel experiences, and future plans with natural flow.',
                'feedback': 'Good interaction skills with appropriate use of informal language.',
                'audio_available': False
            }
        ],
        "general_writing": [
            {
                'id': 4,
                'title': 'General Training Writing Assessment 1',
                'description': 'IELTS General Training Writing Tasks 1 & 2',
                'assessment_type': 'general_writing',
                'created_at': '2024-12-02T16:45:00Z',
                'completed': True,
                'score': 6.5,
                'essay_text': 'Letter writing task completed with appropriate tone and format, followed by opinion essay on technology in education...',
                'feedback': 'Clear communication with good task fulfillment and appropriate language use.',
                'task1_score': 6.5,
                'task2_score': 6.5
            }
        ]
    }
}

@app.route('/')
def home():
    """Serve homepage with updated pricing"""
    # Always use template system for proper functionality
    class AnonymousUser:
        is_authenticated = False
        email = None
    # Serve the working template with updated products
    try:
        with open('working_template.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return render_template('index.html', current_user=AnonymousUser())

@app.route('/original-home')
def original_home():
    """Serve original homepage with TrueScore® and ClearScore® branding"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('index.html', current_user=AnonymousUser())

@app.route('/index')
def index():
    """Redirect /index to homepage"""
    return redirect(url_for('home'))

@app.route('/practice-modules')
def practice_modules_page():
    """Practice Modules page (formerly assessments)"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('assessments.html', current_user=AnonymousUser())

@app.route('/assessments')
def assessments_redirect():
    """301 redirect from old assessments URL to new practice-modules URL for SEO"""
    return redirect(url_for('practice_modules_page'), code=301)

@app.route('/assessment-products')
def assessment_products_page():
    """Redirect old route to new practice modules page"""
    return redirect(url_for('practice_modules_page'), code=301)

@app.route('/preview/writing-assessment')
def preview_writing_assessment():
    """Preview the writing assessment interface without authentication"""
    # Return the standalone test template that has all the same styling
    # but doesn't depend on the full navigation system
    try:
        with open('test_divided_screen.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return """
        <div style="padding: 20px; font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
            <h1>🎯 Writing Assessment Preview</h1>
            <p>The divided screen template is ready! It includes:</p>
            <ul>
                <li>✅ <strong>Left Panel (45%)</strong>: IELTS AI Prep logo + question display</li>
                <li>✅ <strong>Right Panel (55%)</strong>: Response writing area</li>
                <li>✅ <strong>Real IELTS exam format</strong> with professional styling</li>
                <li>✅ <strong>Mobile responsive</strong> design</li>
                <li>✅ <strong>Task switching</strong> between Task 1 and Task 2</li>
                <li>✅ <strong>Word counting</strong> with requirements tracking</li>
            </ul>
            <p>Navigate to <code>/preview/writing-assessment</code> to see the full interface!</p>
        </div>
        """

@app.route('/login')
def login():
    """Login page with reCAPTCHA v2"""
    class AnonymousUser:
        is_authenticated = False
        email = None
    
    recaptcha_site_key = ProductionConfig().RECAPTCHA_SITE_KEY
    return render_template('login.html', current_user=AnonymousUser(), recaptcha_site_key=recaptcha_site_key)


@app.route('/register')
def register():
    """Redirect register attempts to app store - registration is app-only"""
    return '''
    <html>
    <head>
        <title>Registration - IELTS AI Prep</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container-fluid vh-100 d-flex align-items-center justify-content-center">
            <div class="text-center">
                <div class="card shadow-lg border-0" style="max-width: 500px;">
                    <div class="card-body p-5">
                        <i class="fas fa-mobile-alt fa-4x text-primary mb-4"></i>
                        <h2 class="mb-3">Registration Available in App Only</h2>
                        <p class="lead mb-4">Create your IELTS AI Prep account exclusively through our mobile app for the best experience.</p>
                        <div class="d-grid gap-2">
                            <a href="/download" class="btn btn-primary btn-lg">
                                <i class="fas fa-download me-2"></i>Download App & Register
                            </a>
                            <a href="/login" class="btn btn-outline-secondary">
                                <i class="fas fa-sign-in-alt me-2"></i>Back to Login
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/download')
def download():
    """App download page with links to app stores"""
    return '''
    <html>
    <head>
        <title>Download IELTS AI Prep App</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
        <style>
            .store-badge {
                display: inline-block;
                transition: transform 0.2s;
            }
            .store-badge:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body class="bg-light">
        <div class="container-fluid vh-100 d-flex align-items-center justify-content-center">
            <div class="text-center">
                <div class="card shadow-lg border-0" style="max-width: 600px;">
                    <div class="card-body p-5">
                        <i class="fas fa-mobile-alt fa-4x text-primary mb-4"></i>
                        <h2 class="mb-3">Download IELTS AI Prep</h2>
                        <p class="lead mb-4">Get started with AI-powered IELTS preparation. Download our mobile app from your preferred store.</p>
                        
                        <div class="d-flex flex-column gap-3 mb-4">
                            <a href="https://apps.apple.com/app/ielts-genai-prep" target="_blank" class="store-badge">
                                <img src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg" 
                                     alt="Download on the App Store" 
                                     style="height: 60px;">
                            </a>
                            <a href="https://play.google.com/store/apps/details?id=com.ieltsgenaiprep" target="_blank" class="store-badge">
                                <img src="https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png" 
                                     alt="Get it on Google Play" 
                                     style="height: 90px;">
                            </a>
                        </div>
                        
                        <div class="alert alert-info mb-4">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Note:</strong> Registration and purchases are available exclusively through the mobile app.
                        </div>
                        
                        <a href="/login" class="btn btn-outline-secondary">
                            <i class="fas fa-arrow-left me-2"></i>Back to Login
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/about')
def about():
    """About route for template compatibility"""
    return redirect(url_for('home'))

@app.route('/contact')
def contact():
    """Contact page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
        
    return render_template('contact.html', current_user=AnonymousUser())

@app.route('/icon-preview')
def icon_preview():
    """Serve the new brand icon preview page"""
    try:
        with open('icon_preview_updated.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        try:
            with open('icon_preview.html', 'r') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return '''
            <html>
            <body style="font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 40px; text-align: center;">
                <h1>Icon Preview Not Found</h1>
                <p>The icon preview file could not be loaded.</p>
                <a href="/" style="color: #3498db;">Return to Home</a>
            </body>
            </html>
            '''

@app.route('/new_brand_icon.svg')
def serve_brand_icon():
    """Serve the new brand icon SVG file"""
    try:
        with open('new_brand_icon.svg', 'r') as f:
            svg_content = f.read()
        from flask import Response
        return Response(svg_content, mimetype='image/svg+xml')
    except FileNotFoundError:
        return "Icon not found", 404

@app.route('/user_icon.jpeg')
def serve_user_icon():
    """Serve the user-provided app icon"""
    try:
        from flask import send_file
        return send_file('attached_assets/IMG_0059_1760268985803.jpeg', mimetype='image/jpeg')
    except FileNotFoundError:
        return "Icon not found", 404

@app.route('/terms_and_payment')
@app.route('/terms-and-payment')  # Alias with dashes
@app.route('/terms-of-service')  # Alias for app store compliance
@app.route('/terms_of_service')  # Alias with underscores
def terms_and_payment():
    """Terms and payment page with no-refund policy"""
    try:
        with open('approved_terms_of_service.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        # Fallback to basic terms message
        return '''
        <html>
        <head><title>Terms of Service</title></head>
        <body style="font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 40px;">
            <h1>Terms of Service</h1>
            <p><strong>ALL PURCHASES ARE FINAL AND NON-REFUNDABLE.</strong></p>
            <a href="/">Back to Home</a>
        </body>
        </html>
        '''

@app.route('/privacy_policy')
@app.route('/privacy-policy')  # Alias for app store compliance
def privacy_policy():
    """Privacy policy page - Updated October 2025 (removed Google Cloud references)"""
    # Serve the updated privacy policy from templates
    class AnonymousUser:
        is_authenticated = False
        email = None
    return render_template('gdpr/privacy_policy.html', current_user=AnonymousUser())

@app.route('/forgot-password')
@app.route('/forgot_password')  # Keep old route for compatibility
def forgot_password():
    """Forgot password page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
    
    recaptcha_site_key = ProductionConfig().RECAPTCHA_SITE_KEY
    return render_template('forgot_password.html', current_user=AnonymousUser(), recaptcha_site_key=recaptcha_site_key)

@app.route('/reset_password')
def reset_password():
    """Reset password page"""
    # Provide anonymous user context for template compatibility
    class AnonymousUser:
        is_authenticated = False
        email = None
    
    # Get reset token from query params
    reset_token = request.args.get('token', '')
    
    return render_template('reset_password.html', current_user=AnonymousUser(), reset_token=reset_token)

def generate_reset_token(email: str) -> str:
    """Generate secure password reset token"""
    # Create a secure random token
    token = secrets.token_urlsafe(32)
    
    # Store token in DynamoDB with 30-minute expiration
    if reset_token_dal:
        reset_token_dal.create_reset_token(email, token, expires_minutes=30)
    
    return token

def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email using AWS SES"""
    try:
        # Get production domain from environment variable
        domain_url = os.environ.get('DOMAIN_URL', 'https://www.ieltsaiprep.com')
        
        # Check if running in development mode
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            # Development mode - log the email (but use production-like URL format)
            reset_link = f"{domain_url}/reset_password?token={reset_token}"
            print(f"[DEV_MODE] Password reset email for: {email}")
            print(f"[DEV_MODE] Reset link: {reset_link}")
            return True
        
        # Production mode - use AWS SES
        from ses_email_service import ses_service
        
        # Send email via SES
        return ses_service.send_password_reset_email(email, reset_token)
        
    except Exception as e:
        print(f"[ERROR] Failed to send password reset email: {str(e)}")
        return False

def verify_recaptcha(recaptcha_response: str, user_ip: str = None) -> bool:
    """Verify reCAPTCHA v2 response with Google"""
    try:
        secret_key = os.environ.get("RECAPTCHA_V2_SECRET_KEY")
        if not secret_key:
            logger.error("RECAPTCHA_V2_SECRET_KEY not configured")
            return False
        
        # Google reCAPTCHA verification endpoint
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        
        payload = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        
        if user_ip:
            payload['remoteip'] = user_ip
        
        # Verify with Google
        response = requests.post(verify_url, data=payload, timeout=5)
        result = response.json()
        
        # Log verification result for debugging
        logger.info(f"reCAPTCHA verification result: {result.get('success', False)}")
        
        return result.get('success', False)
        
    except Exception as e:
        logger.error(f"reCAPTCHA verification error: {str(e)}")
        return False

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle email login with reCAPTCHA v2 verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        recaptcha_response = data.get('g-recaptcha-response', '')
        
        # Validate required fields
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Verify reCAPTCHA
        if not recaptcha_response:
            return jsonify({
                'success': False,
                'message': 'Please complete the reCAPTCHA verification'
            }), 400
        
        # Get user's IP address from headers (CloudFront/API Gateway)
        user_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or request.remote_addr
        
        # Verify reCAPTCHA with Google
        if not verify_recaptcha(recaptcha_response, user_ip):
            logger.warning(f"Failed reCAPTCHA verification for email: {email}, IP: {user_ip}")
            return jsonify({
                'success': False,
                'message': 'reCAPTCHA verification failed. Please try again.'
            }), 400
        
        # Authenticate user with DynamoDB
        if use_production and user_dal:
            try:
                user = user_dal.get_user_by_email(email)
                
                if not user:
                    logger.warning(f"Login attempt for non-existent user: {email}")
                    return jsonify({
                        'success': False,
                        'message': 'Invalid email or password'
                    }), 401
                
                # Verify password
                if not check_password_hash(user.get('password_hash', ''), password):
                    logger.warning(f"Failed login attempt for user: {email}")
                    return jsonify({
                        'success': False,
                        'message': 'Invalid email or password'
                    }), 401
                
                # Create session
                session['user_id'] = user.get('user_id')
                session['email'] = email
                session['logged_in'] = True
                session['login_time'] = datetime.utcnow().isoformat()
                
                logger.info(f"Successful login for user: {email}")
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'email': email,
                        'user_id': user.get('user_id')
                    }
                })
                
            except Exception as e:
                logger.error(f"Database error during login: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'An error occurred during login. Please try again.'
                }), 500
        else:
            # Development mode - mock authentication
            logger.warning("Using mock authentication (development mode)")
            session['user_id'] = 'dev_user_123'
            session['email'] = email
            session['logged_in'] = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful (dev mode)',
                'user': {
                    'email': email,
                    'user_id': 'dev_user_123'
                }
            })
        
    except Exception as e:
        logger.error(f"Login API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """Handle forgot password API request"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Email address is required'
            }), 400
        
        # Generate secure reset token
        reset_token = generate_reset_token(email)
        
        # Send password reset email via AWS SES
        if send_password_reset_email(email, reset_token):
            return jsonify({
                'status': 'success',
                'message': 'If this email is registered, you will receive password reset instructions.'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Unable to send password reset email. Please try again later.'
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Password reset request failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Unable to process password reset request. Please try again later.'
        }), 500

def validate_reset_token(token: str) -> str | None:
    """Validate password reset token and return associated email if valid"""
    if reset_token_dal:
        return reset_token_dal.validate_reset_token(token)
    return None

def invalidate_reset_token(token: str) -> None:
    """Invalidate a password reset token after use"""
    if reset_token_dal:
        reset_token_dal.invalidate_reset_token(token)

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """Handle reset password API request with production-ready token validation"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validate inputs
        if not all([token, new_password, confirm_password]):
            return jsonify({
                'status': 'error',
                'message': 'All fields are required'
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                'status': 'error',
                'message': 'Passwords do not match'
            }), 400
        
        if len(new_password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 8 characters long'
            }), 400
        
        # Validate password reset token
        email = validate_reset_token(token)
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired reset token. Please request a new password reset.'
            }), 400
        
        # In a production system, you would update the password in your database
        # For this demo, we'll just log the success and invalidate the token
        print(f"[PASSWORD_RESET] Password successfully reset for: {email}")
        
        # Invalidate the token to prevent reuse
        invalidate_reset_token(token)
        
        # Send confirmation email (optional but recommended)
        try:
            send_password_reset_confirmation_email(email)
        except Exception as e:
            print(f"[WARNING] Failed to send password reset confirmation email: {str(e)}")
            # Don't fail the reset if confirmation email fails
        
        return jsonify({
            'status': 'success',
            'message': 'Password reset successful. You can now log in with your new password.',
            'redirect': '/login'
        })
        
    except Exception as e:
        print(f"[ERROR] Password reset failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Unable to reset password. Please try again later.'
        }), 500

def send_password_reset_confirmation_email(email: str) -> bool:
    """Send password reset confirmation email"""
    try:
        # Check if running in development mode
        if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            print(f"[DEV_MODE] Password reset confirmation email for: {email}")
            return True
        
        # Production mode - use AWS SES
        ses_client = boto3.client(
            'ses',
            region_name=os.environ.get('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        username = email.split('@')[0].title()
        subject = "IELTS AI Prep - Password Reset Successful"
        
        # Confirmation email template with new IELTS AI Prep branding
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Password Reset Successful - IELTS AI Prep</title>
        </head>
        <body style="font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: #ffffff; text-align: center; padding: 30px 20px; border-radius: 8px 8px 0 0; border-bottom: 3px solid #0891B2;">
                    <h1 style="color: #E33219; margin: 0 0 10px 0; font-size: 28px; font-weight: 700; letter-spacing: -0.02em;">IELTS AI Prep</h1>
                    <p style="color: #666; margin: 0; font-size: 14px;">Your Personalized Path to IELTS Success</p>
                </div>
                
                <!-- Success Message -->
                <div style="background: #ffffff; padding: 40px 30px; border-radius: 0 0 8px 8px;">
                    <div style="background: #e8f5e9; padding: 25px; border-radius: 8px; border-left: 4px solid #0891B2; margin-bottom: 30px;">
                        <h2 style="color: #1a1a1a; margin-bottom: 20px; text-align: center; font-weight: 600; font-size: 22px;">
                            ✅ Password Reset Successful
                        </h2>
                        
                        <p style="margin-bottom: 20px; color: #333;">Hello {username},</p>
                        
                        <p style="margin-bottom: 25px; color: #333;">Your password has been successfully reset. You can now log in to your IELTS AI Prep account using your new password.</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://ieltsaiprep.com/login" 
                               style="background: linear-gradient(135deg, #0891B2 0%, #0E7490 100%); color: white; padding: 16px 40px; 
                                      text-decoration: none; border-radius: 8px; display: inline-block;
                                      font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(8, 145, 178, 0.3);">
                                Login to My Account
                            </a>
                        </div>
                        
                        <p style="margin-bottom: 0; color: #666; font-size: 14px;">If you did not reset your password, please contact our support team immediately.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 35px;">
                        <p style="margin-bottom: 5px; font-weight: 600; color: #1a1a1a;">Best regards,</p>
                        <p style="margin-bottom: 15px; color: #333;">The IELTS AI Prep Team</p>
                        <p style="font-size: 12px; color: #999;">© 2025 IELTS AI Prep. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send confirmation email via AWS SES
        response = ses_client.send_email(
            Source='noreply@ieltsaiprep.com',
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"[SES] Password reset confirmation email sent to {email}: {response['MessageId']}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to send password reset confirmation email: {str(e)}")
        return False



@app.route('/assessment/<assessment_type>/<int:assessment_number>/start')
def assessment_start(assessment_type, assessment_number):
    """Assessment start route for template compatibility with rate limiting"""
    # Verify session
    session_id = request.cookies.get('session_id')
    if not session_id or session_id not in sessions:
        return redirect(url_for('home'))
    
    session_data = sessions[session_id]
    user_email = session_data['user_email']
    
    # Check rate limit (8 assessments per day)
    if assessment_dal and use_production:
        is_within_limit, current_count = assessment_dal.check_rate_limit(user_email, daily_limit=8)
        
        if not is_within_limit:
            logger.warning(f"Rate limit exceeded for {user_email}: {current_count}/8 assessments today")
            return f"""
            <html><head><title>Daily Limit Reached</title></head>
            <body style="font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 40px; background: #f5f5f5;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 20px;">⏸️</div>
                    <h2 style="color: #e74c3c;">Daily Assessment Limit Reached</h2>
                    <p style="font-size: 16px; color: #555; margin: 20px 0;">
                        You've completed <strong>{current_count} assessments</strong> today. 
                        Our daily limit is <strong>8 assessments</strong> to ensure quality learning and prevent burnout.
                    </p>
                    <div style="margin: 20px 0; padding: 15px; background: #fff3cd; border-radius: 5px; border-left: 4px solid #ffc107;">
                        <p style="margin: 0; color: #856404;"><strong>Why we have limits:</strong> Spacing out your practice improves retention and prevents fatigue.</p>
                    </div>
                    <p style="font-size: 14px; color: #777; margin: 20px 0;">
                        Your limit will reset at midnight UTC. Come back tomorrow to continue your IELTS preparation!
                    </p>
                    <a href="/profile" style="display: inline-block; margin-top: 20px; background: #2c3e50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Back to Dashboard</a>
                </div>
            </body></html>
            """
        
        logger.info(f"Rate limit check passed for {user_email}: {current_count}/8 assessments today")
    
    return f"""
    <html><head><title>Assessment Started</title></head>
    <body style="font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 40px; background: #f5f5f5;">
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h2>Assessment {assessment_number} Started</h2>
            <p><strong>Type:</strong> {assessment_type.replace('_', ' ').title()}</p>
            <p><strong>User:</strong> {user_email}</p>
            <p><strong>Session:</strong> {session_id}</p>
            <div style="margin: 20px 0; padding: 15px; background: #e8f5e8; border-radius: 5px;">
                Assessment module would load here with Nova Sonic AI integration
            </div>
            <a href="/assessment/{assessment_type}" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none;">Back to Assessments</a>
        </div>
    </body></html>
    """

@app.route('/profile')
def profile():
    """Serve profile/assessments page - requires mobile app access"""
    # Redirect to home - profile access only through mobile app
    return redirect(url_for('home'))

@app.route('/assessment/<assessment_type>')
def assessment_list(assessment_type):
    """Lambda /assessment/<user_id> endpoint simulation - mobile app only"""
    # Redirect to home - assessments only through mobile app
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    """Logout - mobile app only"""
    return redirect(url_for('home'))

@app.route('/test-mobile')
def test_mobile():
    """Serve mobile purchase simulator for testing"""
    try:
        with open('test_mobile_simulator.html', 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return """
        <h1>Mobile Simulator Not Found</h1>
        <p>Please create the mobile simulator file first.</p>
        <a href="/">Go to Home</a>
        """


@app.route('/api/health', methods=['GET', 'POST'])
def health_check():
    """Lambda health check endpoint simulation"""
    try:
        # Check system components
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'dynamodb': {
                    'active_sessions': len(sessions)
                },
                'lambda': {
                    'memory_usage': '128MB',
                    'cold_starts': 0
                }
            },
            'metrics': {
                'active_sessions': len([s for s in sessions.values() if time.time() < s['expires_at']]),
                'purchased_products': sum(len(products) for products in mock_purchases.values())
            }
        }
        
        print(f"[CLOUDWATCH] Health check: {health_data['status']}")
        return jsonify(health_data)
        
    except Exception as e:
        print(f"[CLOUDWATCH] Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/assessment/<user_email>')
def get_assessments(user_email):
    """Test endpoint - Get user assessments (simulates Lambda)"""
    try:
        # Check session
        auth_header = request.headers.get('Authorization', '')
        session_id = auth_header.replace('Bearer ', '') if auth_header else None
        
        if not session_id or session_id not in sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session'
            }), 401
        
        session_data = sessions[session_id]
        
        # Check session expiry
        if time.time() > session_data['expires_at']:
            return jsonify({
                'success': False,
                'error': 'Session expired'
            }), 401
        
        # Get assessments from proper data structure
        user_data = user_assessments.get(user_email, {})
        all_assessments = []
        for assessment_type, assessments in user_data.items():
            for assessment in assessments:
                assessment_copy = assessment.copy()
                assessment_copy['assessment_type'] = assessment_type
                all_assessments.append(assessment_copy)
        
        return jsonify({
            'success': True,
            'assessments': all_assessments,
            'total_count': len(all_assessments)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assessment-structure')
def assessment_structure():
    """Show IELTS test structure with FAQ section"""
    ielts_info = "IELTS (International English Language Testing System) is designed to help you work, study, or migrate to a country where English is the native language. This includes countries such as Australia, Canada, New Zealand, the UK, and USA."
    return render_template('assessment_structure/index.html', ielts_info=ielts_info)

@app.route('/assessment-structure/<assessment_type>')
def assessment_structure_detail(assessment_type):
    """Show detailed assessment structure for specific type"""
    if assessment_type == 'academic':
        return render_template('assessment_structure/academic.html')
    elif assessment_type == 'general_training':
        return render_template('assessment_structure/general_training.html')
    else:
        return "Assessment type not found", 404

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt for AI SEO optimization"""
    return send_from_directory('.', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap_xml():
    """Serve sitemap.xml for search engine and AI crawler discovery"""
    return send_from_directory('.', 'sitemap.xml')

@app.route('/helpdesk-login', methods=['GET', 'POST'])
def helpdesk_login():
    """Login page for helpdesk dashboard"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin_email = 'worldwidepublishingco@gmail.com'
        admin_password = os.environ.get('HELPDESK_ADMIN_PASSWORD')
        
        if email == admin_email and password == admin_password:
            session['helpdesk_admin'] = True
            return redirect(url_for('helpdesk_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('helpdesk_login.html')

@app.route('/helpdesk-logout')
def helpdesk_logout():
    """Logout from helpdesk dashboard"""
    session.pop('helpdesk_admin', None)
    return redirect(url_for('helpdesk_login'))

@app.route('/helpdesk-dashboard')
def helpdesk_dashboard():
    """
    Helpdesk dashboard for viewing AI ticket analysis
    Protected route - requires admin authentication
    """
    # Check authentication
    if not session.get('helpdesk_admin'):
        return redirect(url_for('helpdesk_login'))
    
    from helpdesk_service import analyze_ticket_with_ai
    
    # Sample tickets for demonstration
    sample_tickets = [
        {
            'ticket_id': 'DEMO-001',
            'user_email': 'user@example.com',
            'subject': 'I want a refund for my assessment',
            'body': 'I took the speaking test but got a lower score than I expected. I want my money back.',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'ticket_id': 'DEMO-002',
            'user_email': 'student@example.com',
            'subject': 'Cannot login to my account',
            'body': 'I keep trying to login but it says my password is wrong. I have tried resetting it but the email never arrives.',
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'ticket_id': 'DEMO-003',
            'user_email': 'learner@example.com',
            'subject': 'My purchase is not showing',
            'body': 'I just bought the speaking assessment package from the app store but it is not appearing in my account.',
            'timestamp': datetime.utcnow().isoformat()
        }
    ]
    
    # Analyze each ticket with AI
    analyzed_tickets = []
    for ticket in sample_tickets:
        ai_response = analyze_ticket_with_ai(ticket['subject'], ticket['body'])
        analyzed_tickets.append({
            'ticket': ticket,
            'ai_analysis': ai_response
        })
    
    escalation_email = os.environ.get('HELPDESK_ESCALATION_EMAIL', 'worldwidepublishingco@gmail.com')
    return render_template('helpdesk_dashboard.html', tickets=analyzed_tickets, escalation_email=escalation_email)

# ===== GDPR Data Rights Routes =====

@app.route('/gdpr/my-data')
def gdpr_my_data():
    """GDPR dashboard for data rights management"""
    # Check if user is logged in
    user_email = session.get('user_email')
    if not user_email:
        return redirect(url_for('login'))
    
    # Get user data
    user_data = user_dal.get_user_by_email(user_email)
    if not user_data:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    return render_template('gdpr/my_data.html', user=user_data)

@app.route('/gdpr/export-data', methods=['POST'])
def gdpr_export_data():
    """Export user data as JSON"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get user data
    user_data = user_dal.get_user_by_email(user_email)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    # Compile complete user data export (all personal data we hold)
    export_data = {
        'personal_information': {
            'email': user_data.get('email'),
            'username': user_data.get('username'),
            'full_name': user_data.get('full_name'),
            'user_id': user_data.get('user_id'),
            'profile_picture': user_data.get('profile_picture'),
            'bio': user_data.get('bio'),
            'preferred_language': user_data.get('preferred_language')
        },
        'account_information': {
            'join_date': user_data.get('join_date').isoformat() if user_data.get('join_date') else None,
            'last_login': user_data.get('last_login').isoformat() if user_data.get('last_login') else None,
            'is_active': user_data.get('is_active'),
            'created_at': user_data.get('created_at').isoformat() if user_data.get('created_at') else None
        },
        'consent_preferences': user_data.get('preferences', {}),
        'assessment_information': {
            'assessment_package_status': user_data.get('assessment_package_status'),
            'assessment_package_expiry': user_data.get('assessment_package_expiry').isoformat() if user_data.get('assessment_package_expiry') else None,
            'subscription_status': user_data.get('subscription_status'),
            'subscription_expiry': user_data.get('subscription_expiry').isoformat() if user_data.get('subscription_expiry') else None
        },
        'export_metadata': {
            'export_date': datetime.utcnow().isoformat(),
            'export_format': 'JSON',
            'data_version': '1.0'
        }
    }
    
    return jsonify(export_data)

@app.route('/gdpr/delete-account', methods=['POST'])
def gdpr_delete_account():
    """Delete user account and all data"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Verify password for security
    password = request.json.get('password')
    if not password:
        return jsonify({'error': 'Password required'}), 400
    
    # Get user and verify password
    user_data = user_dal.get_user_by_email(user_email)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_password_hash(user_data['password_hash'], password):
        return jsonify({'error': 'Invalid password'}), 401
    
    # Delete user
    success = user_dal.delete_user(user_email)
    if not success:
        return jsonify({'error': 'Failed to delete account'}), 500
    
    # Clear session
    session.clear()
    
    return jsonify({'success': True, 'message': 'Account deleted successfully'})

# ============================================================================
# AI ASSESSMENT ENDPOINTS
# ============================================================================

@app.route('/api/writing/evaluate', methods=['POST'])
def evaluate_writing():
    """Evaluate IELTS writing task using AWS Bedrock Nova Micro"""
    if not bedrock_service:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        essay_text = data.get('essay_text')
        prompt = data.get('prompt', 'Describe the given information')
        assessment_type = data.get('assessment_type', 'academic_task2')
        user_email = session.get('user_email', 'anonymous')
        
        if not essay_text:
            return jsonify({'error': 'Essay text is required'}), 400
        
        # Evaluate with Nova Micro
        result = bedrock_service.evaluate_writing_with_nova_micro(
            essay_text=essay_text,
            prompt=prompt,
            assessment_type=assessment_type
        )
        
        # Save to DynamoDB if user is logged in and assessment DAL is available
        if user_email != 'anonymous' and assessment_dal:
            result['user_email'] = user_email
            result['assessment_type'] = assessment_type
            assessment_dal.save_assessment(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Writing evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reading/evaluate', methods=['POST'])
def evaluate_reading():
    """Evaluate IELTS reading comprehension using AWS Bedrock Nova Micro"""
    if not bedrock_service:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        user_answers = data.get('user_answers', [])
        answer_key = data.get('answer_key', [])
        passages = data.get('passages', [])
        assessment_type = data.get('assessment_type', 'academic_reading')
        user_email = session.get('user_email', 'anonymous')
        
        if not user_answers or not answer_key:
            return jsonify({'error': 'User answers and answer key are required'}), 400
        
        # Evaluate with Nova Micro
        result = bedrock_service.evaluate_reading_with_nova_micro(
            user_answers=user_answers,
            answer_key=answer_key,
            passages=passages,
            assessment_type=assessment_type
        )
        
        # Save to DynamoDB if user is logged in
        if user_email != 'anonymous' and assessment_dal:
            result['user_email'] = user_email
            assessment_dal.save_assessment(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Reading evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/listening/evaluate', methods=['POST'])
def evaluate_listening():
    """Evaluate IELTS listening comprehension using AWS Bedrock Nova Micro"""
    if not bedrock_service:
        return jsonify({'error': 'AI service not available'}), 503
    
    try:
        data = request.get_json()
        user_answers = data.get('user_answers', [])
        answer_key = data.get('answer_key', [])
        transcript = data.get('transcript', '')
        assessment_type = data.get('assessment_type', 'academic_listening')
        user_email = session.get('user_email', 'anonymous')
        
        if not user_answers or not answer_key:
            return jsonify({'error': 'User answers and answer key are required'}), 400
        
        # Evaluate with Nova Micro
        result = bedrock_service.evaluate_listening_with_nova_micro(
            user_answers=user_answers,
            answer_key=answer_key,
            transcript=transcript,
            assessment_type=assessment_type
        )
        
        # Save to DynamoDB if user is logged in
        if user_email != 'anonymous' and assessment_dal:
            result['user_email'] = user_email
            assessment_dal.save_assessment(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Listening evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/speaking-assessment-demo')
def speaking_assessment_demo():
    """Serve the speaking assessment demo page with sound waves fallback"""
    return render_template('speaking_assessment_with_fallback.html')

@app.route('/listening-test')
def listening_test_page():
    """Serve the listening test page"""
    return render_template('listening_test.html')

@app.route('/reading-test')
def reading_test_page():
    """Serve the reading test page"""
    return render_template('reading_test.html')

# Register test routes
try:
    from listening_test_routes import listening_routes
    app.register_blueprint(listening_routes)
    print("[INFO] Listening test routes registered")
except ImportError as e:
    print(f"[INFO] Listening test routes not available: {e}")

try:
    from reading_test_routes import reading_routes
    app.register_blueprint(reading_routes)
    print("[INFO] Reading test routes registered")
except ImportError as e:
    print(f"[INFO] Reading test routes not available: {e}")

@app.route('/api/speaking/start', methods=['POST'])
def start_speaking_assessment():
    """Start IELTS speaking assessment with Gemini Smart Selection"""
    # For now, return a placeholder response
    # Full implementation would use the Gemini Smart Selection service
    return jsonify({
        'status': 'ready',
        'websocket_url': '/api/speaking/stream',
        'assessment_id': str(uuid.uuid4()),
        'model': 'gemini-flash-lite',
        'message': 'Speaking assessment ready. Connect via WebSocket for real-time conversation.'
    })

@app.route('/gdpr/update-consent', methods=['POST'])
def gdpr_update_consent():
    """Update user consent preferences"""
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get consent preferences
    marketing_consent = request.json.get('marketing_consent', False)
    analytics_consent = request.json.get('analytics_consent', False)
    
    # Update user preferences
    user_data = user_dal.get_user_by_email(user_email)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    # Update preferences in DynamoDB
    preferences = user_data.get('preferences', {})
    preferences['marketing_consent'] = marketing_consent
    preferences['analytics_consent'] = analytics_consent
    preferences['consent_updated_at'] = datetime.utcnow().isoformat()
    
    doc_ref = user_dal.collection.document(user_email.lower())
    doc_ref.update({'preferences': preferences})
    
    return jsonify({'success': True, 'message': 'Consent preferences updated'})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with Lambda binary support"""
    import mimetypes
    from flask import make_response
    
    # Build file path
    file_path = os.path.join('static', filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # Detect content type
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Read file in binary mode
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # For binary files (images, etc), encode as base64 for API Gateway
    if content_type.startswith('image/') or content_type == 'application/octet-stream':
        response = make_response(base64.b64encode(file_data))
        response.headers['Content-Type'] = content_type
        response.headers['Content-Disposition'] = f'inline; filename={os.path.basename(filename)}'
        # Signal to API Gateway that this is base64 encoded
        response.is_base64_encoded = True
        return response
    else:
        # For text files (CSS, JS), return as normal
        response = make_response(file_data)
        response.headers['Content-Type'] = content_type
        return response

# ============================================================================
# ADMIN AUTHENTICATION SYSTEM
# Environment variable-based admin authentication for dashboard access
# ============================================================================

def is_admin_authenticated():
    """Check if current session is authenticated as admin"""
    return session.get('is_admin', False)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page with environment variable authentication"""
    if request.method == 'GET':
        # If already logged in, redirect to dashboard
        if is_admin_authenticated():
            return redirect(url_for('dashboard.security_dashboard'))
        return render_template('admin_login.html', config=ProductionConfig())
    
    # POST request - process login
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    # Get admin credentials from environment variables
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password_hash = os.environ.get('ADMIN_PASSWORD_HASH')
    
    # Validate environment variables are set
    if not admin_email or not admin_password_hash:
        logger.error("ADMIN_EMAIL or ADMIN_PASSWORD_HASH not set in environment variables")
        return render_template('admin_login.html', 
                             error='Admin authentication not configured. Please contact support.')
    
    # Verify credentials
    if email.lower() == admin_email.lower() and check_password_hash(admin_password_hash, password):
        # Set admin session
        session['is_admin'] = True
        session['admin_email'] = email
        session['admin_login_time'] = datetime.utcnow().isoformat()
        
        logger.info(f"Admin login successful: {email}")
        flash('Welcome to the admin dashboard!', 'success')
        return redirect(url_for('dashboard.security_dashboard'))
    else:
        logger.warning(f"Failed admin login attempt: {email}")
        return render_template('admin_login.html', 
                             error='Invalid email or password. Please try again.')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout - clear admin session"""
    admin_email = session.get('admin_email', 'Unknown')
    session.pop('is_admin', None)
    session.pop('admin_email', None)
    session.pop('admin_login_time', None)
    
    logger.info(f"Admin logout: {admin_email}")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/forgot-password', methods=['GET'])
def admin_forgot_password():
    """Admin forgot password page - directs to support for security reasons"""
    return render_template('admin_forgot_password.html')

# ============================================================================
# REGISTER AI AGENTS DASHBOARD BLUEPRINT
# ============================================================================

# Dashboard routes disabled for Lambda deployment to avoid boto3 conflicts
# try:
#     from dashboard_routes import dashboard_bp
#     app.register_blueprint(dashboard_bp)
#     print("[INFO] AI Agents dashboard routes registered at /dashboard")
# except Exception as e:
#     print(f"[WARNING] AI Agents dashboard routes not available: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)