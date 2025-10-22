"""
Repurchase Handler for IELTS GenAI Prep Platform
Handles scenarios where users want to repurchase products they've already bought
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from lambda_security import apply_security
from payment_sync_service import get_payment_sync_service
from assessment_access_control import get_assessment_controller
from dynamodb_dal import get_dal

logger = logging.getLogger(__name__)

class RepurchaseService:
    """Service for handling product repurchases and attempt additions"""
    
    def __init__(self):
        self.dal = get_dal()
        self.payment_service = get_payment_sync_service()
        self.assessment_controller = get_assessment_controller()
    
    def can_repurchase(self, user_email: str, product_id: str) -> Dict[str, Any]:
        """
        Check if user can repurchase a specific product
        
        Returns:
            Dict with repurchase eligibility and reasoning
        """
        try:
            user = self.dal.get_user_by_email(user_email)
            if not user:
                return {
                    'can_repurchase': True,
                    'reason': 'new_user',
                    'message': 'User has not purchased this product before'
                }
            
            # Get existing purchases for this product
            purchases = user.get('purchases', [])
            product_purchases = [p for p in purchases if p.get('product_id') == product_id]
            
            if not product_purchases:
                return {
                    'can_repurchase': True,
                    'reason': 'new_product',
                    'message': 'User has not purchased this product before'
                }
            
            # Find latest active purchase for this product
            active_purchases = [p for p in product_purchases if p.get('is_active', True)]
            if not active_purchases:
                return {
                    'can_repurchase': True,
                    'reason': 'expired_purchases',
                    'message': 'All previous purchases are inactive/expired'
                }
            
            # Sort by purchase date to get latest
            latest_purchase = sorted(active_purchases, key=lambda x: x.get('purchase_date', ''), reverse=True)[0]
            attempts_remaining = latest_purchase.get('attempts_remaining', 0)
            
            if attempts_remaining == 0:
                return {
                    'can_repurchase': True,
                    'reason': 'no_attempts_remaining',
                    'message': 'All attempts have been used for this product',
                    'last_purchase_date': latest_purchase.get('purchase_date'),
                    'total_previous_purchases': len(product_purchases)
                }
            
            # User has remaining attempts - they can still repurchase for additional attempts
            return {
                'can_repurchase': True,
                'reason': 'additional_attempts',
                'message': f'Can purchase additional attempts (currently has {attempts_remaining} remaining)',
                'current_attempts': attempts_remaining,
                'last_purchase_date': latest_purchase.get('purchase_date'),
                'total_previous_purchases': len(product_purchases)
            }
            
        except Exception as e:
            logger.error(f"Error checking repurchase eligibility for {user_email}, {product_id}: {e}")
            return {
                'can_repurchase': False,
                'reason': 'error',
                'message': 'Unable to check repurchase eligibility'
            }
    
    def process_repurchase(self, user_email: str, platform: str, receipt_data: str, 
                          product_id: str, force_allow: bool = False) -> Dict[str, Any]:
        """
        Process a repurchase request
        
        Args:
            user_email: User's email address
            platform: 'apple' or 'google'  
            receipt_data: Receipt data from app store
            product_id: Product being repurchased
            force_allow: Allow repurchase even if not typically allowed
            
        Returns:
            Dict with repurchase result
        """
        try:
            # Check repurchase eligibility first
            eligibility = self.can_repurchase(user_email, product_id)
            
            if not eligibility['can_repurchase'] and not force_allow:
                return {
                    'success': False,
                    'error': 'Repurchase not allowed',
                    'details': eligibility
                }
            
            # Process the purchase using existing payment service
            # but with special repurchase handling
            result = self.payment_service.confirm_purchase_and_sync_user(
                user_email=user_email,
                platform=platform,
                receipt_data=receipt_data,
                product_id=product_id,
                allow_duplicate=True  # Key difference - allow duplicate transactions
            )
            
            if result['success']:
                # Log the repurchase
                repurchase_data = {
                    'user_email': user_email,
                    'product_id': product_id,
                    'platform': platform,
                    'repurchase_reason': eligibility.get('reason', 'unknown'),
                    'previous_purchases': eligibility.get('total_previous_purchases', 0),
                    'repurchase_date': datetime.utcnow().isoformat()
                }
                
                logger.info(f"Repurchase successful: {repurchase_data}")
                
                # Add repurchase info to result
                result['repurchase_info'] = {
                    'is_repurchase': True,
                    'reason': eligibility.get('reason'),
                    'previous_purchases': eligibility.get('total_previous_purchases', 0),
                    'message': eligibility.get('message')
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Repurchase processing error for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to process repurchase',
                'details': str(e)
            }
    
    def get_repurchase_history(self, user_email: str) -> Dict[str, Any]:
        """Get user's repurchase history"""
        try:
            user = self.dal.get_user_by_email(user_email)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            purchases = user.get('purchases', [])
            
            # Group purchases by product_id to identify repurchases
            product_groups = {}
            for purchase in purchases:
                product_id = purchase.get('product_id')
                if product_id not in product_groups:
                    product_groups[product_id] = []
                product_groups[product_id].append(purchase)
            
            # Identify repurchases (products with multiple purchases)
            repurchases = {}
            for product_id, product_purchases in product_groups.items():
                if len(product_purchases) > 1:
                    # Sort by purchase date
                    sorted_purchases = sorted(product_purchases, key=lambda x: x.get('purchase_date', ''))
                    
                    repurchases[product_id] = {
                        'product_type': sorted_purchases[0].get('product_type'),
                        'total_purchases': len(sorted_purchases),
                        'first_purchase': sorted_purchases[0].get('purchase_date'),
                        'last_purchase': sorted_purchases[-1].get('purchase_date'),
                        'total_attempts_purchased': sum(p.get('total_attempts', 0) for p in sorted_purchases),
                        'remaining_attempts': sum(p.get('attempts_remaining', 0) for p in sorted_purchases if p.get('is_active')),
                        'purchase_history': sorted_purchases
                    }
            
            return {
                'success': True,
                'user_email': user_email,
                'repurchased_products': len(repurchases),
                'repurchase_details': repurchases,
                'total_unique_products': len(product_groups),
                'total_purchases': len(purchases)
            }
            
        except Exception as e:
            logger.error(f"Error getting repurchase history for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to get repurchase history'
            }

