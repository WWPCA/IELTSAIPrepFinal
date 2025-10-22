"""
Environment Detection Utilities for IELTS GenAI Prep Platform

Provides centralized environment detection for AWS Lambda, Replit development,
and local development environments.
"""
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EnvironmentDetector:
    """Centralized environment detection for all deployment contexts"""
    
    def __init__(self):
        self._detected_env = None
        self._is_development = None
        self._is_lambda = None
        self._is_replit = None
        
    def detect_environment(self) -> str:
        """
        Detect the current runtime environment
        
        Returns:
            str: 'aws_lambda', 'replit_dev', 'local_dev'
        """
        if self._detected_env:
            return self._detected_env
            
        # AWS Lambda detection - multiple indicators
        lambda_indicators = [
            os.environ.get('AWS_EXECUTION_ENVIRONMENT'),  # Set to 'AWS_Lambda_python3.x'
            os.environ.get('LAMBDA_RUNTIME_DIR'),         # Lambda runtime directory
            os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),   # Function name
            os.environ.get('_LAMBDA_RUNTIME_LOAD_TIME'),  # Lambda load time
        ]
        
        if any(lambda_indicators):
            self._detected_env = 'aws_lambda'
            logger.info("[ENV] Detected AWS Lambda runtime environment")
            
        # Replit development environment
        elif os.environ.get('REPLIT_ENVIRONMENT') == 'true':
            self._detected_env = 'replit_dev' 
            logger.info("[ENV] Detected Replit development environment")
            
        # Local development fallback
        else:
            self._detected_env = 'local_dev'
            logger.info("[ENV] Detected local development environment")
            
        return self._detected_env
    
    def is_development(self) -> bool:
        """Check if running in any development environment"""
        if self._is_development is not None:
            return self._is_development
            
        env = self.detect_environment()
        self._is_development = env in ['replit_dev', 'local_dev']
        return self._is_development
    
    def is_production(self) -> bool:
        """Check if running in production (AWS Lambda)"""
        return not self.is_development()
    
    def is_aws_lambda(self) -> bool:
        """Check if running specifically in AWS Lambda"""
        if self._is_lambda is not None:
            return self._is_lambda
            
        env = self.detect_environment()
        self._is_lambda = (env == 'aws_lambda')
        return self._is_lambda
    
    def is_replit(self) -> bool:
        """Check if running in Replit environment"""
        if self._is_replit is not None:
            return self._is_replit
            
        env = self.detect_environment()
        self._is_replit = (env == 'replit_dev')
        return self._is_replit
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive environment information"""
        return {
            'environment': self.detect_environment(),
            'is_development': self.is_development(),
            'is_production': self.is_production(),
            'is_aws_lambda': self.is_aws_lambda(),
            'is_replit': self.is_replit(),
            'aws_region': os.environ.get('AWS_DEFAULT_REGION', os.environ.get('AWS_REGION')),
            'function_name': os.environ.get('AWS_LAMBDA_FUNCTION_NAME'),
            'runtime': os.environ.get('AWS_EXECUTION_ENVIRONMENT'),
            'stage': os.environ.get('STAGE', 'unknown')
        }
    
    def get_base_url(self) -> str:
        """Get the appropriate base URL for the current environment"""
        if self.is_aws_lambda():
            # AWS Lambda/API Gateway URL
            api_id = os.environ.get('AWS_API_GATEWAY_ID')
            region = os.environ.get('AWS_REGION', 'us-east-1')
            stage = os.environ.get('STAGE', 'prod')
            
            if api_id:
                return f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"
            else:
                # Fallback to production domain
                return "https://api.ieltsgenaiprep.com"
                
        elif self.is_replit():
            # Replit development URL
            return "https://replit-domain.replit.app"
            
        else:
            # Local development
            return "http://localhost:5000"
    
    def should_use_mock_services(self) -> bool:
        """Determine if mock services should be used instead of real AWS services"""
        return self.is_development()
    
    def get_log_level(self) -> str:
        """Get appropriate log level for environment"""
        if self.is_development():
            return "DEBUG"
        else:
            return "INFO"

# Global instance
_detector = EnvironmentDetector()

# Convenience functions for backward compatibility
def is_development() -> bool:
    """Check if running in development environment"""
    return _detector.is_development()

def is_production() -> bool:
    """Check if running in production environment"""
    return _detector.is_production()

def is_aws_lambda() -> bool:
    """Check if running in AWS Lambda"""
    return _detector.is_aws_lambda()

def is_replit() -> bool:
    """Check if running in Replit"""
    return _detector.is_replit()

def get_environment() -> str:
    """Get current environment string"""
    return _detector.detect_environment()

def get_environment_info() -> Dict[str, Any]:
    """Get comprehensive environment information"""
    return _detector.get_environment_info()

def get_base_url() -> str:
    """Get base URL for current environment"""
    return _detector.get_base_url()

# Initialize on import
if __name__ != "__main__":
    _detector.detect_environment()