"""
AWS Lambda Handler for IELTS GenAI Prep Platform
Adapts Flask WSGI application for AWS Lambda + API Gateway deployment
"""
import json
import logging
import base64
import io
import sys
from urllib.parse import unquote, urlparse, parse_qs
from typing import Any, Dict
from app import app

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function
    
    Handles both API Gateway REST API and HTTP API events,
    routing them to the Flask application via awsgi adapter.
    
    Args:
        event: API Gateway event
        context: Lambda context object
        
    Returns:
        API Gateway compatible response
    """
    try:
        # Log incoming request for debugging
        logger.info(f"Lambda invocation - Path: {event.get('path', 'unknown')}")
        logger.info(f"HTTP Method: {event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'unknown'))}")
        
        # Handle different API Gateway event formats
        if 'version' in event and event['version'] == '2.0':
            # HTTP API (v2.0) format
            logger.info("Processing HTTP API v2.0 event")
        else:
            # REST API (v1.0) format or WebSocket
            logger.info("Processing REST API v1.0 event")
        
        # Convert Lambda event to WSGI environment
        environ = _build_wsgi_environ(event, context)
        
        # Create response buffer  
        response_buffer = io.BytesIO()
        response_buffer.status = None
        response_buffer.headers = None
        
        # WSGI response handler
        def start_response(status, headers, exc_info=None):
            response_buffer.status = status
            response_buffer.headers = headers
            return response_buffer.write
        
        # Call WSGI application
        response_iter = app(environ, start_response)
        
        # Build response data properly handling bytes
        response_data = b''
        for chunk in response_iter:
            if isinstance(chunk, bytes):
                response_data += chunk
            else:
                response_data += chunk.encode('utf-8')
        
        # Parse status code
        status_code = int(response_buffer.status.split(' ')[0])
        
        # Preserve multi-value headers (critical for Set-Cookie)
        headers_dict = {}
        cookies = []
        
        for header_name, header_value in response_buffer.headers:
            if header_name.lower() == 'set-cookie':
                cookies.append(header_value)
            else:
                # Handle duplicate headers by keeping last value
                headers_dict[header_name] = header_value
        
        # Handle binary vs text content
        is_base64 = False
        try:
            # Try to decode as UTF-8 text
            response_body = response_data.decode('utf-8')
            
            # Check content type for binary content
            content_type = headers_dict.get('Content-Type', headers_dict.get('content-type', '')).lower()
            if any(ct in content_type for ct in ['image/', 'audio/', 'video/', 'application/pdf', 'application/octet-stream']):
                response_body = base64.b64encode(response_data).decode('utf-8')
                is_base64 = True
        except UnicodeDecodeError:
            # Binary content - encode as base64
            response_body = base64.b64encode(response_data).decode('utf-8')
            is_base64 = True
        
        # Build Lambda response with proper multi-value header support
        response = {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': response_body,
            'isBase64Encoded': is_base64
        }
        
        # Add multi-value headers for API Gateway v1 format
        if cookies:
            response['multiValueHeaders'] = {'Set-Cookie': cookies}
        
        # Log successful response
        logger.info(f"Response status: {response.get('statusCode', 'unknown')}")
        
        return response
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        
        # Return error response in API Gateway format
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Lambda function encountered an error',
                'requestId': context.aws_request_id if context else 'unknown'
            })
        }

def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Dedicated health check handler for AWS Load Balancer health checks
    """
    try:
        # Perform basic health checks
        from dynamodb_dal import get_dal
        
        # Test DynamoDB connection
        dal = get_dal()
        health_status = {
            'status': 'healthy',
            'timestamp': context.get_remaining_time_in_millis() if context else 0,
            'services': {
                'dynamodb': 'connected',
                'flask_app': 'running'
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(health_status)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'}, 
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e)
            })
        }

# For local testing and debugging
def _build_wsgi_environ(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Convert API Gateway event to WSGI environ dict"""
    
    # Handle both REST API and HTTP API formats
    path = event.get('path', '/')
    method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
    query_string = event.get('queryStringParameters') or {}
    headers = event.get('headers') or {}
    body = event.get('body', '')
    is_base64 = event.get('isBase64Encoded', False)
    
    # Decode body if base64 encoded
    if is_base64 and body:
        body = base64.b64decode(body).decode('utf-8')
    
    # Build query string
    query_string_encoded = '&'.join([f"{k}={v}" for k, v in query_string.items()])
    
    # Create WSGI environ
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': unquote(path),
        'QUERY_STRING': query_string_encoded,
        'CONTENT_TYPE': headers.get('Content-Type', headers.get('content-type', '')),
        'CONTENT_LENGTH': str(len(body)) if body else '0',
        'SERVER_NAME': headers.get('Host', headers.get('host', 'localhost')),
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': io.StringIO(body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'lambda.event': event,
        'lambda.context': context,
    }
    
    # Add HTTP headers as environ variables
    for header_name, header_value in headers.items():
        key = f'HTTP_{header_name.upper().replace("-", "_")}'
        environ[key] = header_value
    
    return environ

def websocket_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """WebSocket handler for Nova Sonic streaming"""
    try:
        route_key = event.get('requestContext', {}).get('routeKey')
        connection_id = event.get('requestContext', {}).get('connectionId')
        
        logger.info(f"WebSocket event - Route: {route_key}, Connection: {connection_id}")
        
        if route_key == '$connect':
            return {'statusCode': 200}
        elif route_key == '$disconnect': 
            return {'statusCode': 200}
        elif route_key == 'nova-sonic-stream':
            # Handle Nova Sonic streaming here
            return {'statusCode': 200}
        else:
            return {'statusCode': 404}
            
    except Exception as e:
        logger.error(f"WebSocket handler error: {str(e)}", exc_info=True)
        return {'statusCode': 500}

if __name__ == "__main__":
    # Local development server
    import os
    
    # Set development environment
    os.environ['REPLIT_ENVIRONMENT'] = 'true'
    
    print("Running Flask app locally for development")
    app.run(host='0.0.0.0', port=5000, debug=True)