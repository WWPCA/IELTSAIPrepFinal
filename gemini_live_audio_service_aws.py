"""
Gemini 2.5 Flash Live API Service - AWS Lambda Compatible
Handles cross-cloud communication between AWS Lambda and Google Vertex AI
Supports WebSocket connections via API Gateway
"""
import asyncio
import json
import logging
import os
import boto3
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import secrets

# Google Generative AI SDK
from google import genai  # type: ignore
from google.genai.types import (  # type: ignore
    LiveConnectConfig, 
    Modality, 
    Blob,
    SpeechConfig,
    VoiceConfig,
    PrebuiltVoiceConfig
)
from google.oauth2 import service_account

# Import workflow manager for Smart Selection
from ielts_workflow_manager import IELTSWorkflowManager, SmartSelectionOrchestrator

# Import regional router for global optimization
from gemini_regional_router import get_regional_router

logger = logging.getLogger(__name__)

# AWS Secrets Manager client (initialized once for Lambda)
_secrets_client = None
_cached_gcp_credentials = None


class GeminiLiveServiceAWS:
    """
    AWS Lambda-compatible Gemini Live service with Smart Selection
    Handles GCP credential retrieval from AWS Secrets Manager
    Supports API Gateway WebSocket connections
    """
    
    def __init__(
        self, 
        project_id: Optional[str] = None, 
        region: Optional[str] = None,
        country_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        auto_regional_routing: bool = True,
        gcp_credentials_secret_name: Optional[str] = None
    ):
        """
        Initialize Gemini service for AWS Lambda environment
        
        Args:
            project_id: Google Cloud project ID (defaults to credentials)
            region: Specific Vertex AI region (overrides auto-detection)
            country_code: ISO 3166-1 alpha-2 country code for routing
            ip_address: User IP for geolocation-based routing
            auto_regional_routing: Enable automatic optimal region selection
            gcp_credentials_secret_name: AWS Secrets Manager secret name for GCP credentials
        """
        # Get GCP credentials from AWS Secrets Manager
        self.credentials = self._get_gcp_credentials(gcp_credentials_secret_name)
        
        # Extract project ID from credentials if not provided
        if self.credentials and not project_id:
            project_id = self.credentials.project_id
        
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT')
        
        # Regional routing
        if auto_regional_routing and not region:
            router = get_regional_router()
            optimal_region, region_info = router.get_optimal_region(
                country_code=country_code,
                ip_address=ip_address
            )
            self.region = optimal_region
            logger.info(f"Auto-selected region: {optimal_region} ({region_info['location']})")
        else:
            self.region = region or 'us-central1'
        
        # Configure for Vertex AI with explicit credentials
        if self.project_id:
            os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
        os.environ['GOOGLE_CLOUD_LOCATION'] = self.region
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'
        
        # Initialize Gemini client with AWS-retrieved credentials
        self.client = genai.Client(credentials=self.credentials)
        
        # Smart Selection models
        self.models = {
            'flash-lite': 'gemini-2.5-flash-lite',
            'flash': 'gemini-2.5-flash',
            'flash-native': 'gemini-2.5-flash-native-audio-preview-09-2025'
        }
        
        # Store regional router for health tracking
        self.regional_router = get_regional_router() if auto_regional_routing else None
        
        logger.info(f"Gemini Live AWS initialized - project: {self.project_id}, region: {self.region}")
    
    def _get_gcp_credentials(self, secret_name: Optional[str] = None) -> Optional[service_account.Credentials]:
        """
        Retrieve GCP service account credentials from AWS Secrets Manager
        Uses caching to avoid repeated API calls within Lambda execution context
        
        Args:
            secret_name: AWS Secrets Manager secret name
        
        Returns:
            Google service account credentials or None
        """
        global _secrets_client, _cached_gcp_credentials
        
        # Return cached credentials if available (Lambda warm start)
        if _cached_gcp_credentials:
            logger.info("Using cached GCP credentials")
            return _cached_gcp_credentials
        
        # Get secret name from environment if not provided
        secret_name = secret_name or os.environ.get('GCP_CREDENTIALS_SECRET_NAME')
        
        if not secret_name:
            logger.warning("No GCP credentials secret name provided, using environment variables")
            return None
        
        try:
            # Initialize Secrets Manager client if needed
            if not _secrets_client:
                _secrets_client = boto3.client('secretsmanager')
            
            # Retrieve secret
            response = _secrets_client.get_secret_value(SecretId=secret_name)
            
            # Parse credentials JSON
            if 'SecretString' in response:
                credentials_json = json.loads(response['SecretString'])
            else:
                # Binary secret (base64 encoded)
                import base64
                credentials_json = json.loads(base64.b64decode(response['SecretBinary']))
            
            # Create credentials object
            credentials = service_account.Credentials.from_service_account_info(
                credentials_json,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Cache for subsequent calls in same Lambda execution
            _cached_gcp_credentials = credentials
            
            logger.info("Successfully retrieved GCP credentials from AWS Secrets Manager")
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to retrieve GCP credentials from Secrets Manager: {e}")
            # Try to use environment-based auth as fallback
            return None
    
    async def start_maya_conversation_smart(
        self,
        assessment_type: str = 'speaking',
        on_text_response: Optional[Callable[[str], None]] = None,
        on_audio_response: Optional[Callable[[bytes], None]] = None,
        content_moderation_callback: Optional[Callable[[str], bool]] = None,
        websocket_connection_id: Optional[str] = None
    ) -> 'GeminiLiveSessionAWS':
        """
        Start Maya conversation with Smart Selection optimization
        AWS Lambda compatible with WebSocket support
        
        Args:
            assessment_type: Type of IELTS assessment
            on_text_response: Callback for text transcripts
            on_audio_response: Callback for audio chunks
            content_moderation_callback: Check if content is appropriate
            websocket_connection_id: API Gateway WebSocket connection ID
        
        Returns:
            GeminiLiveSessionAWS object with workflow management
        """
        # Create a NEW workflow manager for THIS session (not shared!)
        workflow_manager = IELTSWorkflowManager()
        
        # Start with Part 1 configuration
        config = workflow_manager.update_state_for_part(1)
        
        # Create Live config with optimized prompt and British female voice
        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],
            system_instruction=config['prompt'],
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(
                        voice_name="Erinome"  # Female British-sounding voice
                    )
                )
            )
        )
        
        # Create AWS-compatible Smart session
        session = GeminiLiveSessionAWS(
            client=self.client,
            model_id=config['model'],
            config=live_config,
            workflow_manager=workflow_manager,
            on_text_response=on_text_response,
            on_audio_response=on_audio_response,
            content_moderation_callback=content_moderation_callback,
            websocket_connection_id=websocket_connection_id,
            region=self.region,
            regional_router=self.regional_router
        )
        
        await session.connect()
        logger.info(f"Started Smart Selection conversation - Part 1 with {config['model']}")
        
        return session


