"""
Question Bank Administration Tools
Tools for managing question banks, adding questions, and monitoring usage
"""

import json
import logging
import random
from datetime import datetime
from typing import Dict, Any, List

from question_bank_dal import QuestionCategory, RepeatPolicy, get_question_bank_dal

logger = logging.getLogger(__name__)

class QuestionBankAdmin:
    """Administrative tools for question bank management"""
    
    def __init__(self):
        self.question_dal = get_question_bank_dal()
        self.shard_count = 128
    
    def add_question(self, assessment_type: str, category: str, content: Dict[str, Any],
                    difficulty: str = 'medium', tags: List[str] = None,
                    repeat_policy: str = 'unique') -> Dict[str, Any]:
        """
        Add new question to question bank
        
        Args:
            assessment_type: Type of assessment (academic_speaking, etc.)
            category: Question category (speaking_part1, etc.)
            content: Question content (text, audio, images, etc.)
            difficulty: Question difficulty (easy, medium, hard)
            tags: Optional tags for categorization
            repeat_policy: 'intro' for repeatable, 'unique' for one-time use
            
        Returns:
            Dict with success status and question details
        """
        try:
            # Generate question ID
            question_id = self._generate_question_id(assessment_type, category)
            
            # Assign to random shard for even distribution
            shard = random.randint(0, self.shard_count - 1)
            pool_id = f"{assessment_type}#{category}#{shard}"
            
            # Create question record
            question_data = {
                'pool_id': pool_id,
                'question_id': question_id,
                'assessment_type': assessment_type,
                'category': category,
                'shard': shard,
                'content': content,
                'difficulty': difficulty,
                'tags': tags or [],
                'repeat_policy': repeat_policy,
                'active': True,
                'created_at': datetime.utcnow().isoformat(),
                'version': 1
            }
            
            # Add to DynamoDB
            self.question_dal.questions_table.put_item(Item=question_data)
            
            logger.info(f"Question added: {question_id} to {pool_id}")
            
            return {
                'success': True,
                'question_id': question_id,
                'pool_id': pool_id,
                'shard': shard
            }
            
        except Exception as e:
            logger.error(f"Failed to add question: {e}")
            return {
                'success': False,
                'error': 'Failed to add question'
            }
    
    def batch_add_questions(self, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add multiple questions in batch"""
        try:
            results = []
            failed_count = 0
            
            for question_spec in questions:
                result = self.add_question(**question_spec)
                results.append(result)
                
                if not result['success']:
                    failed_count += 1
            
            return {
                'success': True,
                'total_questions': len(questions),
                'successful': len(questions) - failed_count,
                'failed': failed_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed to batch add questions: {e}")
            return {
                'success': False,
                'error': 'Failed to batch add questions'
            }
    
    def get_question_pool_stats(self, assessment_type: str = None) -> Dict[str, Any]:
        """Get statistics about question pools"""
        try:
            # This would require scanning - in production, consider maintaining counters
            # For now, return basic structure
            
            stats = {
                'success': True,
                'assessment_types': {
                    'academic_speaking': self._get_assessment_stats('academic_speaking'),
                    'general_speaking': self._get_assessment_stats('general_speaking'),
                    'academic_writing': self._get_assessment_stats('academic_writing'),
                    'general_writing': self._get_assessment_stats('general_writing')
                }
            }
            
            if assessment_type:
                stats = {
                    'success': True,
                    'assessment_type': assessment_type,
                    'stats': stats['assessment_types'].get(assessment_type, {})
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get question pool stats: {e}")
            return {
                'success': False,
                'error': 'Failed to get statistics'
            }
    
    def _get_assessment_stats(self, assessment_type: str) -> Dict[str, Any]:
        """Get stats for specific assessment type"""
        try:
            # Sample a few shards to estimate totals (production implementation)
            sample_shards = [0, 1, 2, 3, 4]  # Sample first 5 shards
            category_stats = {}
            
            for category in QuestionCategory:
                if not self._category_applies_to_assessment(category, assessment_type):
                    continue
                    
                total_estimate = 0
                active_estimate = 0
                
                for shard in sample_shards:
                    pool_id = f"{assessment_type}#{category.value}#{shard}"
                    
                    try:
                        response = self.question_dal.questions_table.query(
                            KeyConditionExpression='pool_id = :pool_id',
                            ExpressionAttributeValues={':pool_id': pool_id}
                        )
                        
                        items = response.get('Items', [])
                        shard_total = len(items)
                        shard_active = sum(1 for item in items if item.get('active', True))
                        
                        total_estimate += shard_total
                        active_estimate += shard_active
                        
                    except Exception:
                        continue
                
                # Extrapolate to all shards
                multiplier = self.shard_count / len(sample_shards)
                category_stats[category.value] = {
                    'estimated_total': int(total_estimate * multiplier),
                    'estimated_active': int(active_estimate * multiplier)
                }
            
            return category_stats
            
        except Exception as e:
            logger.warning(f"Failed to get stats for {assessment_type}: {e}")
            return {}
    
    def _category_applies_to_assessment(self, category: QuestionCategory, assessment_type: str) -> bool:
        """Check if category applies to assessment type"""
        if 'speaking' in assessment_type:
            return category.value.startswith('speaking_')
        elif 'writing' in assessment_type:
            return category.value.startswith('writing_')
        return False
    
    def _generate_question_id(self, assessment_type: str, category: str) -> str:
        """Generate unique question ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000000)
        prefix = f"{assessment_type}_{category}".replace('_', '')[:20]
        return f"{prefix}_{timestamp}"
    
    def initialize_sample_questions(self) -> Dict[str, Any]:
        """Initialize question bank with sample questions for testing"""
        try:
            sample_questions = []
            
            # Maya's introduction questions (can repeat)
            intro_questions = [
                {
                    'assessment_type': 'academic_speaking',
                    'category': 'speaking_intro',
                    'content': {
                        'type': 'intro',
                        'text': "Hello, I'm Maya, your IELTS examiner. Could you please tell me your full name?",
                        'follow_up': "Thank you. Now, could you tell me a little bit about yourself and where you're from?"
                    },
                    'repeat_policy': 'intro'
                },
                {
                    'assessment_type': 'general_speaking',
                    'category': 'speaking_intro', 
                    'content': {
                        'type': 'intro',
                        'text': "Good day, I'm Maya, your IELTS speaking examiner. May I have your name please?",
                        'follow_up': "Nice to meet you. Can you tell me about your hometown and what you like about it?"
                    },
                    'repeat_policy': 'intro'
                }
            ]
            
            # Academic Speaking Part 1 questions (unique)
            part1_academic = [
                {
                    'assessment_type': 'academic_speaking',
                    'category': 'speaking_part1',
                    'content': {
                        'type': 'personal',
                        'text': "Do you work or are you a student?",
                        'follow_up': "What do you enjoy most about your studies/work?"
                    }
                },
                {
                    'assessment_type': 'academic_speaking',
                    'category': 'speaking_part1',
                    'content': {
                        'type': 'personal',
                        'text': "What kind of music do you like?",
                        'follow_up': "Has your taste in music changed since you were young?"
                    }
                }
            ]
            
            # Academic Writing Task 1 questions
            writing_task1_academic = [
                {
                    'assessment_type': 'academic_writing',
                    'category': 'writing_task1',
                    'content': {
                        'type': 'chart_description',
                        'text': "The chart below shows the percentage of households in different income brackets in three countries in 2020.",
                        'chart_type': 'bar_chart',
                        'time_limit': 20
                    }
                }
            ]
            
            # Combine all samples
            all_samples = intro_questions + part1_academic + writing_task1_academic
            
            # Add them to database
            result = self.batch_add_questions(all_samples)
            
            logger.info(f"Initialized {len(all_samples)} sample questions")
            return result
            
        except Exception as e:
            logger.error(f"Failed to initialize sample questions: {e}")
            return {
                'success': False,
                'error': 'Failed to initialize sample questions'
            }

# Global instance
_admin = None

def get_question_bank_admin() -> QuestionBankAdmin:
    """Get global question bank admin instance"""
    global _admin
    if _admin is None:
        _admin = QuestionBankAdmin()
    return _admin

# Export
__all__ = ['QuestionBankAdmin', 'get_question_bank_admin']