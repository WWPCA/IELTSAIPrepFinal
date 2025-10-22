"""
Question Bank Data Access Layer for IELTS Assessments
Handles question storage, selection, and usage tracking to prevent repeats
"""

import json
import logging
import random
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from dynamodb_dal import get_dal

logger = logging.getLogger(__name__)

class QuestionCategory(Enum):
    """Question categories for different assessment parts"""
    # Speaking categories
    SPEAKING_INTRO = "speaking_intro"
    SPEAKING_PART1 = "speaking_part1"
    SPEAKING_PART2 = "speaking_part2"
    SPEAKING_PART3 = "speaking_part3"
    
    # Writing categories
    WRITING_TASK1 = "writing_task1"
    WRITING_TASK2 = "writing_task2"

class RepeatPolicy(Enum):
    """Question repeat policies"""
    INTRO = "intro"  # Can repeat (Maya's introduction)
    UNIQUE = "unique"  # Must be unique per user per assessment type

class QuestionBankDAL:
    """Data Access Layer for Question Bank Management"""
    
    def __init__(self):
        import os
        self.dynamodb = get_dal().dynamodb  # Use existing DynamoDB resource
        stage = os.environ.get('STAGE', 'prod')
        
        # Table names
        self.questions_table_name = f'ielts-questions-{stage}'
        self.sessions_table_name = f'ielts-assessment-sessions-{stage}'
        self.usage_table_name = f'ielts-user-question-usage-{stage}'
        self.profiles_table_name = f'ielts-user-profiles-{stage}'
        
        # Get tables
        self.questions_table = self.dynamodb.Table(self.questions_table_name)
        self.sessions_table = self.dynamodb.Table(self.sessions_table_name)
        self.usage_table = self.dynamodb.Table(self.usage_table_name)
        self.profiles_table = self.dynamodb.Table(self.profiles_table_name)
        
        # Question requirements per assessment type
        self.question_requirements = {
            'academic_speaking': {
                QuestionCategory.SPEAKING_INTRO: 3,  # Maya's introduction variety
                QuestionCategory.SPEAKING_PART1: 10,  # Personal questions
                QuestionCategory.SPEAKING_PART2: 1,   # Cue card + follow-ups
                QuestionCategory.SPEAKING_PART3: 4    # Abstract discussion
            },
            'general_speaking': {
                QuestionCategory.SPEAKING_INTRO: 3,
                QuestionCategory.SPEAKING_PART1: 10,
                QuestionCategory.SPEAKING_PART2: 1,
                QuestionCategory.SPEAKING_PART3: 4
            },
            'academic_writing': {
                QuestionCategory.WRITING_TASK1: 1,    # Describe graph/chart
                QuestionCategory.WRITING_TASK2: 1     # Essay question
            },
            'general_writing': {
                QuestionCategory.WRITING_TASK1: 1,    # Letter writing
                QuestionCategory.WRITING_TASK2: 1     # Essay question
            }
        }
        
        # Sharding configuration (0-127 for even distribution)
        self.shard_count = 128
    
    def start_assessment_session(self, user_email: str, assessment_type: str, 
                                purchase_id: str) -> Dict[str, Any]:
        """
        Start new assessment session with question selection
        
        Args:
            user_email: User's email address
            assessment_type: Type of assessment (academic_speaking, etc.)
            purchase_id: Purchase/attempt identifier
            
        Returns:
            Dict with session details and selected questions
        """
        try:
            logger.info(f"Starting assessment session for {user_email} - {assessment_type}")
            
            # Validate assessment type
            if assessment_type not in self.question_requirements:
                return {
                    'success': False,
                    'error': f'Invalid assessment type: {assessment_type}'
                }
            
            # Generate session ID
            session_id = self._generate_session_id()
            
            # Select questions for each category
            selected_questions = {}
            question_ids_by_category = {}
            
            requirements = self.question_requirements[assessment_type]
            
            for category, count in requirements.items():
                questions = self._select_questions_for_category(
                    user_email, assessment_type, category, count
                )
                
                if not questions:
                    return {
                        'success': False,
                        'error': f'Insufficient questions available for {category.value}',
                        'category': category.value
                    }
                
                selected_questions[category.value] = questions
                question_ids_by_category[category.value] = [q['question_id'] for q in questions]
            
            # Create session record
            session_data = {
                'session_id': session_id,
                'user_email': user_email,
                'assessment_type': assessment_type,
                'purchase_id': purchase_id,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'question_ids_by_category': question_ids_by_category,
                'version': 1
            }
            
            # Reserve questions transactionally
            reservation_success = self._reserve_questions_transactionally(
                session_data, selected_questions, user_email, assessment_type
            )
            
            if not reservation_success:
                return {
                    'success': False,
                    'error': 'Failed to reserve questions - possible race condition'
                }
            
            logger.info(f"Assessment session started: {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'assessment_type': assessment_type,
                'questions': selected_questions,
                'total_questions': sum(len(qs) for qs in selected_questions.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to start assessment session for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to start assessment session'
            }
    
    def complete_assessment_session(self, session_id: str, user_email: str) -> Dict[str, Any]:
        """Mark assessment session as completed"""
        try:
            # Update session status
            self.sessions_table.update_item(
                Key={'session_id': session_id},
                UpdateExpression='SET #status = :status, completed_at = :completed_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'completed',
                    ':completed_at': datetime.utcnow().isoformat(),
                    ':user_email': user_email,
                    ':active_status': 'active'
                },
                ConditionExpression='user_email = :user_email AND #status = :active_status'
            )
            
            logger.info(f"Assessment session completed: {session_id}")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to complete assessment session {session_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to complete session'
            }
    
    def get_assessment_session(self, session_id: str) -> Dict[str, Any]:
        """Get assessment session details"""
        try:
            response = self.sessions_table.get_item(Key={'session_id': session_id})
            
            if 'Item' not in response:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
            
            return {
                'success': True,
                'session': response['Item']
            }
            
        except Exception as e:
            logger.error(f"Failed to get assessment session {session_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to get session'
            }
    
    def _select_questions_for_category(self, user_email: str, assessment_type: str, 
                                     category: QuestionCategory, count: int) -> List[Dict[str, Any]]:
        """Select questions for specific category avoiding user's previous questions"""
        try:
            # Get user's previously used questions for this assessment type
            used_question_ids = self._get_user_used_questions(user_email, assessment_type, category)
            
            # Try multiple random shards to find enough questions
            selected_questions = []
            attempted_shards = set()
            max_attempts = min(20, self.shard_count)  # Don't try all shards
            
            while len(selected_questions) < count and len(attempted_shards) < max_attempts:
                shard = random.randint(0, self.shard_count - 1)
                
                if shard in attempted_shards:
                    continue
                    
                attempted_shards.add(shard)
                
                # Query questions from this shard
                pool_id = f"{assessment_type}#{category.value}#{shard}"
                
                try:
                    response = self.questions_table.query(
                        KeyConditionExpression='pool_id = :pool_id',
                        FilterExpression='active = :active',
                        ExpressionAttributeValues={
                            ':pool_id': pool_id,
                            ':active': True
                        },
                        Limit=count * 3  # Get more than needed for filtering
                    )
                    
                    candidate_questions = response.get('Items', [])
                    
                    # Filter out previously used questions (unless intro policy)
                    for question in candidate_questions:
                        if len(selected_questions) >= count:
                            break
                            
                        question_id = question['question_id']
                        repeat_policy = question.get('repeat_policy', RepeatPolicy.UNIQUE.value)
                        
                        # Allow intro questions to repeat, filter others
                        if repeat_policy == RepeatPolicy.INTRO.value or question_id not in used_question_ids:
                            selected_questions.append(question)
                    
                except Exception as e:
                    logger.warning(f"Failed to query shard {shard} for {pool_id}: {e}")
                    continue
            
            if len(selected_questions) < count:
                logger.warning(f"Only found {len(selected_questions)}/{count} questions for {category.value}")
            
            return selected_questions[:count]
            
        except Exception as e:
            logger.error(f"Failed to select questions for {category.value}: {e}")
            return []
    
    def _get_user_used_questions(self, user_email: str, assessment_type: str, 
                               category: QuestionCategory) -> set:
        """Get set of question IDs user has previously used for this assessment type"""
        try:
            # Query user's question usage
            pk = f"{user_email}#{assessment_type}"
            
            response = self.usage_table.query(
                KeyConditionExpression='user_assessment_key = :pk',
                ExpressionAttributeValues={':pk': pk}
            )
            
            used_ids = set()
            for item in response.get('Items', []):
                # Filter by category if question has category info
                question_category = item.get('category')
                if not question_category or question_category == category.value:
                    used_ids.add(item['question_id'])
            
            return used_ids
            
        except Exception as e:
            logger.error(f"Failed to get user used questions: {e}")
            return set()
    
    def _reserve_questions_transactionally(self, session_data: Dict[str, Any], 
                                         selected_questions: Dict[str, List[Dict[str, Any]]],
                                         user_email: str, assessment_type: str) -> bool:
        """Reserve questions using DynamoDB transactions to prevent race conditions"""
        try:
            from boto3.dynamodb.conditions import Attr
            
            transaction_items = []
            
            # 1. Put session record
            transaction_items.append({
                'Put': {
                    'TableName': self.sessions_table_name,
                    'Item': session_data,
                    'ConditionExpression': 'attribute_not_exists(session_id)'
                }
            })
            
            # 2. Put user question usage records (except intro questions)
            user_assessment_key = f"{user_email}#{assessment_type}"
            current_time = datetime.utcnow().isoformat()
            
            for category, questions in selected_questions.items():
                for question in questions:
                    question_id = question['question_id']
                    repeat_policy = question.get('repeat_policy', RepeatPolicy.UNIQUE.value)
                    
                    # Only track non-intro questions
                    if repeat_policy != RepeatPolicy.INTRO.value:
                        usage_item = {
                            'user_assessment_key': user_assessment_key,
                            'question_id': question_id,
                            'category': category,
                            'first_used_at': current_time,
                            'last_used_at': current_time,
                            'session_id': session_data['session_id']
                        }
                        
                        transaction_items.append({
                            'Put': {
                                'TableName': self.usage_table_name,
                                'Item': usage_item,
                                'ConditionExpression': 'attribute_not_exists(user_assessment_key) AND attribute_not_exists(question_id)'
                            }
                        })
            
            # Execute transaction
            self.dynamodb.meta.client.transact_write_items(
                TransactItems=transaction_items
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to reserve questions transactionally: {e}")
            return False
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000000)
        random_part = secrets.token_hex(8)
        return f"session_{timestamp}_{random_part}"
    
    def get_user_question_stats(self, user_email: str, assessment_type: str) -> Dict[str, Any]:
        """Get user's question usage statistics"""
        try:
            pk = f"{user_email}#{assessment_type}"
            
            response = self.usage_table.query(
                KeyConditionExpression='user_assessment_key = :pk',
                ExpressionAttributeValues={':pk': pk}
            )
            
            items = response.get('Items', [])
            
            # Group by category
            stats_by_category = {}
            for item in items:
                category = item.get('category', 'unknown')
                if category not in stats_by_category:
                    stats_by_category[category] = []
                stats_by_category[category].append(item)
            
            return {
                'success': True,
                'user_email': user_email,
                'assessment_type': assessment_type,
                'total_questions_used': len(items),
                'questions_by_category': stats_by_category,
                'unique_sessions': len(set(item.get('session_id') for item in items if item.get('session_id')))
            }
            
        except Exception as e:
            logger.error(f"Failed to get user question stats: {e}")
            return {
                'success': False,
                'error': 'Failed to get question statistics'
            }
    
    def get_user_profile(self, user_email: str) -> Dict[str, Any]:
        """Get user profile data including assessment history"""
        try:
            response = self.profiles_table.get_item(
                Key={'user_email': user_email}
            )
            
            if 'Item' in response:
                return {
                    'success': True,
                    'profile': response['Item']
                }
            else:
                return {
                    'success': False,
                    'error': 'Profile not found'
                }
        except Exception as e:
            logger.error(f"Error getting user profile for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to get user profile'
            }
    
    def store_user_profile(self, user_email: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store or update user profile data"""
        try:
            # Add metadata
            profile_data['user_email'] = user_email
            profile_data['last_updated'] = datetime.utcnow().isoformat()
            
            # Store in DynamoDB
            self.profiles_table.put_item(Item=profile_data)
            
            logger.info(f"User profile stored for {user_email}")
            return {
                'success': True,
                'message': 'Profile stored successfully'
            }
            
        except Exception as e:
            logger.error(f"Error storing user profile for {user_email}: {e}")
            return {
                'success': False,
                'error': 'Failed to store user profile'
            }
    
    def update_assessment_session(self, session_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update assessment session data"""
        try:
            # Add update timestamp
            session_data['last_updated'] = datetime.utcnow().isoformat()
            
            # Update in DynamoDB
            self.sessions_table.put_item(Item=session_data)
            
            logger.info(f"Assessment session updated: {session_id}")
            return {
                'success': True,
                'message': 'Session updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating assessment session {session_id}: {e}")
            return {
                'success': False,
                'error': 'Failed to update assessment session'
            }

# Global instance
_question_bank_dal = None

def get_question_bank_dal() -> QuestionBankDAL:
    """Get global question bank DAL instance"""
    global _question_bank_dal
    if _question_bank_dal is None:
        _question_bank_dal = QuestionBankDAL()
    return _question_bank_dal

# Export
__all__ = [
    'QuestionBankDAL',
    'QuestionCategory', 
    'RepeatPolicy',
    'get_question_bank_dal'
]