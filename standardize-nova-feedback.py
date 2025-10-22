#!/usr/bin/env python3
"""
Standardize Nova Micro and Nova Sonic feedback formats
Ensures consistent assessment output across writing and speaking assessments
"""

import boto3
import json
from datetime import datetime
import os

def update_academic_writing_prompts():
    """Update Academic Writing Nova Micro prompts with standardized feedback format"""
    return {
        'system_prompt': '''You are an expert IELTS examiner specializing in Academic Writing Task 1 and Task 2 assessments. Evaluate using official IELTS criteria:

Task Achievement (25%): How well the task is addressed
Coherence and Cohesion (25%): Organization and linking
Lexical Resource (25%): Vocabulary range and accuracy
Grammatical Range and Accuracy (25%): Grammar complexity and correctness

REQUIRED OUTPUT FORMAT:
{
  "overall_band": 7.5,
  "criteria": {
    "task_achievement": {
      "score": 7.0,
      "feedback": "Specific feedback with examples from the text"
    },
    "coherence_cohesion": {
      "score": 8.0,
      "feedback": "Specific feedback about organization and linking"
    },
    "lexical_resource": {
      "score": 7.0,
      "feedback": "Specific feedback about vocabulary usage"
    },
    "grammatical_range": {
      "score": 8.0,
      "feedback": "Specific feedback about grammar structures"
    }
  },
  "detailed_feedback": "Comprehensive analysis with specific examples and improvement suggestions",
  "word_count": [actual_count],
  "strengths": ["Key strength 1", "Key strength 2"],
  "areas_for_improvement": ["Improvement area 1", "Improvement area 2"],
  "assessment_id": "auto_generated",
  "timestamp": "auto_generated"
}

Provide detailed, constructive feedback with specific examples from the text.''',
        'assessment_prompt': 'Analyze this IELTS Academic Writing response and provide comprehensive feedback following the exact JSON format specified in the system prompt.'
    }

def update_general_writing_prompts():
    """Update General Writing Nova Micro prompts with standardized feedback format"""
    return {
        'system_prompt': '''You are an expert IELTS examiner specializing in General Training Writing Task 1 (letters) and Task 2 (essays). Evaluate using official IELTS criteria:

Task Achievement (25%): Addressing requirements, tone, format
Coherence and Cohesion (25%): Organization and linking
Lexical Resource (25%): Vocabulary range and accuracy
Grammatical Range and Accuracy (25%): Grammar complexity and correctness

REQUIRED OUTPUT FORMAT:
{
  "overall_band": 7.5,
  "criteria": {
    "task_achievement": {
      "score": 7.0,
      "feedback": "Specific feedback about task requirements, tone, and format"
    },
    "coherence_cohesion": {
      "score": 8.0,
      "feedback": "Specific feedback about organization and linking"
    },
    "lexical_resource": {
      "score": 7.0,
      "feedback": "Specific feedback about vocabulary usage"
    },
    "grammatical_range": {
      "score": 8.0,
      "feedback": "Specific feedback about grammar structures"
    }
  },
  "detailed_feedback": "Comprehensive analysis with specific examples and improvement suggestions",
  "word_count": [actual_count],
  "strengths": ["Key strength 1", "Key strength 2"],
  "areas_for_improvement": ["Improvement area 1", "Improvement area 2"],
  "assessment_id": "auto_generated",
  "timestamp": "auto_generated"
}

Provide detailed, constructive feedback with specific examples from the text.''',
        'assessment_prompt': 'Analyze this IELTS General Training Writing response and provide comprehensive feedback following the exact JSON format specified in the system prompt.'
    }

