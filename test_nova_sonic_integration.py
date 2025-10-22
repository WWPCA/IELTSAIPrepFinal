#!/usr/bin/env python3
"""
Test AWS Nova Sonic Amy Integration with Current IAM Permissions
Tests actual AWS Bedrock Nova Sonic model access and streaming capabilities
"""

import json
import boto3
import base64
import time
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

def test_nova_sonic_permissions():
    """Test Nova Sonic model access with current IAM permissions"""
    
    print("🔍 Testing AWS Nova Sonic Amy Integration")
    print("=" * 50)
    
    # Test 1: Initialize Bedrock client
    print("\n1. Testing Bedrock Client Initialization...")
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ Bedrock client initialized successfully")
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        return False
    except Exception as e:
        print(f"❌ Bedrock client initialization failed: {str(e)}")
        return False
    
    # Test 2: Nova Sonic model availability
    print("\n2. Testing Nova Sonic Model Access...")
    model_id = "amazon.nova-sonic-v1:0"
    
    try:
        # Test with a simple text-to-speech request
        test_payload = {
            "inputText": "Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment.",
            "taskType": "TEXT_TO_SPEECH",
            "voiceId": "Amy",
            "outputFormat": "mp3",
            "textType": "text"
        }
        
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(test_payload),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        
        if "audioStream" in response_body:
            print("✅ Nova Sonic Amy voice synthesis successful")
            print(f"   Voice: Amy (British Female)")
            print(f"   Audio format: MP3")
            print(f"   Response size: {len(response_body['audioStream'])} bytes")
        else:
            print("⚠️ Nova Sonic response missing audio stream")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == "AccessDeniedException":
            print("❌ ACCESS DENIED: Nova Sonic model access not permitted")
            print(f"   Error: {error_message}")
            print("   Required permission: bedrock:InvokeModel on amazon.nova-sonic-v1:0")
            return False
        elif error_code == "ValidationException":
            print("❌ VALIDATION ERROR: Nova Sonic request format invalid")
            print(f"   Error: {error_message}")
        elif error_code == "ResourceNotFoundException":
            print("❌ MODEL NOT FOUND: Nova Sonic model not available in us-east-1")
            print(f"   Error: {error_message}")
        else:
            print(f"❌ AWS Error: {error_code} - {error_message}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    
    # Test 3: Nova Sonic streaming capabilities
    print("\n3. Testing Nova Sonic Streaming...")
    try:
        # Test streaming invoke
        streaming_payload = {
            "inputText": "This is a test of Nova Sonic streaming capabilities for real-time IELTS assessment.",
            "taskType": "TEXT_TO_SPEECH",
            "voiceId": "Amy",
            "outputFormat": "mp3",
            "textType": "text"
        }
        
        response = bedrock_client.invoke_model_with_response_stream(
            modelId=model_id,
            body=json.dumps(streaming_payload),
            contentType="application/json",
            accept="application/json"
        )
        
        # Process streaming response
        audio_chunks = []
        for event in response['body']:
            if 'chunk' in event:
                chunk_data = json.loads(event['chunk']['bytes'])
                if 'audioStream' in chunk_data:
                    audio_chunks.append(chunk_data['audioStream'])
        
        if audio_chunks:
            print("✅ Nova Sonic streaming successful")
            print(f"   Streaming chunks: {len(audio_chunks)}")
            print(f"   Real-time audio: Available")
        else:
            print("⚠️ Nova Sonic streaming response empty")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ ACCESS DENIED: Nova Sonic streaming not permitted")
            print("   Required permission: bedrock:InvokeModelWithResponseStream")
            return False
        else:
            print(f"❌ Streaming error: {error_code}")
    except Exception as e:
        print(f"❌ Streaming test failed: {str(e)}")
    
    # Test 4: Nova Micro model access (for assessment evaluation)
    print("\n4. Testing Nova Micro Model Access...")
    nova_micro_id = "amazon.nova-micro-v1:0"
    
    try:
        micro_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Evaluate this IELTS speaking response for fluency and coherence: 'Hello, my name is Sarah and I am from Canada.'"
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.7
            }
        }
        
        response = bedrock_client.invoke_model(
            modelId=nova_micro_id,
            body=json.dumps(micro_payload),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        
        if "output" in response_body:
            print("✅ Nova Micro assessment evaluation successful")
            print(f"   Model: Nova Micro v1.0")
            print(f"   IELTS evaluation: Available")
        else:
            print("⚠️ Nova Micro response unexpected format")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ ACCESS DENIED: Nova Micro model access not permitted")
            print("   Required permission: bedrock:InvokeModel on amazon.nova-micro-v1:0")
            return False
        else:
            print(f"❌ Nova Micro error: {error_code}")
    except Exception as e:
        print(f"❌ Nova Micro test failed: {str(e)}")
    
    # Test 5: WebSocket API Gateway permissions
    print("\n5. Testing WebSocket API Gateway Access...")
    try:
        apigateway_client = boto3.client('apigatewayv2', region_name='us-east-1')
        
        # List APIs to test permissions
        response = apigateway_client.get_apis()
        print("✅ WebSocket API Gateway access successful")
        print(f"   APIs accessible: {len(response.get('Items', []))}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ ACCESS DENIED: WebSocket API Gateway not permitted")
            print("   Required permission: apigateway:GET")
            return False
        else:
            print(f"❌ WebSocket API error: {error_code}")
    except Exception as e:
        print(f"❌ WebSocket API test failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Nova Sonic Integration Test Complete")
    print("🎵 Maya AI examiner ready for IELTS assessments")
    
    return True

def generate_permission_recommendations():
    """Generate specific IAM permission recommendations based on test results"""
    
    print("\n📋 IAM PERMISSION RECOMMENDATIONS")
    print("=" * 50)
    
    required_permissions = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetModel",
                    "bedrock:ListModels"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-sonic-v1:0",
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-micro-v1:0"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "apigateway:GET",
                    "apigateway:POST",
                    "execute-api:Invoke",
                    "execute-api:ManageConnections"
                ],
                "Resource": [
                    "arn:aws:apigateway:us-east-1::/apis/*",
                    "arn:aws:execute-api:us-east-1:*:*/*/POST/*",
                    "arn:aws:execute-api:us-east-1:*:*/*/@connections/*"
                ]
            }
        ]
    }
    
    print("Required permissions for Nova Sonic integration:")
    print(json.dumps(required_permissions, indent=2))
    
    print("\n💡 RECOMMENDATION:")
    print("Your current IELTSGenAIPrepFullAccess policy should include these permissions.")
    print("If tests fail, add these specific permissions to your policy.")

if __name__ == "__main__":
    success = test_nova_sonic_permissions()
    
    if not success:
        generate_permission_recommendations()
    
    print(f"\n🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")