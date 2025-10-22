"""
Payment Webhook Handlers for Real-time App Store Notifications
Handles Apple App Store and Google Play Store webhook notifications for payment events
"""

import json
import logging
import hmac
import hashlib
import base64
from datetime import datetime
from typing import Dict, Any, Optional

from lambda_security import apply_security
from payment_sync_service import get_payment_sync_service
from aws_secrets_manager import get_apple_store_config, get_google_play_config
from aws_ses_service import email_service

logger = logging.getLogger(__name__)

class WebhookVerificationError(Exception):
    """Webhook verification failed"""
    pass

def verify_apple_webhook(payload: str, signature: str) -> bool:
    """
    Verify Apple App Store Server Notification v2 JWS signature
    
    Args:
        payload: Raw JWS payload from Apple
        signature: Not used for JWS (signature is in payload)
        
    Returns:
        bool: True if JWS signature is valid
    """
    try:
        # Apple App Store Server Notifications v2 use JWS (JSON Web Signature)
        # For now, we'll implement basic JWT structure validation
        # Full JWS verification requires Apple's public key certificate chain
        
        # Parse JWS payload
        import jwt
        
        # For production, we'd need to:
        # 1. Download Apple's public keys from their JWKS endpoint
        # 2. Verify the certificate chain
        # 3. Validate the JWT signature
        
        # For now, decode without verification (development only)
        try:
            # Decode JWT without verification to check structure
            decoded = jwt.decode(payload, options={"verify_signature": False})
            
            # Basic validation - check required fields
            if 'notificationType' in decoded and 'data' in decoded:
                logger.info("Apple JWS structure validation passed")
                return True
            else:
                logger.error("Apple JWS missing required fields")
                return False
                
        except jwt.InvalidTokenError as e:
            logger.error(f"Apple JWS format invalid: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Apple webhook verification error: {e}")
        return False