def update_academic_speaking_prompts():
    """Update Academic Speaking Nova Sonic prompts with standardized feedback format"""
    return {
        'system_prompt': '''You are Maya, an expert IELTS speaking examiner. Conduct natural conversation following IELTS Academic Speaking test format:

Part 1 (4-5 minutes): Introduction and interview about familiar topics
Part 2 (3-4 minutes): Individual long turn with preparation time
Part 3 (4-5 minutes): Discussion of abstract topics

Evaluate on: Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, Pronunciation.

CONVERSATION ROLE: Be encouraging, natural, and follow IELTS speaking test protocols.

FINAL ASSESSMENT FORMAT (provide at end of conversation):
{
  "overall_band": 7.5,
  "criteria": {
    "fluency_coherence": {
      "score": 7.0,
      "feedback": "Specific feedback about fluency and coherence"
    },
    "lexical_resource": {
      "score": 8.0,
      "feedback": "Specific feedback about vocabulary usage"
    },
    "grammatical_range": {
      "score": 7.0,
      "feedback": "Specific feedback about grammar structures"
    },
    "pronunciation": {
      "score": 8.0,
      "feedback": "Specific feedback about pronunciation features"
    }
  },
  "detailed_feedback": "Comprehensive analysis of speaking performance",
  "conversation_duration": "[minutes]",
  "strengths": ["Key strength 1", "Key strength 2"],
  "areas_for_improvement": ["Improvement area 1", "Improvement area 2"],
  "assessment_id": "auto_generated",
  "timestamp": "auto_generated"
}

Focus on academic topics and abstract discussion.''',
        'maya_personality': 'Professional, encouraging IELTS examiner focused on academic topics and abstract discussion. Warm but maintains test structure.',
        'assessment_prompt': 'Conduct IELTS Academic Speaking assessment and provide final evaluation following the exact JSON format specified in the system prompt.'
    }

def update_general_speaking_prompts():
    """Update General Speaking Nova Sonic prompts with standardized feedback format"""
    return {
        'system_prompt': '''You are Maya, an expert IELTS speaking examiner for General Training. Conduct natural conversation following format:

Part 1 (4-5 minutes): Introduction and familiar topics about daily life, family, work
Part 2 (3-4 minutes): Individual long turn on personal experiences
Part 3 (4-5 minutes): Discussion of practical topics and experiences

Evaluate on: Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, Pronunciation.

CONVERSATION ROLE: Be warm, encouraging, and focus on practical communication.

FINAL ASSESSMENT FORMAT (provide at end of conversation):
{
  "overall_band": 7.5,
  "criteria": {
    "fluency_coherence": {
      "score": 7.0,
      "feedback": "Specific feedback about fluency and coherence"
    },
    "lexical_resource": {
      "score": 8.0,
      "feedback": "Specific feedback about vocabulary usage"
    },
    "grammatical_range": {
      "score": 7.0,
      "feedback": "Specific feedback about grammar structures"
    },
    "pronunciation": {
      "score": 8.0,
      "feedback": "Specific feedback about pronunciation features"
    }
  },
  "detailed_feedback": "Comprehensive analysis of speaking performance",
  "conversation_duration": "[minutes]",
  "strengths": ["Key strength 1", "Key strength 2"],
  "areas_for_improvement": ["Improvement area 1", "Improvement area 2"],
  "assessment_id": "auto_generated",
  "timestamp": "auto_generated"
}

Focus on practical communication skills and real-world topics.''',
        'maya_personality': 'Warm, encouraging examiner focused on practical communication. Ask about real experiences and daily life situations.',
        'assessment_prompt': 'Conduct IELTS General Training Speaking assessment and provide final evaluation following the exact JSON format specified in the system prompt.'
    }

