#!/usr/bin/env python3
"""
Nova Sonic Speech Integration - Correct Implementation
Focus on Nova Sonic for both speech synthesis and processing
"""

import boto3
import json
import base64
from botocore.exceptions import ClientError

def test_nova_sonic_speech_synthesis():
    """Test Nova Sonic with correct speech synthesis format"""
    
    print("🎵 Testing Nova Sonic Speech Synthesis")
    print("=" * 50)
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test different Nova Sonic request formats
        test_formats = [
            {
                "name": "Format 1: Direct speech request",
                "payload": {
                    "inputText": "Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment.",
                    "voice": "Amy",
                    "outputFormat": "mp3"
                }
            },
            {
                "name": "Format 2: Message-based request",
                "payload": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": "Generate speech: Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment."
                                }
                            ]
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": 1000,
                        "temperature": 0.3
                    },
                    "speechConfig": {
                        "voice": "Amy",
                        "format": "mp3"
                    }
                }
            },
            {
                "name": "Format 3: Audio generation",
                "payload": {
                    "text": "Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment.",
                    "voice_id": "Amy",
                    "output_format": "mp3",
                    "task_type": "text_to_speech"
                }
            }
        ]
        
        for test_format in test_formats:
            print(f"\n🔧 Testing {test_format['name']}...")
            
            try:
                response = bedrock_client.invoke_model(
                    modelId="amazon.nova-sonic-v1:0",
                    body=json.dumps(test_format['payload']),
                    contentType="application/json"
                )
                
                result = json.loads(response['body'].read())
                print(f"✅ {test_format['name']} - Success!")
                print(f"   Response keys: {list(result.keys())}")
                
                # Check for audio data
                if 'audioStream' in result:
                    print(f"   Audio data: {len(result['audioStream'])} bytes")
                    return True, test_format['payload']
                elif 'audio' in result:
                    print(f"   Audio data: {len(result['audio'])} bytes")
                    return True, test_format['payload']
                else:
                    print(f"   Content: {str(result)[:200]}...")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                print(f"❌ {test_format['name']} - {error_code}")
                print(f"   Message: {error_message}")
            except Exception as e:
                print(f"❌ {test_format['name']} - {str(e)}")
        
        return False, None
        
    except Exception as e:
        print(f"❌ Nova Sonic test failed: {str(e)}")
        return False, None

def check_nova_sonic_capabilities():
    """Check Nova Sonic model capabilities and documentation"""
    
    print("\n📋 Checking Nova Sonic Model Capabilities")
    print("=" * 50)
    
    try:
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        
        # Get detailed model information
        response = bedrock_client.get_foundation_model(
            modelIdentifier="amazon.nova-sonic-v1:0"
        )
        
        model_details = response['modelDetails']
        print(f"✅ Model Name: {model_details.get('modelName')}")
        print(f"   Provider: {model_details.get('providerName')}")
        print(f"   Input Modalities: {model_details.get('inputModalities', [])}")
        print(f"   Output Modalities: {model_details.get('outputModalities', [])}")
        print(f"   Streaming Support: {model_details.get('responseStreamingSupported', False)}")
        
        # Check inference types
        if 'inferenceTypesSupported' in model_details:
            print(f"   Inference Types: {model_details['inferenceTypesSupported']}")
        
        # Check customization
        if 'customizationsSupported' in model_details:
            print(f"   Customizations: {model_details['customizationsSupported']}")
        
        return True
        
    except ClientError as e:
        print(f"❌ Error getting model details: {e.response['Error']['Code']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_nova_sonic_streaming():
    """Test Nova Sonic streaming capabilities"""
    
    print("\n🌊 Testing Nova Sonic Streaming")
    print("=" * 40)
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test streaming with conversation
        streaming_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Start IELTS speaking assessment Part 1. Ask about my name and where I'm from."
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.7
            }
        }
        
        response = bedrock_client.invoke_model_with_response_stream(
            modelId="amazon.nova-sonic-v1:0",
            body=json.dumps(streaming_payload),
            contentType="application/json"
        )
        
        # Process streaming response
        chunks = []
        for event in response['body']:
            if 'chunk' in event:
                chunk_data = json.loads(event['chunk']['bytes'])
                chunks.append(chunk_data)
        
        if chunks:
            print(f"✅ Nova Sonic streaming working")
            print(f"   Chunks received: {len(chunks)}")
            print(f"   First chunk: {str(chunks[0])[:100]}...")
            return True
        else:
            print("❌ No streaming chunks received")
            return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ Need bedrock:InvokeModelWithResponseStream permission")
        else:
            print(f"❌ Streaming error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Streaming test failed: {str(e)}")
        return False

def generate_nova_sonic_iam_requirements():
    """Generate Nova Sonic specific IAM requirements"""
    
    print("\n🔑 NOVA SONIC IAM REQUIREMENTS")
    print("=" * 50)
    
    nova_sonic_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetFoundationModel",
                    "bedrock:ListFoundationModels"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-sonic-v1:0"
                ]
            }
        ]
    }
    
    print("Add this to your IELTSGenAIPrepFullAccess policy:")
    print(json.dumps(nova_sonic_policy, indent=2))
    
    print("\n💡 Key Requirements:")
    print("- bedrock:InvokeModel for Nova Sonic speech synthesis")
    print("- bedrock:InvokeModelWithResponseStream for real-time Maya conversations")
    print("- bedrock:GetFoundationModel for model capability checking")

if __name__ == "__main__":
    # Check Nova Sonic capabilities
    capabilities_ok = check_nova_sonic_capabilities()
    
    # Test speech synthesis
    synthesis_ok, working_format = test_nova_sonic_speech_synthesis()
    
    # Test streaming
    streaming_ok = test_nova_sonic_streaming()
    
    # Generate IAM requirements
    generate_nova_sonic_iam_requirements()
    
    print("\n🎯 NOVA SONIC STATUS:")
    print(f"   Model Available: {capabilities_ok}")
    print(f"   Speech Synthesis: {synthesis_ok}")
    print(f"   Streaming: {streaming_ok}")
    
    if working_format:
        print("\n✅ Working Format Found:")
        print(json.dumps(working_format, indent=2))
    else:
        print("\n❌ No working speech synthesis format found")
        print("   Check AWS documentation for Nova Sonic speech synthesis")