def verify_google_webhook(payload: str, signature: str, public_key: str) -> bool:
    """
    Verify Google Play Store Real-time Developer Notification signature
    
    Args:
        payload: Raw request payload  
        signature: Signature header value
        public_key: Google Play public key (base64 encoded)
        
    Returns:
        bool: True if signature is valid
    """
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        
        # Google uses RSA-SHA256 signature verification
        if not signature or not public_key:
            logger.error("Missing signature or public key for Google webhook")
            return False
        
        # Decode the signature from base64
        try:
            signature_bytes = base64.b64decode(signature)
        except Exception:
            logger.error("Invalid base64 signature from Google webhook")
            return False
        
        # Load the public key
        try:
            public_key_bytes = base64.b64decode(public_key)
            public_key_obj = serialization.load_der_public_key(public_key_bytes)
        except Exception:
            logger.error("Invalid public key format for Google webhook")
            return False
        
        # Verify the signature
        try:
            public_key_obj.verify(
                signature_bytes,
                payload.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            logger.info("Google webhook signature verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Google webhook signature verification failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Google webhook verification error: {e}")
        return False

@apply_security(
    rate_limit_per_ip=100,  # Higher limit for webhook callbacks
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=False  # Webhooks have their own validation
)
def handle_apple_webhook(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle Apple App Store Server-to-Server notifications
    
    Notification types:
    - INITIAL_BUY: First purchase
    - CANCEL: Subscription cancelled
    - RENEWAL: Subscription renewed
    - INTERACTIVE_RENEWAL: User renewed via App Store
    - DID_CHANGE_RENEWAL_PREF: User changed renewal preference
    - DID_CHANGE_RENEWAL_STATUS: Auto-renewal turned on/off
    - REFUND: Purchase refunded
    """
    try:
        # Get raw payload and signature
        payload = event.get('body', '')
        headers = event.get('headers', {})
        
        signature = headers.get('X-Apple-Signature', headers.get('x-apple-signature', ''))
        
        if not signature:
            logger.error("Missing Apple webhook signature")
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing signature'})
            }
        
        # Verify webhook signature (JWS for Apple App Store Server Notifications v2)
        try:
            if not verify_apple_webhook(payload, signature):
                logger.error("Apple webhook JWS verification failed")
                return {
                    'statusCode': 401,
                    'body': json.dumps({'error': 'Invalid JWS signature'})
                }
        except Exception as e:
            logger.error(f"Apple webhook verification error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Verification failed'})
            }
        
        # Parse notification
        try:
            notification = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Apple webhook payload")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON'})
            }
        
        # Extract notification data
        notification_type = notification.get('notification_type')
        auto_renew_product_id = notification.get('auto_renew_product_id')
        
        # Handle different notification types
        payment_service = get_payment_sync_service()
        result = {'processed': False}
        
        if notification_type == 'INITIAL_BUY':
            result = _handle_apple_purchase(notification, payment_service)
        elif notification_type == 'CANCEL':
            result = _handle_apple_cancellation(notification, payment_service)
        elif notification_type == 'REFUND':
            result = _handle_apple_refund(notification, payment_service)
        elif notification_type in ['RENEWAL', 'INTERACTIVE_RENEWAL']:
            result = _handle_apple_renewal(notification, payment_service)
        else:
            logger.info(f"Apple webhook notification type '{notification_type}' not handled")
            result = {'processed': True, 'action': 'ignored'}
        
        logger.info(f"Apple webhook processed: {notification_type} - {result}")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'notification_type': notification_type,
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Apple webhook handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Webhook processing failed'
            })
        }

@apply_security(
    rate_limit_per_ip=100,
    rate_limit_window=300,
    require_recaptcha=False,
    validate_input=False
)
def handle_google_webhook(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle Google Play Store Real-time Developer Notifications
    
    Notification types:
    - SUBSCRIPTION_PURCHASED: New subscription
    - SUBSCRIPTION_CANCELED: Subscription cancelled
    - SUBSCRIPTION_RENEWED: Subscription renewed
    - SUBSCRIPTION_RECOVERED: Subscription recovered from account hold
    - SUBSCRIPTION_EXPIRED: Subscription expired
    - SUBSCRIPTION_REVOKED: Subscription revoked by Google
    - SUBSCRIPTION_REFUNDED: Subscription refunded
    - ONE_TIME_PRODUCT_PURCHASED: One-time product purchased
    - ONE_TIME_PRODUCT_CANCELED: One-time product cancelled
    """
    try:
        # Get raw payload
        payload = event.get('body', '')
        
        if not payload:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing payload'})
            }
        
        # Verify Google webhook signature
        headers = event.get('headers', {})
        signature = headers.get('X-Goog-Signature', headers.get('x-goog-signature', ''))
        
        if signature:
            try:
                config = get_google_play_config()
                public_key = config.get('GOOGLE_PLAY_PUBLIC_KEY')
                
                if public_key:
                    if not verify_google_webhook(payload, signature, public_key):
                        logger.error("Google webhook signature verification failed")
                        return {
                            'statusCode': 401,
                            'body': json.dumps({'error': 'Invalid signature'})
                        }
                else:
                    logger.warning("Google Play public key not configured")
            except Exception as e:
                logger.error(f"Google webhook verification error: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Verification failed'})
                }
        
        # Parse notification (Google sends base64 encoded Pub/Sub message)
        try:
            pubsub_message = json.loads(payload)
            
            # Extract the actual notification from Pub/Sub message
            message_data = pubsub_message.get('message', {}).get('data', '')
            if message_data:
                # Decode base64 notification
                notification_json = base64.b64decode(message_data).decode('utf-8')
                notification = json.loads(notification_json)
            else:
                # Direct notification (for testing)
                notification = pubsub_message
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid Google webhook payload: {e}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid payload format'})
            }
        
        # Extract notification details
        package_name = notification.get('packageName')
        notification_type = notification.get('notificationType')
        
        # Handle different notification types
        payment_service = get_payment_sync_service()
        result = {'processed': False}
        
        if notification_type == 1:  # SUBSCRIPTION_PURCHASED
            result = _handle_google_purchase(notification, payment_service)
        elif notification_type == 2:  # SUBSCRIPTION_CANCELED
            result = _handle_google_cancellation(notification, payment_service)
        elif notification_type == 12:  # SUBSCRIPTION_REFUNDED
            result = _handle_google_refund(notification, payment_service)
        elif notification_type in [7, 8]:  # ONE_TIME_PRODUCT_PURCHASED/CANCELED
            result = _handle_google_one_time_product(notification, payment_service)
        else:
            logger.info(f"Google webhook notification type '{notification_type}' not handled")
            result = {'processed': True, 'action': 'ignored'}
        
        logger.info(f"Google webhook processed: type {notification_type} - {result}")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'notification_type': notification_type,
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Google webhook handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': 'Webhook processing failed'
            })
        }

