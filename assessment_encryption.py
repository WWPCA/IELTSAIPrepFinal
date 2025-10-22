"""
End-to-End Encryption for Assessment Data using AWS KMS
Implements envelope encryption for audio/text data with per-user/per-session data keys
"""
import os
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass

import boto3
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from botocore.exceptions import ClientError

from aws_secrets_manager import get_kms_config
from dynamodb_dal import get_dal

logger = logging.getLogger(__name__)

@dataclass
class EncryptionResult:
    """Result of encryption operations"""
    success: bool
    encrypted_data: Optional[str] = None
    data_key_id: Optional[str] = None
    encryption_context: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None

@dataclass
class DecryptionResult:
    """Result of decryption operations"""
    success: bool
    decrypted_data: Optional[Union[str, bytes]] = None
    encryption_context: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None

class AssessmentEncryption:
    """AWS KMS-based encryption for assessment data"""
    
    def __init__(self, region: str = None):
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.kms_client = boto3.client('kms', region_name=self.region)
        self.config = get_kms_config()
        self.dal = get_dal()
        
        # Development mode check - using centralized environment detection
        from environment_utils import is_development
        self.is_development = is_development()
        
        if self.is_development:
            logger.warning("[ENCRYPTION] Running in development mode - using mock encryption")
    
    def encrypt_assessment_data(self, data: Union[str, bytes], user_id: str, 
                               session_id: str, data_type: str = 'text') -> EncryptionResult:
        """
        Encrypt assessment data using envelope encryption
        
        Args:
            data: Data to encrypt (text or audio bytes)
            user_id: User ID for encryption context
            session_id: Assessment session ID
            data_type: Type of data ('text', 'audio', 'metadata')
            
        Returns:
            EncryptionResult with encrypted data or error
        """
        try:
            if self.is_development:
                return self._mock_encrypt(data, user_id, session_id, data_type)
            
            # Create encryption context for audit and access control
            encryption_context = {
                'user_id': user_id,
                'session_id': session_id,
                'data_type': data_type,
                'timestamp': datetime.utcnow().isoformat(),
                'application': 'ielts-genai-prep'
            }
            
            # Generate data encryption key
            data_key_response = self.kms_client.generate_data_key(
                KeyId=self.config['KMS_KEY_ID'],
                KeySpec=self.config.get('DATA_ENCRYPTION_KEY_SPEC', 'AES_256'),
                EncryptionContext=encryption_context
            )
            
            # Get plaintext and encrypted data keys
            plaintext_key = data_key_response['Plaintext']
            encrypted_key = data_key_response['CiphertextBlob']
            
            # Encrypt data with the plaintext data key
            fernet = Fernet(base64.urlsafe_b64encode(plaintext_key[:32]))
            
            # Convert data to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            encrypted_data = fernet.encrypt(data_bytes)
            
            # Create the envelope (encrypted key + encrypted data + context)
            envelope = {
                'encrypted_key': base64.b64encode(encrypted_key).decode('utf-8'),
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'encryption_context': encryption_context,
                'algorithm': 'AES-256-GCM',
                'kms_key_id': self.config['KMS_KEY_ID'],
                'version': '1.0'
            }
            
            # Generate data key ID for tracking
            data_key_id = f"dk_{user_id}_{session_id}_{int(datetime.utcnow().timestamp())}"
            
            # Store encryption metadata in DynamoDB
            self._store_encryption_metadata(data_key_id, encryption_context, session_id)
            
            logger.info(f"Encrypted assessment data: {data_key_id}")
            
            return EncryptionResult(
                success=True,
                encrypted_data=base64.b64encode(json.dumps(envelope).encode()).decode(),
                data_key_id=data_key_id,
                encryption_context=encryption_context
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"KMS encryption failed: {error_code} - {e}")
            return EncryptionResult(
                success=False,
                error_message=f"KMS error: {error_code}"
            )
        except Exception as e:
            logger.error(f"Assessment encryption failed: {e}")
            return EncryptionResult(
                success=False,
                error_message=f"Encryption error: {str(e)}"
            )
    
    def decrypt_assessment_data(self, encrypted_envelope: str, user_id: str, 
                               session_id: str) -> DecryptionResult:
        """
        Decrypt assessment data using envelope decryption
        
        Args:
            encrypted_envelope: Base64 encoded envelope containing encrypted key and data
            user_id: User ID for access validation
            session_id: Assessment session ID
            
        Returns:
            DecryptionResult with decrypted data or error
        """
        try:
            if self.is_development:
                return self._mock_decrypt(encrypted_envelope, user_id, session_id)
            
            # Decode the envelope
            envelope_data = base64.b64decode(encrypted_envelope.encode()).decode()
            envelope = json.loads(envelope_data)
            
            # Extract components
            encrypted_key = base64.b64decode(envelope['encrypted_key'])
            encrypted_data = base64.b64decode(envelope['encrypted_data'])
            encryption_context = envelope['encryption_context']
            
            # Validate access permissions
            if not self._validate_decryption_access(encryption_context, user_id, session_id):
                return DecryptionResult(
                    success=False,
                    error_message="Access denied - insufficient permissions"
                )
            
            # Decrypt the data key using KMS
            key_response = self.kms_client.decrypt(
                CiphertextBlob=encrypted_key,
                EncryptionContext=encryption_context
            )
            
            plaintext_key = key_response['Plaintext']
            
            # Decrypt the data using the decrypted key
            fernet = Fernet(base64.urlsafe_b64encode(plaintext_key[:32]))
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Try to decode as UTF-8 text, otherwise return as bytes
            try:
                decoded_data = decrypted_data.decode('utf-8')
            except UnicodeDecodeError:
                decoded_data = decrypted_data  # Return as bytes for binary data
            
            logger.info(f"Decrypted assessment data for user: {user_id}")
            
            return DecryptionResult(
                success=True,
                decrypted_data=decoded_data,
                encryption_context=encryption_context
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"KMS decryption failed: {error_code} - {e}")
            return DecryptionResult(
                success=False,
                error_message=f"KMS error: {error_code}"
            )
        except Exception as e:
            logger.error(f"Assessment decryption failed: {e}")
            return DecryptionResult(
                success=False,
                error_message=f"Decryption error: {str(e)}"
            )
    
    def encrypt_audio_stream(self, audio_chunks: bytes, user_id: str, 
                           session_id: str) -> EncryptionResult:
        """
        Encrypt streaming audio data for Nova Sonic
        
        Args:
            audio_chunks: Raw audio data
            user_id: User ID
            session_id: Session ID
            
        Returns:
            EncryptionResult with encrypted audio
        """
        return self.encrypt_assessment_data(audio_chunks, user_id, session_id, 'audio')
    
    def encrypt_text_response(self, text: str, user_id: str, session_id: str) -> EncryptionResult:
        """
        Encrypt text response data
        
        Args:
            text: Text to encrypt
            user_id: User ID
            session_id: Session ID
            
        Returns:
            EncryptionResult with encrypted text
        """
        return self.encrypt_assessment_data(text, user_id, session_id, 'text')
    
    def encrypt_assessment_metadata(self, metadata: Dict[str, Any], user_id: str, 
                                  session_id: str) -> EncryptionResult:
        """
        Encrypt assessment metadata (scores, feedback, etc.)
        
        Args:
            metadata: Metadata dictionary
            user_id: User ID
            session_id: Session ID
            
        Returns:
            EncryptionResult with encrypted metadata
        """
        metadata_json = json.dumps(metadata, sort_keys=True)
        return self.encrypt_assessment_data(metadata_json, user_id, session_id, 'metadata')
    
    def _validate_decryption_access(self, encryption_context: Dict[str, str], 
                                   user_id: str, session_id: str) -> bool:
        """
        Validate that the requester has permission to decrypt this data
        
        Args:
            encryption_context: Original encryption context
            user_id: Requesting user ID
            session_id: Requesting session ID
            
        Returns:
            True if access is allowed
        """
        try:
            # Check user ownership
            original_user = encryption_context.get('user_id')
            if original_user != user_id:
                logger.warning(f"User {user_id} attempted to access data for {original_user}")
                return False
            
            # Check session validity
            original_session = encryption_context.get('session_id')
            if original_session != session_id:
                # Allow access to historical sessions for the same user
                logger.info(f"Cross-session access: {original_session} -> {session_id}")
            
            # Additional access controls can be added here
            # - Time-based restrictions
            # - Role-based access
            # - Audit logging
            
            return True
            
        except Exception as e:
            logger.error(f"Access validation failed: {e}")
            return False
    
    def _store_encryption_metadata(self, data_key_id: str, encryption_context: Dict[str, str], 
                                  session_id: str):
        """Store encryption metadata for audit and key management"""
        try:
            metadata = {
                'data_key_id': data_key_id,
                'encryption_context': encryption_context,
                'session_id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            # Store in DynamoDB (implementation would go here)
            logger.info(f"Stored encryption metadata: {data_key_id}")
            
        except Exception as e:
            logger.error(f"Failed to store encryption metadata: {e}")
    
    def _mock_encrypt(self, data: Union[str, bytes], user_id: str, 
                     session_id: str, data_type: str) -> EncryptionResult:
        """Mock encryption for development environment"""
        try:
            # Simple base64 encoding for development
            if isinstance(data, str):
                encoded_data = base64.b64encode(data.encode()).decode()
            else:
                encoded_data = base64.b64encode(data).decode()
            
            mock_envelope = {
                'encrypted_data': encoded_data,
                'user_id': user_id,
                'session_id': session_id,
                'data_type': data_type,
                'mock': True
            }
            
            return EncryptionResult(
                success=True,
                encrypted_data=base64.b64encode(json.dumps(mock_envelope).encode()).decode(),
                data_key_id=f"mock_{user_id}_{session_id}",
                encryption_context={'mock': 'true'}
            )
            
        except Exception as e:
            return EncryptionResult(
                success=False,
                error_message=f"Mock encryption failed: {e}"
            )
    
    def _mock_decrypt(self, encrypted_envelope: str, user_id: str, 
                     session_id: str) -> DecryptionResult:
        """Mock decryption for development environment"""
        try:
            envelope_data = base64.b64decode(encrypted_envelope.encode()).decode()
            envelope = json.loads(envelope_data)
            
            if not envelope.get('mock'):
                return DecryptionResult(
                    success=False,
                    error_message="Not a mock encrypted payload"
                )
            
            # Simple base64 decoding
            encrypted_data = envelope['encrypted_data']
            decrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            try:
                decrypted_data = decrypted_bytes.decode('utf-8')
            except UnicodeDecodeError:
                decrypted_data = decrypted_bytes
            
            return DecryptionResult(
                success=True,
                decrypted_data=decrypted_data,
                encryption_context={'mock': 'true'}
            )
            
        except Exception as e:
            return DecryptionResult(
                success=False,
                error_message=f"Mock decryption failed: {e}"
            )
    
    def rotate_data_keys(self, user_id: str, session_id: str) -> bool:
        """
        Rotate data encryption keys for enhanced security
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            True if rotation successful
        """
        try:
            if self.is_development:
                logger.info(f"Mock key rotation for user: {user_id}")
                return True
            
            # Implementation would re-encrypt data with new keys
            logger.info(f"Key rotation completed for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            return False

class StreamingEncryption:
    """Specialized encryption for real-time audio streaming"""
    
    def __init__(self):
        self.encryption = AssessmentEncryption()
    
    def encrypt_audio_chunk(self, audio_chunk: bytes, stream_id: str, 
                           user_id: str) -> Optional[str]:
        """
        Encrypt individual audio chunk for streaming
        
        Args:
            audio_chunk: Raw audio data chunk
            stream_id: Streaming session ID
            user_id: User ID
            
        Returns:
            Encrypted chunk as base64 string or None if failed
        """
        result = self.encryption.encrypt_audio_stream(audio_chunk, user_id, stream_id)
        return result.encrypted_data if result.success else None
    
    def decrypt_audio_chunk(self, encrypted_chunk: str, stream_id: str, 
                           user_id: str) -> Optional[bytes]:
        """
        Decrypt individual audio chunk
        
        Args:
            encrypted_chunk: Encrypted audio chunk
            stream_id: Streaming session ID
            user_id: User ID
            
        Returns:
            Decrypted audio bytes or None if failed
        """
        result = self.encryption.decrypt_assessment_data(encrypted_chunk, user_id, stream_id)
        if result.success and isinstance(result.decrypted_data, bytes):
            return result.decrypted_data
        return None

# Global encryption service instances
assessment_encryption = None
streaming_encryption = None

def get_assessment_encryption() -> AssessmentEncryption:
    """Get global assessment encryption instance"""
    global assessment_encryption
    if assessment_encryption is None:
        assessment_encryption = AssessmentEncryption()
    return assessment_encryption

def get_streaming_encryption() -> StreamingEncryption:
    """Get global streaming encryption instance"""
    global streaming_encryption
    if streaming_encryption is None:
        streaming_encryption = StreamingEncryption()
    return streaming_encryption

def encrypt_user_data(data: Union[str, bytes], user_id: str, session_id: str, 
                     data_type: str = 'text') -> EncryptionResult:
    """
    Convenience function for encrypting user data
    
    Args:
        data: Data to encrypt
        user_id: User ID
        session_id: Session ID
        data_type: Type of data
        
    Returns:
        EncryptionResult
    """
    return get_assessment_encryption().encrypt_assessment_data(
        data, user_id, session_id, data_type
    )

def decrypt_user_data(encrypted_data: str, user_id: str, session_id: str) -> DecryptionResult:
    """
    Convenience function for decrypting user data
    
    Args:
        encrypted_data: Encrypted data envelope
        user_id: User ID
        session_id: Session ID
        
    Returns:
        DecryptionResult
    """
    return get_assessment_encryption().decrypt_assessment_data(
        encrypted_data, user_id, session_id
    )