@apply_security(
    rate_limit_per_ip=20,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_check_repurchase_eligibility(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Check if user can repurchase a specific product
    
    Query parameters:
    ?product_id=com.ielts.academic_speaking
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
        product_id = query_params.get('product_id', '').strip()
        
        if not product_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'product_id parameter required'
                })
            }
        
        # Check repurchase eligibility
        repurchase_service = RepurchaseService()
        eligibility = repurchase_service.can_repurchase(user_email, product_id)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'user_email': user_email,
                'product_id': product_id,
                'eligibility': eligibility
            })
        }
        
    except Exception as e:
        logger.error(f"Check repurchase eligibility error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=10,
    rate_limit_window=300,
    require_recaptcha=True,  # Higher security for actual purchases
    validate_input=True,
    require_auth=True
)
def handle_process_repurchase(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process a repurchase request
    
    Expected payload:
    {
        "platform": "apple",
        "receipt_data": "base64_encoded_receipt",
        "product_id": "com.ielts.academic_speaking", 
        "force_allow": false
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
        
        platform = body.get('platform', '').strip().lower()
        receipt_data = body.get('receipt_data', '').strip()
        product_id = body.get('product_id', '').strip()
        force_allow = body.get('force_allow', False)
        
        # Validate required fields
        required_fields = ['platform', 'receipt_data', 'product_id']
        missing_fields = [field for field in required_fields if not body.get(field)]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                })
            }
        
        # Validate platform
        if platform not in ['apple', 'google']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid platform. Must be "apple" or "google"'
                })
            }
        
        logger.info(f"Processing repurchase for {user_email} - {product_id} on {platform}")
        
        # Process repurchase
        repurchase_service = RepurchaseService()
        result = repurchase_service.process_repurchase(
            user_email=user_email,
            platform=platform,
            receipt_data=receipt_data,
            product_id=product_id,
            force_allow=force_allow
        )
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Repurchase processed successfully',
                    'data': result
                })
            }
        else:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Repurchase failed'),
                    'details': result
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
        logger.error(f"Process repurchase error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=15,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True,
    require_auth=True
)
def handle_get_repurchase_history(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Get user's repurchase history"""
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
        
        # Get repurchase history
        repurchase_service = RepurchaseService()
        history = repurchase_service.get_repurchase_history(user_email)
        
        if history['success']:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'data': history
                })
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': history.get('error', 'Failed to get repurchase history')
                })
            }
        
    except Exception as e:
        logger.error(f"Get repurchase history error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

# Export handlers and service
__all__ = [
    'RepurchaseService',
    'handle_check_repurchase_eligibility',
    'handle_process_repurchase', 
    'handle_get_repurchase_history'
]