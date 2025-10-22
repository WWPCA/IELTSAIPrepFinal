#!/usr/bin/env python3
"""
IELTS GenAI Prep - Assessment Data Population Script
Populates DynamoDB tables with IELTS assessment rubrics and system prompts
"""

import boto3
import json
import os
from datetime import datetime

def get_dynamodb_client(region='us-east-1'):
    """Initialize DynamoDB client"""
    return boto3.client('dynamodb', region_name=region)

def populate_assessment_rubrics(dynamodb_client, table_name):
    """Populate DynamoDB with IELTS assessment rubrics"""
    
    # Academic Writing Assessment Rubric
    academic_writing_rubric = {
        'assessment_type': {'S': 'academic_writing'},
        'rubric_name': {'S': 'TrueScore® GenAI Writing Assessment'},
        'criteria': {'M': {
            'task_achievement': {'M': {
                'band_9': {'S': 'Fully addresses all parts of the task with comprehensive ideas and clear position'},
                'band_8': {'S': 'Sufficiently addresses all parts with well-developed ideas'},
                'band_7': {'S': 'Addresses all parts though some may be more fully covered than others'},
                'band_6': {'S': 'Addresses the requirements though some parts may be inadequately covered'},
                'band_5': {'S': 'Addresses the task only partially with limited development'},
                'band_4': {'S': 'Attempts to address the task but does not cover all requirements'},
                'weight': {'N': '25'}
            }},
            'coherence_cohesion': {'M': {
                'band_9': {'S': 'Uses cohesion in such a way that it attracts no attention'},
                'band_8': {'S': 'Sequences information logically with clear progression'},
                'band_7': {'S': 'Logically organizes information with clear progression throughout'},
                'band_6': {'S': 'Arranges information coherently with overall progression'},
                'band_5': {'S': 'Presents information with some organization but lacks overall progression'},
                'band_4': {'S': 'Information and ideas not arranged coherently'},
                'weight': {'N': '25'}
            }},
            'lexical_resource': {'M': {
                'band_9': {'S': 'Wide range of vocabulary used naturally and flexibly'},
                'band_8': {'S': 'Wide range of vocabulary fluently and flexibly used'},
                'band_7': {'S': 'Sufficient range of vocabulary with some flexibility'},
                'band_6': {'S': 'Adequate range of vocabulary for the task'},
                'band_5': {'S': 'Limited range of vocabulary with repetition'},
                'band_4': {'S': 'Limited range affecting meaning and clarity'},
                'weight': {'N': '25'}
            }},
            'grammatical_accuracy': {'M': {
                'band_9': {'S': 'Wide range of structures used accurately and appropriately'},
                'band_8': {'S': 'Wide range of structures with majority error-free'},
                'band_7': {'S': 'Variety of complex structures with good control'},
                'band_6': {'S': 'Mix of simple and complex structures with some errors'},
                'band_5': {'S': 'Limited range of structures with frequent errors'},
                'band_4': {'S': 'Limited structures with frequent errors affecting meaning'},
                'weight': {'N': '25'}
            }}
        }},
        'nova_micro_prompts': {'M': {
            'system_prompt': {'S': '''You are an expert IELTS examiner specializing in Academic Writing Task 1 and Task 2 assessments. Evaluate the essay using official IELTS criteria:

Task Achievement (25%): How well the task is addressed
Coherence and Cohesion (25%): Organization and linking
Lexical Resource (25%): Vocabulary range and accuracy
Grammatical Range and Accuracy (25%): Grammar complexity and correctness

Provide detailed feedback with specific examples and an overall band score (1-9).'''},
            'assessment_prompt': {'S': 'Analyze this IELTS Academic Writing response and provide comprehensive feedback with band scores for each criterion and overall assessment.'}
        }},
        'updated_at': {'S': datetime.utcnow().isoformat()}
    }

    # General Writing Assessment Rubric
    general_writing_rubric = {
        'assessment_type': {'S': 'general_writing'},
        'rubric_name': {'S': 'TrueScore® GenAI Writing Assessment'},
        'criteria': {'M': {
            'task_achievement': {'M': {
                'band_9': {'S': 'Fully addresses all requirements with appropriate tone and format'},
                'band_8': {'S': 'Covers all requirements with consistent appropriate tone'},
                'band_7': {'S': 'Covers requirements with generally appropriate tone'},
                'band_6': {'S': 'Addresses requirements though tone may be inappropriate'},
                'band_5': {'S': 'Addresses some requirements with inconsistent tone'},
                'band_4': {'S': 'Attempts to address requirements but format/tone unclear'},
                'weight': {'N': '25'}
            }},
            'coherence_cohesion': {'M': {
                'band_9': {'S': 'Uses cohesion perfectly with natural flow'},
                'band_8': {'S': 'Sequences information logically with clear progression'},
                'band_7': {'S': 'Logically organizes information with clear progression'},
                'band_6': {'S': 'Arranges information coherently with overall progression'},
                'band_5': {'S': 'Presents information with some organization'},
                'band_4': {'S': 'Information not arranged coherently'},
                'weight': {'N': '25'}
            }},
            'lexical_resource': {'M': {
                'band_9': {'S': 'Wide range of vocabulary used naturally'},
                'band_8': {'S': 'Wide range of vocabulary fluently used'},
                'band_7': {'S': 'Sufficient range of vocabulary with flexibility'},
                'band_6': {'S': 'Adequate range of vocabulary for the task'},
                'band_5': {'S': 'Limited range with repetition'},
                'band_4': {'S': 'Limited range affecting clarity'},
                'weight': {'N': '25'}
            }},
            'grammatical_accuracy': {'M': {
                'band_9': {'S': 'Wide range of structures used accurately'},
                'band_8': {'S': 'Wide range with majority error-free'},
                'band_7': {'S': 'Variety of structures with good control'},
                'band_6': {'S': 'Mix of structures with some errors'},
                'band_5': {'S': 'Limited structures with frequent errors'},
                'band_4': {'S': 'Limited structures affecting meaning'},
                'weight': {'N': '25'}
            }}
        }},
        'nova_micro_prompts': {'M': {
            'system_prompt': {'S': '''You are an expert IELTS examiner specializing in General Training Writing Task 1 (letters) and Task 2 (essays). Evaluate using official IELTS criteria:

Task Achievement (25%): Addressing requirements, tone, format
Coherence and Cohesion (25%): Organization and linking
Lexical Resource (25%): Vocabulary range and accuracy
Grammatical Range and Accuracy (25%): Grammar complexity and correctness

Provide detailed feedback with specific examples and band scores.'''},
            'assessment_prompt': {'S': 'Analyze this IELTS General Training Writing response and provide comprehensive feedback with band scores for each criterion.'}
        }},
        'updated_at': {'S': datetime.utcnow().isoformat()}
    }

    # Academic Speaking Assessment Rubric
    academic_speaking_rubric = {
        'assessment_type': {'S': 'academic_speaking'},
        'rubric_name': {'S': 'ClearScore® GenAI Speaking Assessment'},
        'criteria': {'M': {
            'fluency_coherence': {'M': {
                'band_9': {'S': 'Speaks fluently with natural hesitation patterns'},
                'band_8': {'S': 'Speaks fluently with occasional repetition or hesitation'},
                'band_7': {'S': 'Speaks at length with some hesitation but maintains flow'},
                'band_6': {'S': 'Willing to speak at length with hesitation and repetition'},
                'band_5': {'S': 'Usually maintains flow with noticeable effort'},
                'band_4': {'S': 'Cannot respond without noticeable pauses'},
                'weight': {'N': '25'}
            }},
            'lexical_resource': {'M': {
                'band_9': {'S': 'Uses vocabulary precisely with natural and sophisticated language'},
                'band_8': {'S': 'Wide range of vocabulary fluently and flexibly used'},
                'band_7': {'S': 'Flexible vocabulary to discuss variety of topics'},
                'band_6': {'S': 'Wide enough vocabulary to discuss topics at length'},
                'band_5': {'S': 'Limited vocabulary but manages to talk about familiar topics'},
                'band_4': {'S': 'Limited vocabulary affects communication'},
                'weight': {'N': '25'}
            }},
            'grammatical_accuracy': {'M': {
                'band_9': {'S': 'Uses wide range of structures naturally and accurately'},
                'band_8': {'S': 'Wide range of structures flexibly used'},
                'band_7': {'S': 'Range of complex structures with some flexibility'},
                'band_6': {'S': 'Mix of simple and complex forms with errors'},
                'band_5': {'S': 'Basic sentence forms with frequent errors'},
                'band_4': {'S': 'Limited structures affecting communication'},
                'weight': {'N': '25'}
            }},
            'pronunciation': {'M': {
                'band_9': {'S': 'Uses wide range of pronunciation features naturally'},
                'band_8': {'S': 'Wide range of pronunciation features flexibly used'},
                'band_7': {'S': 'Shows pronunciation features with generally clear speech'},
                'band_6': {'S': 'Uses range of pronunciation features with some effective use'},
                'band_5': {'S': 'Shows some effective use of pronunciation features'},
                'band_4': {'S': 'Limited pronunciation features affecting understanding'},
                'weight': {'N': '25'}
            }}
        }},
        'nova_sonic_prompts': {'M': {
            'system_prompt': {'S': '''You are Maya, an expert IELTS speaking examiner. Conduct a natural conversation following IELTS Academic Speaking test format:

Part 1: Introduction and familiar topics (4-5 minutes)
Part 2: Individual long turn with cue card (3-4 minutes)  
Part 3: Discussion of abstract ideas (4-5 minutes)

Evaluate on: Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, Pronunciation (25% each).

Maintain natural conversation flow while assessing all criteria.'''},
            'maya_personality': {'S': 'Professional, encouraging, and naturally conversational. Ask follow-up questions and maintain authentic examiner demeanor.'}
        }},
        'updated_at': {'S': datetime.utcnow().isoformat()}
    }

    # General Speaking Assessment Rubric
    general_speaking_rubric = {
        'assessment_type': {'S': 'general_speaking'},
        'rubric_name': {'S': 'ClearScore® GenAI Speaking Assessment'},
        'criteria': {'M': {
            'fluency_coherence': {'M': {
                'band_9': {'S': 'Speaks fluently with natural hesitation patterns'},
                'band_8': {'S': 'Speaks fluently with occasional repetition'},
                'band_7': {'S': 'Speaks at length with some hesitation'},
                'band_6': {'S': 'Willing to speak at length with hesitation'},
                'band_5': {'S': 'Usually maintains flow with effort'},
                'band_4': {'S': 'Cannot respond without noticeable pauses'},
                'weight': {'N': '25'}
            }},
            'lexical_resource': {'M': {
                'band_9': {'S': 'Uses vocabulary precisely with sophisticated language'},
                'band_8': {'S': 'Wide range of vocabulary fluently used'},
                'band_7': {'S': 'Flexible vocabulary for variety of topics'},
                'band_6': {'S': 'Wide enough vocabulary for discussion'},
                'band_5': {'S': 'Limited vocabulary for familiar topics'},
                'band_4': {'S': 'Limited vocabulary affects communication'},
                'weight': {'N': '25'}
            }},
            'grammatical_accuracy': {'M': {
                'band_9': {'S': 'Uses structures naturally and accurately'},
                'band_8': {'S': 'Wide range of structures flexibly used'},
                'band_7': {'S': 'Range of complex structures'},
                'band_6': {'S': 'Mix of simple and complex forms'},
                'band_5': {'S': 'Basic sentence forms with errors'},
                'band_4': {'S': 'Limited structures affecting communication'},
                'weight': {'N': '25'}
            }},
            'pronunciation': {'M': {
                'band_9': {'S': 'Uses pronunciation features naturally'},
                'band_8': {'S': 'Wide range of pronunciation features'},
                'band_7': {'S': 'Shows pronunciation features clearly'},
                'band_6': {'S': 'Uses pronunciation features effectively'},
                'band_5': {'S': 'Shows some effective pronunciation use'},
                'band_4': {'S': 'Limited pronunciation affecting understanding'},
                'weight': {'N': '25'}
            }}
        }},
        'nova_sonic_prompts': {'M': {
            'system_prompt': {'S': '''You are Maya, an expert IELTS speaking examiner for General Training. Conduct natural conversation following format:

Part 1: Introduction and familiar topics about daily life, family, work
Part 2: Individual long turn on personal experiences
Part 3: Discussion of practical topics and experiences

Evaluate on: Fluency and Coherence, Lexical Resource, Grammatical Range and Accuracy, Pronunciation.

Focus on practical communication skills and real-world topics.'''},
            'maya_personality': {'S': 'Warm, encouraging, and focused on practical communication. Ask about real experiences and daily life situations.'}
        }},
        'updated_at': {'S': datetime.utcnow().isoformat()}
    }

    # Insert all rubrics
    rubrics = [
        academic_writing_rubric,
        general_writing_rubric,
        academic_speaking_rubric,
        general_speaking_rubric
    ]

    for rubric in rubrics:
        try:
            response = dynamodb_client.put_item(
                TableName=table_name,
                Item=rubric
            )
            print(f"✅ Inserted {rubric['assessment_type']['S']} rubric")
        except Exception as e:
            print(f"❌ Failed to insert {rubric['assessment_type']['S']}: {str(e)}")

def main():
    """Main execution function"""
    region = os.environ.get('AWS_REGION', 'us-east-1')
    stack_name = os.environ.get('STACK_NAME', 'ielts-genai-prep')
    
    # Table names based on stack
    rubrics_table = f"{stack_name}-rubrics"
    
    print(f"🚀 Populating IELTS assessment data in region: {region}")
    print(f"📊 Target table: {rubrics_table}")
    
    try:
        dynamodb_client = get_dynamodb_client(region)
        
        # Populate assessment rubrics
        populate_assessment_rubrics(dynamodb_client, rubrics_table)
        
        print("✅ Assessment data population completed successfully!")
        print("")
        print("📋 Populated assessment types:")
        print("  • academic_writing - TrueScore® GenAI Writing Assessment")
        print("  • general_writing - TrueScore® GenAI Writing Assessment") 
        print("  • academic_speaking - ClearScore® GenAI Speaking Assessment")
        print("  • general_speaking - ClearScore® GenAI Speaking Assessment")
        print("")
        print("🤖 Nova AI integration ready:")
        print("  • Nova Micro prompts configured for writing assessments")
        print("  • Nova Sonic prompts configured for Maya speaking examiner")
        
    except Exception as e:
        print(f"❌ Error populating data: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())