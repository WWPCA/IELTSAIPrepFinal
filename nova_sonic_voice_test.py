#!/usr/bin/env python3
"""
Nova Sonic Voice Test - Verify EN-GB-feminine Voice Integration
Tests Nova Sonic Amy (British female voice) functionality and UI integration
"""

import requests
import json
import base64
import time

def test_nova_sonic_connection():
    """Test Nova Sonic connection endpoint"""
    print("🧪 Testing Nova Sonic Connection...")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/nova-sonic-connect',
            headers={'Content-Type': 'application/json'},
            json={'test': 'connection'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection Status: {data.get('status')}")
            print(f"📢 Voice: {data.get('voice')}")
            print(f"🔊 Provider: {data.get('provider')}")
            print(f"🎵 Audio Data: {'Available' if data.get('audio_data') else 'Not Available'}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {str(e)}")
        return False

def test_nova_sonic_streaming():
    """Test Nova Sonic streaming endpoint"""
    print("\n🧪 Testing Nova Sonic Streaming...")
    
    test_phrases = [
        "Hello, I'm Maya, your IELTS examiner. Welcome to your speaking assessment.",
        "Please tell me about your hometown.",
        "Can you describe your daily routine?",
        "Thank you for your response. Let's move to the next question."
    ]
    
    for i, phrase in enumerate(test_phrases):
        print(f"\n📝 Test {i+1}: {phrase[:50]}...")
        
        try:
            response = requests.post(
                'http://localhost:5000/api/nova-sonic-stream',
                headers={'Content-Type': 'application/json'},
                json={
                    'user_text': phrase,
                    'conversation_id': f'test-{i+1}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Stream Status: {data.get('status')}")
                print(f"🎭 Maya Response: {data.get('maya_text', 'No response')[:80]}...")
                print(f"🔊 Voice: {data.get('voice')}")
                print(f"🎵 Audio: {'Available' if data.get('maya_audio') else 'Not Available'}")
                
                # Check if audio data is base64 encoded
                if data.get('maya_audio'):
                    try:
                        audio_bytes = base64.b64decode(data['maya_audio'])
                        print(f"📊 Audio Size: {len(audio_bytes)} bytes")
                    except Exception as e:
                        print(f"⚠️ Audio decode error: {str(e)}")
                        
            else:
                print(f"❌ Stream failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Stream test error: {str(e)}")
            
        time.sleep(1)  # Brief pause between tests

def test_assessment_page_integration():
    """Test if assessment page can load Nova Sonic integration"""
    print("\n🧪 Testing Assessment Page Integration...")
    
    try:
        response = requests.get('http://localhost:5000/assessment/academic-speaking')
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for Nova Sonic integration in the page
            checks = [
                ('Nova Sonic Connect', '/api/nova-sonic-connect' in html_content),
                ('Nova Sonic Stream', '/api/nova-sonic-stream' in html_content),
                ('Maya Voice', 'Maya' in html_content),
                ('British Voice', 'en-GB-feminine' in html_content or 'British' in html_content),
                ('Voice Test Function', 'testVoiceBtn' in html_content),
                ('Audio Setup', 'setupAudioBtn' in html_content)
            ]
            
            print("📋 Assessment Page Integration:")
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}: {'Found' if result else 'Not Found'}")
                
            return any(result for _, result in checks)
            
        else:
            print(f"❌ Assessment page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Assessment page test error: {str(e)}")
        return False

def test_voice_ui_workflow():
    """Test complete voice UI workflow"""
    print("\n🧪 Testing Complete Voice UI Workflow...")
    
    workflow_steps = [
        ("Connection Test", test_nova_sonic_connection),
        ("Streaming Test", lambda: test_nova_sonic_streaming()),
        ("Page Integration", test_assessment_page_integration)
    ]
    
    results = []
    for step_name, test_func in workflow_steps:
        print(f"\n🔄 Running {step_name}...")
        try:
            result = test_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ {step_name} failed: {str(e)}")
            results.append((step_name, False))
    
    print("\n📊 NOVA SONIC VOICE TEST RESULTS")
    print("=" * 50)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {step_name}")
    
    overall_success = all(result for _, result in results)
    print(f"\n🎯 Overall Status: {'✅ EN-GB-feminine Voice Working' if overall_success else '❌ Voice Issues Detected'}")
    
    return overall_success

if __name__ == "__main__":
    print("🚀 Nova Sonic EN-GB-feminine Voice Verification")
    print("=" * 60)
    
    success = test_voice_ui_workflow()
    
    if success:
        print("\n🎉 Nova Sonic Amy (British female voice) is working correctly!")
        print("Users should be able to hear Maya's EN-GB-feminine voice in assessments.")
    else:
        print("\n⚠️ Nova Sonic voice integration needs attention.")
        print("Check the test results above for specific issues.")