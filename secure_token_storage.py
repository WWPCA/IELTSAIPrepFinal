"""
Secure Token Storage - DynamoDB-backed token management with TTL and atomic operations
Replaces in-memory token storage for production-grade security
"""

import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
import os

logger = logging.getLogger(__name__)

# Environment detection
try:
    from environment_utils import is_development
    IS_DEVELOPMENT = is_development()
except ImportError:
    IS_DEVELOPMENT = True

# DynamoDB connection
try:
    if not IS_DEVELOPMENT:
        import boto3
        region = os.environ.get('AWS_REGION', 'us-east-1')
        dynamodb = boto3.resource('dynamodb', region_name=region)
        DYNAMODB_AVAILABLE = True
    else:
        from aws_mock_config import aws_mock
        dynamodb = aws_mock
        DYNAMODB_AVAILABLE = False
except ImportError:
    dynamodb = None
    DYNAMODB_AVAILABLE = False

class SecureTokenStorage:
    """DynamoDB-backed secure token storage with TTL and atomic operations"""
    
    def __init__(self):
        self.tokens_table_name = 'ielts-genai-prep-secure-tokens'
        self.sessions_table_name = 'ielts-genai-prep-sessions'
        
        # Fallback storage for development
        if not DYNAMODB_AVAILABLE:
            self._dev_tokens = {}
            self._dev_sessions = {}
    
    def store_qr_token(self, token: str, data: Dict[str, Any], ttl_seconds: int = 300) -> bool:
        """Store QR token with TTL and one-time use flag"""
        try:
            token_data = {
                'token_id': token,
                'data': data,
                'created_at': int(time.time()),
                'expires_at': int(time.time()) + ttl_seconds,
                'used': False,
                'token_type': 'qr_auth',
                'ttl': int(time.time()) + ttl_seconds  # DynamoDB TTL
            }
            
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.tokens_table_name)
                
                # Use conditional put to prevent overwrites
                table.put_item(
                    Item=token_data,
                    ConditionExpression='attribute_not_exists(token_id)'
                )
                
                logger.info(f"QR token stored in DynamoDB: {token[:8]}...")
                return True
            else:
                # Development fallback
                self._dev_tokens[token] = token_data
                logger.info(f"QR token stored in development cache: {token[:8]}...")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store QR token: {e}")
            return False
    
    def validate_and_consume_qr_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate QR token and mark as used (atomic operation)"""
        try:
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.tokens_table_name)
                
                # Get current token
                response = table.get_item(Key={'token_id': token})
                
                if 'Item' not in response:
                    return False, None
                
                item = response['Item']
                
                # Check expiration and usage
                current_time = int(time.time())
                if item.get('used', True) or current_time > item.get('expires_at', 0):
                    return False, None
                
                # Atomic update: mark as used only if still unused
                try:
                    table.update_item(
                        Key={'token_id': token},
                        UpdateExpression='SET used = :used_val',
                        ConditionExpression='used = :not_used',
                        ExpressionAttributeValues={
                            ':used_val': True,
                            ':not_used': False
                        }
                    )
                    
                    logger.info(f"QR token consumed: {token[:8]}...")
                    return True, item.get('data')
                    
                except Exception as e:
                    # Token was already used by another request
                    logger.warning(f"QR token already consumed: {token[:8]}...")
                    return False, None
            else:
                # Development fallback
                if token not in self._dev_tokens:
                    return False, None
                
                token_data = self._dev_tokens[token]
                current_time = int(time.time())
                
                if token_data.get('used', True) or current_time > token_data.get('expires_at', 0):
                    return False, None
                
                # Mark as used
                token_data['used'] = True
                logger.info(f"QR token consumed (dev): {token[:8]}...")
                return True, token_data.get('data')
                
        except Exception as e:
            logger.error(f"Failed to validate QR token: {e}")
            return False, None
    
    def store_session(self, session_id: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Store secure session with TTL"""
        try:
            session_data = {
                'session_id': session_id,
                'data': data,
                'created_at': int(time.time()),
                'expires_at': int(time.time()) + ttl_seconds,
                'ttl': int(time.time()) + ttl_seconds
            }
            
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.sessions_table_name)
                table.put_item(Item=session_data)
                logger.info(f"Session stored in DynamoDB: {session_id[:8]}...")
                return True
            else:
                # Development fallback
                self._dev_sessions[session_id] = session_data
                logger.info(f"Session stored in development cache: {session_id[:8]}...")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data if valid and not expired"""
        try:
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.sessions_table_name)
                response = table.get_item(Key={'session_id': session_id})
                
                if 'Item' not in response:
                    return None
                
                item = response['Item']
                current_time = int(time.time())
                
                if current_time > item.get('expires_at', 0):
                    # Session expired, clean up
                    try:
                        table.delete_item(Key={'session_id': session_id})
                    except:
                        pass
                    return None
                
                return item.get('data')
            else:
                # Development fallback
                if session_id not in self._dev_sessions:
                    return None
                
                session_data = self._dev_sessions[session_id]
                current_time = int(time.time())
                
                if current_time > session_data.get('expires_at', 0):
                    # Session expired
                    del self._dev_sessions[session_id]
                    return None
                
                return session_data.get('data')
                
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke/delete session"""
        try:
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.sessions_table_name)
                table.delete_item(Key={'session_id': session_id})
                logger.info(f"Session revoked: {session_id[:8]}...")
                return True
            else:
                # Development fallback
                if session_id in self._dev_sessions:
                    del self._dev_sessions[session_id]
                    logger.info(f"Session revoked (dev): {session_id[:8]}...")
                return True
                
        except Exception as e:
            logger.error(f"Failed to revoke session: {e}")
            return False
    
    def store_password_reset_token(self, token: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> bool:
        """Store password reset token with TTL"""
        try:
            token_data = {
                'token_id': token,
                'data': data,
                'created_at': int(time.time()),
                'expires_at': int(time.time()) + ttl_seconds,
                'used': False,
                'token_type': 'password_reset',
                'ttl': int(time.time()) + ttl_seconds
            }
            
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.tokens_table_name)
                table.put_item(
                    Item=token_data,
                    ConditionExpression='attribute_not_exists(token_id)'
                )
                logger.info(f"Password reset token stored: {token[:8]}...")
                return True
            else:
                # Development fallback
                self._dev_tokens[token] = token_data
                logger.info(f"Password reset token stored (dev): {token[:8]}...")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store password reset token: {e}")
            return False
    
    def validate_and_consume_password_reset_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate password reset token and mark as used"""
        try:
            if DYNAMODB_AVAILABLE:
                table = dynamodb.Table(self.tokens_table_name)
                
                # Get current token
                response = table.get_item(Key={'token_id': token})
                
                if 'Item' not in response:
                    return False, None
                
                item = response['Item']
                
                # Check expiration, usage, and type
                current_time = int(time.time())
                if (item.get('used', True) or 
                    current_time > item.get('expires_at', 0) or 
                    item.get('token_type') != 'password_reset'):
                    return False, None
                
                # Atomic update: mark as used
                try:
                    table.update_item(
                        Key={'token_id': token},
                        UpdateExpression='SET used = :used_val',
                        ConditionExpression='used = :not_used',
                        ExpressionAttributeValues={
                            ':used_val': True,
                            ':not_used': False
                        }
                    )
                    
                    logger.info(f"Password reset token consumed: {token[:8]}...")
                    return True, item.get('data')
                    
                except Exception:
                    # Token already used
                    return False, None
            else:
                # Development fallback
                if token not in self._dev_tokens:
                    return False, None
                
                token_data = self._dev_tokens[token]
                current_time = int(time.time())
                
                if (token_data.get('used', True) or 
                    current_time > token_data.get('expires_at', 0) or 
                    token_data.get('token_type') != 'password_reset'):
                    return False, None
                
                # Mark as used
                token_data['used'] = True
                logger.info(f"Password reset token consumed (dev): {token[:8]}...")
                return True, token_data.get('data')
                
        except Exception as e:
            logger.error(f"Failed to validate password reset token: {e}")
            return False, None

# Global instance
secure_storage = SecureTokenStorage()

# Export
__all__ = ['SecureTokenStorage', 'secure_storage']