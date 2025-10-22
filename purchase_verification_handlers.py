"""
Purchase Verification API Handlers
Handles receipt validation and user access synchronization endpoints
"""

import json
import logging
from typing import Dict, Any

from lambda_security import apply_security
from payment_sync_service import get_payment_sync_service, PaymentPlatform

logger = logging.getLogger(__name__)

@apply_security(
    rate_limit_per_ip=10,  # 10 requests per window
    rate_limit_window=300,  # 5 minutes
    require_recaptcha=False,  # Mobile apps don't use reCAPTCHA
    validate_input=True
)
def handle_verify_purchase(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Verify app store purchase and sync user access
    
    Expected payload:
    {
        "user_email": "user@example.com",
        "platform": "apple" | "google",
        "receipt_data": "base64_encoded_receipt",
        "device_id": "optional_device_identifier"
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        user_email = body.get('user_email', '').strip().lower()
        platform = body.get('platform', '').strip().lower()
        receipt_data = body.get('receipt_data', '').strip()
        device_id = body.get('device_id', '').strip()
        
        # Validate required fields
        if not user_email or not platform or not receipt_data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required fields',
                    'required_fields': ['user_email', 'platform', 'receipt_data']
                })
            }
        
        # Validate platform
        if platform not in ['apple', 'google']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid platform',
                    'valid_platforms': ['apple', 'google']
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
        
        logger.info(f"Processing purchase verification for {user_email} on {platform}")
        
        # Get payment sync service
        payment_service = get_payment_sync_service()
        
        # Confirm purchase and sync user
        result = payment_service.confirm_purchase_and_sync_user(
            user_email=user_email,
            platform=platform,
            receipt_data=receipt_data,
            device_id=device_id
        )
        
        if result['success']:
            logger.info(f"Purchase verified successfully for {user_email}")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': 'Purchase verified and access granted',
                    'data': {
                        'user_email': result['user_email'],
                        'product_type': result['product_type'],
                        'platform': result['platform'],
                        'transaction_id': result['transaction_id'],
                        'attempts_remaining': result['attempts_remaining'],
                        'purchase_date': result['purchase_date'],
                        'access_granted': result['access_granted']
                    }
                })
            }
        else:
            logger.warning(f"Purchase verification failed for {user_email}: {result.get('error')}")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Purchase verification failed'),
                    'details': result.get('details')
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
        logger.error(f"Purchase verification handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=20,  # Higher limit for status checks
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True
)
def handle_get_purchase_status(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Get user's purchase status and assessment access
    
    Query parameters:
    ?user_email=user@example.com&refresh=true|false
    """
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        
        user_email = query_params.get('user_email', '').strip().lower()
        refresh = query_params.get('refresh', 'false').lower() == 'true'
        
        # Validate email
        if not user_email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'user_email parameter required'
                })
            }
        
        if '@' not in user_email or '.' not in user_email.split('@')[1]:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'Invalid email format'
                })
            }
        
        logger.info(f"Getting purchase status for {user_email} (refresh={refresh})")
        
        # Get payment sync service
        payment_service = get_payment_sync_service()
        
        # Get or refresh purchase status
        if refresh:
            result = payment_service.refresh_user_purchase_status(user_email)
        else:
            result = payment_service.get_user_purchase_status(user_email)
        
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
                'statusCode': 404 if 'not found' in result.get('error', '').lower() else 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': result.get('error', 'Failed to get purchase status')
                })
            }
    
    except Exception as e:
        logger.error(f"Purchase status handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

@apply_security(
    rate_limit_per_ip=5,  # Lower limit for sync operations
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=True
)
def handle_sync_user_purchases(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Sync all purchases for a user from both app stores
    
    Expected payload:
    {
        "user_email": "user@example.com",
        "apple_receipts": ["receipt1", "receipt2"],
        "google_receipts": ["receipt1", "receipt2"]
    }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        user_email = body.get('user_email', '').strip().lower()
        apple_receipts = body.get('apple_receipts', [])
        google_receipts = body.get('google_receipts', [])
        
        # Validate required fields
        if not user_email:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'user_email is required'
                })
            }
        
        if not apple_receipts and not google_receipts:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'At least one receipt required'
                })
            }
        
        logger.info(f"Syncing purchases for {user_email}: {len(apple_receipts)} Apple, {len(google_receipts)} Google")
        
        payment_service = get_payment_sync_service()
        sync_results = {
            'apple': [],
            'google': [],
            'total_success': 0,
            'total_failed': 0
        }
        
        # Process Apple receipts
        for receipt in apple_receipts:
            if receipt.strip():
                result = payment_service.confirm_purchase_and_sync_user(
                    user_email=user_email,
                    platform='apple',
                    receipt_data=receipt.strip()
                )
                sync_results['apple'].append(result)
                if result['success']:
                    sync_results['total_success'] += 1
                else:
                    sync_results['total_failed'] += 1
        
        # Process Google receipts
        for receipt in google_receipts:
            if receipt.strip():
                result = payment_service.confirm_purchase_and_sync_user(
                    user_email=user_email,
                    platform='google',
                    receipt_data=receipt.strip()
                )
                sync_results['google'].append(result)
                if result['success']:
                    sync_results['total_success'] += 1
                else:
                    sync_results['total_failed'] += 1
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': f"Processed {sync_results['total_success'] + sync_results['total_failed']} receipts",
                'data': {
                    'user_email': user_email,
                    'successful_syncs': sync_results['total_success'],
                    'failed_syncs': sync_results['total_failed'],
                    'results': sync_results
                }
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
        logger.error(f"Purchase sync handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }

# Export handlers
__all__ = ['handle_verify_purchase', 'handle_get_purchase_status', 'handle_sync_user_purchases']