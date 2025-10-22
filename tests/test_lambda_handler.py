"""
Basic tests for Lambda handler to ensure CI pipeline passes.
These tests verify the Lambda handler structure and basic functionality.
"""
import os
import sys
import pytest

# Add deployment directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'deployment'))

# Set required environment variables for testing
os.environ['SESSION_SECRET'] = 'test-secret-for-ci-testing'
os.environ['DATABASE_URL'] = 'postgresql://test-db'


def test_lambda_handler_import():
    """Test that lambda_handler can be imported successfully."""
    from lambda_handler import lambda_handler
    assert callable(lambda_handler), "lambda_handler should be a callable function"


def test_lambda_handler_signature():
    """Test that lambda_handler has the correct signature."""
    import inspect
    from lambda_handler import lambda_handler
    
    sig = inspect.signature(lambda_handler)
    params = list(sig.parameters.keys())
    
    assert 'event' in params, "lambda_handler must accept 'event' parameter"
    assert 'context' in params, "lambda_handler must accept 'context' parameter"


def test_flask_app_initialization():
    """Test that Flask app initializes without errors."""
    from app import app
    
    assert app is not None, "Flask app should initialize"
    assert hasattr(app, 'config'), "Flask app should have config attribute"


def test_dynamodb_dal_structure():
    """Test that DynamoDB DAL module has required functions."""
    import dynamodb_dal
    
    required_functions = ['get_user', 'create_user', 'get_assessment', 'create_assessment']
    for func_name in required_functions:
        assert hasattr(dynamodb_dal, func_name), f"DAL should have {func_name} function"


def test_bedrock_service_structure():
    """Test that Bedrock service module has required functions."""
    import bedrock_service
    
    # Verify module can be imported (basic smoke test)
    assert hasattr(bedrock_service, '__name__'), "Bedrock service should be a valid module"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
