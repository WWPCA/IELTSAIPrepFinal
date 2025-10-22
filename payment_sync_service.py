"""
Payment Confirmation and User Email Sync Service
Synchronizes user email addresses and payment status between App Stores and DynamoDB
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from receipt_validation import get_receipt_service, PurchaseStatus, PurchaseVerificationResult
from dynamodb_dal import get_dal
from aws_secrets_manager import get_apple_store_config, get_google_play_config

logger = logging.getLogger(__name__)

class PurchaseProductType(Enum):
    """IELTS Assessment Product Types"""
    ACADEMIC_SPEAKING = "academic_speaking"
    ACADEMIC_WRITING = "academic_writing"
    GENERAL_SPEAKING = "general_speaking"
    GENERAL_WRITING = "general_writing"
    ASSESSMENT_PACKAGE = "assessment_package"  # All 4 assessments

class PaymentPlatform(Enum):
    """Payment platforms supported"""
    APPLE_APP_STORE = "apple"
    GOOGLE_PLAY_STORE = "google"

@dataclass
class UserPurchaseRecord:
    """User purchase record for DynamoDB sync"""
    user_email: str
    platform: PaymentPlatform
    product_id: str
    product_type: PurchaseProductType
    transaction_id: str
    purchase_date: datetime
    receipt_data: str
    is_active: bool
    attempts_remaining: int
    expiry_date: Optional[datetime] = None

class PaymentSyncService:
    """Service for syncing payments between app stores and DynamoDB"""
    
    def __init__(self):
        self.dal = get_dal()
        self.receipt_service = get_receipt_service()
        
        # IELTS Assessment Product IDs (as configured in app stores)
        self.product_mapping = {
            # Apple App Store Product IDs
            'com.ieltsgenaiprep.academic_speaking': PurchaseProductType.ACADEMIC_SPEAKING,
            'com.ieltsgenaiprep.academic_writing': PurchaseProductType.ACADEMIC_WRITING,
            'com.ieltsgenaiprep.general_speaking': PurchaseProductType.GENERAL_SPEAKING,
            'com.ieltsgenaiprep.general_writing': PurchaseProductType.GENERAL_WRITING,
            'com.ieltsgenaiprep.assessment_package': PurchaseProductType.ASSESSMENT_PACKAGE,
            
            # Google Play Store Product IDs
            'academic_speaking_assessment': PurchaseProductType.ACADEMIC_SPEAKING,
            'academic_writing_assessment': PurchaseProductType.ACADEMIC_WRITING,
            'general_speaking_assessment': PurchaseProductType.GENERAL_SPEAKING,
            'general_writing_assessment': PurchaseProductType.GENERAL_WRITING,
            'full_assessment_package': PurchaseProductType.ASSESSMENT_PACKAGE,
        }
    
    def confirm_purchase_and_sync_user(self, user_email: str, platform: str, 
                                      receipt_data: str, device_id: str = None, 
                                      allow_duplicate: bool = False) -> Dict[str, Any]:
        """
        Confirm purchase with app store and sync user access in DynamoDB
        
        Args:
            user_email: User's email address from mobile app
            platform: 'apple' or 'google'
            receipt_data: Receipt data from app store
            device_id: Optional device identifier
            allow_duplicate: Allow duplicate transactions for repurchases
            
        Returns:
            Dict with success status and purchase details
        """
        try:
            logger.info(f"Processing purchase confirmation for {user_email} on {platform}")
            
            # Validate receipt with app store
            verification_result = self.receipt_service.validate_purchase(
                platform=platform,
                receipt_data=receipt_data,
                user_id=user_email,
                product_id=None  # Will be extracted from receipt
            )
            
            if verification_result.status != PurchaseStatus.VALID:
                logger.warning(f"Invalid receipt for {user_email}: {verification_result.error_message}")
                return {
                    'success': False,
                    'error': 'Purchase verification failed',
                    'details': verification_result.error_message
                }
            
            # Extract product information
            product_type = self._get_product_type(verification_result.product_id)
            if not product_type:
                logger.error(f"Unknown product ID: {verification_result.product_id}")
                return {
                    'success': False,
                    'error': 'Unknown product type',
                    'product_id': verification_result.product_id
                }
            
            # Ensure user exists in DynamoDB
            user = self.dal.get_user_by_email(user_email)
            if not user:
                logger.info(f"Creating new user account for {user_email}")
                # Create user with basic info (mobile registration)
                try:
                    username = user_email.split('@')[0]  # Use email prefix as username
                    self.dal.create_user(
                        username=username,
                        email=user_email,
                        password='',  # Mobile users don't need web passwords initially
                        full_name='',
                        account_source='mobile_purchase'
                    )
                    user = self.dal.get_user_by_email(user_email)
                except Exception as e:
                    logger.error(f"Failed to create user {user_email}: {e}")
                    return {
                        'success': False,
                        'error': 'Failed to create user account'
                    }
            
            # Create purchase record
            purchase_record = self._create_purchase_record(
                user_email=user_email,
                platform=PaymentPlatform.APPLE_APP_STORE if platform == 'apple' else PaymentPlatform.GOOGLE_PLAY_STORE,
                verification_result=verification_result,
                product_type=product_type
            )
            
            # Update user's purchase records in DynamoDB
            sync_result = self._sync_purchase_to_database(user, purchase_record, allow_duplicate)
            if not sync_result['success']:
                logger.error(f"Failed to sync purchase for {user_email}")
                return sync_result
            
            # Update assessment access permissions
            access_result = self._update_assessment_access(user_email, product_type, verification_result)
            if not access_result['success']:
                logger.error(f"Failed to update assessment access for {user_email}")
                return access_result
            
            logger.info(f"Successfully synced purchase for {user_email}: {product_type.value}")
            
            return {
                'success': True,
                'user_email': user_email,
                'product_type': product_type.value,
                'platform': platform,
                'transaction_id': verification_result.transaction_id,
                'attempts_remaining': self._get_attempts_for_product(product_type),
                'purchase_date': verification_result.purchase_date.isoformat() if verification_result.purchase_date else None,
                'access_granted': True
            }
            
        except Exception as e:
            logger.error(f"Purchase confirmation failed for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Internal error during purchase confirmation',
                'details': str(e)
            }
    
    def get_user_purchase_status(self, user_email: str) -> Dict[str, Any]:
        """Get comprehensive purchase status for user"""
        try:
            user = self.dal.get_user_by_email(user_email)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Get assessment access status
            assessment_access = {}
            for product_type in PurchaseProductType:
                has_access = self.dal.has_assessment_access(user_email, product_type.value)
                assessment_access[product_type.value] = {
                    'has_access': has_access,
                    'attempts_remaining': self._get_remaining_attempts(user_email, product_type.value)
                }
            
            # Get purchase history
            purchases = user.get('purchases', [])
            active_purchases = [p for p in purchases if p.get('is_active', True)]
            
            return {
                'success': True,
                'user_email': user_email,
                'assessment_package_status': user.get('assessment_package_status', 'none'),
                'subscription_status': user.get('subscription_status', 'none'),
                'assessment_access': assessment_access,
                'active_purchases': len(active_purchases),
                'purchase_history': purchases,
                'last_purchase_date': max([p.get('purchase_date', '') for p in purchases]) if purchases else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get purchase status for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to retrieve purchase status'
            }
    
    def refresh_user_purchase_status(self, user_email: str) -> Dict[str, Any]:
        """Refresh user's purchase status by validating all stored receipts"""
        try:
            user = self.dal.get_user_by_email(user_email)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            purchases = user.get('purchases', [])
            refreshed_purchases = []
            access_changes = []
            
            for purchase in purchases:
                # Re-validate receipt if available
                if 'receipt_data' in purchase and purchase.get('is_active', True):
                    platform = purchase.get('platform', 'apple')
                    verification_result = self.receipt_service.validate_purchase(
                        platform=platform,
                        receipt_data=purchase['receipt_data'],
                        user_id=user_email,
                        product_id=purchase.get('product_id')
                    )
                    
                    if verification_result.status == PurchaseStatus.VALID:
                        refreshed_purchases.append(purchase)
                    else:
                        # Purchase is no longer valid
                        purchase['is_active'] = False
                        purchase['deactivation_reason'] = verification_result.error_message
                        purchase['deactivated_at'] = datetime.utcnow().isoformat()
                        refreshed_purchases.append(purchase)
                        access_changes.append(f"Deactivated {purchase.get('product_type', 'unknown')}")
                else:
                    refreshed_purchases.append(purchase)
            
            # Update user record with refreshed purchases
            self.dal.update_user(user_email, purchases=refreshed_purchases)
            
            return {
                'success': True,
                'user_email': user_email,
                'refreshed_purchases': len(refreshed_purchases),
                'active_purchases': len([p for p in refreshed_purchases if p.get('is_active', True)]),
                'access_changes': access_changes
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh purchase status for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to refresh purchase status'
            }
    
    def _get_product_type(self, product_id: str) -> Optional[PurchaseProductType]:
        """Map product ID to product type"""
        return self.product_mapping.get(product_id)
    
    def _create_purchase_record(self, user_email: str, platform: PaymentPlatform, 
                               verification_result: PurchaseVerificationResult, 
                               product_type: PurchaseProductType) -> UserPurchaseRecord:
        """Create purchase record for database sync"""
        return UserPurchaseRecord(
            user_email=user_email,
            platform=platform,
            product_id=verification_result.product_id,
            product_type=product_type,
            transaction_id=verification_result.transaction_id,
            purchase_date=verification_result.purchase_date or datetime.utcnow(),
            receipt_data=json.dumps(verification_result.receipt_data) if verification_result.receipt_data else '',
            is_active=True,
            attempts_remaining=self._get_attempts_for_product(product_type),
            expiry_date=verification_result.expiry_date
        )
    
    def _sync_purchase_to_database(self, user: Dict[str, Any], 
                                  purchase_record: UserPurchaseRecord,
                                  allow_duplicate: bool = False) -> Dict[str, Any]:
        """Sync purchase record to DynamoDB"""
        try:
            # Check for duplicate transactions (unless explicitly allowed for repurchases)
            if not allow_duplicate:
                existing_purchases = user.get('purchases', [])
                for existing in existing_purchases:
                    if existing.get('transaction_id') == purchase_record.transaction_id:
                        logger.warning(f"Duplicate transaction {purchase_record.transaction_id} for {purchase_record.user_email}")
                        return {
                            'success': False,
                            'error': 'Duplicate transaction',
                            'transaction_id': purchase_record.transaction_id
                        }
            
            # Add new purchase record
            purchase_data = {
                'product_id': purchase_record.product_id,
                'product_type': purchase_record.product_type.value,
                'platform': purchase_record.platform.value,
                'transaction_id': purchase_record.transaction_id,
                'purchase_date': purchase_record.purchase_date.isoformat(),
                'receipt_data': purchase_record.receipt_data,
                'is_active': purchase_record.is_active,
                'attempts_remaining': purchase_record.attempts_remaining,
                'total_attempts': purchase_record.attempts_remaining,
                'expiry_date': purchase_record.expiry_date.isoformat() if purchase_record.expiry_date else None,
                'sync_date': datetime.utcnow().isoformat()
            }
            
            # Use DynamoDB DAL to add purchase
            success = self.dal.add_user_purchase(user['user_id'], purchase_data)
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to add purchase to database'
                }
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to sync purchase to database: {e}")
            return {
                'success': False,
                'error': 'Database sync failed'
            }
    
    def _update_assessment_access(self, user_email: str, product_type: PurchaseProductType, 
                                 verification_result: PurchaseVerificationResult) -> Dict[str, Any]:
        """Update user's assessment access permissions"""
        try:
            update_data = {}
            
            # Set assessment package status
            if product_type == PurchaseProductType.ASSESSMENT_PACKAGE:
                update_data['assessment_package_status'] = 'active'
                update_data['assessment_package_expiry'] = (
                    verification_result.expiry_date.isoformat() 
                    if verification_result.expiry_date 
                    else (datetime.utcnow() + timedelta(days=365)).isoformat()  # Default 1 year
                )
            else:
                # Individual assessment purchase
                current_status = self.dal.get_user_by_email(user_email).get('assessment_package_status', 'none')
                if current_status == 'none':
                    update_data['assessment_package_status'] = 'partial'
            
            # Update user record
            if update_data:
                success = self.dal.update_user(user_email, **update_data)
                if not success:
                    return {
                        'success': False,
                        'error': 'Failed to update assessment access'
                    }
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to update assessment access: {e}")
            return {
                'success': False,
                'error': 'Access update failed'
            }
    
    def _get_attempts_for_product(self, product_type: PurchaseProductType) -> int:
        """Get number of attempts for product type"""
        if product_type == PurchaseProductType.ASSESSMENT_PACKAGE:
            return 4  # 1 attempt per assessment type
        else:
            return 1  # Single assessment purchase
    
    def _get_remaining_attempts(self, user_email: str, assessment_type: str) -> int:
        """Get remaining attempts for specific assessment type"""
        try:
            counts = self.dal.get_user_assessment_counts(user_email)
            assessment_data = counts.get(assessment_type, {})
            return assessment_data.get('attempts_remaining', 0)
        except Exception:
            return 0

# Global service instance
payment_sync_service = PaymentSyncService()

def get_payment_sync_service() -> PaymentSyncService:
    """Get global payment sync service instance"""
    return payment_sync_service

# Export
__all__ = ['PaymentSyncService', 'PaymentPlatform', 'PurchaseProductType', 'get_payment_sync_service']