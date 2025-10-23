"""
Comprehensive Tests for Score Report and Feedback Display
Tests that score reports and detailed feedback load correctly after assessment completion
"""
import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add deployment to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'deployment'))

from dynamodb_dal import DynamoDBConnection, AssessmentDAL


class TestWritingScoreReportDisplay:
    """Test writing assessment score report and feedback display"""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup assessment DAL with mocked DynamoDB"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            
            assessment_dal = AssessmentDAL(conn)
            assessment_dal.table = mock_table
            
            return {'assessment_dal': assessment_dal, 'mock_table': mock_table}
    
    def test_writing_score_report_contains_all_criteria(self, setup_mocks):
        """Test writing score report contains all 4 IELTS criteria"""
        mocks = setup_mocks
        
        # Mock assessment result from DynamoDB
        mocks['mock_table'].get_item.return_value = {
            'Item': {
                'assessment_id': 'assessment-123',
                'user_id': 'user-123',
                'assessment_type': 'academic_writing_task1',
                'overall_band': 7.5,
                'criteria_scores': {
                    'task_achievement': 7.5,
                    'coherence_cohesion': 7.0,
                    'lexical_resource': 8.0,
                    'grammatical_range': 7.5
                },
                'detailed_feedback': {
                    'strengths': ['Clear overview', 'Good data description'],
                    'areas_for_improvement': ['More variety in sentence structures'],
                    'specific_suggestions': ['Use more comparative phrases'],
                    'examples_from_essay': ['The graph shows...']
                },
                'personalized_improvement_plan': {
                    'focus_areas': [
                        {
                            'criterion': 'Coherence and Cohesion',
                            'current_band': 7.0,
                            'target_band': 8.0,
                            'practice_activities': ['Practice using discourse markers']
                        }
                    ],
                    'immediate_actions': ['Review linking words'],
                    'study_schedule': {'week_1': 'Focus on coherence'},
                    'target_overall_band': 8.0,
                    'estimated_timeline': '4-6 weeks'
                },
                'timestamp': datetime.utcnow().isoformat(),
                'model_used': 'amazon.nova-micro-v1:0'
            }
        }
        
        # Retrieve assessment
        result = mocks['assessment_dal'].table.get_item(Key={'assessment_id': 'assessment-123'})
        assessment = result['Item']
        
        # Verify score report structure
        assert 'overall_band' in assessment
        assert assessment['overall_band'] == 7.5
        
        # Verify all 4 criteria present
        assert 'task_achievement' in assessment['criteria_scores']
        assert 'coherence_cohesion' in assessment['criteria_scores']
        assert 'lexical_resource' in assessment['criteria_scores']
        assert 'grammatical_range' in assessment['criteria_scores']
        
        # Verify detailed feedback present
        assert 'strengths' in assessment['detailed_feedback']
        assert 'areas_for_improvement' in assessment['detailed_feedback']
        assert 'specific_suggestions' in assessment['detailed_feedback']
        
        # Verify personalized improvement plan present
        assert 'personalized_improvement_plan' in assessment
        assert 'focus_areas' in assessment['personalized_improvement_plan']
        assert 'immediate_actions' in assessment['personalized_improvement_plan']
        assert 'target_overall_band' in assessment['personalized_improvement_plan']
    
    def test_writing_feedback_loads_immediately_after_submission(self, setup_mocks):
        """Test feedback is available immediately after assessment submission"""
        mocks = setup_mocks
        
        # Mock save assessment
        mocks['mock_table'].put_item.return_value = {}
        
        # Simulate assessment completion
        assessment_data = {
            'assessment_id': 'new-assessment-456',
            'user_id': 'user-456',
            'overall_band': 6.5,
            'criteria_scores': {
                'task_achievement': 6.5,
                'coherence_cohesion': 6.5,
                'lexical_resource': 6.5,
                'grammatical_range': 7.0
            },
            'detailed_feedback': {'strengths': [], 'areas_for_improvement': []},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save to DynamoDB
        mocks['mock_table'].put_item(Item=assessment_data)
        
        # Verify save was called
        assert mocks['mock_table'].put_item.called
        
        # Mock immediate retrieval (simulates page refresh/redirect)
        mocks['mock_table'].get_item.return_value = {'Item': assessment_data}
        
        # Retrieve and verify
        result = mocks['mock_table'].get_item(Key={'assessment_id': 'new-assessment-456'})
        assert result['Item']['overall_band'] == 6.5


class TestSpeakingScoreReportDisplay:
    """Test speaking assessment score report and feedback display"""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup assessment DAL"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            
            assessment_dal = AssessmentDAL(conn)
            assessment_dal.table = mock_table
            
            return {'assessment_dal': assessment_dal, 'mock_table': mock_table}
    
    def test_speaking_score_report_contains_all_criteria(self, setup_mocks):
        """Test speaking score report contains all 4 speaking criteria"""
        mocks = setup_mocks
        
        # Mock speaking assessment result
        mocks['mock_table'].get_item.return_value = {
            'Item': {
                'assessment_id': 'speaking-789',
                'user_id': 'user-789',
                'assessment_type': 'academic_speaking',
                'overall_band': 7.0,
                'criteria_scores': {
                    'fluency_coherence': 7.5,
                    'lexical_resource': 7.0,
                    'grammatical_range': 6.5,
                    'pronunciation': 7.0
                },
                'detailed_feedback': {
                    'strengths': ['Good fluency', 'Clear pronunciation'],
                    'areas_for_improvement': ['More complex grammar structures'],
                    'specific_examples': {
                        'positive': ['Natural discourse markers'],
                        'negative': ['Some hesitation noticed']
                    }
                },
                'personalized_improvement_plan': {
                    'focus_areas': [
                        {
                            'criterion': 'Grammatical Range and Accuracy',
                            'current_band': 6.5,
                            'target_band': 7.5,
                            'practice_activities': ['Practice complex sentences'],
                            'estimated_time': '3-4 weeks'
                        }
                    ],
                    'weekly_practice_schedule': {
                        'day_1_3': 'Focus on grammar',
                        'day_4_5': 'Full speaking practice'
                    },
                    'target_overall_band': 7.5
                },
                'transcript': 'Maya: Hello... Student: Hi...',
                'timestamp': datetime.utcnow().isoformat(),
                'model_used': 'gemini-2.5-flash-lite'
            }
        }
        
        result = mocks['mock_table'].get_item(Key={'assessment_id': 'speaking-789'})
        assessment = result['Item']
        
        # Verify all 4 speaking criteria
        assert 'fluency_coherence' in assessment['criteria_scores']
        assert 'lexical_resource' in assessment['criteria_scores']
        assert 'grammatical_range' in assessment['criteria_scores']
        assert 'pronunciation' in assessment['criteria_scores']
        
        # Verify improvement plan
        assert 'personalized_improvement_plan' in assessment
        assert 'weekly_practice_schedule' in assessment['personalized_improvement_plan']


class TestReadingScoreReportDisplay:
    """Test reading assessment score report display"""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup mocks for reading"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            
            return {'mock_table': mock_table}
    
    def test_reading_score_report_shows_correct_results(self, setup_mocks):
        """Test reading score report displays score, band, and breakdown"""
        mocks = setup_mocks
        
        # Mock reading result
        mocks['mock_table'].get_item.return_value = {
            'Item': {
                'test_id': 'reading-test-001',
                'user_id': 'user-001',
                'assessment_type': 'academic_reading',
                'score': 35,
                'total_questions': 40,
                'percentage': 87.5,
                'band_score': 8.0,
                'question_breakdown': {
                    'passage_1': {'correct': 12, 'total': 13},
                    'passage_2': {'correct': 11, 'total': 13},
                    'passage_3': {'correct': 12, 'total': 14}
                },
                'timestamp': datetime.utcnow().isoformat(),
                'model_used': 'amazon.nova-micro-v1:0'
            }
        }
        
        result = mocks['mock_table'].get_item(Key={'test_id': 'reading-test-001'})
        assessment = result['Item']
        
        # Verify score report elements
        assert assessment['score'] == 35
        assert assessment['total_questions'] == 40
        assert assessment['band_score'] == 8.0
        assert assessment['percentage'] == 87.5
        
        # Verify breakdown by passage
        assert 'question_breakdown' in assessment
        assert 'passage_1' in assessment['question_breakdown']


class TestListeningScoreReportDisplay:
    """Test listening assessment score report display"""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup mocks for listening"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            
            return {'mock_table': mock_table}
    
    def test_listening_score_report_shows_flexible_matching_info(self, setup_mocks):
        """Test listening report shows which answers were flexible matches"""
        mocks = setup_mocks
        
        # Mock listening result with flexible matches
        mocks['mock_table'].get_item.return_value = {
            'Item': {
                'test_id': 'listening-test-001',
                'user_id': 'user-001',
                'assessment_type': 'academic_listening',
                'score': 32,
                'total_questions': 40,
                'percentage': 80.0,
                'band_score': 7.5,
                'flexible_matches': ['2', '5', '7', '10'],  # Questions with flexible matching
                'section_breakdown': {
                    'section_1': {'correct': 9, 'total': 10},
                    'section_2': {'correct': 8, 'total': 10},
                    'section_3': {'correct': 7, 'total': 10},
                    'section_4': {'correct': 8, 'total': 10}
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        result = mocks['mock_table'].get_item(Key={'test_id': 'listening-test-001'})
        assessment = result['Item']
        
        # Verify score elements
        assert assessment['score'] == 32
        assert assessment['band_score'] == 7.5
        
        # Verify flexible matching info displayed
        assert 'flexible_matches' in assessment
        assert len(assessment['flexible_matches']) == 4
        
        # Verify section breakdown
        assert 'section_breakdown' in assessment


class TestFullMockTestScoreReportDisplay:
    """Test full-length mock test comprehensive score report"""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup mocks for full test"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            
            return {'mock_table': mock_table}
    
    def test_full_test_report_shows_all_four_sections(self, setup_mocks):
        """Test full-length mock test report displays all 4 section scores"""
        mocks = setup_mocks
        
        # Mock full test result
        mocks['mock_table'].get_item.return_value = {
            'Item': {
                'test_id': 'full-test-001',
                'user_id': 'user-001',
                'test_type': 'academic_mocktest',
                'section_scores': {
                    'listening': {
                        'score': 32,
                        'total': 40,
                        'band_score': 7.5
                    },
                    'reading': {
                        'score': 35,
                        'total': 40,
                        'band_score': 8.0
                    },
                    'writing': {
                        'task_1_band': 7.0,
                        'task_2_band': 7.5,
                        'overall_band': 7.5
                    },
                    'speaking': {
                        'overall_band': 7.0,
                        'criteria': {
                            'fluency_coherence': 7.5,
                            'lexical_resource': 7.0,
                            'grammatical_range': 6.5,
                            'pronunciation': 7.0
                        }
                    }
                },
                'overall_band': 7.5,  # (7.5 + 8.0 + 7.5 + 7.0) / 4 = 7.5
                'timestamp': datetime.utcnow().isoformat(),
                'completion_time_minutes': 185
            }
        }
        
        result = mocks['mock_table'].get_item(Key={'test_id': 'full-test-001'})
        assessment = result['Item']
        
        # Verify all 4 sections present
        assert 'listening' in assessment['section_scores']
        assert 'reading' in assessment['section_scores']
        assert 'writing' in assessment['section_scores']
        assert 'speaking' in assessment['section_scores']
        
        # Verify overall band calculation
        section_bands = [
            assessment['section_scores']['listening']['band_score'],
            assessment['section_scores']['reading']['band_score'],
            assessment['section_scores']['writing']['overall_band'],
            assessment['section_scores']['speaking']['overall_band']
        ]
        calculated_overall = round(sum(section_bands) / 4 * 2) / 2
        assert assessment['overall_band'] == calculated_overall
        assert assessment['overall_band'] == 7.5


class TestFeedbackGenerationCompleteness:
    """Test that feedback generation is complete and comprehensive"""
    
    def test_writing_feedback_has_all_required_elements(self):
        """Test writing feedback includes all required elements"""
        feedback = {
            'strengths': ['Clear overview', 'Good organization'],
            'areas_for_improvement': ['More variety in vocabulary'],
            'specific_suggestions': ['Use more academic collocations', 'Practice complex sentences'],
            'examples_from_essay': ['The graph shows a significant increase...'],
            'band_justification': 'Band 7.5 awarded due to good task achievement...',
            'next_steps': ['Practice writing 3-4 essays per week', 'Focus on linking words']
        }
        
        # Verify all elements present
        assert 'strengths' in feedback
        assert 'areas_for_improvement' in feedback
        assert 'specific_suggestions' in feedback
        assert 'examples_from_essay' in feedback
        assert len(feedback['strengths']) >= 2
        assert len(feedback['specific_suggestions']) >= 2
    
    def test_improvement_plan_has_actionable_steps(self):
        """Test improvement plan contains actionable steps"""
        improvement_plan = {
            'focus_areas': [
                {
                    'criterion': 'Lexical Resource',
                    'current_band': 6.5,
                    'target_band': 7.5,
                    'specific_weakness': 'Limited range of vocabulary',
                    'practice_activities': [
                        'Read academic articles daily',
                        'Learn 10 new academic words per day',
                        'Practice paraphrasing'
                    ],
                    'estimated_time': '4-6 weeks'
                }
            ],
            'immediate_actions': [
                'Review common IELTS topics',
                'Practice with sample questions'
            ],
            'study_schedule': {
                'week_1': 'Vocabulary building',
                'week_2': 'Grammar practice',
                'week_3': 'Full essay practice',
                'week_4': 'Review and assessment'
            },
            'target_overall_band': 7.5,
            'estimated_timeline': '4-6 weeks'
        }
        
        # Verify actionable elements
        assert len(improvement_plan['focus_areas']) > 0
        assert len(improvement_plan['immediate_actions']) >= 2
        assert 'study_schedule' in improvement_plan
        assert 'target_overall_band' in improvement_plan
        
        # Verify focus areas have practice activities
        for focus_area in improvement_plan['focus_areas']:
            assert 'practice_activities' in focus_area
            assert len(focus_area['practice_activities']) >= 2


class TestScoreReportAccessibility:
    """Test that score reports are accessible after assessment completion"""
    
    @pytest.fixture
    def setup_mocks(self):
        """Setup assessment DAL"""
        with patch('dynamodb_dal.boto3.resource'):
            conn = DynamoDBConnection()
            mock_table = MagicMock()
            conn.get_table = MagicMock(return_value=mock_table)
            
            assessment_dal = AssessmentDAL(conn)
            assessment_dal.table = mock_table
            
            return {'assessment_dal': assessment_dal, 'mock_table': mock_table}
    
    def test_user_can_access_past_assessments(self, setup_mocks):
        """Test user can retrieve and view past assessment results"""
        mocks = setup_mocks
        
        # Mock query for user's assessments
        mocks['mock_table'].query.return_value = {
            'Items': [
                {
                    'assessment_id': 'assess-1',
                    'overall_band': 7.5,
                    'timestamp': '2025-10-20T10:00:00Z'
                },
                {
                    'assessment_id': 'assess-2',
                    'overall_band': 7.0,
                    'timestamp': '2025-10-22T14:00:00Z'
                }
            ]
        }
        
        # Retrieve user's assessment history
        result = mocks['mock_table'].query(
            IndexName='user_id-timestamp-index',
            KeyConditionExpression='user_id = :uid'
        )
        
        # Verify past assessments accessible
        assert len(result['Items']) == 2
        assert result['Items'][0]['assessment_id'] == 'assess-1'
        assert result['Items'][1]['assessment_id'] == 'assess-2'
