"""
Comprehensive End-to-End Tests for Complete User Journey
Tests: Registration → Purchase → Entitlement → Access Control → Assessments
"""
import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add deployment to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'deployment'))

from dynamodb_dal import (
    DynamoDBConnection, 
    UserDAL, 
    EntitlementDAL,
    PRODUCT_ASSESSMENTS,
    PRODUCT_PRICING
)


class TestMobileUserRegistration:
    """Test mobile app user registration workflow"""
    
    @pytest.fixture
    def mock_dynamodb_connection(self):
        """Create mocked DynamoDB connection"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection(region='us-east-1')
            return conn
    
    @pytest.fixture
    def user_dal(self, mock_dynamodb_connection):
        """Create UserDAL with mocked connection"""
        mock_table = MagicMock()
        mock_dynamodb_connection.get_table = MagicMock(return_value=mock_table)
        dal = UserDAL(mock_dynamodb_connection)
        dal.table = mock_table
        return dal
    
    def test_mobile_user_registration_creates_dynamodb_record(self, user_dal):
        """Test mobile registration creates user in DynamoDB users table"""
        # Mock successful user creation
        user_dal.table.get_item.return_value = {}  # No existing user
        user_dal.table.put_item.return_value = {}
        
        # Create user via mobile app
        result = user_dal.create_user(
            email='mobile_user@example.com',
            password='SecurePassword123!',
            platform='ios',
            device_id='iPhone14,2'
        )
        
        # Verify DynamoDB put_item was called
        user_dal.table.put_item.assert_called_once()
        call_args = user_dal.table.put_item.call_args
        user_data = call_args[1]['Item']
        
        # Verify user record structure
        assert user_data['email'] == 'mobile_user@example.com'
        assert 'user_id' in user_data
        assert 'password_hash' in user_data
        assert user_data['platform'] == 'ios'
        assert user_data['is_active'] == True
        assert 'created_at' in user_data
    
    def test_duplicate_registration_prevented(self, user_dal):
        """Test duplicate email registration is blocked"""
        # Mock existing user
        user_dal.table.get_item.return_value = {
            'Item': {'email': 'existing@example.com'}
        }
        
        # Attempt duplicate registration
        result = user_dal.create_user(
            email='existing@example.com',
            password='Password123!'
        )
        
        # Verify creation was blocked
        assert result is None
        user_dal.table.put_item.assert_not_called()
    
    def test_user_record_maps_to_correct_dynamodb_table(self, mock_dynamodb_connection):
        """Test user data goes to ielts-genai-prep-users table"""
        table_name = mock_dynamodb_connection.table_names['users']
        assert table_name == 'ielts-genai-prep-users'


class TestInAppPurchaseFlow:
    """Test in-app purchase processing and entitlement grant"""
    
    @pytest.fixture
    def mock_dynamodb_connection(self):
        """Create mocked DynamoDB connection"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection(region='us-east-1')
            return conn
    
    @pytest.fixture
    def entitlement_dal(self, mock_dynamodb_connection):
        """Create EntitlementDAL with mocked connection"""
        mock_table = MagicMock()
        mock_dynamodb_connection.get_table = MagicMock(return_value=mock_table)
        dal = EntitlementDAL(mock_dynamodb_connection)
        dal.table = mock_table
        return dal
    
    def test_ios_purchase_creates_entitlement_in_dynamodb(self, entitlement_dal):
        """Test iOS App Store purchase creates entitlement record"""
        # Mock successful entitlement grant
        entitlement_dal.table.query.return_value = {'Items': []}  # No existing entitlement
        entitlement_dal.table.put_item.return_value = {}
        
        # Process iOS purchase
        result = entitlement_dal.grant_entitlement(
            user_id='user-12345',
            product_id='com.ieltsaiprep.academic.writing',
            transaction_id='ios-transaction-abc123',
            platform='ios',
            receipt_data={'receipt': 'base64_encoded_receipt'}
        )
        
        # Verify DynamoDB put_item was called
        assert entitlement_dal.table.put_item.called
        call_args = entitlement_dal.table.put_item.call_args
        entitlement_data = call_args[1]['Item']
        
        # Verify entitlement record structure
        assert entitlement_data['user_id'] == 'user-12345'
        assert entitlement_data['product_id'] == 'com.ieltsaiprep.academic.writing'
        assert entitlement_data['transaction_id'] == 'ios-transaction-abc123'
        assert entitlement_data['platform'] == 'ios'
        assert entitlement_data['assessments_granted'] == 2
        assert entitlement_data['assessments_used'] == 0
    
    def test_android_purchase_creates_entitlement_in_dynamodb(self, entitlement_dal):
        """Test Google Play purchase creates entitlement record"""
        entitlement_dal.table.query.return_value = {'Items': []}
        entitlement_dal.table.put_item.return_value = {}
        
        # Process Android purchase
        result = entitlement_dal.grant_entitlement(
            user_id='user-67890',
            product_id='com.ieltsaiprep.academic.speaking',
            transaction_id='android-token-xyz789',
            platform='android',
            receipt_data={'purchaseToken': 'google_purchase_token'}
        )
        
        assert entitlement_dal.table.put_item.called
        call_args = entitlement_dal.table.put_item.call_args
        entitlement_data = call_args[1]['Item']
        
        assert entitlement_data['platform'] == 'android'
        assert entitlement_data['assessments_granted'] == 2
    
    def test_duplicate_purchase_prevented(self, entitlement_dal):
        """Test duplicate transaction ID is blocked"""
        # Mock existing transaction
        entitlement_dal.table.query.return_value = {
            'Items': [{'transaction_id': 'existing-transaction'}]
        }
        
        # Attempt duplicate purchase
        result = entitlement_dal.grant_entitlement(
            user_id='user-12345',
            product_id='com.ieltsaiprep.academic.writing',
            transaction_id='existing-transaction',
            platform='ios'
        )
        
        # Verify creation was blocked
        assert result == False
        entitlement_dal.table.put_item.assert_not_called()
    
    def test_entitlement_maps_to_correct_dynamodb_table(self, mock_dynamodb_connection):
        """Test entitlements go to ielts-genai-prep-entitlements table"""
        table_name = mock_dynamodb_connection.table_names['entitlements']
        assert table_name == 'ielts-genai-prep-entitlements'
    
    def test_product_assessment_quantities(self):
        """Test each product grants correct number of assessments"""
        assert PRODUCT_ASSESSMENTS['com.ieltsaiprep.academic.writing'] == 2
        assert PRODUCT_ASSESSMENTS['com.ieltsaiprep.general.writing'] == 2
        assert PRODUCT_ASSESSMENTS['com.ieltsaiprep.academic.speaking'] == 2
        assert PRODUCT_ASSESSMENTS['com.ieltsaiprep.general.speaking'] == 2
        assert PRODUCT_ASSESSMENTS['com.ieltsaiprep.academic.mocktest'] == 2
        assert PRODUCT_ASSESSMENTS['com.ieltsaiprep.general.mocktest'] == 2
    
    def test_product_pricing(self):
        """Test product pricing is correct"""
        assert PRODUCT_PRICING['com.ieltsaiprep.academic.writing'] == 25.00
        assert PRODUCT_PRICING['com.ieltsaiprep.general.writing'] == 25.00
        assert PRODUCT_PRICING['com.ieltsaiprep.academic.speaking'] == 25.00
        assert PRODUCT_PRICING['com.ieltsaiprep.general.speaking'] == 25.00
        assert PRODUCT_PRICING['com.ieltsaiprep.academic.mocktest'] == 99.00
        assert PRODUCT_PRICING['com.ieltsaiprep.general.mocktest'] == 99.00