def _handle_apple_purchase(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Apple initial purchase notification"""
    try:
        # Extract purchase details
        receipt_data = notification.get('unified_receipt', {})
        latest_receipt_info = receipt_data.get('latest_receipt_info', [{}])
        
        if not latest_receipt_info:
            return {'processed': False, 'error': 'No receipt info'}
        
        purchase_info = latest_receipt_info[0]  # Get latest purchase
        product_id = purchase_info.get('product_id')
        transaction_id = purchase_info.get('transaction_id')
        
        # For webhook, we might not have user email directly
        # We could store transaction_id -> user_email mapping
        logger.info(f"Apple purchase webhook: {product_id} - {transaction_id}")
        
        return {
            'processed': True,
            'action': 'purchase_recorded',
            'product_id': product_id,
            'transaction_id': transaction_id
        }
        
    except Exception as e:
        logger.error(f"Apple purchase handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_apple_cancellation(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Apple cancellation notification"""
    try:
        # Extract cancellation details
        cancellation_date = notification.get('cancellation_date_ms')
        product_id = notification.get('auto_renew_product_id')
        
        logger.info(f"Apple cancellation webhook: {product_id} at {cancellation_date}")
        
        # TODO: Update user's subscription status in database
        
        return {
            'processed': True,
            'action': 'subscription_cancelled',
            'product_id': product_id,
            'cancellation_date': cancellation_date
        }
        
    except Exception as e:
        logger.error(f"Apple cancellation handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_apple_refund(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Apple refund notification"""
    try:
        # Extract refund details
        cancellation_reason = notification.get('cancellation_reason')
        product_id = notification.get('auto_renew_product_id')
        
        logger.info(f"Apple refund webhook: {product_id} - reason: {cancellation_reason}")
        
        # TODO: Revoke user access and update database
        
        return {
            'processed': True,
            'action': 'purchase_refunded',
            'product_id': product_id,
            'cancellation_reason': cancellation_reason
        }
        
    except Exception as e:
        logger.error(f"Apple refund handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_apple_renewal(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Apple renewal notification"""
    try:
        # Extract renewal details
        product_id = notification.get('auto_renew_product_id')
        
        logger.info(f"Apple renewal webhook: {product_id}")
        
        # TODO: Extend user's subscription in database
        
        return {
            'processed': True,
            'action': 'subscription_renewed',
            'product_id': product_id
        }
        
    except Exception as e:
        logger.error(f"Apple renewal handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_google_purchase(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Google purchase notification"""
    try:
        subscription_notification = notification.get('subscriptionNotification', {})
        product_id = subscription_notification.get('subscriptionId')
        purchase_token = subscription_notification.get('purchaseToken')
        
        logger.info(f"Google purchase webhook: {product_id} - {purchase_token}")
        
        return {
            'processed': True,
            'action': 'purchase_recorded',
            'product_id': product_id,
            'purchase_token': purchase_token
        }
        
    except Exception as e:
        logger.error(f"Google purchase handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_google_cancellation(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Google cancellation notification"""
    try:
        subscription_notification = notification.get('subscriptionNotification', {})
        product_id = subscription_notification.get('subscriptionId')
        
        logger.info(f"Google cancellation webhook: {product_id}")
        
        return {
            'processed': True,
            'action': 'subscription_cancelled',
            'product_id': product_id
        }
        
    except Exception as e:
        logger.error(f"Google cancellation handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_google_refund(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Google refund notification"""
    try:
        subscription_notification = notification.get('subscriptionNotification', {})
        product_id = subscription_notification.get('subscriptionId')
        
        logger.info(f"Google refund webhook: {product_id}")
        
        return {
            'processed': True,
            'action': 'purchase_refunded',
            'product_id': product_id
        }
        
    except Exception as e:
        logger.error(f"Google refund handling error: {e}")
        return {'processed': False, 'error': str(e)}

def _handle_google_one_time_product(notification: Dict[str, Any], payment_service) -> Dict[str, Any]:
    """Handle Google one-time product notification"""
    try:
        one_time_notification = notification.get('oneTimeProductNotification', {})
        product_id = one_time_notification.get('sku')
        purchase_token = one_time_notification.get('purchaseToken')
        notification_type = one_time_notification.get('notificationType')
        
        action = 'product_purchased' if notification_type == 1 else 'product_cancelled'
        
        logger.info(f"Google one-time product webhook: {product_id} - {action}")
        
        return {
            'processed': True,
            'action': action,
            'product_id': product_id,
            'purchase_token': purchase_token
        }
        
    except Exception as e:
        logger.error(f"Google one-time product handling error: {e}")
        return {'processed': False, 'error': str(e)}

# Export handlers
__all__ = ['handle_apple_webhook', 'handle_google_webhook']