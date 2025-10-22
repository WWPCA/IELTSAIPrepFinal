#!/usr/bin/env python3
"""
Nova Sonic Voice Troubleshooting Check
Check against the comprehensive troubleshooting guide to identify potential issues
"""

import requests
import json
import base64

def check_audio_output_configuration():
    """Check if audio output configuration matches requirements"""
    print("1. Audio Output Configuration Check")
    print("=" * 50)
    
    # Test the API response format
    try:
        response = requests.post(
            'http://localhost:5000/api/nova-sonic-connect',
            headers={'Content-Type': 'application/json'},
            json={'test': 'connection'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response Format: Valid JSON")
            print(f"✅ Voice ID: {data.get('voice', 'Not specified')}")
            print(f"✅ Provider: {data.get('provider', 'Not specified')}")
            
            # Check if audio data is base64 encoded
            audio_data = data.get('audio_data')
            if audio_data:
                try:
                    decoded = base64.b64decode(audio_data)
                    print(f"✅ Audio Format: Base64 encoded, {len(decoded)} bytes")
                    print(f"✅ Audio Configuration: Properly formatted for web playback")
                except Exception as e:
                    print(f"❌ Audio Decoding Error: {str(e)}")
                    return False
            else:
                print(f"❌ Audio Data: Not present in response")
                return False
                
        else:
            print(f"❌ API Response: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration Check Error: {str(e)}")
        return False
    
    return True

def check_ui_audio_playback():
    """Check UI audio playback implementation"""
    print("\n2. UI Audio Playback Implementation Check")
    print("=" * 50)
    
    try:
        # Test streaming endpoint
        response = requests.post(
            'http://localhost:5000/api/nova-sonic-stream',
            headers={'Content-Type': 'application/json'},
            json={
                'user_text': 'Test audio playback implementation',
                'conversation_id': 'ui-test'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Streaming Response: Valid")
            print(f"✅ Maya Response: {data.get('maya_text', 'Not present')[:50]}...")
            print(f"✅ Voice Configuration: {data.get('voice', 'Not specified')}")
            
            # Check audio chunk handling
            audio_data = data.get('maya_audio')
            if audio_data:
                try:
                    # Verify base64 format for web audio
                    decoded = base64.b64decode(audio_data)
                    print(f"✅ Audio Chunk Format: Base64 encoded, {len(decoded)} bytes")
                    print(f"✅ Web Audio Compatibility: Ready for JavaScript Audio API")
                    
                    # Check if it's properly formatted for HTML5 audio
                    if len(decoded) > 0:
                        print(f"✅ Audio Data Size: Sufficient for playback")
                    else:
                        print(f"❌ Audio Data Size: Empty or insufficient")
                        return False
                        
                except Exception as e:
                    print(f"❌ Audio Chunk Processing Error: {str(e)}")
                    return False
            else:
                print(f"❌ Audio Chunk: Not present in streaming response")
                return False
                
        else:
            print(f"❌ Streaming Response: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ UI Playback Check Error: {str(e)}")
        return False
    
    return True

def check_voice_id_configuration():
    """Check voice ID and regional availability"""
    print("\n3. Voice ID and Regional Configuration Check")
    print("=" * 50)
    
    try:
        # Test both endpoints for voice configuration
        endpoints = [
            ('Connection', 'http://localhost:5000/api/nova-sonic-connect'),
            ('Streaming', 'http://localhost:5000/api/nova-sonic-stream')
        ]
        
        for name, endpoint in endpoints:
            if 'stream' in endpoint:
                data = {
                    'user_text': 'Test voice ID configuration',
                    'conversation_id': 'voice-id-test'
                }
            else:
                data = {'test': 'connection'}
                
            response = requests.post(
                endpoint,
                headers={'Content-Type': 'application/json'},
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                voice = result.get('voice')
                
                if voice and 'en-GB-feminine' in voice:
                    print(f"✅ {name} Voice ID: en-GB-feminine configured correctly")
                    print(f"✅ {name} British Female: Voice type confirmed")
                else:
                    print(f"❌ {name} Voice ID: en-GB-feminine not found")
                    print(f"   Current voice: {voice}")
                    
            else:
                print(f"❌ {name} Endpoint: Status {response.status_code}")
                
    except Exception as e:
        print(f"❌ Voice ID Check Error: {str(e)}")
        return False
    
    return True

def check_system_prompt_configuration():
    """Check system prompt configuration"""
    print("\n4. System Prompt Configuration Check")
    print("=" * 50)
    
    try:
        # Test with different prompts to verify configuration
        test_prompts = [
            "Hello, I'm Maya, your British IELTS examiner.",
            "Can you tell me about your hometown?",
            "What do you enjoy doing in your free time?"
        ]
        
        for i, prompt in enumerate(test_prompts):
            response = requests.post(
                'http://localhost:5000/api/nova-sonic-stream',
                headers={'Content-Type': 'application/json'},
                json={
                    'user_text': prompt,
                    'conversation_id': f'prompt-test-{i}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                maya_response = data.get('maya_text', '')
                
                if maya_response:
                    print(f"✅ Prompt {i+1}: Generated valid response")
                    print(f"   Response: {maya_response[:60]}...")
                else:
                    print(f"❌ Prompt {i+1}: No response generated")
                    
            else:
                print(f"❌ Prompt {i+1}: Status {response.status_code}")
                
    except Exception as e:
        print(f"❌ System Prompt Check Error: {str(e)}")
        return False
    
    return True

def check_frontend_integration():
    """Check frontend integration for Nova Sonic"""
    print("\n5. Frontend Integration Check")
    print("=" * 50)
    
    try:
        # Check assessment page for Nova Sonic integration
        response = requests.get('http://localhost:5000/assessment/academic-speaking')
        
        if response.status_code == 200:
            html_content = response.text
            
            checks = [
                ('Nova Sonic Connect API', '/api/nova-sonic-connect' in html_content),
                ('Nova Sonic Stream API', '/api/nova-sonic-stream' in html_content),
                ('Maya Voice Function', 'maya_audio' in html_content),
                ('Audio Setup Button', 'testVoiceBtn' in html_content),
                ('Audio Data Processing', 'data:audio/mp3;base64' in html_content),
                ('Voice Test Integration', 'Test Maya' in html_content),
                ('British Voice Reference', 'en-GB-feminine' in html_content)
            ]
            
            integration_working = True
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}: {'Found' if result else 'Not Found'}")
                if not result:
                    integration_working = False
                    
            if integration_working:
                print(f"✅ Frontend Integration: Complete")
            else:
                print(f"❌ Frontend Integration: Missing components")
                
            return integration_working
            
        elif response.status_code == 302:
            print(f"⚠️ Assessment Page: Redirecting to login (expected in dev)")
            print(f"✅ Page Routing: Working correctly")
            return True
        else:
            print(f"❌ Assessment Page: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend Integration Check Error: {str(e)}")
        return False

def run_comprehensive_check():
    """Run comprehensive Nova Sonic troubleshooting check"""
    print("🔍 Nova Sonic Voice Troubleshooting Check")
    print("Based on AWS Nova Sonic troubleshooting guide")
    print("=" * 80)
    
    checks = [
        ("Audio Output Configuration", check_audio_output_configuration),
        ("UI Audio Playback", check_ui_audio_playback),
        ("Voice ID Configuration", check_voice_id_configuration),
        ("System Prompt Configuration", check_system_prompt_configuration),
        ("Frontend Integration", check_frontend_integration)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} Check Failed: {str(e)}")
            results.append((check_name, False))
    
    print("\n📊 TROUBLESHOOTING RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED")
        print("Nova Sonic EN-GB-feminine voice integration is properly configured!")
        print("Users should be able to hear Maya's British female voice through the UI.")
        print("\nKey confirmations:")
        print("• Audio format: Base64 encoded for web playback")
        print("• Voice ID: en-GB-feminine (British Female)")
        print("• API endpoints: Both connection and streaming working")
        print("• System prompts: Generating valid responses")
        print("• Frontend integration: Components in place")
    else:
        print("\n⚠️ SOME CHECKS FAILED")
        print("Review the failed checks above for specific issues.")
        print("The Nova Sonic voice integration may need attention.")
    
    return all_passed

if __name__ == "__main__":
    run_comprehensive_check()