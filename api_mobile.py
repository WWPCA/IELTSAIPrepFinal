"""
Mobile API endpoints for IELTS GenAI Prep
Provides JWT-based authentication and user management for mobile clients
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash
# Using DynamoDB UserDAL instead of SQLAlchemy models
# from dynamodb_dal import UserDAL  # Import when needed in specific functions
from auth_jwt import generate_jwt_token, jwt_required, create_api_response

# Create API blueprint
api_mobile = Blueprint('api_mobile', __name__, url_prefix='/api/v1')


@api_mobile.route('/auth/login', methods=['POST'])
def mobile_login():
    """
    Mobile login endpoint that returns JWT token
    """
    try:
        data = request.get_json()
        if not data:
            return create_api_response(False, 'Request body must be JSON', status_code=400)
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return create_api_response(False, 'Email and password are required', status_code=400)
        
        # Find user using DynamoDB UserDAL
        from dynamodb_dal import DynamoDBConnection, UserDAL
        from aws_secrets_manager import get_jwt_config
        from datetime import datetime
        import os
        
        region = os.environ.get('AWS_REGION', 'us-east-1')
        db_connection = DynamoDBConnection(region=region)
        user_dal = UserDAL(db_connection)
        
        user = user_dal.get_user_by_email(email)
        
        if not user or not check_password_hash(user['password_hash'], password):
            return create_api_response(False, 'Invalid email or password', status_code=401)
        
        if not user.get('is_active', False):
            return create_api_response(False, 'Account is deactivated', status_code=401)
        
        # Generate JWT token
        token = generate_jwt_token(user['user_id'])
        
        # Update last login
        user_dal.update_user(user['email'], last_login=datetime.utcnow().isoformat())
        
        # Get JWT expiry from config
        jwt_config = get_jwt_config()
        
        # Return token and user info
        user_data = {
            'id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name'),
            'join_date': user.get('join_date'),
            'last_login': datetime.utcnow().isoformat(),
            'has_active_assessment': user.get('assessment_package_status') == 'active'
        }
        
        return create_api_response(True, 'Login successful', {
            'token': token,
            'user': user_data,
            'token_expires_in': jwt_config['ACCESS_TOKEN_EXPIRES_MINUTES'] * 60
        })
        
    except Exception as e:
        current_app.logger.error(f"Mobile login error: {e}")
        return create_api_response(False, 'Login failed', status_code=500)


@api_mobile.route('/auth/register', methods=['POST'])
def mobile_register():
    """
    Mobile registration endpoint
    """
    try:
        data = request.get_json()
        if not data:
            return create_api_response(False, 'Request body must be JSON', status_code=400)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not all([username, email, password]):
            return create_api_response(False, 'Username, email, and password are required', status_code=400)
        
        # Check if user already exists using DynamoDB UserDAL
        from dynamodb_dal import DynamoDBConnection, UserDAL
        from aws_secrets_manager import get_jwt_config
        from datetime import datetime
        import os
        
        region = os.environ.get('AWS_REGION', 'us-east-1')
        db_connection = DynamoDBConnection(region=region)
        user_dal = UserDAL(db_connection)
        
        if user_dal.get_user_by_email(email):
            return create_api_response(False, 'Email already registered', status_code=409)
        
        if user_dal.get_user_by_username(username):
            return create_api_response(False, 'Username already taken', status_code=409)
        
        # Create new user using UserDAL
        new_user = user_dal.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        # Generate JWT token for immediate login
        token = generate_jwt_token(new_user['user_id'])
        
        # Get JWT expiry from config
        jwt_config = get_jwt_config()
        
        user_data = {
            'id': new_user['user_id'],
            'username': new_user['username'],
            'email': new_user['email'],
            'full_name': new_user.get('full_name'),
            'join_date': new_user.get('join_date')
        }
        
        return create_api_response(True, 'Registration successful', {
            'token': token,
            'user': user_data,
            'token_expires_in': jwt_config['ACCESS_TOKEN_EXPIRES_MINUTES'] * 60
        }, 201)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Mobile registration error: {e}")
        return create_api_response(False, 'Registration failed', status_code=500)


@api_mobile.route('/user/profile', methods=['GET'])
@jwt_required
def get_user_profile():
    """
    Get current user profile (requires JWT token)
    """
    try:
        from flask import g
        user = g.current_user
        
        # Get assessment entitlements
        entitlements = AssessmentEntitlement.query.filter_by(user_id=user.id).all()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'bio': user.bio,
            'join_date': user.join_date.isoformat() if user.join_date else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'preferred_language': user.preferred_language,
            'assessment_package_status': user.assessment_package_status,
            'assessment_package_expiry': user.assessment_package_expiry.isoformat() if user.assessment_package_expiry else None,
            'preferences': user.preferences,
            'assessment_entitlements': [
                {
                    'product_id': ent.product_id,
                    'remaining_uses': ent.remaining_uses,
                    'expires_at': ent.expires_at.isoformat() if ent.expires_at else None
                }
                for ent in entitlements
            ]
        }
        
        return create_api_response(True, 'Profile retrieved successfully', user_data)
        
    except Exception as e:
        current_app.logger.error(f"Get profile error: {e}")
        return create_api_response(False, 'Failed to retrieve profile', status_code=500)


@api_mobile.route('/user/profile', methods=['PUT'])
@jwt_required
def update_user_profile():
    """
    Update current user profile (requires JWT token)
    """
    try:
        from flask import g
        user = g.current_user
        data = request.get_json()
        
        if not data:
            return create_api_response(False, 'Request body must be JSON', status_code=400)
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        
        if 'bio' in data:
            user.bio = data['bio'].strip()
        
        if 'preferred_language' in data:
            user.preferred_language = data['preferred_language']
        
        if 'preferences' in data and isinstance(data['preferences'], dict):
            user.preferences = data['preferences']
        
        db.session.commit()
        
        return create_api_response(True, 'Profile updated successfully')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update profile error: {e}")
        return create_api_response(False, 'Failed to update profile', status_code=500)


@api_mobile.route('/health', methods=['GET'])
def api_health():
    """
    API health check endpoint
    """
    return create_api_response(True, 'API is healthy', {
        'version': '1.0',
        'service': 'IELTS GenAI Prep Mobile API'
    })


# Error handlers for the API blueprint
@api_mobile.errorhandler(404)
def api_not_found(error):
    return create_api_response(False, 'Endpoint not found', status_code=404)


@api_mobile.errorhandler(405)
def api_method_not_allowed(error):
    return create_api_response(False, 'Method not allowed', status_code=405)


@api_mobile.errorhandler(500)
def api_internal_error(error):
    return create_api_response(False, 'Internal server error', status_code=500)