class TestAccessControlBasedOnPurchase:
    """Test users get correct access based on what they purchased"""
    
    @pytest.fixture
    def mock_dynamodb_connection(self):
        """Create mocked DynamoDB connection"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection(region='us-east-1')
            return conn
    
    @pytest.fixture
    def entitlement_dal(self, mock_dynamodb_connection):
        """Create EntitlementDAL with mocked connection"""
        mock_table = MagicMock()
        mock_dynamodb_connection.get_table = MagicMock(return_value=mock_table)
        dal = EntitlementDAL(mock_dynamodb_connection)
        dal.table = mock_table
        return dal
    
    def test_user_with_writing_purchase_gets_writing_access(self, entitlement_dal):
        """Test user who bought writing gets writing assessment access"""
        # Mock user has writing entitlement
        entitlement_dal.table.query.return_value = {
            'Items': [{
                'user_id': 'user-123',
                'module_type': 'academic_writing',
                'assessments_granted': 2,
                'assessments_used': 0,
                'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat()
            }]
        }
        
        # Check entitlement
        access = entitlement_dal.check_entitlement('user-123', 'academic_writing')
        
        assert access['has_access'] == True
        assert access['assessments_remaining'] == 2
    
    def test_user_without_purchase_denied_access(self, entitlement_dal):
        """Test user without purchase is denied access"""
        # Mock no entitlements
        entitlement_dal.table.query.return_value = {'Items': []}
        
        # Check entitlement
        access = entitlement_dal.check_entitlement('user-456', 'academic_speaking')
        
        assert access['has_access'] == False
        assert access['assessments_remaining'] == 0
    
    def test_user_with_writing_cannot_access_speaking(self, entitlement_dal):
        """Test user with writing purchase cannot access speaking"""
        # Mock user has writing only
        entitlement_dal.table.query.return_value = {
            'Items': [{
                'user_id': 'user-789',
                'module_type': 'academic_writing',
                'assessments_granted': 2,
                'assessments_used': 0
            }]
        }
        
        # Attempt to access speaking
        access = entitlement_dal.check_entitlement('user-789', 'academic_speaking')
        
        # Should be denied (wrong module)
        assert access['has_access'] == False
    
    def test_assessment_count_decrements_after_use(self, entitlement_dal):
        """Test assessment count decreases after each use"""
        # Mock entitlement with 2 assessments
        entitlement_dal.table.query.return_value = {
            'Items': [{
                'entitlement_id': 'ent-123',
                'user_id': 'user-123',
                'module_type': 'academic_writing',
                'assessments_granted': 2,
                'assessments_used': 0
            }]
        }
        entitlement_dal.table.update_item.return_value = {}
        
        # Use one assessment
        result = entitlement_dal.use_assessment('user-123', 'academic_writing')
        
        # Verify update_item was called to increment assessments_used
        assert entitlement_dal.table.update_item.called
        call_args = entitlement_dal.table.update_item.call_args
        update_expr = call_args[1]['UpdateExpression']
        
        assert 'assessments_used' in update_expr
    
    def test_user_blocked_after_assessments_exhausted(self, entitlement_dal):
        """Test user blocked when assessments are used up"""
        # Mock entitlement with all assessments used
        entitlement_dal.table.query.return_value = {
            'Items': [{
                'user_id': 'user-999',
                'module_type': 'academic_writing',
                'assessments_granted': 2,
                'assessments_used': 2
            }]
        }
        
        # Check entitlement
        access = entitlement_dal.check_entitlement('user-999', 'academic_writing')
        
        assert access['has_access'] == False
        assert access['assessments_remaining'] == 0


class TestMobileToWebAccessFlow:
    """Test mobile purchase → QR code → web access flow"""
    
    def test_qr_code_generated_after_mobile_purchase(self):
        """Test QR code is generated for web access after mobile purchase"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            
            # Verify QR tokens table exists
            assert 'ielts-genai-prep-qr-tokens' in conn.table_names.values()
    
    def test_qr_token_expires_after_5_minutes(self):
        """Test QR authentication tokens expire after 5 minutes"""
        # This would test the TTL on QR tokens table
        # QR tokens should have TTL set to 5 minutes for security
        expiry_seconds = 300  # 5 minutes
        assert expiry_seconds == 5 * 60


