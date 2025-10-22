#!/usr/bin/env python3
"""
Nova Sonic Integration using Bedrock Converse API
Proper implementation for speech-to-speech conversations
"""

import boto3
import json
import base64
from botocore.exceptions import ClientError

def test_nova_sonic_converse_api():
    """Test Nova Sonic using the Bedrock Converse API"""
    
    print("🎵 Testing Nova Sonic with Bedrock Converse API")
    print("=" * 50)
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test 1: Text conversation (Maya speaking)
        print("\n1. Testing text-to-speech conversation...")
        
        response = bedrock_client.converse(
            modelId="amazon.nova-sonic-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Hello, I am Maya, your IELTS examiner. Welcome to your speaking assessment. Please tell me your name and where you are from."
                        }
                    ]
                }
            ],
            inferenceConfig={
                "maxTokens": 500,
                "temperature": 0.7
            }
        )
        
        if 'output' in response:
            print("✅ Nova Sonic Converse API working")
            output = response['output']
            if 'message' in output:
                content = output['message']['content']
                print(f"   Response: {str(content)[:100]}...")
                return True
        else:
            print("⚠️ Unexpected response format")
            print(f"   Response: {response}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Converse API error: {error_code}")
        print(f"   Message: {error_message}")
        
        if error_code == "ValidationException":
            print("   💡 Nova Sonic might need different integration approach")
        elif error_code == "AccessDeniedException":
            print("   🔑 Need bedrock:Converse permission")
            
    except Exception as e:
        print(f"❌ Converse API test failed: {str(e)}")
    
    return False

def test_nova_sonic_streaming_converse():
    """Test Nova Sonic streaming with Converse API"""
    
    print("\n🌊 Testing Nova Sonic Streaming Converse")
    print("=" * 40)
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        response = bedrock_client.converse_stream(
            modelId="amazon.nova-sonic-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "Start IELTS speaking assessment. Ask me about my background."
                        }
                    ]
                }
            ],
            inferenceConfig={
                "maxTokens": 500,
                "temperature": 0.7
            }
        )
        
        chunks = []
        for event in response['stream']:
            if 'messageStart' in event:
                print("✅ Stream started")
            elif 'contentBlockDelta' in event:
                delta = event['contentBlockDelta']
                if 'text' in delta:
                    chunks.append(delta['text'])
            elif 'messageStop' in event:
                print("✅ Stream completed")
        
        if chunks:
            print(f"   Received {len(chunks)} text chunks")
            print(f"   Content: {''.join(chunks)[:100]}...")
            return True
        else:
            print("❌ No streaming content received")
            return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "AccessDeniedException":
            print("❌ Need bedrock:ConverseStream permission")
        else:
            print(f"❌ Streaming error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Streaming test failed: {str(e)}")
        return False

def check_nova_sonic_model_access():
    """Check specific Nova Sonic model access"""
    
    print("\n🔍 Checking Nova Sonic Model Access")
    print("=" * 40)
    
    try:
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test different Nova Sonic approaches
        test_cases = [
            {
                "name": "Standard invoke_model",
                "method": "invoke_model",
                "payload": {
                    "messages": [{"role": "user", "content": [{"text": "Hello"}]}],
                    "inferenceConfig": {"maxTokens": 100}
                }
            },
            {
                "name": "Converse API",
                "method": "converse",
                "payload": {
                    "messages": [{"role": "user", "content": [{"text": "Hello"}]}],
                    "inferenceConfig": {"maxTokens": 100}
                }
            }
        ]
        
        working_methods = []
        
        for test_case in test_cases:
            print(f"\n🔧 Testing {test_case['name']}...")
            
            try:
                if test_case['method'] == 'invoke_model':
                    response = bedrock_client.invoke_model(
                        modelId="amazon.nova-sonic-v1:0",
                        body=json.dumps(test_case['payload']),
                        contentType="application/json"
                    )
                    result = json.loads(response['body'].read())
                    
                elif test_case['method'] == 'converse':
                    response = bedrock_client.converse(
                        modelId="amazon.nova-sonic-v1:0",
                        **test_case['payload']
                    )
                    result = response
                
                print(f"✅ {test_case['name']} - Success")
                print(f"   Response keys: {list(result.keys())}")
                working_methods.append(test_case['method'])
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                print(f"❌ {test_case['name']} - {error_code}")
                
                if error_code == "AccessDeniedException":
                    print(f"   Need permission for {test_case['method']}")
                elif error_code == "ValidationException":
                    print(f"   Model doesn't support {test_case['method']}")
            except Exception as e:
                print(f"❌ {test_case['name']} - {str(e)}")
        
        return working_methods
        
    except Exception as e:
        print(f"❌ Model access check failed: {str(e)}")
        return []

def generate_nova_sonic_permissions():
    """Generate complete Nova Sonic permissions"""
    
    print("\n🔑 COMPLETE NOVA SONIC PERMISSIONS")
    print("=" * 50)
    
    permissions = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:Converse",
                    "bedrock:ConverseStream",
                    "bedrock:GetFoundationModel",
                    "bedrock:ListFoundationModels"
                ],
                "Resource": [
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-sonic-v1:0",
                    "arn:aws:bedrock:us-east-1:*:foundation-model/amazon.nova-micro-v1:0"
                ]
            }
        ]
    }
    
    print("🔑 ADD THESE PERMISSIONS TO YOUR IAM POLICY:")
    print(json.dumps(permissions, indent=2))
    
    print("\n💡 CRITICAL NOVA SONIC PERMISSIONS:")
    print("- bedrock:Converse (for Nova Sonic conversations)")
    print("- bedrock:ConverseStream (for real-time Maya interactions)")
    print("- bedrock:InvokeModel (for Nova Micro assessment)")

if __name__ == "__main__":
    # Check model access methods
    working_methods = check_nova_sonic_model_access()
    
    # Test Converse API
    converse_ok = test_nova_sonic_converse_api()
    
    # Test streaming
    streaming_ok = test_nova_sonic_streaming_converse()
    
    # Generate permissions
    generate_nova_sonic_permissions()
    
    print("\n🎯 NOVA SONIC INTEGRATION STATUS:")
    print(f"   Working Methods: {working_methods}")
    print(f"   Converse API: {converse_ok}")
    print(f"   Streaming: {streaming_ok}")
    
    if working_methods:
        print("\n✅ SOLUTION FOUND:")
        print("   Nova Sonic requires Bedrock Converse API")
        print("   Add bedrock:Converse and bedrock:ConverseStream permissions")
    else:
        print("\n❌ NO WORKING METHODS FOUND")
        print("   Check AWS documentation for Nova Sonic availability")