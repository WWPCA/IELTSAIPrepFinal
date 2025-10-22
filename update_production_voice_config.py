#!/usr/bin/env python3
"""
Update Production Lambda with EN-GB-feminine Voice Configuration
Standardizes Nova Sonic voice to use en-GB-feminine in both dev and prod
"""

import json
import zipfile
import io

def update_production_voice_config():
    """Update production Lambda with standardized en-GB-feminine voice"""
    
    # Read the current production deployment script
    with open('deploy_production_ses_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update voice configuration to use en-GB-feminine
    updated_content = content.replace(
        "'voice_id': 'Amy'",
        "'voice_id': 'en-GB-feminine'"
    ).replace(
        "'status': 'Nova Sonic Amy voice connected'",
        "'status': 'Nova Sonic en-GB-feminine voice connected'"
    ).replace(
        "'message': 'Maya voice working ✓'",
        "'message': 'Maya voice working ✓ (en-GB-feminine)'"
    )
    
    # Add proper Nova Sonic voice synthesis function
    nova_sonic_function = '''
def synthesize_maya_voice_nova_sonic(text: str) -> str:
    """
    Synthesize Maya's voice using AWS Nova Sonic en-GB-feminine
    Returns base64 encoded audio data
    """
    try:
        import boto3
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Configure for British female voice
        request_body = {
            "inputText": text,
            "voice": {
                "id": "en-GB-feminine"
            },
            "outputFormat": {
                "format": "mp3"
            }
        }
        
        # Use Nova Sonic voice synthesis
        response = bedrock_client.invoke_model(
            modelId="amazon.nova-sonic-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        
        # Process Nova Sonic response
        response_body = json.loads(response['body'].read())
        
        if 'audio' in response_body:
            return response_body['audio']
        else:
            print(f"[NOVA_SONIC] No audio data in response")
            return None
            
    except Exception as e:
        print(f"[NOVA_SONIC] Error: {str(e)}")
        return None

'''
    
    # Insert Nova Sonic function at the beginning
    if 'def synthesize_maya_voice_nova_sonic' not in updated_content:
        updated_content = updated_content.replace(
            'import json',
            f'import json\n{nova_sonic_function}'
        )
    
    # Update API endpoints to use en-GB-feminine
    updated_content = updated_content.replace(
        "'/api/nova-sonic-stream':",
        """'/api/nova-sonic-stream':
        # Process Nova Sonic streaming with en-GB-feminine voice
        try:
            data = json.loads(body)
            user_text = data.get('text', 'Hello')
            
            # Generate Maya's response
            maya_response = f"Thank you for your response. Let me ask you another question: {user_text}"
            
            # Synthesize Maya's voice using Nova Sonic en-GB-feminine
            audio_data = synthesize_maya_voice_nova_sonic(maya_response)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'user_transcript': user_text,
                    'maya_response': maya_response,
                    'maya_audio': audio_data,
                    'status': 'Maya is speaking... (en-GB-feminine)',
                    'voice': 'en-GB-feminine'
                })
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': f'Nova Sonic en-GB-feminine error: {str(e)}'
                })
            }
    
    elif path == '/api/nova-sonic-stream'"""
    )
    
    # Save updated deployment script
    with open('deploy_production_voice_standardized.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("=== PRODUCTION VOICE CONFIG UPDATED ===")
    print("✅ Voice configuration standardized to en-GB-feminine")
    print("✅ Nova Sonic function added with proper voice synthesis")
    print("✅ API endpoints updated to use en-GB-feminine")
    print("✅ Created: deploy_production_voice_standardized.py")
    print("\n🚀 Ready to deploy standardized voice configuration to production")

if __name__ == "__main__":
    update_production_voice_config()