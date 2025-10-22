"""
Mobile API Routes for IELTS AI Prep
Handles mobile-exclusive registration and in-app purchase verification
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from dynamodb_dal import DynamoDBConnection, UserDAL, EntitlementDAL
from receipt_validation import AppleReceiptValidator, GooglePlayReceiptValidator, PurchaseStatus

logger = logging.getLogger(__name__)

# Create blueprint for mobile API
mobile_api = Blueprint('mobile_api', __name__, url_prefix='/api/v1/mobile')

# Initialize DynamoDB connection
db_connection = DynamoDBConnection(
    region=os.environ.get('AWS_REGION', 'us-east-1'),
    environment=os.environ.get('ENVIRONMENT', 'production')
)
user_dal = UserDAL(db_connection)
entitlement_dal = EntitlementDAL(db_connection)

# Initialize receipt validators
apple_validator = AppleReceiptValidator()
google_validator = GooglePlayReceiptValidator()

@mobile_api.route('/register', methods=['POST'])
def mobile_register():
    """
    Mobile-exclusive registration endpoint
    Creates user account from mobile app
    
    Request JSON:
    {
        "email": "user@example.com",
        "password": "secure_password",
        "device_id": "unique_device_identifier",
        "platform": "ios" or "android"
    }
    
    Response:
    {
        "success": true,
        "user_id": "uuid",
        "email": "user@example.com",
        "message": "Registration successful"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        device_id = data.get('device_id', '')
        platform = data.get('platform', '').lower()
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        if platform not in ['ios', 'android']:
            return jsonify({
                'success': False,
                'error': 'Invalid platform. Must be ios or android'
            }), 400
        
        # Check if user already exists
        existing_user = user_dal.get_user_by_email(email)
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409
        
        # Create user account
        user = user_dal.create_user(
            email=email,
            password=password,
            registration_source='mobile_app',
            platform=platform,
            device_id=device_id,
            email_verified=False
        )
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Failed to create user account'
            }), 500
        
        logger.info(f"Mobile registration successful: {email} ({platform})")
        
        return jsonify({
            'success': True,
            'user_id': user['user_id'],
            'email': user['email'],
            'message': 'Registration successful. Welcome to IELTS AI Prep!'
        }), 201
        
    except Exception as e:
        logger.error(f"Mobile registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }), 500

@mobile_api.route('/verify-purchase', methods=['POST'])
def verify_purchase():
    """
    Verify in-app purchase receipt and grant entitlement
    
    Request JSON:
    {
        "user_id": "uuid",
        "platform": "ios" or "android",
        "receipt_data": "base64_encoded_receipt" (iOS) or receipt object (Android),
        "product_id": "com.ieltsaiprep.academic.writing",
        "transaction_id": "unique_transaction_id"
    }
    
    Response:
    {
        "success": true,
        "verified": true,
        "product_id": "com.ieltsaiprep.academic.writing",
        "assessments_granted": 2,
        "message": "Purchase verified successfully"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        user_id = data.get('user_id', '').strip()
        platform = data.get('platform', '').lower().strip()
        receipt_data = data.get('receipt_data', '')
        product_id = data.get('product_id', '').strip()
        transaction_id = data.get('transaction_id', '').strip()
        
        # CRITICAL: Validate ALL required fields including transaction_id
        if not all([user_id, platform, receipt_data, product_id, transaction_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: user_id, platform, receipt_data, product_id, transaction_id'
            }), 400
        
        # Additional validation: transaction_id must not be empty after stripping
        if len(transaction_id) < 1:
            return jsonify({
                'success': False,
                'error': 'transaction_id cannot be empty'
            }), 400
        
        if platform not in ['ios', 'android']:
            return jsonify({
                'success': False,
                'error': 'Invalid platform'
            }), 400
        
        # Verify receipt with appropriate validator
        if platform == 'ios':
            result = apple_validator.validate_receipt(receipt_data, user_id)
        else:  # android
            result = google_validator.validate_receipt(receipt_data, user_id)
        
        # Check verification result
        if result.status != PurchaseStatus.VALID:
            logger.warning(f"Purchase verification failed: {result.error_message}")
            return jsonify({
                'success': False,
                'verified': False,
                'error': result.error_message or 'Receipt verification failed'
            }), 400
        
        # Grant entitlement
        entitlement_granted = entitlement_dal.grant_entitlement(
            user_id=user_id,
            product_id=product_id,
            transaction_id=result.transaction_id or transaction_id,
            platform=platform,
            receipt_data=result.receipt_data
        )
        
        if not entitlement_granted:
            return jsonify({
                'success': False,
                'verified': True,
                'error': 'Failed to grant entitlement (may already be processed)'
            }), 409
        
        # Get assessment count for this product
        from dynamodb_dal import PRODUCT_ASSESSMENTS
        assessments_count = PRODUCT_ASSESSMENTS.get(product_id, 2)
        
        logger.info(f"Purchase verified and entitlement granted: {user_id} - {product_id}")
        
        return jsonify({
            'success': True,
            'verified': True,
            'product_id': product_id,
            'assessments_granted': assessments_count,
            'transaction_id': result.transaction_id,
            'message': f'Purchase verified! You now have {assessments_count} assessments available.'
        }), 200
        
    except Exception as e:
        logger.error(f"Purchase verification error: {e}")
        return jsonify({
            'success': False,
            'error': 'Purchase verification failed'
        }), 500

@mobile_api.route('/check-entitlement', methods=['POST'])
def check_entitlement():
    """
    Check user's entitlements for a specific module
    
    Request JSON:
    {
        "user_id": "uuid",
        "module_type": "academic_writing"
    }
    
    Response:
    {
        "success": true,
        "has_access": true,
        "assessments_remaining": 2,
        "products": [...]
    }
    """
    try:
        data = request.get_json()
        
        user_id = data.get('user_id', '')
        module_type = data.get('module_type', '')
        
        if not user_id or not module_type:
            return jsonify({
                'success': False,
                'error': 'user_id and module_type are required'
            }), 400
        
        # Check entitlement
        entitlement = entitlement_dal.check_entitlement(user_id, module_type)
        
        return jsonify({
            'success': True,
            **entitlement
        }), 200
        
    except Exception as e:
        logger.error(f"Entitlement check error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to check entitlement'
        }), 500

@mobile_api.route('/restore-purchases', methods=['POST'])
def restore_purchases():
    """
    Restore previous purchases for a user
    
    Request JSON:
    {
        "user_id": "uuid"
    }
    
    Response:
    {
        "success": true,
        "entitlements": [...],
        "total_assessments": 6
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', '')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Get all user entitlements
        entitlements = entitlement_dal.get_user_entitlements(user_id)
        
        # Calculate total remaining assessments
        total_remaining = sum(
            ent.get('assessments_remaining', 0) 
            for ent in entitlements 
            if ent.get('status') == 'active'
        )
        
        return jsonify({
            'success': True,
            'entitlements': entitlements,
            'total_active_products': len([e for e in entitlements if e.get('status') == 'active']),
            'total_assessments_remaining': total_remaining
        }), 200
        
    except Exception as e:
        logger.error(f"Restore purchases error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to restore purchases'
        }), 500

@mobile_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for mobile API"""
    return jsonify({
        'status': 'healthy',
        'service': 'mobile-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Export blueprint
__all__ = ['mobile_api']
