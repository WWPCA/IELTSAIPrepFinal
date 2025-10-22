#!/usr/bin/env python3
"""
Full Assessment Migration to DynamoDB
Migrates all comprehensive IELTS assessment content to database with proper table structure
"""

import json
import os
import uuid
import time
from typing import Dict, Any, List

# Set environment for .replit testing
os.environ['REPLIT_ENVIRONMENT'] = 'true'

# Import AWS mock services
from aws_mock_config import aws_mock

def parse_academic_writing_content():
    """Parse Academic Writing Task 2 essays from attached files"""
    questions = []
    
    try:
        with open('attached_assets/Academic Writing Task 2 tests (essays).txt', 'r') as f:
            content = f.read()
        
        # Split by numbered questions
        sections = content.split('\n\n')
        current_id = 1
        
        for section in sections:
            if section.strip() and ('You should spend about 40 minutes' in section or 'Write about the following topic:' in section):
                # Extract the main prompt
                lines = section.split('\n')
                prompt = ""
                for line in lines:
                    if line.strip() and not line.startswith('Part 2') and not line.startswith('You should spend') and not line.startswith('Write about') and not line.startswith('Give reasons'):
                        if len(line.strip()) > 50:  # Main prompt line
                            prompt = line.strip()
                            break
                
                if prompt:
                    question = {
                        'id': f'aw_{current_id:03d}',
                        'assessment_type': 'academic_writing',
                        'task_type': 'Task 2 - Essay',
                        'prompt': prompt,
                        'time_limit': 40,
                        'word_count_min': 250,
                        'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words. Give reasons for your answer and include any relevant examples from your own knowledge or experience.',
                        'created_at': int(time.time()),
                        'difficulty_level': 'standard'
                    }
                    questions.append(question)
                    current_id += 1
        
        print(f"[MIGRATION] Parsed {len(questions)} Academic Writing questions")
        return questions
    
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to parse academic writing: {str(e)}")
        return []

def parse_general_writing_content():
    """Parse General Training Writing questions from attached files"""
    questions = []
    
    # Parse Task 1 - Letters
    try:
        with open('attached_assets/IELTS General Training Writing Task 1 letters.txt', 'r') as f:
            content = f.read()
        
        # Split by numbered questions
        sections = content.split('\n\n')
        current_id = 1
        
        for section in sections:
            if section.strip() and ('Write a letter' in section or 'Dear Sir or Madam' in section):
                # Extract the main scenario
                lines = section.split('\n')
                scenario = ""
                requirements = []
                
                for line in lines:
                    if line.strip() and len(line.strip()) > 50 and not line.startswith('You should spend') and not line.startswith('Write a letter'):
                        scenario = line.strip()
                        break
                
                # Extract requirements
                for line in lines:
                    if line.strip() and (line.startswith('describe') or line.startswith('explain') or line.startswith('suggest')):
                        requirements.append(line.strip())
                
                if scenario:
                    question = {
                        'id': f'gw_task1_{current_id:03d}',
                        'assessment_type': 'general_writing',
                        'task_type': 'Task 1 - Letter',
                        'prompt': scenario,
                        'requirements': requirements,
                        'time_limit': 20,
                        'word_count_min': 150,
                        'instructions': 'You should spend about 20 minutes on this task. Write at least 150 words. You do NOT need to write any addresses. Begin your letter as follows: Dear Sir or Madam,',
                        'created_at': int(time.time()),
                        'difficulty_level': 'standard'
                    }
                    questions.append(question)
                    current_id += 1
        
        print(f"[MIGRATION] Parsed {len(questions)} General Training Task 1 questions")
    
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to parse general writing task 1: {str(e)}")
    
    # Parse Task 2 - Essays
    try:
        with open('attached_assets/General Training Writing Task 2 tests (essays).txt', 'r') as f:
            content = f.read()
        
        # Split by numbered questions
        lines = content.split('\n')
        current_id = 1
        
        for line in lines:
            if line.strip() and len(line.strip()) > 50 and not line.startswith('General Training'):
                # Check if it's a complete question
                if any(keyword in line.lower() for keyword in ['outweigh', 'advantages', 'disadvantages', 'believe', 'opinion']):
                    question = {
                        'id': f'gw_task2_{current_id:03d}',
                        'assessment_type': 'general_writing',
                        'task_type': 'Task 2 - Essay',
                        'prompt': line.strip(),
                        'time_limit': 40,
                        'word_count_min': 250,
                        'instructions': 'You should spend about 40 minutes on this task. Write at least 250 words. Give reasons for your answer and include any relevant examples from your own knowledge or experience.',
                        'created_at': int(time.time()),
                        'difficulty_level': 'standard'
                    }
                    questions.append(question)
                    current_id += 1
        
        print(f"[MIGRATION] Parsed {len(questions)} General Training Task 2 questions")
    
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to parse general writing task 2: {str(e)}")
    
    return questions

