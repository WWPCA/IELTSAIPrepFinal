"""
Assessment Access Control API Handlers
"""

import json
import logging
from typing import Dict, Any

from lambda_security import apply_security
from assessment_access_control import get_assessment_controller
from secure_token_storage import secure_storage

logger = logging.getLogger(__name__)

@apply_security(
    rate_limit_per_ip=30,  # Reasonable limit for access checks
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True  # Require authenticated session
)
def handle_get_assessment_access(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Check user's access to specific assessment type
    
    Query parameters:
    ?user_email=user@example.com&assessment_type=academic_speaking&auto_refresh=true
    """
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Get user email from authenticated session instead of query params
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        assessment_type = query_params.get('assessment_type', '').strip().lower()
        auto_refresh = query_params.get('auto_refresh', 'true').lower() == 'true'
        
        if not assessment_type:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'assessment_type parameter required'
                })
            }
        
        # Validate email format
        if '@' not in user_email or '.' not in user_email.split('@')[1]:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid email format'
                })
            }
        
        logger.info(f"Checking assessment access for {user_email} - {assessment_type}")
        
        # Check access
        controller = get_assessment_controller()
        access_result = controller.check_assessment_access(user_email, assessment_type, auto_refresh)
        
        if access_result['has_access']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Access granted',
                    'data': access_result
                })
            }
        else:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'message': 'Access denied',
                    'data': access_result
                })
            }
    
    except Exception as e:
        logger.error(f"Assessment access check error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=20,  # Lower limit for comprehensive overviews
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True  # Require authenticated session
)
def handle_get_assessment_overview(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get comprehensive assessment access overview for user
    
    Query parameters:
    ?user_email=user@example.com
    """
    try:
        # Get user email from authenticated session instead of query params
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        # Validate email format
        if '@' not in user_email or '.' not in user_email.split('@')[1]:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid email format'
                })
            }
        
        logger.info(f"Getting assessment overview for {user_email}")
        
        # Get overview
        controller = get_assessment_controller()
        overview_result = controller.get_user_assessment_overview(user_email)
        
        if overview_result.get('success'):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'data': overview_result
                })
            }
        else:
            return {
                'statusCode': 404 if 'not found' in overview_result.get('error', '').lower() else 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': overview_result.get('error', 'Failed to get assessment overview')
                })
            }
    
    except Exception as e:
        logger.error(f"Assessment overview error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=10,  # Lower limit for attempt usage
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True  # Require authenticated session
)
def handle_use_assessment_attempt(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Use an assessment attempt for the user
    
    Expected payload:
    {
        "user_email": "user@example.com",
        "assessment_type": "academic_speaking"
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Get user email from authenticated session instead of request body
        session_data = event.get('session_data', {})
        user_email = session_data.get('user_email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Authentication required'
                })
            }
        
        assessment_type = body.get('assessment_type', '').strip().lower()
        
        # Validate required fields
        if not assessment_type:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required field: assessment_type'
                })
            }
        
        # Validate email format
        if '@' not in user_email or '.' not in user_email.split('@')[1]:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid email format'
                })
            }
        
        logger.info(f"Using assessment attempt for {user_email} - {assessment_type}")
        
        # Use attempt
        controller = get_assessment_controller()
        result = controller.use_assessment_attempt(user_email, assessment_type)
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Assessment attempt used',
                    'data': result
                })
            }
        else:
            return {
                'statusCode': 403 if 'access' in result.get('error', '').lower() else 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Failed to use assessment attempt')
                })
            }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Invalid JSON payload'
            })
        }
    
    except Exception as e:
        logger.error(f"Use assessment attempt error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

# Export handlers
__all__ = [
    'handle_get_assessment_access',
    'handle_get_assessment_overview', 
    'handle_use_assessment_attempt'
]