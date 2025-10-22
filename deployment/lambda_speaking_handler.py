"""
AWS Lambda Handler for IELTS Speaking Assessments
Manages WebSocket connections via API Gateway for real-time Gemini Live API streaming
"""
import json
import os
import asyncio
import logging
import boto3
import base64
from typing import Dict, Any, Optional
from datetime import datetime

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Import Gemini service
import sys
sys.path.append(os.path.dirname(__file__))
from gemini_live_audio_service_aws import GeminiLiveServiceAWS

# AWS clients (initialized once for warm starts)
dynamodb = boto3.resource('dynamodb')
sessions_table = dynamodb.Table(os.environ.get('SESSIONS_TABLE', 'ielts-genai-prep-sessions'))
apigw_client = None

# Global session cache (survives Lambda warm starts)
active_sessions = {}


def get_apigw_client(event):
    """Initialize API Gateway Management API client"""
    global apigw_client
    if not apigw_client:
        domain = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        endpoint = f"https://{domain}/{stage}"
        apigw_client = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint)
        logger.info(f"Initialized API Gateway client: {endpoint}")
    return apigw_client


def send_to_websocket(connection_id: str, data: Dict[str, Any], apigw):
    """Send message to WebSocket client"""
    try:
        apigw.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8')
        )
        return True
    except apigw.exceptions.GoneException:
        logger.warning(f"Connection {connection_id} is gone")
        return False
    except Exception as e:
        logger.error(f"Failed to send to WebSocket {connection_id}: {e}")
        return False


def lambda_handler(event, context):
    """
    Main Lambda handler for WebSocket routes
    Routes: $connect, $disconnect, start_speaking, audio_chunk, end_speaking
    """
    try:
        route_key = event['requestContext']['routeKey']
        connection_id = event['requestContext']['connectionId']
        
        logger.info(f"Route: {route_key}, Connection: {connection_id}")
        
        # Handle routes
        if route_key == '$connect':
            return handle_connect(event, context, connection_id)
        
        elif route_key == '$disconnect':
            return handle_disconnect(event, context, connection_id)
        
        elif route_key == 'start_speaking':
            return asyncio.run(handle_start_speaking(event, context, connection_id))
        
        elif route_key == 'audio_chunk':
            return asyncio.run(handle_audio_chunk(event, context, connection_id))
        
        elif route_key == 'end_speaking':
            return asyncio.run(handle_end_speaking(event, context, connection_id))
        
        elif route_key == '$default':
            return {'statusCode': 400, 'body': 'Unknown action'}
        
        else:
            return {'statusCode': 400, 'body': f'Unknown route: {route_key}'}
    
    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': str(e)}


def handle_connect(event, context, connection_id):
    """Handle WebSocket connection"""
    try:
        # Store connection in DynamoDB
        sessions_table.put_item(
            Item={
                'connection_id': connection_id,
                'connected_at': datetime.utcnow().isoformat(),
                'status': 'connected',
                'ttl': int(datetime.utcnow().timestamp()) + 7200  # 2 hours
            }
        )
        
        logger.info(f"WebSocket connected: {connection_id}")
        return {'statusCode': 200}
    
    except Exception as e:
        logger.error(f"Connect error: {e}")
        return {'statusCode': 500}


def handle_disconnect(event, context, connection_id):
    """Handle WebSocket disconnection"""
    try:
        # Clean up active session if exists
        if connection_id in active_sessions:
            asyncio.run(active_sessions[connection_id].close())
            del active_sessions[connection_id]
            logger.info(f"Closed active session for {connection_id}")
        
        # Remove from DynamoDB
        sessions_table.delete_item(
            Key={'connection_id': connection_id}
        )
        
        logger.info(f"WebSocket disconnected: {connection_id}")
        return {'statusCode': 200}
    
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        return {'statusCode': 500}


