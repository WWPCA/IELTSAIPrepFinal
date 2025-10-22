"""
Desktop-Only Access Middleware for IELTS AI Prep
Enforces that assessments can only be taken on laptop/desktop devices
Maintains authentic IELTS test experience
"""
import re
from functools import wraps
from flask import request, render_template_string, jsonify

# Mobile user agent patterns
MOBILE_PATTERNS = [
    r'(android|bb\d+|meego).+mobile',
    r'avantgo',
    r'bada/',
    r'blackberry',
    r'blazer',
    r'compal',
    r'elaine',
    r'fennec',
    r'hiptop',
    r'iemobile',
    r'ip(hone|od)',
    r'iris',
    r'kindle',
    r'lge ',
    r'maemo',
    r'midp',
    r'mmp',
    r'mobile.+firefox',
    r'netfront',
    r'opera m(ob|in)i',
    r'palm( os)?',
    r'phone',
    r'p(ixi|re)/',
    r'plucker',
    r'pocket',
    r'psp',
    r'series(4|6)0',
    r'symbian',
    r'treo',
    r'up\.(browser|link)',
    r'vodafone',
    r'wap',
    r'windows ce',
    r'windows phone',
    r'xda',
    r'xiino',
    r'android',
    r'ipad',
    r'playbook',
    r'silk'
]

# Compile mobile detection regex
MOBILE_RE = re.compile(r'|'.join(MOBILE_PATTERNS), re.IGNORECASE)

def is_mobile_device(user_agent):
    """
    Detect if request is from a mobile device
    
    Args:
        user_agent: User-Agent header string
        
    Returns:
        True if mobile device detected
    """
    if not user_agent:
        return False
    
    # Check against mobile patterns
    return bool(MOBILE_RE.search(user_agent))

def require_desktop(f):
    """
    Decorator to enforce desktop-only access for assessment routes
    Redirects mobile users to a "desktop required" page
    
    Usage:
        @app.route('/assessment/writing')
        @require_desktop
        def writing_assessment():
            return render_template('assessment.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_agent = request.headers.get('User-Agent', '')
        
        # Check if device is mobile
        if is_mobile_device(user_agent):
            # For API requests, return JSON error
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'desktop_required',
                    'message': 'Assessments can only be taken on laptop or desktop computers for authentic IELTS test experience.'
                }), 403
            
            # For web requests, show desktop-required page
            return render_desktop_required_page(), 403
        
        # Desktop device - allow access
        return f(*args, **kwargs)
    
    return decorated_function

def render_desktop_required_page():
    """Render the desktop-required message page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Desktop Required - IELTS AI Prep</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #E33219 0%, #8B1A10 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            .desktop-required-container {
                background: white;
                border-radius: 24px;
                padding: 48px 32px;
                max-width: 500px;
                margin: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            .icon-container {
                background: linear-gradient(135deg, #E33219 0%, #FF6B55 100%);
                width: 100px;
                height: 100px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 32px;
                box-shadow: 0 8px 24px rgba(227, 50, 25, 0.3);
            }
            .icon-container i {
                font-size: 48px;
                color: white;
            }
            h1 {
                color: #1a1a1a;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 16px;
            }
            p {
                color: #666;
                font-size: 16px;
                line-height: 1.6;
                margin-bottom: 24px;
            }
            .highlight-text {
                color: #E33219;
                font-weight: 600;
            }
            .back-btn {
                display: inline-block;
                padding: 14px 32px;
                background: linear-gradient(135deg, #E33219 0%, #FF6B55 100%);
                color: white;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(227, 50, 25, 0.3);
            }
            .back-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(227, 50, 25, 0.4);
                color: white;
            }
            .device-icons {
                display: flex;
                justify-content: center;
                gap: 24px;
                margin-top: 32px;
                padding-top: 32px;
                border-top: 1px solid #eee;
            }
            .device-icons i {
                font-size: 32px;
                color: #E33219;
            }
        </style>
    </head>
    <body>
        <div class="desktop-required-container">
            <div class="icon-container">
                <i class="fas fa-laptop"></i>
            </div>
            
            <h1>Desktop Required</h1>
            
            <p>
                IELTS assessments must be taken on a <span class="highlight-text">laptop or desktop computer</span> 
                to provide you with an <span class="highlight-text">authentic IELTS test experience</span>.
            </p>
            
            <p>
                The official IELTS examination is conducted on desktop computers, and we maintain the 
                same environment to help you prepare effectively.
            </p>
            
            <a href="/" class="back-btn">
                <i class="fas fa-home"></i> Return to Homepage
            </a>
            
            <div class="device-icons">
                <i class="fas fa-laptop" title="Laptop"></i>
                <i class="fas fa-desktop" title="Desktop"></i>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# Export decorator
__all__ = ['require_desktop', 'is_mobile_device']
