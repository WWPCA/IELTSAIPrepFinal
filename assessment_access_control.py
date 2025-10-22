"""
Assessment Access Control Middleware
Checks payment status before allowing assessment access
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps

from payment_sync_service import get_payment_sync_service, PurchaseProductType
from dynamodb_dal import get_dal

logger = logging.getLogger(__name__)

class AssessmentAccessController:
    """Controls access to assessments based on payment verification"""
    
    def __init__(self):
        self.dal = get_dal()
        self.payment_service = get_payment_sync_service()
        
        # Assessment type mapping
        self.assessment_types = {
            'academic_speaking': PurchaseProductType.ACADEMIC_SPEAKING,
            'academic_writing': PurchaseProductType.ACADEMIC_WRITING,
            'general_speaking': PurchaseProductType.GENERAL_SPEAKING,
            'general_writing': PurchaseProductType.GENERAL_WRITING
        }
    
    def check_assessment_access(self, user_email: str, assessment_type: str, 
                               auto_refresh: bool = True) -> Dict[str, Any]:
        """
        Check if user has valid access to specific assessment type
        
        Args:
            user_email: User's email address
            assessment_type: Assessment type (academic_speaking, etc.)
            auto_refresh: Automatically refresh purchase status if no access found
            
        Returns:
            Dict with access status and details
        """
        try:
            # Validate assessment type
            if assessment_type not in self.assessment_types:
                return {
                    'has_access': False,
                    'error': 'Invalid assessment type',
                    'valid_types': list(self.assessment_types.keys())
                }
            
            # Get user from database
            user = self.dal.get_user_by_email(user_email)
            if not user:
                return {
                    'has_access': False,
                    'error': 'User not found',
                    'user_email': user_email
                }
            
            # Check direct assessment access
            has_access = self.dal.has_assessment_access(user_email, assessment_type)
            attempts_remaining = self._get_remaining_attempts(user_email, assessment_type)
            
            # If user has access and attempts, allow access
            if has_access and attempts_remaining > 0:
                return {
                    'has_access': True,
                    'assessment_type': assessment_type,
                    'attempts_remaining': attempts_remaining,
                    'access_source': 'direct_purchase',
                    'user_email': user_email
                }
            
            # Check for assessment package access
            package_status = user.get('assessment_package_status', 'none')
            package_expiry = user.get('assessment_package_expiry')
            
            if package_status == 'active':
                # Check if package hasn't expired
                if package_expiry:
                    expiry_date = datetime.fromisoformat(package_expiry.replace('Z', '+00:00'))
                    if datetime.utcnow() > expiry_date:
                        # Package expired - update status
                        self.dal.update_user(user_email, assessment_package_status='expired')
                        return {
                            'has_access': False,
                            'error': 'Assessment package expired',
                            'expired_date': expiry_date.isoformat(),
                            'user_email': user_email
                        }
                
                # Package is active - check attempts
                package_attempts = self._get_package_attempts(user_email, assessment_type)
                if package_attempts > 0:
                    return {
                        'has_access': True,
                        'assessment_type': assessment_type,
                        'attempts_remaining': package_attempts,
                        'access_source': 'assessment_package',
                        'package_expiry': package_expiry,
                        'user_email': user_email
                    }
            
            # If no access found and auto_refresh enabled, try refreshing purchase status
            if auto_refresh and not has_access:
                logger.info(f"No access found for {user_email}, refreshing purchase status")
                refresh_result = self.payment_service.refresh_user_purchase_status(user_email)
                
                if refresh_result.get('success'):
                    # Re-check access after refresh
                    return self.check_assessment_access(user_email, assessment_type, auto_refresh=False)
            
            # No access found
            return {
                'has_access': False,
                'error': 'No valid purchase found for this assessment',
                'assessment_type': assessment_type,
                'user_email': user_email,
                'suggestions': [
                    'Purchase this assessment in the mobile app',
                    'Check if you have an active assessment package',
                    'Contact support if you believe this is an error'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error checking assessment access for {user_email}: {e}")
            return {
                'has_access': False,
                'error': 'Internal error checking access',
                'details': str(e)
            }
    
    def use_assessment_attempt(self, user_email: str, assessment_type: str) -> Dict[str, Any]:
        """
        Use one assessment attempt for the user
        
        Args:
            user_email: User's email address
            assessment_type: Assessment type being used
            
        Returns:
            Dict with success status and remaining attempts
        """
        try:
            # First check if user has access
            access_check = self.check_assessment_access(user_email, assessment_type)
            if not access_check['has_access']:
                return {
                    'success': False,
                    'error': 'No access to this assessment',
                    'details': access_check
                }
            
            # Use the attempt
            success = self.dal.use_assessment_attempt(user_email, assessment_type)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to use assessment attempt'
                }
            
            # Get updated attempt count
            new_attempts = self._get_remaining_attempts(user_email, assessment_type)
            
            logger.info(f"Assessment attempt used for {user_email} - {assessment_type}, {new_attempts} remaining")
            
            return {
                'success': True,
                'assessment_type': assessment_type,
                'attempts_remaining': new_attempts,
                'user_email': user_email
            }
            
        except Exception as e:
            logger.error(f"Error using assessment attempt for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Internal error using attempt'
            }
    
    def get_user_assessment_overview(self, user_email: str) -> Dict[str, Any]:
        """
        Get comprehensive assessment access overview for user
        
        Args:
            user_email: User's email address
            
        Returns:
            Dict with complete access information
        """
        try:
            # Get payment status
            payment_status = self.payment_service.get_user_purchase_status(user_email)
            if not payment_status.get('success'):
                return payment_status
            
            # Get access for each assessment type
            assessment_access = {}
            total_attempts = 0
            
            for assessment_type in self.assessment_types.keys():
                access_info = self.check_assessment_access(user_email, assessment_type, auto_refresh=False)
                assessment_access[assessment_type] = access_info
                
                if access_info.get('has_access'):
                    total_attempts += access_info.get('attempts_remaining', 0)
            
            # Get purchase summary
            user = self.dal.get_user_by_email(user_email)
            purchases = user.get('purchases', []) if user else []
            active_purchases = [p for p in purchases if p.get('is_active', True)]
            
            return {
                'success': True,
                'user_email': user_email,
                'total_attempts_remaining': total_attempts,
                'assessment_access': assessment_access,
                'purchase_summary': {
                    'total_purchases': len(purchases),
                    'active_purchases': len(active_purchases),
                    'assessment_package_status': user.get('assessment_package_status', 'none') if user else 'none',
                    'last_purchase_date': max([p.get('purchase_date', '') for p in purchases]) if purchases else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment overview for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to get assessment overview'
            }
    
    def _get_remaining_attempts(self, user_email: str, assessment_type: str) -> int:
        """Get remaining attempts for specific assessment type"""
        try:
            counts = self.dal.get_user_assessment_counts(user_email)
            assessment_data = counts.get(assessment_type, {})
            return assessment_data.get('attempts_remaining', 0)
        except Exception:
            return 0
    
    def _get_package_attempts(self, user_email: str, assessment_type: str) -> int:
        """Get attempts available from assessment package"""
        try:
            # Assessment package gives 1 attempt per assessment type
            user = self.dal.get_user_by_email(user_email)
            if not user:
                return 0
            
            purchases = user.get('purchases', [])
            for purchase in purchases:
                if (purchase.get('product_type') == 'assessment_package' 
                    and purchase.get('is_active', True)):
                    
                    # Check if this assessment type has been used
                    assessments = purchase.get('assessments', {})
                    assessment_info = assessments.get(assessment_type, {})
                    return assessment_info.get('attempts_remaining', 1)
            
            return 0
        except Exception:
            return 0

def require_assessment_access(assessment_type_param: str = 'assessment_type'):
    """
    Decorator to require valid assessment access before executing function
    
    Args:
        assessment_type_param: Name of parameter containing assessment type
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # Extract user email and assessment type from event
                body = json.loads(event.get('body', '{}'))
                query_params = event.get('queryStringParameters', {}) or {}
                path_params = event.get('pathParameters', {}) or {}
                
                # Get user email (multiple sources)
                user_email = (body.get('user_email') or 
                             query_params.get('user_email') or 
                             path_params.get('user_email') or
                             '').strip().lower()
                
                # Get assessment type (multiple sources)
                assessment_type = (body.get(assessment_type_param) or 
                                 query_params.get(assessment_type_param) or 
                                 path_params.get(assessment_type_param) or
                                 '').strip().lower()
                
                # Extract from path if needed (e.g., /api/assessment/academic_speaking)
                if not assessment_type:
                    path = event.get('path', '')
                    path_parts = path.split('/')
                    if len(path_parts) >= 3 and 'assessment' in path_parts:
                        assessment_idx = path_parts.index('assessment')
                        if assessment_idx + 1 < len(path_parts):
                            assessment_type = path_parts[assessment_idx + 1]
                
                # Validate required parameters
                if not user_email:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': False,
                            'error': 'user_email is required'
                        })
                    }
                
                if not assessment_type:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': False,
                            'error': f'{assessment_type_param} is required'
                        })
                    }
                
                # Check access
                controller = AssessmentAccessController()
                access_check = controller.check_assessment_access(user_email, assessment_type)
                
                if not access_check['has_access']:
                    return {
                        'statusCode': 403,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({
                            'success': False,
                            'error': 'Access denied - no valid purchase found',
                            'details': access_check,
                            'user_email': user_email,
                            'assessment_type': assessment_type
                        })
                    }
                
                # Add access info to event for function to use
                event['assessment_access'] = access_check
                
                # Call original function
                return func(event, context)
                
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': False,
                        'error': 'Invalid JSON in request body'
                    })
                }
            except Exception as e:
                logger.error(f"Assessment access check error: {e}")
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': False,
                        'error': 'Internal error checking assessment access'
                    })
                }
        
        return wrapper
    return decorator

# Global controller instance
assessment_controller = AssessmentAccessController()

def get_assessment_controller() -> AssessmentAccessController:
    """Get global assessment access controller instance"""
    return assessment_controller

# Export
__all__ = [
    'AssessmentAccessController', 
    'require_assessment_access', 
    'get_assessment_controller'
]