def update_dynamodb_rubrics():
    """Update DynamoDB with standardized Nova prompts"""
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    # Update Academic Writing
    try:
        response = dynamodb.update_item(
            TableName='ielts-genai-prep-rubrics',
            Key={'assessment_type': {'S': 'academic_writing'}},
            UpdateExpression='SET nova_micro_prompts = :prompts, updated_at = :timestamp',
            ExpressionAttributeValues={
                ':prompts': {'M': {
                    'system_prompt': {'S': update_academic_writing_prompts()['system_prompt']},
                    'assessment_prompt': {'S': update_academic_writing_prompts()['assessment_prompt']}
                }},
                ':timestamp': {'S': datetime.utcnow().isoformat()}
            }
        )
        print("✅ Updated Academic Writing Nova Micro prompts")
    except Exception as e:
        print(f"❌ Failed to update Academic Writing: {e}")

    # Update General Writing
    try:
        response = dynamodb.update_item(
            TableName='ielts-genai-prep-rubrics',
            Key={'assessment_type': {'S': 'general_writing'}},
            UpdateExpression='SET nova_micro_prompts = :prompts, updated_at = :timestamp',
            ExpressionAttributeValues={
                ':prompts': {'M': {
                    'system_prompt': {'S': update_general_writing_prompts()['system_prompt']},
                    'assessment_prompt': {'S': update_general_writing_prompts()['assessment_prompt']}
                }},
                ':timestamp': {'S': datetime.utcnow().isoformat()}
            }
        )
        print("✅ Updated General Writing Nova Micro prompts")
    except Exception as e:
        print(f"❌ Failed to update General Writing: {e}")

    # Update Academic Speaking
    try:
        response = dynamodb.update_item(
            TableName='ielts-genai-prep-rubrics',
            Key={'assessment_type': {'S': 'academic_speaking'}},
            UpdateExpression='SET nova_sonic_prompts = :prompts, updated_at = :timestamp',
            ExpressionAttributeValues={
                ':prompts': {'M': {
                    'system_prompt': {'S': update_academic_speaking_prompts()['system_prompt']},
                    'maya_personality': {'S': update_academic_speaking_prompts()['maya_personality']},
                    'assessment_prompt': {'S': update_academic_speaking_prompts()['assessment_prompt']}
                }},
                ':timestamp': {'S': datetime.utcnow().isoformat()}
            }
        )
        print("✅ Updated Academic Speaking Nova Sonic prompts")
    except Exception as e:
        print(f"❌ Failed to update Academic Speaking: {e}")

    # Update General Speaking
    try:
        response = dynamodb.update_item(
            TableName='ielts-genai-prep-rubrics',
            Key={'assessment_type': {'S': 'general_speaking'}},
            UpdateExpression='SET nova_sonic_prompts = :prompts, updated_at = :timestamp',
            ExpressionAttributeValues={
                ':prompts': {'M': {
                    'system_prompt': {'S': update_general_speaking_prompts()['system_prompt']},
                    'maya_personality': {'S': update_general_speaking_prompts()['maya_personality']},
                    'assessment_prompt': {'S': update_general_speaking_prompts()['assessment_prompt']}
                }},
                ':timestamp': {'S': datetime.utcnow().isoformat()}
            }
        )
        print("✅ Updated General Speaking Nova Sonic prompts")
    except Exception as e:
        print(f"❌ Failed to update General Speaking: {e}")

def update_local_mock_config():
    """Update local AWS mock configuration with standardized prompts"""
    # Update the aws_mock_config.py file
    with open('aws_mock_config.py', 'r') as f:
        content = f.read()
    
    # This would require more complex string replacement
    # For now, we'll create a new initialization method
    print("📝 Local mock configuration should be updated manually")
    print("   The DynamoDB updates will be reflected in production")

def main():
    """Main function to standardize Nova feedback formats"""
    print("=== Standardizing Nova Feedback Formats ===")
    print()
    
    print("🔄 Updating DynamoDB rubrics with standardized prompts...")
    update_dynamodb_rubrics()
    
    print()
    print("✅ Standardization Complete!")
    print()
    print("📊 Updated Components:")
    print("  • Nova Micro (Academic Writing) - Standardized JSON feedback")
    print("  • Nova Micro (General Writing) - Standardized JSON feedback")
    print("  • Nova Sonic (Academic Speaking) - Standardized JSON feedback")
    print("  • Nova Sonic (General Speaking) - Standardized JSON feedback")
    print()
    print("📋 Standardized Feedback Format:")
    print("  • overall_band: Overall IELTS band score")
    print("  • criteria: 4-criterion breakdown with scores and feedback")
    print("  • detailed_feedback: Comprehensive analysis")
    print("  • strengths: Key areas of strength")
    print("  • areas_for_improvement: Specific improvement areas")
    print("  • word_count/conversation_duration: Assessment metrics")
    print()
    print("🎯 Benefits:")
    print("  • Consistent assessment output across all modules")
    print("  • Structured feedback for better user experience")
    print("  • Enhanced TrueScore® and ClearScore® branding alignment")
    print("  • Improved assessment analytics and tracking")

if __name__ == "__main__":
    main()