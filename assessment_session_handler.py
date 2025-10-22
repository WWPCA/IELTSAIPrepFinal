"""
Assessment Session Handler
Manages assessment sessions with question selection and tracking
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from lambda_security import apply_security
from assessment_access_control import get_assessment_controller
from question_bank_dal import get_question_bank_dal

logger = logging.getLogger(__name__)

@apply_security(
    rate_limit_per_ip=10,  # Reasonable limit for session starts
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_start_assessment_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Start new assessment session with question selection
    
    Expected payload:
    {
        "assessment_type": "academic_speaking",
        "purchase_id": "purchase_123"
    }
    """
    try:
        # Get user email from authenticated session
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
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        assessment_type = body.get('assessment_type', '').strip().lower()
        purchase_id = body.get('purchase_id', '').strip()
        
        # Validate required fields
        if not assessment_type:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'assessment_type is required'
                })
            }
        
        # Verify user has access to this assessment
        access_controller = get_assessment_controller()
        access_check = access_controller.check_assessment_access(user_email, assessment_type)
        
        if not access_check['has_access']:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Access denied - no valid purchase found',
                    'details': access_check
                })
            }
        
        # Use attempt (this consumes one attempt)
        attempt_result = access_controller.use_assessment_attempt(user_email, assessment_type)
        
        if not attempt_result['success']:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Failed to use assessment attempt',
                    'details': attempt_result
                })
            }
        
        # Generate purchase_id if not provided (link to attempt)
        if not purchase_id:
            purchase_id = f"attempt_{user_email}_{assessment_type}_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"Starting assessment session for {user_email} - {assessment_type}")
        
        # Start assessment session with question selection
        question_dal = get_question_bank_dal()
        session_result = question_dal.start_assessment_session(
            user_email=user_email,
            assessment_type=assessment_type,
            purchase_id=purchase_id
        )
        
        if session_result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Assessment session started successfully',
                    'data': session_result,
                    'attempts_remaining': attempt_result.get('attempts_remaining', 0)
                })
            }
        else:
            # If session failed, we should potentially restore the attempt
            # For now, log the issue - in production you might implement compensation
            logger.error(f"Session start failed after using attempt: {session_result}")
            
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': session_result.get('error', 'Failed to start assessment session'),
                    'details': session_result
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
        logger.error(f"Start assessment session error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=20,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_complete_assessment_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Complete assessment session
    
    Expected payload:
    {
        "session_id": "session_123456"
    }
    """
    try:
        # Get user email from authenticated session
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
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        session_id = body.get('session_id', '').strip()
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'session_id is required'
                })
            }
        
        # Complete the session
        question_dal = get_question_bank_dal()
        result = question_dal.complete_assessment_session(session_id, user_email)
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Assessment session completed successfully'
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Failed to complete session')
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
        logger.error(f"Complete assessment session error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=30,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_get_assessment_session(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get assessment session details
    
    Query parameters:
    ?session_id=session_123456
    """
    try:
        # Get user email from authenticated session
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
        
        query_params = event.get('queryStringParameters', {}) or {}
        session_id = query_params.get('session_id', '').strip()
        
        if not session_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'session_id parameter required'
                })
            }
        
        # Get session details
        question_dal = get_question_bank_dal()
        result = question_dal.get_assessment_session(session_id)
        
        if result['success']:
            # Verify session belongs to authenticated user
            session = result['session']
            if session.get('user_email') != user_email:
                return {
                    'statusCode': 403,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': False,
                        'error': 'Access denied - session belongs to different user'
                    })
                }
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'data': result
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Session not found')
                })
            }
    
    except Exception as e:
        logger.error(f"Get assessment session error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=20,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_get_user_question_stats(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user's question usage statistics
    
    Query parameters:
    ?assessment_type=academic_speaking
    """
    try:
        # Get user email from authenticated session
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
        
        query_params = event.get('queryStringParameters', {}) or {}
        assessment_type = query_params.get('assessment_type', '').strip().lower()
        
        if not assessment_type:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'assessment_type parameter required'
                })
            }
        
        # Get question statistics
        question_dal = get_question_bank_dal()
        result = question_dal.get_user_question_stats(user_email, assessment_type)
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'data': result
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Failed to get question statistics')
                })
            }
    
    except Exception as e:
        logger.error(f"Get user question stats error: {e}")
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
    'handle_start_assessment_session',
    'handle_complete_assessment_session',
    'handle_get_assessment_session',
    'handle_get_user_question_stats'
]