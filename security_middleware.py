"""
Security Middleware for IELTS GenAI Prep
Provides request validation, input sanitization, and rate limiting
"""
import json
import re
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from functools import wraps
from datetime import datetime, timedelta

import jsonschema
from jsonschema import validate, ValidationError
from flask import request, jsonify, current_app, g

logger = logging.getLogger(__name__)

# Request schemas for validation
API_SCHEMAS = {
    'user_registration': {
        'type': 'object',
        'properties': {
            'username': {'type': 'string', 'minLength': 3, 'maxLength': 50, 'pattern': '^[a-zA-Z0-9_]+$'},
            'email': {'type': 'string', 'format': 'email', 'maxLength': 254},
            'password': {'type': 'string', 'minLength': 8, 'maxLength': 128},
            'full_name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
            'recaptcha_token': {'type': 'string'}
        },
        'required': ['username', 'email', 'password', 'full_name'],
        'additionalProperties': False
    },
    
    'user_login': {
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'format': 'email', 'maxLength': 254},
            'password': {'type': 'string', 'minLength': 1, 'maxLength': 128},
            'recaptcha_token': {'type': 'string'}
        },
        'required': ['email', 'password'],
        'additionalProperties': False
    },
    
    'nova_sonic_stream': {
        'type': 'object',
        'properties': {
            'user_text': {'type': 'string', 'maxLength': 2000},
            'audio_data': {'type': 'string'},
            'conversation_id': {'type': 'string', 'maxLength': 100},
            'user_email': {'type': 'string', 'format': 'email', 'maxLength': 254}
        },
        'additionalProperties': False
    },
    
    'qr_token_request': {
        'type': 'object',
        'properties': {
            'browser_session_id': {'type': 'string', 'maxLength': 128},
            'device_type': {'type': 'string', 'enum': ['mobile', 'web', 'tablet']}
        },
        'required': ['browser_session_id'],
        'additionalProperties': False
    },
    
    'purchase_verification': {
        'type': 'object',
        'properties': {
            'receipt_data': {'type': 'string'},
            'platform': {'type': 'string', 'enum': ['ios', 'android']},
            'product_id': {'type': 'string', 'maxLength': 100},
            'transaction_id': {'type': 'string', 'maxLength': 200}
        },
        'required': ['receipt_data', 'platform', 'product_id'],
        'additionalProperties': False
    }
}

# Rate limiting configuration
RATE_LIMITS = {
    'auth_endpoints': {'requests': 5, 'window': 60},  # 5 requests per minute
    'api_endpoints': {'requests': 30, 'window': 60},  # 30 requests per minute
    'nova_sonic': {'requests': 10, 'window': 60},     # 10 requests per minute
    'default': {'requests': 20, 'window': 60}         # 20 requests per minute
}

# Content size limits (bytes)
MAX_CONTENT_LENGTHS = {
    'json': 50 * 1024,      # 50KB for JSON
    'audio': 10 * 1024 * 1024,  # 10MB for audio
    'default': 5 * 1024      # 5KB default
}