class GeminiLiveSessionAWS:
    """
    AWS Lambda-compatible Gemini Live session with Smart Selection
    Manages WebSocket connections via API Gateway
    Handles Lambda timeout constraints (15-minute max)
    """
    
    def __init__(
        self,
        client: genai.Client,
        model_id: str,
        config: LiveConnectConfig,
        workflow_manager: IELTSWorkflowManager,
        on_text_response: Optional[Callable] = None,
        on_audio_response: Optional[Callable] = None,
        content_moderation_callback: Optional[Callable] = None,
        websocket_connection_id: Optional[str] = None,
        region: Optional[str] = None,
        regional_router: Optional[Any] = None
    ):
        self.client = client
        self.model_id = model_id
        self.config = config
        self.workflow_manager = workflow_manager
        self.on_text_response = on_text_response
        self.on_audio_response = on_audio_response
        self.content_moderation_callback = content_moderation_callback
        self.websocket_connection_id = websocket_connection_id
        self.region = region
        self.regional_router = regional_router
        
        self.session = None
        self.is_connected = False
        self.conversation_transcript = []
        self.audio_buffer = []
        self.response_task = None
        
        # Track messages for part transitions
        self.messages_in_current_part = 0
        
        # AWS-specific: Track Lambda execution time
        self.start_time = datetime.utcnow()
        self.lambda_timeout_warning_seconds = 840  # 14 minutes (leave 1 min buffer)
        
        # API Gateway WebSocket client (initialized if connection_id provided)
        self.apigw_client = None
        if websocket_connection_id:
            self._initialize_websocket_client()
    
    def _initialize_websocket_client(self):
        """Initialize API Gateway Management API for WebSocket responses"""
        try:
            # Get API Gateway endpoint from environment
            apigw_endpoint = os.environ.get('APIGW_ENDPOINT')
            if apigw_endpoint:
                self.apigw_client = boto3.client(
                    'apigatewaymanagementapi',
                    endpoint_url=apigw_endpoint
                )
                logger.info("Initialized API Gateway WebSocket client")
        except Exception as e:
            logger.warning(f"Failed to initialize WebSocket client: {e}")
    
    async def send_websocket_message(self, data: Dict[str, Any]):
        """Send message to client via API Gateway WebSocket"""
        if not self.apigw_client or not self.websocket_connection_id:
            return
        
        try:
            self.apigw_client.post_to_connection(
                ConnectionId=self.websocket_connection_id,
                Data=json.dumps(data).encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
    
    def _check_lambda_timeout(self) -> bool:
        """Check if Lambda is approaching timeout"""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        if elapsed > self.lambda_timeout_warning_seconds:
            logger.warning(f"Lambda approaching timeout: {elapsed}s elapsed")
            return True
        return False
    
    async def connect(self):
        """Establish connection with Gemini Live API"""
        try:
            # Create session with current model
            self.session = await self.client.models.generate_content_stream(
                model=self.model_id,
                config=self.config
            )
            self.is_connected = True
            
            # Start response handler
            self.response_task = asyncio.create_task(self._handle_responses())
            
            logger.info(f"Connected to Gemini Live API with model {self.model_id}")
            
            # Notify via WebSocket if available
            await self.send_websocket_message({
                'type': 'connection_established',
                'model': self.model_id,
                'region': self.region
            })
            
        except Exception as e:
            logger.error(f"Failed to connect to Gemini Live API: {e}")
            await self.send_websocket_message({
                'type': 'error',
                'message': f'Connection failed: {str(e)}'
            })
            raise
    
    async def switch_model(self, new_model: str, new_prompt: str):
        """Switch to a different model mid-conversation"""
        if not self.is_connected:
            logger.warning("Cannot switch model - not connected")
            return
        
        try:
            logger.info(f"Switching model from {self.model_id} to {new_model}")
            
            # Update config with new prompt
            self.config.system_instruction = new_prompt
            
            # Close current session
            if self.session:
                await self.session.close()
            
            # Create new session with new model
            self.model_id = new_model
            self.session = await self.client.models.generate_content_stream(
                model=self.model_id,
                config=self.config
            )
            
            # Reset message counter for new part
            self.messages_in_current_part = 0
            
            logger.info(f"Successfully switched to {new_model}")
            
            # Notify via WebSocket
            await self.send_websocket_message({
                'type': 'model_switched',
                'new_model': new_model
            })
            
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            raise
    
    async def check_and_transition_parts(self):
        """Check if it's time to transition to next IELTS part"""
        # Check Lambda timeout first
        if self._check_lambda_timeout():
            logger.warning("Approaching Lambda timeout - cannot transition parts")
            await self.send_websocket_message({
                'type': 'timeout_warning',
                'message': 'Assessment will end soon due to time limit'
            })
            return False
        
        if self.workflow_manager.should_transition():
            next_part = self.workflow_manager.state.current_part + 1
            
            if next_part <= 3:
                # Get configuration for next part
                config = self.workflow_manager.update_state_for_part(next_part)
                
                # Switch model and prompt
                await self.switch_model(config['model'], config['prompt'])
                
                logger.info(f"Transitioned to Part {next_part} with {config['model']}")
                
                # Notify about transition
                if self.on_text_response:
                    transition_msg = f"[Transitioning to Part {next_part}]"
                    self.on_text_response(transition_msg)
                
                await self.send_websocket_message({
                    'type': 'part_transition',
                    'part': next_part,
                    'model': config['model']
                })
                
                return True
        
        return False
    
    async def send_audio(self, audio_data: bytes, mime_type: str = 'audio/wav'):
        """Send audio input to Gemini with automatic part tracking"""
        if not self.is_connected or not self.session:
            raise RuntimeError("Session not connected")
        
        try:
            # Track response for workflow
            self.workflow_manager.track_response('candidate', f"[Audio input {len(audio_data)} bytes]")
            self.messages_in_current_part += 1
            
            # Convert audio to required format
            audio_blob = Blob(
                data=audio_data,
                mime_type=mime_type
            )
            
            await self.session.send_realtime_input(audio=audio_blob)
            
            # Check if we should transition parts
            await self.check_and_transition_parts()
            
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            await self.send_websocket_message({
                'type': 'error',
                'message': f'Audio send failed: {str(e)}'
            })
            raise
    
    async def send_text(self, text: str, end_of_turn: bool = True):
        """Send text input to Gemini with automatic part tracking"""
        if not self.is_connected or not self.session:
            raise RuntimeError("Session not connected")
        
        try:
            # Content moderation check
            if self.content_moderation_callback:
                if not self.content_moderation_callback(text):
                    logger.warning(f"Content moderation blocked text: {text[:50]}...")
                    return
            
            # Track response for workflow
            self.workflow_manager.track_response('candidate', text)
            self.messages_in_current_part += 1
            
            # Add to transcript
            self.conversation_transcript.append({
                'role': 'candidate',
                'content': text,
                'timestamp': datetime.utcnow().isoformat(),
                'part': self.workflow_manager.state.current_part
            })
            
            await self.session.send(text, end_of_turn=end_of_turn)
            
            # Check if we should transition parts
            await self.check_and_transition_parts()
            
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            raise
    
    async def _handle_responses(self):
        """Handle responses from Gemini with Smart Selection tracking"""
        if not self.session:
            return
            
        try:
            async for message in self.session.receive():
                # Handle text response
                if message.text:
                    # Track for workflow
                    self.workflow_manager.track_response('maya', message.text)
                    
                    # Add to transcript
                    self.conversation_transcript.append({
                        'role': 'maya',
                        'content': message.text,
                        'timestamp': datetime.utcnow().isoformat(),
                        'part': self.workflow_manager.state.current_part
                    })
                    
                    if self.on_text_response:
                        self.on_text_response(message.text)
                    
                    # Send via WebSocket
                    await self.send_websocket_message({
                        'type': 'text_response',
                        'text': message.text
                    })
                
                # Handle audio response
                if message.data:
                    # Audio is 16-bit PCM, 24kHz, mono
                    self.audio_buffer.append(message.data)
                    
                    if self.on_audio_response:
                        self.on_audio_response(message.data)
                    
                    # Send via WebSocket (base64 encoded)
                    import base64
                    await self.send_websocket_message({
                        'type': 'audio_response',
                        'audio': base64.b64encode(message.data).decode('utf-8')
                    })
                
                # Check if turn is complete
                if message.server_content and message.server_content.turn_complete:
                    logger.debug(f"Turn complete in Part {self.workflow_manager.state.current_part}")
                    
        except Exception as e:
            if not "cancelled" in str(e).lower():
                logger.error(f"Error handling responses: {e}")
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get full conversation transcript with part annotations"""
        return self.conversation_transcript
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get assessment summary with Smart Selection metrics"""
        return self.workflow_manager.get_assessment_summary()
    
    async def close(self):
        """Close session and generate summary with regional health tracking"""
        if self.session:
            # Get final summary
            summary = self.get_assessment_summary()
            
            # Track regional health if router available
            if self.regional_router and self.region:
                assessment_duration = summary.get('duration_seconds', 0)
                # Estimate latency based on duration
                latency_ms = (assessment_duration * 1000) / 10 if assessment_duration > 0 else 100
                self.regional_router.mark_success(self.region, latency_ms)
                logger.info(f"Marked region {self.region} as healthy (latency: {latency_ms}ms)")
            
            logger.info(f"Assessment completed - Cost: {summary['cost_breakdown']['total']}")
            
            # Notify via WebSocket
            await self.send_websocket_message({
                'type': 'assessment_complete',
                'summary': summary
            })
            
            # Cancel response handler
            if self.response_task:
                self.response_task.cancel()
            
            # Close session
            await self.session.close()
            
        self.is_connected = False