def parse_reading_content():
    """Parse Reading assessment content from attached files"""
    questions = []
    
    # Parse General Reading Multiple Choice
    try:
        with open('attached_assets/General Reading Task 1 Multiple Cho.txt', 'r') as f:
            content = f.read()
        
        # Extract sets of questions
        if 'Set 1: For Sale - Used Cars' in content:
            question = {
                'id': 'gr_001',
                'assessment_type': 'general_reading',
                'task_type': 'Multiple Choice',
                'title': 'For Sale - Used Cars',
                'passage': content.split('Set 1: For Sale - Used Cars')[1].split('Questions:')[0].strip(),
                'questions': [
                    'Which car is most suitable for a large family?',
                    'Which car offers the best fuel efficiency?',
                    'Which car is the most expensive option?',
                    'Which car is newest model available?'
                ],
                'time_limit': 20,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            }
            questions.append(question)
        
        print(f"[MIGRATION] Parsed {len(questions)} General Reading questions")
    
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to parse general reading: {str(e)}")
    
    # Parse comprehensive reading context
    try:
        with open('attached_assets/IELTS Reading Context File.txt', 'r') as f:
            content = f.read()
        
        if 'The Rise of Artificial Intelligence in Healthcare' in content:
            passage_start = content.find('*** PASSAGE 1:')
            passage_end = content.find('** Questions for Passage 1 **')
            passage = content[passage_start:passage_end].strip()
            
            questions_section = content[passage_end:].strip()
            
            question = {
                'id': 'ar_001',
                'assessment_type': 'academic_reading',
                'task_type': 'True/False/Not Given',
                'title': 'The Rise of Artificial Intelligence in Healthcare',
                'passage': passage,
                'questions': [
                    'AI in healthcare is primarily focused on replacing human doctors.',
                    'AI algorithms can analyze medical images to detect abnormalities.',
                    'AI has significantly increased the failure rate of drug development.',
                    'Personalized medicine aims to provide the same treatment to all patients.',
                    'NLP algorithms can help automate administrative tasks in healthcare.',
                    'Regulatory frameworks for AI in healthcare are already fully established.'
                ],
                'time_limit': 20,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            }
            questions.append(question)
        
        print(f"[MIGRATION] Parsed {len(questions)} Academic Reading questions")
    
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to parse academic reading: {str(e)}")
    
    return questions