class SecurityValidationError(Exception):
    """Custom exception for security validation errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise SecurityValidationError("Invalid string input")
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Limit length
        if len(value) > max_length:
            raise SecurityValidationError(f"Input too long (max {max_length} characters)")
        
        # Basic XSS prevention
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise SecurityValidationError("Potentially dangerous input detected")
        
        return value.strip()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize and validate email"""
        email = InputSanitizer.sanitize_string(email, 254).lower()
        
        # RFC 5322 compliant email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise SecurityValidationError("Invalid email format")
        
        return email
    
    @staticmethod
    def sanitize_audio_data(audio_data: str) -> str:
        """Validate base64 audio data"""
        if not isinstance(audio_data, str):
            raise SecurityValidationError("Invalid audio data format")
        
        # Check if it's valid base64
        try:
            import base64
            decoded = base64.b64decode(audio_data, validate=True)
            
            # Check size limits
            if len(decoded) > MAX_CONTENT_LENGTHS['audio']:
                raise SecurityValidationError("Audio data too large")
            
            return audio_data
        except Exception:
            raise SecurityValidationError("Invalid base64 audio data")
    
    @staticmethod
    def sanitize_json_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize JSON payload"""
        if not isinstance(payload, dict):
            raise SecurityValidationError("Invalid JSON payload")
        
        sanitized = {}
        for key, value in payload.items():
            # Sanitize keys
            clean_key = InputSanitizer.sanitize_string(str(key), 100)
            
            # Sanitize values based on type
            if isinstance(value, str):
                if key in ['audio_data', 'receipt_data']:
                    sanitized[clean_key] = InputSanitizer.sanitize_audio_data(value)
                elif key == 'email':
                    sanitized[clean_key] = InputSanitizer.sanitize_email(value)
                else:
                    sanitized[clean_key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[clean_key] = value
            elif isinstance(value, dict):
                sanitized[clean_key] = InputSanitizer.sanitize_json_payload(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    InputSanitizer.sanitize_string(str(item)) if isinstance(item, str) else item
                    for item in value[:50]  # Limit array size
                ]
            else:
                sanitized[clean_key] = str(value)
        
        return sanitized

class RateLimiter:
    """In-memory rate limiter (use Redis in production)"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier: str, endpoint_type: str = 'default') -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limits"""
        now = time.time()
        limits = RATE_LIMITS.get(endpoint_type, RATE_LIMITS['default'])
        
        # Clean old entries
        if identifier in self.requests:
            self.requests[identifier] = [
                timestamp for timestamp in self.requests[identifier]
                if now - timestamp < limits['window']
            ]
        else:
            self.requests[identifier] = []
        
        # Check limits
        current_requests = len(self.requests[identifier])
        
        if current_requests >= limits['requests']:
            return False, {
                'limit': limits['requests'],
                'window': limits['window'],
                'current': current_requests,
                'reset_time': int(now + limits['window'])
            }
        
        # Record this request
        self.requests[identifier].append(now)
        
        return True, {
            'limit': limits['requests'],
            'window': limits['window'],
            'current': current_requests + 1,
            'reset_time': int(now + limits['window'])
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

def validate_content_length():
    """Validate request content length"""
    content_type = request.content_type or ''
    
    if 'json' in content_type.lower():
        max_size = MAX_CONTENT_LENGTHS['json']
    elif 'audio' in content_type.lower():
        max_size = MAX_CONTENT_LENGTHS['audio']
    else:
        max_size = MAX_CONTENT_LENGTHS['default']
    
    content_length = request.content_length or 0
    if content_length > max_size:
        raise SecurityValidationError(
            f"Request too large: {content_length} bytes (max: {max_size})",
            status_code=413
        )

def validate_request_headers():
    """Validate required security headers"""
    # Check CloudFront custom header (if configured)
    cloudfront_header = current_app.config.get('CLOUDFRONT_CUSTOM_HEADER')
    if cloudfront_header:
        expected_value = current_app.config.get('CLOUDFRONT_CUSTOM_VALUE')
        if request.headers.get(cloudfront_header) != expected_value:
            raise SecurityValidationError("Direct access not allowed", status_code=403)
    
    # Validate User-Agent
    user_agent = request.headers.get('User-Agent', '')
    if not user_agent or len(user_agent) > 500:
        raise SecurityValidationError("Invalid User-Agent", status_code=400)

def get_client_identifier() -> str:
    """Get client identifier for rate limiting"""
    # Try to get authenticated user
    if hasattr(g, 'current_user') and g.current_user:
        return f"user:{g.current_user.get('email', 'unknown')}"
    
    # Fallback to IP address
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        # Get first IP from X-Forwarded-For
        client_ip = forwarded_for.split(',')[0].strip()
    else:
        client_ip = request.remote_addr or 'unknown'
    
    return f"ip:{client_ip}"

def security_middleware(schema_name: Optional[str] = None, 
                       endpoint_type: str = 'default',
                       require_auth: bool = False):
    """
    Security middleware decorator
    
    Args:
        schema_name: JSON schema to validate against
        endpoint_type: Rate limiting category
        require_auth: Whether authentication is required
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                # 1. Validate content length
                validate_content_length()
                
                # 2. Validate headers
                validate_request_headers()
                
                # 3. Rate limiting
                client_id = get_client_identifier()
                allowed, rate_info = rate_limiter.is_allowed(client_id, endpoint_type)
                
                if not allowed:
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'rate_limit': rate_info
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = str(rate_info['window'])
                    return response
                
                # 4. Authentication check (if required)
                if require_auth:
                    if not hasattr(g, 'current_user') or not g.current_user:
                        return jsonify({'error': 'Authentication required'}), 401
                
                # 5. JSON schema validation
                if schema_name and request.is_json:
                    try:
                        data = request.get_json()
                        if data is None:
                            raise SecurityValidationError("Invalid JSON payload")
                        
                        # Sanitize input
                        sanitized_data = InputSanitizer.sanitize_json_payload(data)
                        
                        # Validate against schema
                        if schema_name in API_SCHEMAS:
                            validate(sanitized_data, API_SCHEMAS[schema_name])
                        
                        # Replace request data with sanitized version
                        request._cached_json = (sanitized_data, sanitized_data)
                        
                    except ValidationError as e:
                        raise SecurityValidationError(f"Invalid input: {e.message}")
                    except json.JSONDecodeError:
                        raise SecurityValidationError("Invalid JSON format")
                
                # Add rate limit headers to response
                response = f(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(rate_info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(max(0, rate_info['limit'] - rate_info['current']))
                    response.headers['X-RateLimit-Reset'] = str(rate_info['reset_time'])
                
                return response
                
            except SecurityValidationError as e:
                logger.warning(f"Security validation failed: {e.message} - Client: {client_id}")
                return jsonify({'error': e.message}), e.status_code
            except Exception as e:
                logger.error(f"Security middleware error: {str(e)} - Client: {client_id}")
                return jsonify({'error': 'Security validation failed'}), 500
        
        return wrapped
    return decorator

def create_api_response(success: bool, message: str, data: Any = None, 
                       status_code: int = 200) -> Tuple[Dict[str, Any], int]:
    """Create standardized API response"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return response, status_code

# PII scrubbing for logs
def scrub_pii(data: Any) -> Any:
    """Remove PII from data for logging"""
    if isinstance(data, dict):
        scrubbed = {}
        for key, value in data.items():
            if key.lower() in ['password', 'token', 'secret', 'key', 'auth']:
                scrubbed[key] = '[REDACTED]'
            elif key.lower() in ['email']:
                if isinstance(value, str) and '@' in value:
                    local, domain = value.split('@', 1)
                    scrubbed[key] = f"{local[:2]}***@{domain}"
                else:
                    scrubbed[key] = '[REDACTED]'
            elif isinstance(value, (dict, list)):
                scrubbed[key] = scrub_pii(value)
            else:
                scrubbed[key] = value
        return scrubbed
    elif isinstance(data, list):
        return [scrub_pii(item) for item in data]
    else:
        return data

def log_security_event(event_type: str, details: Dict[str, Any], user_id: str = None):
    """Log security events with PII scrubbing"""
    scrubbed_details = scrub_pii(details)
    
    log_entry = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'client_id': get_client_identifier(),
        'details': scrubbed_details
    }
    
    logger.info(f"Security Event: {json.dumps(log_entry)}")

# Decorator for securing Flask routes
def secure_route(schema_name: Optional[str] = None, 
                endpoint_type: str = 'default',
                require_auth: bool = False):
    """Simplified decorator for Flask routes"""
    return security_middleware(schema_name, endpoint_type, require_auth)