#!/usr/bin/env python3
"""
IELTS GenAI Prep - Nova AI Testing Script
Test real Nova Sonic and Nova Micro integration before full deployment
"""

import boto3
import json
import os
from datetime import datetime

def test_nova_micro_writing():
    """Test Nova Micro writing assessment with real AWS Bedrock"""
    print("🧪 Testing Nova Micro writing assessment...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Sample IELTS Academic Writing Task 2 essay
        sample_essay = """
        In today's world, technology has become an integral part of education. Many people believe that computers and tablets should replace traditional textbooks in schools, while others argue that physical books are still essential for learning.

        I believe that while technology offers significant advantages in education, traditional textbooks should not be completely replaced. Digital devices provide interactive learning experiences, instant access to updated information, and multimedia content that can enhance understanding. For example, students can watch educational videos, take interactive quizzes, and access vast online libraries.

        However, physical books offer unique benefits that cannot be replicated digitally. Reading from paper reduces eye strain during long study sessions and helps improve concentration by eliminating digital distractions. Additionally, many students retain information better when reading from physical pages rather than screens.

        The ideal approach would be to integrate both digital technology and traditional textbooks in education. This combination allows students to benefit from the advantages of both mediums while developing diverse learning skills necessary for the modern world.

        In conclusion, rather than replacing textbooks entirely, schools should adopt a balanced approach that incorporates both digital tools and traditional books to create a comprehensive learning environment.
        """
        
        # Nova Micro system prompt for IELTS assessment
        system_prompt = """You are an expert IELTS examiner specializing in Academic Writing Task 2 assessments. Evaluate the essay using official IELTS criteria:

Task Achievement (25%): How well the task is addressed
Coherence and Cohesion (25%): Organization and linking
Lexical Resource (25%): Vocabulary range and accuracy
Grammatical Range and Accuracy (25%): Grammar complexity and correctness

Provide detailed feedback with specific examples and band scores for each criterion (1-9), plus an overall band score."""

        # Prepare Nova Micro request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": f"Please assess this IELTS Academic Writing Task 2 essay:\n\n{sample_essay}"
                }
            ]
        }
        
        # Call Nova Micro
        response = bedrock.invoke_model(
            modelId='amazon.nova-micro-v1:0',
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        # Parse response
        result = json.loads(response['body'].read())
        assessment = result['content'][0]['text']
        
        print("✅ Nova Micro assessment completed:")
        print("-" * 50)
        print(assessment)
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Nova Micro test failed: {str(e)}")
        if "AccessDeniedException" in str(e):
            print("💡 Enable Nova Micro access in AWS Bedrock console")
        return False

def test_nova_sonic_streaming():
    """Test Nova Sonic bi-directional streaming capabilities"""
    print("\n🧪 Testing Nova Sonic streaming setup...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Maya's IELTS examiner system prompt
        maya_prompt = """You are Maya, an expert IELTS speaking examiner. Conduct a natural conversation following IELTS Academic Speaking test format:

Part 1: Introduction and familiar topics (4-5 minutes)
Part 2: Individual long turn with cue card (3-4 minutes)  
Part 3: Discussion of abstract ideas (4-5 minutes)

Evaluate on: Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, Pronunciation (25% each).

Maintain natural conversation flow while assessing all criteria. Start with a warm introduction."""
        
        # Test Nova Sonic text generation (streaming will be handled via WebSocket in production)
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": maya_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, I'm ready to start my IELTS Speaking test."
                }
            ]
        }
        
        # Call Nova Sonic
        response = bedrock.invoke_model(
            modelId='amazon.nova-sonic-v1:0',
            body=json.dumps(request_body),
            contentType='application/json'
        )
        
        # Parse response
        result = json.loads(response['body'].read())
        maya_response = result['content'][0]['text']
        
        print("✅ Nova Sonic (Maya) response:")
        print("-" * 50)
        print(maya_response)
        print("-" * 50)
        print("💡 Full bi-directional streaming available via WebSocket in production")
        return True
        
    except Exception as e:
        print(f"❌ Nova Sonic test failed: {str(e)}")
        if "AccessDeniedException" in str(e):
            print("💡 Enable Nova Sonic access in AWS Bedrock console")
        return False