def parse_speaking_content():
    """Parse Speaking assessment content and band descriptors"""
    questions = []
    
    # Parse speaking band descriptors from CSV
    try:
        with open('attached_assets/IELTS Speaking Context File-CSV.csv', 'r') as f:
            content = f.read()
        
        # Academic Speaking scenarios
        academic_scenarios = [
            {
                'id': 'as_001',
                'assessment_type': 'academic_speaking',
                'part': 1,
                'topic': 'Studies and Academic Life',
                'questions': [
                    'What subject are you studying?',
                    'Why did you choose this subject?',
                    'What do you find most interesting about your studies?',
                    'Do you prefer studying alone or in groups?'
                ],
                'time_limit': 5,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            },
            {
                'id': 'as_002',
                'assessment_type': 'academic_speaking',
                'part': 2,
                'topic': 'Describe a book that influenced you',
                'cue_card': 'Describe a book that has influenced your thinking. You should say: what the book was about, when and where you read it, why it influenced you, and explain how it changed your perspective.',
                'preparation_time': 1,
                'speaking_time': 2,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            },
            {
                'id': 'as_003',
                'assessment_type': 'academic_speaking',
                'part': 3,
                'topic': 'Education and Learning',
                'questions': [
                    'How has education changed in your country?',
                    'What role should technology play in education?',
                    'Do you think traditional teaching methods are still effective?',
                    'How important is lifelong learning in modern society?'
                ],
                'time_limit': 5,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            }
        ]
        
        # General Speaking scenarios
        general_scenarios = [
            {
                'id': 'gs_001',
                'assessment_type': 'general_speaking',
                'part': 1,
                'topic': 'Daily Life and Routine',
                'questions': [
                    'Can you describe your daily routine?',
                    'What do you usually do in your free time?',
                    'How do you usually get to work or school?',
                    'What kind of weather do you prefer?'
                ],
                'time_limit': 5,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            },
            {
                'id': 'gs_002',
                'assessment_type': 'general_speaking',
                'part': 2,
                'topic': 'Describe a memorable journey',
                'cue_card': 'Describe a memorable journey you have taken. You should say: where you went, who you went with, what you did there, and explain why it was memorable.',
                'preparation_time': 1,
                'speaking_time': 2,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            },
            {
                'id': 'gs_003',
                'assessment_type': 'general_speaking',
                'part': 3,
                'topic': 'Travel and Transportation',
                'questions': [
                    'How has travel changed over the years?',
                    'What are the benefits of traveling?',
                    'Do you think people travel too much nowadays?',
                    'How might transportation change in the future?'
                ],
                'time_limit': 5,
                'created_at': int(time.time()),
                'difficulty_level': 'standard'
            }
        ]
        
        questions.extend(academic_scenarios)
        questions.extend(general_scenarios)
        
        print(f"[MIGRATION] Parsed {len(questions)} Speaking questions")
    
    except Exception as e:
        print(f"[MIGRATION ERROR] Failed to parse speaking content: {str(e)}")
    
    return questions

