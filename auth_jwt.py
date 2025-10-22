"""
JWT Authentication utilities for IELTS GenAI Prep
Provides JWT token generation and verification for mobile API clients
Integrates with unified User model and AWS Secrets Manager
"""
import json
import datetime
import jwt
from functools import wraps
from flask import current_app, request, jsonify, g
# Using DynamoDB UserDAL instead of SQLAlchemy models
# from dynamodb_dal import UserDAL  # Import when needed in specific functions
from aws_secrets_manager import get_jwt_config
import logging

logger = logging.getLogger(__name__)


def generate_jwt_token(user_id):
    """
    Generate a JWT token for the given user ID using AWS Secrets Manager
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: JWT token
    """
    try:
        jwt_config = get_jwt_config()
        
        payload = {
            'user_id': user_id,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(
                minutes=jwt_config['ACCESS_TOKEN_EXPIRES_MINUTES']
            ),
            'iss': 'ielts-genai-prep',  # Issuer
            'aud': 'mobile-app'  # Audience
        }
        
        token = jwt.encode(
            payload, 
            jwt_config['SECRET_KEY'], 
            jwt_config['ALGORITHM']
        )
        return token
        
    except Exception as e:
        logger.error(f"Failed to generate JWT token: {e}")
        raise RuntimeError("Token generation failed")


def verify_jwt_token(token):
    """
    Verify a JWT token using AWS Secrets Manager configuration
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Token payload if valid, None otherwise
    """
    try:
        jwt_config = get_jwt_config()
        
        payload = jwt.decode(
            token, 
            jwt_config['SECRET_KEY'], 
            algorithms=[jwt_config['ALGORITHM']],
            audience='mobile-app',
            issuer='ielts-genai-prep'
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid JWT token")
        return None
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        return None


def jwt_required(f):
    """
    Decorator for API endpoints that require a valid JWT token
    Provides mobile authentication without sessions
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user info to request context (using g for proper Flask request context)
        from flask import g
        g.user_id = payload['user_id']
        
        # Load user object for convenience using DynamoDB UserDAL
        try:
            from dynamodb_dal import DynamoDBConnection, UserDAL
            from flask import current_app
            import os
            
            region = os.environ.get('AWS_REGION', 'us-east-1')
            db_connection = DynamoDBConnection(region=region)
            user_dal = UserDAL(db_connection)
            
            g.current_user = user_dal.get_user_by_id(payload['user_id'])
            if not g.current_user or not g.current_user.get('is_active', False):
                return jsonify({'error': 'User account is inactive'}), 401
        except Exception as e:
            logger.error(f"Failed to load user {payload['user_id']}: {e}")
            return jsonify({'error': 'User not found'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def create_api_response(success=True, message=None, data=None, status_code=200):
    """
    Standardized API response format for mobile clients
    
    Args:
        success: Boolean indicating if request was successful
        message: Optional message
        data: Response data
        status_code: HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    response = {
        'success': success,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    if message:
        response['message'] = message
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code