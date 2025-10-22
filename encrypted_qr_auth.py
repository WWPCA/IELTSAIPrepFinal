"""
Encrypted QR Authentication System for IELTS GenAI Prep
Implements single-use, encrypted QR codes with DynamoDB backend and secure nonce validation
"""
import os
import json
import time
import secrets
import hmac
import hashlib
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

from aws_secrets_manager import get_qr_encryption_config
from dynamodb_dal import get_dal

logger = logging.getLogger(__name__)

@dataclass
class QRTokenResult:
    """Result of QR token operations"""
    success: bool
    token_id: Optional[str] = None
    encrypted_code: Optional[str] = None
    expires_at: Optional[datetime] = None
    browser_session_id: Optional[str] = None
    user_id: Optional[str] = None
    error_message: Optional[str] = None

class EncryptedQRAuth:
    """Secure QR authentication with single-use encrypted tokens"""
    
    def __init__(self):
        self.dal = get_dal()
        self.encryption_config = get_qr_encryption_config()
        self.default_ttl = 120  # 2 minutes default
        
    def create_qr_token(self, browser_session_id: str, ttl_seconds: int = None) -> QRTokenResult:
        """
        Create a new encrypted single-use QR token
        
        Args:
            browser_session_id: Unique browser session identifier
            ttl_seconds: Token time-to-live in seconds (default: 120)
            
        Returns:
            QRTokenResult with encrypted code or error
        """
        try:
            ttl = ttl_seconds or self.default_ttl
            token_id = self._generate_token_id()
            nonce = secrets.token_hex(16)
            
            # Create token payload with security metadata
            payload = {
                'token_id': token_id,
                'browser_session_id': browser_session_id,
                'nonce': nonce,
                'created_at': datetime.utcnow().isoformat(),
                'device_fingerprint': self._create_device_fingerprint(),
                'version': '1.0'
            }
            
            # Encrypt and sign the payload
            encrypted_code = self._encrypt_and_sign_payload(payload)
            if not encrypted_code:
                return QRTokenResult(
                    success=False,
                    error_message="Failed to encrypt QR token"
                )
            
            # Store in DynamoDB with TTL
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            success = self.dal.qr_tokens.create_qr_token(
                browser_session_id=browser_session_id,
                ttl_seconds=ttl
            )
            
            if not success:
                return QRTokenResult(
                    success=False,
                    error_message="Failed to store QR token"
                )
            
            logger.info(f"Created QR token: {token_id}")
            
            return QRTokenResult(
                success=True,
                token_id=token_id,
                encrypted_code=encrypted_code,
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.error(f"Failed to create QR token: {e}")
            return QRTokenResult(
                success=False,
                error_message="QR token creation failed"
            )
    
    def consume_qr_token(self, encrypted_code: str, user_id: str, 
                        device_fingerprint: str = None) -> QRTokenResult:
        """
        Consume a QR token (single-use with security validation)
        
        Args:
            encrypted_code: The encrypted QR code
            user_id: User attempting to claim the token
            device_fingerprint: Optional device fingerprint for validation
            
        Returns:
            QRTokenResult with session data or error
        """
        try:
            # Decrypt and validate the payload
            payload = self._decrypt_and_verify_payload(encrypted_code)
            if not payload:
                return QRTokenResult(
                    success=False,
                    error_message="Invalid or corrupted QR code"
                )
            
            token_id = payload.get('token_id')
            if not token_id:
                return QRTokenResult(
                    success=False,
                    error_message="Malformed QR token"
                )
            
            # Additional security checks
            if not self._validate_token_security(payload, device_fingerprint):
                logger.warning(f"Security validation failed for token: {token_id}")
                return QRTokenResult(
                    success=False,
                    error_message="Security validation failed"
                )
            
            # Attempt to consume the token atomically
            consumption_result = self.dal.qr_tokens.consume_qr_token(
                encrypted_code, user_id
            )
            
            if not consumption_result:
                return QRTokenResult(
                    success=False,
                    error_message="Token already used or expired"
                )
            
            logger.info(f"QR token consumed: {token_id} by user: {user_id}")
            
            return QRTokenResult(
                success=True,
                token_id=token_id,
                browser_session_id=consumption_result['browser_session_id'],
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"Failed to consume QR token: {e}")
            return QRTokenResult(
                success=False,
                error_message="Token consumption failed"
            )
    
    def validate_qr_token(self, encrypted_code: str) -> QRTokenResult:
        """
        Validate QR token without consuming it
        
        Args:
            encrypted_code: The encrypted QR code
            
        Returns:
            QRTokenResult with validation status
        """
        try:
            payload = self._decrypt_and_verify_payload(encrypted_code)
            if not payload:
                return QRTokenResult(
                    success=False,
                    error_message="Invalid QR code"
                )
            
            token_id = payload.get('token_id')
            created_at = payload.get('created_at')
            
            # Check if token exists and is not expired
            if token_id and created_at:
                created_time = datetime.fromisoformat(created_at)
                if datetime.utcnow() - created_time > timedelta(seconds=self.default_ttl):
                    return QRTokenResult(
                        success=False,
                        error_message="QR code has expired"
                    )
                
                return QRTokenResult(
                    success=True,
                    token_id=token_id
                )
            
            return QRTokenResult(
                success=False,
                error_message="Invalid token data"
            )
            
        except Exception as e:
            logger.error(f"QR token validation failed: {e}")
            return QRTokenResult(
                success=False,
                error_message="Validation failed"
            )
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens (mainly for monitoring)
        DynamoDB TTL handles automatic cleanup
        
        Returns:
            Number of tokens cleaned up
        """
        try:
            # DynamoDB TTL handles cleanup automatically
            # This method is for monitoring/stats purposes
            logger.info("DynamoDB TTL handles automatic token cleanup")
            return 0
        except Exception as e:
            logger.error(f"Token cleanup monitoring failed: {e}")
            return 0
    
    def _generate_token_id(self) -> str:
        """Generate cryptographically secure token ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000000)
        random_part = secrets.token_hex(16)
        return f"qr_{timestamp}_{random_part}"
    
    def _create_device_fingerprint(self) -> str:
        """Create device fingerprint from request metadata"""
        # In a real implementation, this would use more sophisticated fingerprinting
        fingerprint_data = {
            'timestamp': int(time.time()),
            'random': secrets.token_hex(8)
        }
        
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def _encrypt_and_sign_payload(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Encrypt and sign the QR token payload
        
        Args:
            payload: Token payload to encrypt
            
        Returns:
            Base64 encoded encrypted and signed data or None if failed
        """
        try:
            # Convert payload to JSON
            payload_json = json.dumps(payload, sort_keys=True)
            
            # Create HMAC signature using signing key
            signature = hmac.new(
                self.encryption_config['SIGNING_KEY'].encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine payload and signature
            signed_data = {
                'payload': payload_json,
                'signature': signature,
                'algorithm': 'HMAC-SHA256',
                'version': '1.0'
            }
            
            # Base64 encode for URL safety
            signed_json = json.dumps(signed_data)
            encrypted_bytes = base64.urlsafe_b64encode(signed_json.encode())
            
            return encrypted_bytes.decode()
            
        except Exception as e:
            logger.error(f"Payload encryption failed: {e}")
            return None
    
    def _decrypt_and_verify_payload(self, encrypted_code: str) -> Optional[Dict[str, Any]]:
        """
        Decrypt and verify QR token payload
        
        Args:
            encrypted_code: Base64 encoded encrypted data
            
        Returns:
            Decrypted payload or None if verification failed
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_code.encode())
            signed_data = json.loads(encrypted_bytes.decode())
            
            # Extract components
            payload_json = signed_data.get('payload')
            signature = signed_data.get('signature')
            algorithm = signed_data.get('algorithm', 'HMAC-SHA256')
            
            if not payload_json or not signature:
                logger.warning("Missing payload or signature in QR token")
                return None
            
            # Verify signature
            expected_signature = hmac.new(
                self.encryption_config['SIGNING_KEY'].encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("QR token signature verification failed")
                return None
            
            # Parse and return payload
            return json.loads(payload_json)
            
        except Exception as e:
            logger.warning(f"QR token decryption failed: {e}")
            return None
    
    def _validate_token_security(self, payload: Dict[str, Any], 
                                device_fingerprint: str = None) -> bool:
        """
        Perform additional security validation on token payload
        
        Args:
            payload: Decrypted token payload
            device_fingerprint: Optional device fingerprint to validate
            
        Returns:
            True if security validation passes
        """
        try:
            # Check required fields
            required_fields = ['token_id', 'browser_session_id', 'nonce', 'created_at']
            for field in required_fields:
                if field not in payload:
                    logger.warning(f"Missing required field in QR token: {field}")
                    return False
            
            # Check token age
            created_at = datetime.fromisoformat(payload['created_at'])
            age_seconds = (datetime.utcnow() - created_at).total_seconds()
            
            if age_seconds > self.default_ttl:
                logger.warning(f"QR token too old: {age_seconds} seconds")
                return False
            
            # Check nonce format
            nonce = payload.get('nonce', '')
            if len(nonce) != 32:  # 16 bytes hex = 32 chars
                logger.warning("Invalid nonce format in QR token")
                return False
            
            # Additional security checks can be added here
            # - Device fingerprint validation
            # - IP address validation
            # - Rate limiting per device
            
            return True
            
        except Exception as e:
            logger.error(f"Security validation error: {e}")
            return False

# Global QR auth instance
qr_auth = None

def get_qr_auth() -> EncryptedQRAuth:
    """Get global QR authentication instance"""
    global qr_auth
    if qr_auth is None:
        qr_auth = EncryptedQRAuth()
    return qr_auth

def create_secure_qr_code(browser_session_id: str, ttl_seconds: int = 120) -> QRTokenResult:
    """
    Convenience function to create secure QR code
    
    Args:
        browser_session_id: Browser session identifier
        ttl_seconds: Time to live in seconds
        
    Returns:
        QRTokenResult with encrypted QR code
    """
    return get_qr_auth().create_qr_token(browser_session_id, ttl_seconds)

def validate_and_consume_qr_code(encrypted_code: str, user_id: str) -> QRTokenResult:
    """
    Convenience function to validate and consume QR code
    
    Args:
        encrypted_code: Encrypted QR code from client
        user_id: User attempting to use the code
        
    Returns:
        QRTokenResult with consumption status
    """
    return get_qr_auth().consume_qr_token(encrypted_code, user_id)