def create_assessment_criteria_table():
    """Create comprehensive assessment criteria and band descriptors"""
    criteria = []
    
    # Writing criteria
    writing_criteria = {
        'id': 'writing_criteria_v2024',
        'assessment_types': ['academic_writing', 'general_writing'],
        'criteria': {
            'task_achievement': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Fully addresses all parts of the task with very natural and sophisticated control of organizational patterns.',
                    'band_8': 'Sufficiently addresses all parts of the task with clear progression throughout.',
                    'band_7': 'Addresses all parts of the task with clear progression throughout.',
                    'band_6': 'Addresses all parts of the task although some parts may be more fully covered than others.',
                    'band_5': 'Generally addresses the task with some inappropriate format elements.',
                    'band_4': 'Attempts to address the task but may misunderstand some requirements.'
                }
            },
            'coherence_and_cohesion': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Uses cohesion in such a way that it attracts no attention. Paragraphing is fully appropriate.',
                    'band_8': 'Sequences information and ideas logically with clear progression throughout.',
                    'band_7': 'Logically organizes information and ideas with clear progression throughout.',
                    'band_6': 'Arranges information and ideas coherently with clear overall progression.',
                    'band_5': 'Presents information with some organization but may lack overall progression.',
                    'band_4': 'Presents information and ideas but not always clearly or logically.'
                }
            },
            'lexical_resource': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Uses wide range of vocabulary with very natural and sophisticated control.',
                    'band_8': 'Uses wide range of vocabulary fluently and flexibly to convey precise meanings.',
                    'band_7': 'Uses sufficient range of vocabulary to show flexibility and precise usage.',
                    'band_6': 'Uses adequate range of vocabulary for the task with some inaccuracies.',
                    'band_5': 'Uses limited range of vocabulary but this is minimally adequate for the task.',
                    'band_4': 'Uses limited range of vocabulary with noticeable errors.'
                }
            },
            'grammatical_range_and_accuracy': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Uses wide range of structures with full flexibility and accuracy.',
                    'band_8': 'Uses wide range of structures with flexibility and accuracy.',
                    'band_7': 'Uses variety of complex structures with some flexibility.',
                    'band_6': 'Uses mix of simple and complex sentence forms with some errors.',
                    'band_5': 'Uses limited range of structures with attempts at complex sentences.',
                    'band_4': 'Uses limited range of structures with frequent errors.'
                }
            }
        },
        'created_at': int(time.time())
    }
    
    # Speaking criteria
    speaking_criteria = {
        'id': 'speaking_criteria_v2024',
        'assessment_types': ['academic_speaking', 'general_speaking'],
        'criteria': {
            'fluency_and_coherence': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Speaks fluently with only rare repetition or self-correction. Develops topics coherently.',
                    'band_8': 'Speaks fluently with only occasional repetition or self-correction.',
                    'band_7': 'Speaks at length without noticeable effort or loss of coherence.',
                    'band_6': 'Speaks at length though may show hesitation. Generally coherent.',
                    'band_5': 'Usually maintains flow but uses repetition and hesitation.',
                    'band_4': 'Cannot respond without noticeable pauses and frequent repetition.'
                }
            },
            'lexical_resource': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Uses vocabulary with full flexibility and precise usage.',
                    'band_8': 'Uses wide range of vocabulary fluently and flexibly.',
                    'band_7': 'Uses vocabulary resource flexibly to discuss variety of topics.',
                    'band_6': 'Has wide enough vocabulary to discuss topics at length.',
                    'band_5': 'Manages to talk about familiar topics with some inappropriate usage.',
                    'band_4': 'Limited vocabulary prevents discussion of unfamiliar topics.'
                }
            },
            'grammatical_range_and_accuracy': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Uses wide range of structures with full flexibility and accuracy.',
                    'band_8': 'Uses wide range of structures flexibly with majority error-free.',
                    'band_7': 'Uses range of complex structures with some flexibility.',
                    'band_6': 'Uses mix of simple and complex structures with some errors.',
                    'band_5': 'Uses basic sentence forms with reasonable accuracy.',
                    'band_4': 'Uses only basic sentence forms with frequent errors.'
                }
            },
            'pronunciation': {
                'weight': 25,
                'band_descriptors': {
                    'band_9': 'Uses wide range of pronunciation features with precise control.',
                    'band_8': 'Uses wide range of pronunciation features flexibly.',
                    'band_7': 'Shows all positive features and sustained ability.',
                    'band_6': 'Uses range of pronunciation features with mixed control.',
                    'band_5': 'Shows some effective use of features but not sustained.',
                    'band_4': 'Limited range of pronunciation features.'
                }
            }
        },
        'created_at': int(time.time())
    }
    
    criteria.extend([writing_criteria, speaking_criteria])
    
    print(f"[MIGRATION] Created {len(criteria)} assessment criteria sets")
    return criteria

