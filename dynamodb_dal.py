"""
AWS DynamoDB Data Access Layer for IELTS AI Prep
Provides data access for users, sessions, assessments, and QR tokens using DynamoDB
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import secrets
import json
import os
import logging

logger = logging.getLogger(__name__)

# Product configuration - number of assessments per purchase
# Pricing: $25 for Writing/Speaking (2 assessments), $99 for Mock Tests (2 complete tests)
PRODUCT_ASSESSMENTS = {
    # iOS/Android App Store Product IDs
    'com.ieltsaiprep.academic.writing': 2,
    'com.ieltsaiprep.general.writing': 2,
    'com.ieltsaiprep.academic.speaking': 2,
    'com.ieltsaiprep.general.speaking': 2,
    'com.ieltsaiprep.academic.mocktest': 2,
    'com.ieltsaiprep.general.mocktest': 2,
    # Legacy product IDs for backwards compatibility
    'academic_writing': 2,
    'general_writing': 2,
    'academic_speaking': 2,
    'general_speaking': 2,
}

# Product pricing in USD
PRODUCT_PRICING = {
    'com.ieltsaiprep.academic.writing': 25.00,
    'com.ieltsaiprep.general.writing': 25.00,
    'com.ieltsaiprep.academic.speaking': 25.00,
    'com.ieltsaiprep.general.speaking': 25.00,
    'com.ieltsaiprep.academic.mocktest': 99.00,
    'com.ieltsaiprep.general.mocktest': 99.00,
}

class DynamoDBConnection:
    """Manages DynamoDB connection for AWS"""
    
    def __init__(self, region: str = None, environment: str = None):
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.environment = environment or os.environ.get('ENVIRONMENT', 'production')
        
        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=self.region,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
        
        # Table name mapping
        self.table_names = {
            'users': 'ielts-genai-prep-users',
            'sessions': 'ielts-genai-prep-sessions',
            'assessments': 'ielts-genai-prep-assessments',
            'entitlements': 'ielts-genai-prep-entitlements',
            'questions': 'ielts-assessment-questions',
            'rubrics': 'ielts-genai-prep-rubrics',
            'reset_tokens': 'ielts-genai-prep-reset-tokens',  # Password reset tokens
            'auth_tokens': 'ielts-genai-prep-auth-tokens',  # Email verification tokens
            'listening_tests': 'ielts-listening-tests',
            'listening_questions': 'ielts-listening-questions',
            'listening_answers': 'ielts-listening-answers',
            'reading_tests': 'ielts-reading-tests',
            'reading_questions': 'ielts-reading-questions',
            'reading_answers': 'ielts-reading-answers',
            'full_tests': 'ielts-full-tests',
            'test_results': 'ielts-test-results',
            'test_progress': 'ielts-test-progress'
        }
        
        logger.info(f"DynamoDB client initialized - region: {self.region}, environment: {self.environment}")
    
    def get_table(self, table_key: str):
        """Get DynamoDB table reference"""
        table_name = self.table_names.get(table_key)
        if not table_name:
            raise ValueError(f"Unknown table key: {table_key}")
        return self.dynamodb.Table(table_name)

class UserDAL:
    """User Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('users')
    
    def create_user(self, email: str, password: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Create new user account"""
        try:
            # Check if user already exists
            existing = self.get_user_by_email(email)
            if existing:
                logger.warning(f"User already exists: {email}")
                return None
            
            user_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            user_data = {
                'email': email,
                'user_id': user_id,
                'password_hash': generate_password_hash(password),
                'created_at': now.isoformat(),
                'last_login': now.isoformat(),
                'join_date': now.isoformat(),
                'email_verified': kwargs.get('email_verified', False),
                'assessment_count': 0,
                'is_active': True,
                **kwargs
            }
            
            # Remove password if passed in kwargs
            user_data.pop('password', None)
            
            self.table.put_item(Item=user_data)
            logger.info(f"User created: {email}")
            
            # Remove sensitive data before returning
            user_data.pop('password_hash', None)
            return user_data
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            response = self.table.get_item(Key={'email': email})
            user = response.get('Item')
            if user:
                logger.info(f"User found: {email}")
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        try:
            user = self.get_user_by_email(email)
            if not user:
                return False
            
            password_hash = user.get('password_hash')
            if not password_hash:
                return False
                
            return check_password_hash(password_hash, password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def update_user(self, email: str, **updates) -> bool:
        """Update user data"""
        try:
            if not updates:
                return True
            
            update_expr_parts = []
            expr_values = {}
            expr_names = {}
            
            for key, value in updates.items():
                # Handle reserved keywords
                attr_name = f"#{key}"
                attr_value = f":{key}"
                update_expr_parts.append(f"{attr_name} = {attr_value}")
                expr_names[attr_name] = key
                expr_values[attr_value] = value
            
            update_expr = "SET " + ", ".join(update_expr_parts)
            
            self.table.update_item(
                Key={'email': email},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values
            )
            
            logger.info(f"User updated: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def update_last_login(self, email: str) -> bool:
        """Update user's last login timestamp"""
        return self.update_user(email, last_login=datetime.utcnow().isoformat())
    
    def get_sanitized_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from user object"""
        if not user_data:
            return None
        
        sanitized = user_data.copy()
        sanitized.pop('password_hash', None)
        sanitized.pop('reset_token', None)
        sanitized.pop('reset_token_expires', None)
        
        return sanitized

class SessionDAL:
    """Session Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('sessions')
    
    def create_session(self, user_email: str, user_id: str, session_type: str = 'web') -> Dict[str, Any]:
        """Create new session"""
        try:
            session_id = f"{session_type}_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=24)
            
            session_data = {
                'session_id': session_id,
                'user_email': user_email,
                'user_id': user_id,
                'created_at': now.isoformat(),
                'expires_at': int(expires_at.timestamp()),  # TTL in Unix timestamp
                'session_type': session_type,
                'is_active': True
            }
            
            self.table.put_item(Item=session_data)
            logger.info(f"Session created: {session_id} for {user_email}")
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            session = response.get('Item')
            
            if session:
                # Check if expired
                if session.get('expires_at', 0) < datetime.utcnow().timestamp():
                    logger.info(f"Session expired: {session_id}")
                    return None
                    
            return session
            
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session (logout)"""
        try:
            self.table.delete_item(Key={'session_id': session_id})
            logger.info(f"Session deleted: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

class AssessmentDAL:
    """Assessment Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('assessments')
    
    def save_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save assessment result"""
        try:
            if 'assessment_id' not in assessment_data:
                assessment_data['assessment_id'] = str(uuid.uuid4())
            
            if 'timestamp' not in assessment_data:
                assessment_data['timestamp'] = datetime.utcnow().isoformat()
            
            self.table.put_item(Item=assessment_data)
            logger.info(f"Assessment saved: {assessment_data['assessment_id']}")
            
            return assessment_data
            
        except Exception as e:
            logger.error(f"Error saving assessment: {e}")
            return None
    
    def get_user_assessments(self, user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's assessment history"""
        try:
            # Query using GSI on user_email
            response = self.table.query(
                IndexName='user-email-index',
                KeyConditionExpression=Key('user_email').eq(user_email),
                Limit=limit,
                ScanIndexForward=False  # Most recent first
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting assessments: {e}")
            return []
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get specific assessment by ID"""
        try:
            response = self.table.get_item(Key={'assessment_id': assessment_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Error getting assessment: {e}")
            return None
    
    def get_daily_assessment_count(self, user_email: str) -> int:
        """Get number of assessments user has taken today"""
        try:
            # Get start and end of today in UTC
            now = datetime.utcnow()
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_of_day = start_of_day + timedelta(days=1)
            
            # Query assessments for today
            response = self.table.query(
                IndexName='user-email-index',
                KeyConditionExpression=Key('user_email').eq(user_email),
                FilterExpression=Attr('timestamp').between(
                    start_of_day.isoformat(),
                    end_of_day.isoformat()
                )
            )
            
            count = len(response.get('Items', []))
            logger.info(f"User {user_email} has completed {count} assessments today")
            return count
            
        except Exception as e:
            logger.error(f"Error counting daily assessments: {e}")
            return 0
    
    def check_rate_limit(self, user_email: str, daily_limit: int = 8) -> tuple[bool, int]:
        """
        Check if user is within daily rate limit
        Returns: (is_within_limit, current_count)
        """
        try:
            current_count = self.get_daily_assessment_count(user_email)
            is_within_limit = current_count < daily_limit
            
            if not is_within_limit:
                logger.warning(f"Rate limit exceeded for {user_email}: {current_count}/{daily_limit}")
            
            return (is_within_limit, current_count)
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Default to allowing access if check fails
            return (True, 0)

class EntitlementDAL:
    """Entitlement Data Access Layer for managing user purchase entitlements"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('entitlements')
    
    def grant_entitlement(self, user_id: str, product_id: str, transaction_id: str, 
                         platform: str, receipt_data: Optional[Dict] = None) -> bool:
        """
        Grant user access to purchased module
        
        Args:
            user_id: User ID
            product_id: Product identifier (e.g., 'com.ieltsaiprep.academic.writing')
            transaction_id: Unique transaction ID from App Store/Play Store
            platform: 'ios' or 'android'
            receipt_data: Optional receipt verification data
            
        Returns:
            True if entitlement granted successfully
        """
        try:
            # CRITICAL: Validate transaction_id is not empty (security requirement)
            if not transaction_id or not transaction_id.strip():
                logger.error("grant_entitlement called with empty transaction_id - rejecting")
                return False
            
            # Check if transaction already processed (prevent duplicate grants)
            existing = self.get_entitlement_by_transaction(transaction_id)
            if existing:
                logger.warning(f"Transaction already processed: {transaction_id}")
                return False
            
            # Get number of assessments for this product
            assessment_count = PRODUCT_ASSESSMENTS.get(product_id, 2)
            now = datetime.utcnow()
            
            entitlement_data = {
                'user_id': user_id,
                'product_id': product_id,
                'transaction_id': transaction_id,
                'platform': platform,
                'assessments_purchased': assessment_count,
                'assessments_remaining': assessment_count,
                'purchase_date': now.isoformat(),
                'status': 'active',
                'receipt_verified': True if receipt_data else False,
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            if receipt_data:
                entitlement_data['receipt_data'] = json.dumps(receipt_data)
            
            self.table.put_item(Item=entitlement_data)
            logger.info(f"Entitlement granted: {user_id} - {product_id} ({assessment_count} assessments)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error granting entitlement: {e}")
            return False
    
    def check_entitlement(self, user_id: str, module_type: str) -> Dict[str, Any]:
        """
        Check if user has access to a module and how many assessments remaining
        
        Args:
            user_id: User ID
            module_type: 'academic_writing', 'general_writing', 'academic_speaking', 'general_speaking'
            
        Returns:
            Dict with 'has_access', 'assessments_remaining', 'products'
        """
        try:
            # Query all entitlements for this user
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            
            entitlements = response.get('Items', [])
            
            # Filter for active entitlements matching the module type
            matching_entitlements = []
            total_remaining = 0
            
            for ent in entitlements:
                product_id = ent.get('product_id', '')
                status = ent.get('status', 'inactive')
                remaining = ent.get('assessments_remaining', 0)
                
                # Check if product matches module type
                if status == 'active' and module_type in product_id.lower():
                    matching_entitlements.append(ent)
                    total_remaining += remaining
            
            return {
                'has_access': total_remaining > 0,
                'assessments_remaining': total_remaining,
                'products': matching_entitlements,
                'total_products': len(matching_entitlements)
            }
            
        except Exception as e:
            logger.error(f"Error checking entitlement: {e}")
            return {
                'has_access': False,
                'assessments_remaining': 0,
                'products': [],
                'total_products': 0
            }
    
    def consume_assessment(self, user_id: str, module_type: str, assessment_id: str) -> bool:
        """
        Decrement assessment count after user completes an assessment
        
        Args:
            user_id: User ID
            module_type: Module type that was used
            assessment_id: ID of the completed assessment
            
        Returns:
            True if consumption successful
        """
        try:
            # Find active entitlement with remaining assessments
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            
            entitlements = response.get('Items', [])
            
            # Find first matching entitlement with remaining assessments
            for ent in entitlements:
                product_id = ent.get('product_id', '')
                status = ent.get('status', 'inactive')
                remaining = ent.get('assessments_remaining', 0)
                
                if status == 'active' and module_type in product_id.lower() and remaining > 0:
                    # Decrement the count
                    new_remaining = remaining - 1
                    new_status = 'active' if new_remaining > 0 else 'consumed'
                    
                    self.table.update_item(
                        Key={
                            'user_id': user_id,
                            'product_id': product_id
                        },
                        UpdateExpression='SET assessments_remaining = :remaining, #status = :status, updated_at = :updated, last_used_assessment = :assessment_id',
                        ExpressionAttributeValues={
                            ':remaining': new_remaining,
                            ':status': new_status,
                            ':updated': datetime.utcnow().isoformat(),
                            ':assessment_id': assessment_id
                        },
                        ExpressionAttributeNames={
                            '#status': 'status'
                        }
                    )
                    
                    logger.info(f"Assessment consumed: {user_id} - {product_id} ({new_remaining} remaining)")
                    return True
            
            logger.warning(f"No active entitlement found for consumption: {user_id} - {module_type}")
            return False
            
        except Exception as e:
            logger.error(f"Error consuming assessment: {e}")
            return False
    
    def get_remaining_assessments(self, user_id: str, module_type: str) -> int:
        """
        Get total remaining assessments for a module type
        
        Args:
            user_id: User ID
            module_type: Module type to check
            
        Returns:
            Total number of remaining assessments
        """
        entitlement_check = self.check_entitlement(user_id, module_type)
        return entitlement_check.get('assessments_remaining', 0)
    
    def get_entitlement_by_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get entitlement by transaction ID (prevent duplicate processing)
        
        Args:
            transaction_id: Transaction ID to check
            
        Returns:
            Entitlement dict if found, None otherwise
        """
        try:
            response = self.table.query(
                IndexName='TransactionIndex',
                KeyConditionExpression=Key('transaction_id').eq(transaction_id)
            )
            
            items = response.get('Items', [])
            return items[0] if items else None
            
        except Exception as e:
            logger.error(f"Error getting entitlement by transaction: {e}")
            return None
    
    def get_user_entitlements(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all entitlements for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of entitlement dicts
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"Error getting user entitlements: {e}")
            return []

class ResetTokenDAL:
    """Password Reset Token Data Access Layer using DynamoDB"""
    
    def __init__(self, connection: DynamoDBConnection):
        self.conn = connection
        self.table = connection.get_table('reset_tokens')
    
    def create_reset_token(self, email: str, token: str, expires_minutes: int = 30) -> bool:
        """
        Create password reset token
        
        Args:
            email: User email
            token: Reset token
            expires_minutes: Token validity in minutes (default 30)
            
        Returns:
            True if created successfully
        """
        try:
            now = datetime.utcnow()
            expires_at = now + timedelta(minutes=expires_minutes)
            
            token_data = {
                'reset_token': token,
                'email': email,
                'created_at': now.isoformat(),
                'expires_at': expires_at.isoformat(),
                'used': False
            }
            
            self.table.put_item(Item=token_data)
            logger.info(f"Reset token created for: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating reset token: {e}")
            return False
    
    def validate_reset_token(self, token: str) -> Optional[str]:
        """
        Validate reset token and return associated email
        
        Args:
            token: Reset token to validate
            
        Returns:
            Email if token is valid, None otherwise
        """
        try:
            response = self.table.get_item(Key={'reset_token': token})
            item = response.get('Item')
            
            if not item:
                logger.warning(f"Reset token not found: {token[:8]}...")
                return None
            
            # Check if already used
            if item.get('used', False):
                logger.warning(f"Reset token already used: {token[:8]}...")
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(item['expires_at'])
            if datetime.utcnow() > expires_at:
                logger.warning(f"Reset token expired: {token[:8]}...")
                return None
            
            return item['email']
            
        except Exception as e:
            logger.error(f"Error validating reset token: {e}")
            return None
    
    def invalidate_reset_token(self, token: str) -> bool:
        """
        Mark reset token as used
        
        Args:
            token: Reset token to invalidate
            
        Returns:
            True if invalidated successfully
        """
        try:
            self.table.update_item(
                Key={'reset_token': token},
                UpdateExpression='SET used = :used',
                ExpressionAttributeValues={':used': True}
            )
            logger.info(f"Reset token invalidated: {token[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating reset token: {e}")
            return False

# Compatibility aliases for easy migration from Firestore
FirestoreConnection = DynamoDBConnection  # Alias for compatibility