def check_bedrock_access():
    """Check if Nova models are accessible"""
    print("🔍 Checking Bedrock model access...")
    
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        
        # List available foundation models
        models = bedrock.list_foundation_models()
        
        nova_models = [
            model for model in models['modelSummaries'] 
            if 'nova' in model['modelId'].lower()
        ]
        
        print(f"📊 Found {len(nova_models)} Nova models:")
        for model in nova_models:
            print(f"  - {model['modelId']}: {model.get('modelName', 'Unknown')}")
            
        # Check specific models we need
        required_models = ['amazon.nova-micro-v1:0', 'amazon.nova-sonic-v1:0']
        available_models = [model['modelId'] for model in nova_models]
        
        for required in required_models:
            if required in available_models:
                print(f"✅ {required} is available")
            else:
                print(f"❌ {required} not found - request access in Bedrock console")
                
        return len([m for m in required_models if m in available_models]) == 2
        
    except Exception as e:
        print(f"❌ Could not check Bedrock access: {str(e)}")
        if "AccessDeniedException" in str(e):
            print("💡 Configure AWS credentials with Bedrock permissions")
        return False

def test_development_endpoints():
    """Test the current development system endpoints"""
    print("\n🧪 Testing development system endpoints...")
    
    import requests
    
    try:
        base_url = "http://localhost:5000"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
        # Test mock Nova Micro
        test_data = {
            "essay_text": "This is a test essay for Nova Micro assessment.",
            "prompt": "Test prompt",
            "assessment_type": "academic_writing"
        }
        
        response = requests.post(
            f"{base_url}/api/nova-micro/writing",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Mock Nova Micro endpoint working")
            result = response.json()
            if result.get('success'):
                print("✅ Mock assessment generated successfully")
            else:
                print("❌ Mock assessment failed")
        else:
            print(f"❌ Nova Micro endpoint failed: {response.status_code}")
            
        # Test mock Maya introduction
        maya_data = {
            "assessment_type": "academic_speaking"
        }
        
        response = requests.post(
            f"{base_url}/api/maya/introduction",
            json=maya_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Mock Maya endpoint working")
            result = response.json()
            if result.get('success'):
                print("✅ Mock Maya introduction generated")
            else:
                print("❌ Mock Maya introduction failed")
        else:
            print(f"❌ Maya endpoint failed: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to development server")
        print("💡 Make sure the development server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Development endpoint test failed: {str(e)}")
        return False

def main():
    """Run comprehensive Nova AI testing"""
    print("🧪 IELTS GenAI Prep - Nova AI Integration Testing")
    print("=" * 60)
    
    # Check AWS credentials
    try:
        aws_session = boto3.Session()
        credentials = aws_session.get_credentials()
        if not credentials:
            print("❌ AWS credentials not configured")
            print("💡 Run: aws configure")
            return 1
        else:
            print("✅ AWS credentials configured")
    except Exception as e:
        print(f"❌ AWS setup error: {str(e)}")
        return 1
    
    # Test development endpoints first
    dev_working = test_development_endpoints()
    
    # Check Bedrock access
    bedrock_access = check_bedrock_access()
    
    if not bedrock_access:
        print("\n⚠️  Nova AI testing requires Bedrock model access")
        print("📋 To enable:")
        print("1. Go to AWS Bedrock console (us-east-1)")
        print("2. Request access to Amazon Nova Sonic and Nova Micro")
        print("3. Wait for approval (usually immediate)")
        print("4. Re-run this test script")
        return 1
    
    # Test real Nova AI
    print("\n🤖 Testing real Nova AI integration...")
    nova_micro_working = test_nova_micro_writing()
    nova_sonic_working = test_nova_sonic_streaming()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"Development endpoints: {'✅ Working' if dev_working else '❌ Failed'}")
    print(f"Nova Micro (writing): {'✅ Working' if nova_micro_working else '❌ Failed'}")
    print(f"Nova Sonic (speaking): {'✅ Working' if nova_sonic_working else '❌ Failed'}")
    
    if nova_micro_working and nova_sonic_working:
        print("\n🎉 All Nova AI tests passed!")
        print("💡 You can now deploy to production with confidence")
        print("📋 Next steps:")
        print("1. Run: ./deploy-aws-infrastructure.sh")
        print("2. Run: sam build && sam deploy --guided")
        print("3. Run: python3 populate-assessment-data.py")
        print("4. Run: ./configure-production-endpoints.sh")
        return 0
    else:
        print("\n⚠️  Some tests failed - review errors above")
        return 1

if __name__ == "__main__":
    exit(main())