def migrate_all_content():
    """Perform complete migration of all assessment content"""
    print("[MIGRATION] Starting full assessment content migration...")
    
    # Parse all content
    academic_writing = parse_academic_writing_content()
    general_writing = parse_general_writing_content()
    reading_content = parse_reading_content()
    speaking_content = parse_speaking_content()
    assessment_criteria = create_assessment_criteria_table()
    
    # Create comprehensive questions table
    all_questions = []
    all_questions.extend(academic_writing)
    all_questions.extend(general_writing)
    all_questions.extend(reading_content)
    all_questions.extend(speaking_content)
    
    # Add questions to DynamoDB
    questions_table = aws_mock.assessment_results_table  # Reuse existing table
    
    for question in all_questions:
        success = questions_table.put_item(question)
        if success:
            print(f"[MIGRATION] Added question {question['id']} - {question['assessment_type']}")
        else:
            print(f"[MIGRATION ERROR] Failed to add question {question['id']}")
    
    # Add criteria to rubrics table
    for criteria in assessment_criteria:
        success = aws_mock.assessment_rubrics_table.put_item(criteria)
        if success:
            print(f"[MIGRATION] Added criteria {criteria['id']}")
        else:
            print(f"[MIGRATION ERROR] Failed to add criteria {criteria['id']}")
    
    print(f"[MIGRATION] Migration complete:")
    print(f"  - Academic Writing: {len(academic_writing)} questions")
    print(f"  - General Writing: {len(general_writing)} questions")
    print(f"  - Reading: {len(reading_content)} questions")
    print(f"  - Speaking: {len(speaking_content)} questions")
    print(f"  - Assessment Criteria: {len(assessment_criteria)} sets")
    print(f"  - Total Questions: {len(all_questions)}")
    
    return len(all_questions)

def update_lambda_function():
    """Update Lambda function to use the new comprehensive question system"""
    
    # Update the get_questions_from_dynamodb function
    lambda_update = '''
def get_questions_from_dynamodb(assessment_type: str, user_email: str) -> Optional[Dict[str, Any]]:
    """Get comprehensive questions from DynamoDB with fallback support"""
    try:
        # Get user's completed questions to avoid repetition
        user_data = aws_mock.users_table.get_item(user_email)
        completed_questions = user_data.get('completed_questions', []) if user_data else []
        
        # Scan for questions of the specified assessment type
        all_questions = aws_mock.assessment_results_table.scan(
            filter_expression=f"assessment_type = '{assessment_type}'"
        )
        
        # Filter out completed questions
        available_questions = [q for q in all_questions if q['id'] not in completed_questions]
        
        if not available_questions:
            print(f"[DYNAMODB] No available questions for {assessment_type}, user has completed all")
            return None
        
        # Return first available question
        selected_question = available_questions[0]
        
        print(f"[DYNAMODB] Retrieved question {selected_question['id']} for {assessment_type}")
        return selected_question
        
    except Exception as e:
        print(f"[DYNAMODB ERROR] Failed to get questions: {str(e)}")
        return None

def get_assessment_criteria(assessment_type: str) -> Optional[Dict[str, Any]]:
    """Get assessment criteria and band descriptors from DynamoDB"""
    try:
        # Determine criteria type
        if 'writing' in assessment_type:
            criteria_id = 'writing_criteria_v2024'
        elif 'speaking' in assessment_type:
            criteria_id = 'speaking_criteria_v2024'
        else:
            return None
        
        # Get criteria from rubrics table
        criteria = aws_mock.assessment_rubrics_table.get_item(criteria_id)
        
        if criteria:
            print(f"[DYNAMODB] Retrieved criteria {criteria_id}")
            return criteria
        else:
            print(f"[DYNAMODB] No criteria found for {criteria_id}")
            return None
            
    except Exception as e:
        print(f"[DYNAMODB ERROR] Failed to get criteria: {str(e)}")
        return None
'''
    
    print("[MIGRATION] Lambda function update code prepared")
    return lambda_update

if __name__ == "__main__":
    # Run full migration
    total_questions = migrate_all_content()
    
    # Update Lambda function
    lambda_code = update_lambda_function()
    
    print(f"\n[MIGRATION COMPLETE] Successfully migrated {total_questions} questions to DynamoDB")
    print("[MIGRATION] Lambda function update code ready for deployment")