async def handle_start_speaking(event, context, connection_id):
    """Initialize Gemini Live session for speaking assessment"""
    try:
        apigw = get_apigw_client(event)
        body = json.loads(event.get('body', '{}'))
        
        # Extract user info and preferences
        user_id = body.get('user_id')
        assessment_type = body.get('assessment_type', 'speaking')
        country_code = body.get('country_code')
        
        # Get user IP for regional routing
        ip_address = event['requestContext']['identity'].get('sourceIp')
        
        logger.info(f"Starting speaking assessment for user {user_id}, country: {country_code}, IP: {ip_address}")
        
        # Send acknowledgment
        send_to_websocket(connection_id, {
            'type': 'initialization_started',
            'message': 'Connecting to AI examiner Maya...'
        }, apigw)
        
        # Initialize Gemini service with regional routing
        service = GeminiLiveServiceAWS(
            country_code=country_code,
            ip_address=ip_address,
            auto_regional_routing=True,
            gcp_credentials_secret_name=os.environ.get('GCP_CREDENTIALS_SECRET')
        )
        
        # Define callbacks for real-time responses
        def on_text_response(text: str):
            """Send Maya's text transcript to user"""
            send_to_websocket(connection_id, {
                'type': 'maya_transcript',
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }, apigw)
        
        def on_audio_response(audio_bytes: bytes):
            """Send Maya's audio response to user"""
            send_to_websocket(connection_id, {
                'type': 'maya_audio',
                'audio': base64.b64encode(audio_bytes).decode('utf-8'),
                'timestamp': datetime.utcnow().isoformat()
            }, apigw)
        
        # Start Maya conversation with callbacks
        session = await service.start_maya_conversation_smart(
            assessment_type=assessment_type,
            on_text_response=on_text_response,
            on_audio_response=on_audio_response,
            websocket_connection_id=connection_id
        )
        
        # Cache session for subsequent audio chunks
        active_sessions[connection_id] = session
        
        # Update DynamoDB with session info
        sessions_table.update_item(
            Key={'connection_id': connection_id},
            UpdateExpression='SET user_id = :uid, session_status = :status, region = :region',
            ExpressionAttributeValues={
                ':uid': user_id,
                ':status': 'active',
                ':region': service.region
            }
        )
        
        # Send success notification
        send_to_websocket(connection_id, {
            'type': 'session_ready',
            'message': 'Connected to Maya! You can start speaking.',
            'region': service.region,
            'model': session.model_id
        }, apigw)
        
        logger.info(f"Session started successfully for {connection_id} in region {service.region}")
        
        return {'statusCode': 200}
    
    except Exception as e:
        logger.error(f"Start speaking error: {e}", exc_info=True)
        
        # Send error to client
        try:
            send_to_websocket(connection_id, {
                'type': 'error',
                'message': f'Failed to start session: {str(e)}'
            }, get_apigw_client(event))
        except:
            pass
        
        return {'statusCode': 500, 'body': str(e)}


async def handle_audio_chunk(event, context, connection_id):
    """Stream audio chunk to Gemini Live API"""
    try:
        # Get active session
        session = active_sessions.get(connection_id)
        if not session:
            logger.error(f"No active session for {connection_id}")
            return {'statusCode': 400, 'body': 'No active session. Call start_speaking first.'}
        
        # Parse audio data
        body = json.loads(event.get('body', '{}'))
        audio_base64 = body.get('audio')
        mime_type = body.get('mime_type', 'audio/wav')
        
        if not audio_base64:
            return {'statusCode': 400, 'body': 'Missing audio data'}
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Send to Gemini (this triggers Maya's response via callbacks)
        await session.send_audio(audio_bytes, mime_type=mime_type)
        
        return {'statusCode': 200}
    
    except Exception as e:
        logger.error(f"Audio chunk error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': str(e)}


async def handle_end_speaking(event, context, connection_id):
    """End speaking assessment and get final evaluation"""
    try:
        apigw = get_apigw_client(event)
        
        # Get active session
        session = active_sessions.get(connection_id)
        if not session:
            return {'statusCode': 400, 'body': 'No active session'}
        
        # Send processing notification
        send_to_websocket(connection_id, {
            'type': 'processing',
            'message': 'Generating your assessment report...'
        }, apigw)
        
        # Get assessment summary
        summary = session.get_assessment_summary()
        transcript = session.get_transcript()
        
        # Close session
        await session.close()
        
        # Remove from cache
        del active_sessions[connection_id]
        
        # Parse assessment data (from summary)
        assessment_result = {
            'overall_band': summary.get('estimated_band', 0.0),
            'criteria_scores': {
                'fluency_coherence': 0.0,  # Would come from AI evaluation
                'lexical_resource': 0.0,
                'grammatical_range': 0.0,
                'pronunciation': 0.0
            },
            'duration_seconds': summary.get('duration_seconds', 0),
            'cost': summary.get('cost_breakdown', {}),
            'transcript': transcript,
            'parts_completed': summary.get('parts_completed', [])
        }
        
        # Generate personalized improvement plan
        try:
            from personalized_improvement_service import get_improvement_service
            improvement_service = get_improvement_service()
            improvement_plan = improvement_service.generate_speaking_improvement_plan(
                assessment_result=assessment_result,
                user_history=None  # TODO: Fetch from DynamoDB
            )
            assessment_result['improvement_plan'] = improvement_plan
        except Exception as e:
            logger.warning(f"Failed to generate improvement plan: {e}")
            assessment_result['improvement_plan'] = None
        
        # Send final results
        send_to_websocket(connection_id, {
            'type': 'assessment_complete',
            'assessment': assessment_result
        }, apigw)
        
        # Update session in DynamoDB
        sessions_table.update_item(
            Key={'connection_id': connection_id},
            UpdateExpression='SET session_status = :status, completed_at = :completed, assessment_result = :result',
            ExpressionAttributeValues={
                ':status': 'completed',
                ':completed': datetime.utcnow().isoformat(),
                ':result': json.dumps(assessment_result)
            }
        )
        
        logger.info(f"Assessment completed for {connection_id}")
        
        return {'statusCode': 200}
    
    except Exception as e:
        logger.error(f"End speaking error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': str(e)}
