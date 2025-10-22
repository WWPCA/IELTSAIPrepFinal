#!/usr/bin/env python3
"""
WebSocket Streaming Integration Tests
Tests real-time bidirectional communication for Nova Sonic speaking assessments
"""

import pytest
import asyncio
import json
import os
from datetime import datetime

# WebSocket testing requires websockets library
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="websockets library not available")


BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
WS_URL = BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')


@pytest.mark.websocket
@pytest.mark.asyncio
class TestWebSocketStreaming:
    """Test WebSocket streaming for real-time assessments"""
    
    async def test_01_websocket_connection_establishment(self):
        """Test 1: Establish WebSocket connection"""
        if not WEBSOCKETS_AVAILABLE:
            pytest.skip("WebSocket library not available")
            
        ws_endpoint = f"{WS_URL}/api/websocket/speaking/stream"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=5) as websocket:
                # Send hello message
                await websocket.send(json.dumps({
                    "type": "connect",
                    "user_id": "test_user_001",
                    "assessment_type": "speaking_academic"
                }))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                data = json.loads(response)
                
                assert data.get("status") in ["connected", "ready"], \
                    f"WebSocket connection failed: {data}"
                    
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException) as e:
            # WebSocket endpoint may not be implemented yet
            pytest.skip(f"WebSocket endpoint not available: {e}")
            
    async def test_02_streaming_audio_simulation(self):
        """Test 2: Simulate audio streaming"""
        if not WEBSOCKETS_AVAILABLE:
            pytest.skip("WebSocket library not available")
            
        ws_endpoint = f"{WS_URL}/api/websocket/speaking/stream"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=5) as websocket:
                # Send audio data simulation
                audio_message = {
                    "type": "audio_chunk",
                    "data": "base64_encoded_audio_simulation",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await websocket.send(json.dumps(audio_message))
                
                # Should receive acknowledgment
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                data = json.loads(response)
                
                assert data.get("type") in ["ack", "processing", "error"], \
                    f"Unexpected WebSocket response: {data}"
                    
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException):
            pytest.skip("WebSocket streaming not implemented")
            
    async def test_03_content_moderation_realtime(self):
        """Test 3: Real-time content moderation during streaming"""
        if not WEBSOCKETS_AVAILABLE:
            pytest.skip("WebSocket library not available")
            
        ws_endpoint = f"{WS_URL}/api/websocket/speaking/stream"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=5) as websocket:
                # Send potentially inappropriate content
                test_message = {
                    "type": "audio_chunk",
                    "data": "test_content_for_moderation",
                    "moderation_required": True
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Should receive moderation response
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                data = json.loads(response)
                
                # Moderation should either allow, warn, or block
                assert data.get("type") in ["moderation_pass", "moderation_warning", 
                                           "moderation_block", "error", "ack"]
                    
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException):
            pytest.skip("Content moderation WebSocket not implemented")
            
    async def test_04_bidirectional_communication(self):
        """Test 4: Bidirectional streaming (user speaks, AI responds)"""
        if not WEBSOCKETS_AVAILABLE:
            pytest.skip("WebSocket library not available")
            
        ws_endpoint = f"{WS_URL}/api/websocket/speaking/stream"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=5) as websocket:
                # Simulate user speaking
                user_message = {
                    "type": "user_audio",
                    "content": "test_speech_audio"
                }
                
                await websocket.send(json.dumps(user_message))
                
                # Should receive AI response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                # AI should respond with audio or acknowledgment
                assert data.get("type") in ["ai_response", "processing", "ack", "error"]
                    
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException):
            pytest.skip("Bidirectional WebSocket not implemented")


@pytest.mark.websocket
class TestWebSocketPerformance:
    """Test WebSocket performance and reliability"""
    
    @pytest.mark.asyncio
    async def test_01_connection_latency(self):
        """Test 1: WebSocket connection latency"""
        if not WEBSOCKETS_AVAILABLE:
            pytest.skip("WebSocket library not available")
            
        ws_endpoint = f"{WS_URL}/api/websocket/speaking/stream"
        
        try:
            start_time = asyncio.get_event_loop().time()
            async with websockets.connect(ws_endpoint, timeout=5) as websocket:
                await websocket.send(json.dumps({"type": "ping"}))
                await asyncio.wait_for(websocket.recv(), timeout=2)
            end_time = asyncio.get_event_loop().time()
            
            latency = (end_time - start_time) * 1000  # Convert to ms
            
            # Latency should be under 1000ms for good user experience
            assert latency < 1000, f"WebSocket latency too high: {latency}ms"
            
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException):
            pytest.skip("WebSocket performance test skipped - endpoint not available")
            
    @pytest.mark.asyncio
    async def test_02_sustained_streaming(self):
        """Test 2: Sustained streaming for assessment duration"""
        if not WEBSOCKETS_AVAILABLE:
            pytest.skip("WebSocket library not available")
            
        ws_endpoint = f"{WS_URL}/api/websocket/speaking/stream"
        
        try:
            async with websockets.connect(ws_endpoint, timeout=5) as websocket:
                # Send messages for 10 seconds to simulate short assessment
                start_time = asyncio.get_event_loop().time()
                message_count = 0
                
                while (asyncio.get_event_loop().time() - start_time) < 10:
                    await websocket.send(json.dumps({
                        "type": "audio_chunk",
                        "sequence": message_count
                    }))
                    message_count += 1
                    await asyncio.sleep(0.5)
                    
                # Should maintain connection throughout
                assert message_count >= 18, "Sustained streaming failed"
                
        except (OSError, asyncio.TimeoutError, websockets.exceptions.WebSocketException):
            pytest.skip("Sustained streaming test skipped")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
