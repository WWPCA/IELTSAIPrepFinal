"""
Lambda Handler for IELTS AI Prep Flask Application
Wraps Flask app using awsgi for Lambda compatibility with binary support
"""

import os
import sys
import base64
import mimetypes

# Ensure all modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import awsgi

# Create Lambda handler using awsgi (for WSGI Flask apps)
def handler(event, context):
    # Get the API Gateway stage (e.g., 'production')
    stage = event.get('requestContext', {}).get('stage', '')
    
    # Normalize path by removing stage prefix if present
    path = event.get('path', '')
    if stage and path.startswith(f'/{stage}/'):
        path = path[len(f'/{stage}'):]  # Remove /production/ to get /static/...
    
    # Handle static files before Flask/awsgi to avoid binary encoding issues
    if path.startswith('/static/'):
        # Extract filename from path
        filename = path[8:]  # Remove '/static/' prefix
        file_path = os.path.join(os.path.dirname(__file__), 'static', filename)
        
        # Check if file exists
        if os.path.exists(file_path):
            # Detect content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Read file in binary mode
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # Return base64-encoded response for API Gateway
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': content_type,
                        'Content-Disposition': f'inline; filename={os.path.basename(filename)}',
                        'Cache-Control': 'public, max-age=31536000'
                    },
                    'body': base64.b64encode(file_data).decode('utf-8'),
                    'isBase64Encoded': True
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': f'{{"error": "Error reading file: {str(e)}"}}',
                    'isBase64Encoded': False
                }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': '{"error": "File not found"}',
                'isBase64Encoded': False
            }
    
    # For non-static routes, use awsgi to process Flask app
    # awsgi automatically handles the stage prefix via SCRIPT_NAME
    return awsgi.response(app, event, context)

# For local testing
if __name__ == "__main__":
    app.run(debug=True, port=5000)