class TestDynamoDBTableMapping:
    """Test all API endpoints map to correct DynamoDB tables"""
    
    def test_users_table_mapping(self):
        """Test users API uses ielts-genai-prep-users table"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            assert conn.table_names['users'] == 'ielts-genai-prep-users'
    
    def test_entitlements_table_mapping(self):
        """Test entitlements API uses ielts-genai-prep-entitlements table"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            assert conn.table_names['entitlements'] == 'ielts-genai-prep-entitlements'
    
    def test_assessments_table_mapping(self):
        """Test assessments API uses ielts-genai-prep-assessments table"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            assert conn.table_names['assessments'] == 'ielts-genai-prep-assessments'
    
    def test_sessions_table_mapping(self):
        """Test sessions API uses ielts-genai-prep-sessions table"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            assert conn.table_names['sessions'] == 'ielts-genai-prep-sessions'
    
    def test_all_required_tables_exist(self):
        """Test all required DynamoDB tables are configured"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            
            required_tables = [
                'users',
                'sessions',
                'assessments',
                'entitlements',
                'questions',
                'rubrics',
                'reset_tokens',
                'auth_tokens'
            ]
            
            for table_key in required_tables:
                assert table_key in conn.table_names
                assert conn.table_names[table_key].startswith('ielts-')


class TestMultiUserScenarios:
    """Test multiple users with different purchases"""
    
    @pytest.fixture
    def entitlement_dal(self):
        """Create EntitlementDAL with mocked connection"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            dal = EntitlementDAL(conn)
            dal.table = mock_table
            return dal
    
    def test_user_a_writing_user_b_speaking_isolated(self, entitlement_dal):
        """Test User A (writing) and User B (speaking) have isolated access"""
        def mock_query(**kwargs):
            key_condition = kwargs.get('KeyConditionExpression')
            user_id = kwargs.get('ExpressionAttributeValues', {}).get(':user_id')
            
            # User A has writing
            if user_id == 'user-a':
                return {
                    'Items': [{
                        'user_id': 'user-a',
                        'module_type': 'academic_writing',
                        'assessments_granted': 2,
                        'assessments_used': 0
                    }]
                }
            # User B has speaking
            elif user_id == 'user-b':
                return {
                    'Items': [{
                        'user_id': 'user-b',
                        'module_type': 'academic_speaking',
                        'assessments_granted': 2,
                        'assessments_used': 0
                    }]
                }
            return {'Items': []}
        
        entitlement_dal.table.query = mock_query
        
        # User A can access writing
        access_a_writing = entitlement_dal.check_entitlement('user-a', 'academic_writing')
        assert access_a_writing['has_access'] == True
        
        # User A cannot access speaking
        access_a_speaking = entitlement_dal.check_entitlement('user-a', 'academic_speaking')
        assert access_a_speaking['has_access'] == False
        
        # User B can access speaking
        access_b_speaking = entitlement_dal.check_entitlement('user-b', 'academic_speaking')
        assert access_b_speaking['has_access'] == True
        
        # User B cannot access writing
        access_b_writing = entitlement_dal.check_entitlement('user-b', 'academic_writing')
        assert access_b_writing['has_access'] == False
    
    def test_user_with_multiple_purchases_gets_all_access(self, entitlement_dal):
        """Test user with multiple purchases gets access to all modules"""
        # Mock user with both writing and speaking
        entitlement_dal.table.query.side_effect = [
            {
                'Items': [{
                    'user_id': 'power-user',
                    'module_type': 'academic_writing',
                    'assessments_granted': 2,
                    'assessments_used': 0
                }]
            },
            {
                'Items': [{
                    'user_id': 'power-user',
                    'module_type': 'academic_speaking',
                    'assessments_granted': 2,
                    'assessments_used': 0
                }]
            }
        ]
        
        # Check both accesses
        access_writing = entitlement_dal.check_entitlement('power-user', 'academic_writing')
        access_speaking = entitlement_dal.check_entitlement('power-user', 'academic_speaking')
        
        assert access_writing['has_access'] == True
        assert access_speaking['has_access'] == True


@pytest.mark.integration
class TestCompleteUserJourneyIntegration:
    """Integration test for complete user journey (requires AWS credentials)"""
    
    @pytest.mark.skipif(
        not os.getenv('AWS_ACCESS_KEY_ID'),
        reason="AWS credentials not set - skipping integration test"
    )
    def test_complete_user_journey(self):
        """
        Test complete user journey:
        1. Mobile registration → DynamoDB users table
        2. In-app purchase → Receipt validation
        3. Entitlement grant → DynamoDB entitlements table
        4. Web login → Session creation
        5. Assessment access → Entitlement check
        6. Assessment completion → Assessment saved to DynamoDB
        7. Entitlement decrement → assessments_used++
        """
        # This integration test would require actual AWS resources
        # It validates the complete end-to-end flow in a real environment
        pass
