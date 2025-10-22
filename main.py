from app import app  # noqa: F401

# Lambda compatibility - only define if running in AWS
if __name__ != "__main__":
    # For Lambda compatibility with proper WSGI adapter
    try:
        import awsgi
        def lambda_handler(event, context):
            """AWS Lambda handler that proxies API Gateway events to Flask WSGI app"""
            return awsgi.response(app, event, context)
    except ImportError:
        # Fallback for development environments without awsgi
        def lambda_handler(event, context):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': 'Flask app running - awsgi not available in development'
            }