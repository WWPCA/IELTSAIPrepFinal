"""
Personalized Improvement Plan Service
Generates evidence-based, actionable improvement plans for all IELTS assessment types
Provides specific examples, focus areas, practice schedules, and progress tracking
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class PersonalizedImprovementService:
    """
    Generates personalized improvement plans for IELTS assessments
    Provides actionable steps, practice schedules, and specific examples
    """
    
    def __init__(self):
        """Initialize improvement plan service"""
        logger.info("Personalized Improvement Service initialized")
    
    def generate_speaking_improvement_plan(
        self,
        assessment_result: Dict[str, Any],
        user_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized improvement plan for speaking assessment
        
        Args:
            assessment_result: Speaking assessment results with scores and feedback
            user_history: Previous assessment attempts for progress tracking
        
        Returns:
            Comprehensive improvement plan with actionable steps
        """
        scores = assessment_result.get('criteria_scores', {})
        overall_band = assessment_result.get('overall_band', 0.0)
        target_band = min(9.0, overall_band + 1.0)
        
        # Identify weakest areas
        weak_areas = self._identify_weak_areas_speaking(scores)
        
        # Generate specific improvement actions
        improvement_actions = self._generate_speaking_actions(scores, weak_areas)
        
        # Create practice schedule
        practice_schedule = self._create_practice_schedule(
            assessment_type='speaking',
            weak_areas=weak_areas,
            current_band=overall_band,
            target_band=target_band
        )
        
        # Generate progress tracking milestones
        milestones = self._create_milestones(
            current_band=overall_band,
            target_band=target_band,
            assessment_type='speaking'
        )
        
        # Provide evidence-based strategies
        strategies = self._get_speaking_strategies(weak_areas, overall_band)
        
        return {
            'assessment_type': 'speaking',
            'current_band': overall_band,
            'target_band': target_band,
            'estimated_improvement_time': self._estimate_time_to_improve(
                overall_band, target_band, 'speaking'
            ),
            'weak_areas': weak_areas,
            'improvement_priority': self._prioritize_areas(weak_areas),
            'specific_actions': improvement_actions,
            'practice_schedule': practice_schedule,
            'evidence_based_strategies': strategies,
            'progress_milestones': milestones,
            'example_responses': self._get_example_responses(overall_band, target_band),
            'common_mistakes_to_avoid': self._get_common_mistakes('speaking', overall_band),
            'recommended_resources': self._get_resources('speaking', weak_areas),
            'progress_tracking': {
                'previous_assessments': len(user_history) if user_history else 0,
                'improvement_trend': self._calculate_trend(user_history) if user_history else None
            }
        }
    
    def generate_writing_improvement_plan(
        self,
        assessment_result: Dict[str, Any],
        user_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized improvement plan for writing assessment
        
        Args:
            assessment_result: Writing assessment results with scores and feedback
            user_history: Previous assessment attempts for progress tracking
        
        Returns:
            Comprehensive improvement plan with actionable steps
        """
        scores = assessment_result.get('criteria_scores', {})
        overall_band = assessment_result.get('overall_band', 0.0)
        target_band = min(9.0, overall_band + 1.0)
        
        # Identify weakest areas
        weak_areas = self._identify_weak_areas_writing(scores)
        
        # Generate specific improvement actions
        improvement_actions = self._generate_writing_actions(scores, weak_areas)
        
        # Create practice schedule
        practice_schedule = self._create_practice_schedule(
            assessment_type='writing',
            weak_areas=weak_areas,
            current_band=overall_band,
            target_band=target_band
        )
        
        # Generate progress tracking milestones
        milestones = self._create_milestones(
            current_band=overall_band,
            target_band=target_band,
            assessment_type='writing'
        )
        
        # Provide evidence-based strategies
        strategies = self._get_writing_strategies(weak_areas, overall_band)
        
        return {
            'assessment_type': 'writing',
            'current_band': overall_band,
            'target_band': target_band,
            'estimated_improvement_time': self._estimate_time_to_improve(
                overall_band, target_band, 'writing'
            ),
            'weak_areas': weak_areas,
            'improvement_priority': self._prioritize_areas(weak_areas),
            'specific_actions': improvement_actions,
            'practice_schedule': practice_schedule,
            'evidence_based_strategies': strategies,
            'progress_milestones': milestones,
            'example_essays': self._get_example_essays(overall_band, target_band),
            'grammar_focus': self._get_grammar_focus(scores.get('grammatical_range', 0)),
            'vocabulary_builders': self._get_vocabulary_builders(scores.get('lexical_resource', 0)),
            'common_mistakes_to_avoid': self._get_common_mistakes('writing', overall_band),
            'recommended_resources': self._get_resources('writing', weak_areas),
            'progress_tracking': {
                'previous_assessments': len(user_history) if user_history else 0,
                'improvement_trend': self._calculate_trend(user_history) if user_history else None
            }
        }
    
    def generate_reading_improvement_plan(
        self,
        assessment_result: Dict[str, Any],
        user_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized improvement plan for reading assessment
        
        Args:
            assessment_result: Reading assessment results with scores
            user_history: Previous assessment attempts for progress tracking
        
        Returns:
            Comprehensive improvement plan with actionable steps
        """
        band_score = assessment_result.get('band_score', 0.0)
        correct_answers = assessment_result.get('correct_answers', 0)
        target_band = min(9.0, band_score + 1.0)
        
        # Calculate needed improvement
        target_correct = self._get_target_correct_answers(target_band, 'reading')
        gap = target_correct - correct_answers
        
        # Identify question types that need work
        weak_question_types = self._identify_weak_question_types_reading(
            assessment_result.get('question_type_performance', {})
        )
        
        # Generate improvement actions
        improvement_actions = self._generate_reading_actions(weak_question_types, gap)
        
        # Create practice schedule
        practice_schedule = self._create_practice_schedule(
            assessment_type='reading',
            weak_areas=weak_question_types,
            current_band=band_score,
            target_band=target_band
        )
        
        # Generate milestones
        milestones = self._create_milestones(
            current_band=band_score,
            target_band=target_band,
            assessment_type='reading'
        )
        
        # Provide strategies
        strategies = self._get_reading_strategies(weak_question_types, band_score)
        
        return {
            'assessment_type': 'reading',
            'current_band': band_score,
            'current_correct': correct_answers,
            'target_band': target_band,
            'target_correct': target_correct,
            'answers_needed': gap,
            'estimated_improvement_time': self._estimate_time_to_improve(
                band_score, target_band, 'reading'
            ),
            'weak_question_types': weak_question_types,
            'improvement_priority': self._prioritize_areas(weak_question_types),
            'specific_actions': improvement_actions,
            'practice_schedule': practice_schedule,
            'evidence_based_strategies': strategies,
            'progress_milestones': milestones,
            'time_management_tips': self._get_time_management_tips('reading', band_score),
            'vocabulary_building': self._get_academic_vocabulary_plan(band_score),
            'skimming_scanning_techniques': self._get_reading_techniques(band_score),
            'recommended_resources': self._get_resources('reading', weak_question_types),
            'progress_tracking': {
                'previous_assessments': len(user_history) if user_history else 0,
                'improvement_trend': self._calculate_trend(user_history) if user_history else None
            }
        }
    
    def generate_listening_improvement_plan(
        self,
        assessment_result: Dict[str, Any],
        user_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized improvement plan for listening assessment
        
        Args:
            assessment_result: Listening assessment results with scores
            user_history: Previous assessment attempts for progress tracking
        
        Returns:
            Comprehensive improvement plan with actionable steps
        """
        band_score = assessment_result.get('band_score', 0.0)
        correct_answers = assessment_result.get('correct_answers', 0)
        target_band = min(9.0, band_score + 1.0)
        
        # Calculate needed improvement
        target_correct = self._get_target_correct_answers(target_band, 'listening')
        gap = target_correct - correct_answers
        
        # Identify section weaknesses
        weak_sections = self._identify_weak_sections_listening(
            assessment_result.get('section_performance', {})
        )
        
        # Generate improvement actions
        improvement_actions = self._generate_listening_actions(weak_sections, gap)
        
        # Create practice schedule
        practice_schedule = self._create_practice_schedule(
            assessment_type='listening',
            weak_areas=weak_sections,
            current_band=band_score,
            target_band=target_band
        )
        
        # Generate milestones
        milestones = self._create_milestones(
            current_band=band_score,
            target_band=target_band,
            assessment_type='listening'
        )
        
        # Provide strategies
        strategies = self._get_listening_strategies(weak_sections, band_score)
        
        return {
            'assessment_type': 'listening',
            'current_band': band_score,
            'current_correct': correct_answers,
            'target_band': target_band,
            'target_correct': target_correct,
            'answers_needed': gap,
            'estimated_improvement_time': self._estimate_time_to_improve(
                band_score, target_band, 'listening'
            ),
            'weak_sections': weak_sections,
            'improvement_priority': self._prioritize_areas(weak_sections),
            'specific_actions': improvement_actions,
            'practice_schedule': practice_schedule,
            'evidence_based_strategies': strategies,
            'progress_milestones': milestones,
            'note_taking_strategies': self._get_note_taking_strategies(band_score),
            'accent_familiarization': self._get_accent_practice_plan(),
            'concentration_tips': self._get_concentration_tips(),
            'recommended_resources': self._get_resources('listening', weak_sections),
            'progress_tracking': {
                'previous_assessments': len(user_history) if user_history else 0,
                'improvement_trend': self._calculate_trend(user_history) if user_history else None
            }
        }
    
    # ==================== HELPER METHODS ====================
    
    def _identify_weak_areas_speaking(self, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify weakest speaking criteria"""
        criteria_map = {
            'fluency_coherence': 'Fluency and Coherence',
            'lexical_resource': 'Lexical Resource',
            'grammatical_range': 'Grammatical Range and Accuracy',
            'pronunciation': 'Pronunciation'
        }
        
        weak_areas = []
        for key, name in criteria_map.items():
            score = scores.get(key, 0.0)
            if score < 7.0:  # Below Band 7 needs improvement
                weak_areas.append({
                    'area': name,
                    'current_score': score,
                    'gap_to_7': 7.0 - score,
                    'severity': 'high' if score < 6.0 else 'medium'
                })
        
        return sorted(weak_areas, key=lambda x: x['current_score'])
    
    def _identify_weak_areas_writing(self, scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify weakest writing criteria"""
        criteria_map = {
            'task_achievement': 'Task Achievement/Response',
            'coherence_cohesion': 'Coherence and Cohesion',
            'lexical_resource': 'Lexical Resource',
            'grammatical_range': 'Grammatical Range and Accuracy'
        }
        
        weak_areas = []
        for key, name in criteria_map.items():
            score = scores.get(key, 0.0)
            if score < 7.0:
                weak_areas.append({
                    'area': name,
                    'current_score': score,
                    'gap_to_7': 7.0 - score,
                    'severity': 'high' if score < 6.0 else 'medium'
                })
        
        return sorted(weak_areas, key=lambda x: x['current_score'])
    
    def _identify_weak_question_types_reading(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify weak reading question types"""
        return [
            {
                'type': q_type,
                'accuracy': stats.get('accuracy', 0),
                'severity': 'high' if stats.get('accuracy', 0) < 60 else 'medium'
            }
            for q_type, stats in performance.items()
            if stats.get('accuracy', 100) < 75
        ]
    
    def _identify_weak_sections_listening(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify weak listening sections"""
        return [
            {
                'section': section,
                'accuracy': stats.get('accuracy', 0),
                'severity': 'high' if stats.get('accuracy', 0) < 60 else 'medium'
            }
            for section, stats in performance.items()
            if stats.get('accuracy', 100) < 75
        ]
    
    def _generate_speaking_actions(
        self, 
        scores: Dict[str, float], 
        weak_areas: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate specific speaking improvement actions"""
        actions = []
        
        # Fluency and Coherence
        if scores.get('fluency_coherence', 10) < 7.0:
            actions.append({
                'focus': 'Fluency and Coherence',
                'action': 'Practice speaking for 2 minutes without stopping on familiar topics',
                'frequency': 'Daily',
                'duration': '15 minutes',
                'examples': [
                    'Describe your daily routine',
                    'Talk about your favorite hobby',
                    'Explain how to cook a simple dish'
                ],
                'success_metric': 'Speak continuously for 2 minutes with fewer than 3 hesitations'
            })
        
        # Lexical Resource
        if scores.get('lexical_resource', 10) < 7.0:
            actions.append({
                'focus': 'Lexical Resource',
                'action': 'Learn and use 5 new topic-specific words daily',
                'frequency': 'Daily',
                'duration': '20 minutes',
                'examples': [
                    'Education: curriculum, pedagogy, assessment, enrollment',
                    'Environment: sustainability, biodiversity, conservation, emissions',
                    'Technology: innovation, automation, artificial intelligence, connectivity'
                ],
                'success_metric': 'Use at least 3 less common words naturally in each response'
            })
        
        # Grammatical Range
        if scores.get('grammatical_range', 10) < 7.0:
            actions.append({
                'focus': 'Grammatical Range and Accuracy',
                'action': 'Practice using complex sentence structures',
                'frequency': '3 times per week',
                'duration': '20 minutes',
                'examples': [
                    'Conditional sentences: "If I had more time, I would travel more"',
                    'Relative clauses: "The book that I read was fascinating"',
                    'Passive voice: "The project was completed ahead of schedule"'
                ],
                'success_metric': 'Use at least 2 complex structures per response without errors'
            })
        
        # Pronunciation
        if scores.get('pronunciation', 10) < 7.0:
            actions.append({
                'focus': 'Pronunciation',
                'action': 'Practice word stress and intonation patterns',
                'frequency': 'Daily',
                'duration': '10 minutes',
                'examples': [
                    'Record yourself and compare with native speakers',
                    'Practice minimal pairs: ship/sheep, bit/beat, cat/cut',
                    'Focus on sentence stress for emphasis'
                ],
                'success_metric': 'Be understood by native speakers without repetition'
            })
        
        return actions
    
    def _generate_writing_actions(
        self, 
        scores: Dict[str, float], 
        weak_areas: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate specific writing improvement actions"""
        actions = []
        
        if scores.get('task_achievement', 10) < 7.0:
            actions.append({
                'focus': 'Task Achievement/Response',
                'action': 'Practice fully addressing all parts of the task',
                'frequency': '3 times per week',
                'duration': '60 minutes',
                'examples': [
                    'Read the question carefully and underline key words',
                    'Plan your response covering all bullet points',
                    'Check you addressed "to what extent" or "advantages and disadvantages"'
                ],
                'success_metric': 'Every paragraph clearly relates to the task'
            })
        
        if scores.get('coherence_cohesion', 10) < 7.0:
            actions.append({
                'focus': 'Coherence and Cohesion',
                'action': 'Master linking words and paragraph structure',
                'frequency': '3 times per week',
                'duration': '30 minutes',
                'examples': [
                    'Use: however, moreover, nevertheless, consequently',
                    'Practice: Topic sentence → Supporting ideas → Example → Conclusion',
                    'Avoid overusing: firstly, secondly, finally'
                ],
                'success_metric': 'Clear logical flow between all paragraphs'
            })
        
        if scores.get('lexical_resource', 10) < 7.0:
            actions.append({
                'focus': 'Lexical Resource',
                'action': 'Build academic vocabulary and collocations',
                'frequency': 'Daily',
                'duration': '20 minutes',
                'examples': [
                    'Learn: achieve success, make progress, raise awareness',
                    'Avoid: get (use obtain, acquire, receive)',
                    'Use: substantial, significant, considerable instead of "big"'
                ],
                'success_metric': 'Use at least 5 less common words accurately per essay'
            })
        
        if scores.get('grammatical_range', 10) < 7.0:
            actions.append({
                'focus': 'Grammatical Range and Accuracy',
                'action': 'Practice error-free complex sentences',
                'frequency': '3 times per week',
                'duration': '25 minutes',
                'examples': [
                    'Mix: simple, compound, and complex sentences',
                    'Use: conditionals, passive voice, participle clauses',
                    'Proofread for: subject-verb agreement, articles, prepositions'
                ],
                'success_metric': 'Majority of sentences error-free with varied structures'
            })
        
        return actions
    
    def _generate_reading_actions(
        self, 
        weak_types: List[Dict], 
        answers_gap: int
    ) -> List[Dict[str, Any]]:
        """Generate specific reading improvement actions"""
        return [
            {
                'focus': 'Speed Reading',
                'action': 'Practice skimming and scanning techniques',
                'frequency': 'Daily',
                'duration': '30 minutes',
                'target': f'Improve by {answers_gap} correct answers',
                'examples': [
                    'Skim passage in 2-3 minutes for main ideas',
                    'Scan for specific details (numbers, names, dates)',
                    'Practice with timer: 20 minutes per passage'
                ]
            },
            {
                'focus': 'Vocabulary Building',
                'action': 'Learn academic word families',
                'frequency': 'Daily',
                'duration': '15 minutes',
                'examples': [
                    'Focus on AWL (Academic Word List)',
                    'Learn prefixes/suffixes for word guessing',
                    'Practice paraphrasing'
                ]
            },
            {
                'focus': 'Question Type Practice',
                'action': 'Master weak question types',
                'frequency': '3 times per week',
                'duration': '45 minutes',
                'weak_types': [w['type'] for w in weak_types],
                'examples': [
                    'True/False/Not Given: Look for exact matches',
                    'Matching Headings: Focus on topic sentences',
                    'Sentence Completion: Follow word limits exactly'
                ]
            }
        ]
    
    def _generate_listening_actions(
        self, 
        weak_sections: List[Dict], 
        answers_gap: int
    ) -> List[Dict[str, Any]]:
        """Generate specific listening improvement actions"""
        return [
            {
                'focus': 'Active Listening',
                'action': 'Practice prediction and note-taking',
                'frequency': 'Daily',
                'duration': '30 minutes',
                'target': f'Improve by {answers_gap} correct answers',
                'examples': [
                    'Read questions before audio starts',
                    'Predict answer types (number, name, date)',
                    'Take brief notes while listening'
                ]
            },
            {
                'focus': 'Accent Familiarization',
                'action': 'Expose yourself to different English accents',
                'frequency': 'Daily',
                'duration': '20 minutes',
                'examples': [
                    'Listen to BBC (British), CNN (American), ABC (Australian)',
                    'Practice with podcasts in different accents',
                    'Watch TED talks with varied speakers'
                ]
            },
            {
                'focus': 'Concentration',
                'action': 'Build listening stamina',
                'frequency': '3 times per week',
                'duration': '40 minutes',
                'examples': [
                    'Practice full 30-minute tests without breaks',
                    'Listen to academic lectures',
                    'Take practice tests in noisy environments'
                ]
            }
        ]
    
    def _create_practice_schedule(
        self,
        assessment_type: str,
        weak_areas: List[Dict],
        current_band: float,
        target_band: float
    ) -> Dict[str, Any]:
        """Create weekly practice schedule"""
        gap = target_band - current_band
        intensity = 'high' if gap >= 1.0 else 'medium'
        
        if assessment_type == 'speaking':
            return {
                'weekly_hours': 7 if intensity == 'high' else 5,
                'daily_practice': [
                    {
                        'day': 'Monday',
                        'focus': 'Part 1 questions - Personal topics',
                        'duration': '60 minutes',
                        'activities': ['Practice common topics', 'Record yourself', 'Review recording']
                    },
                    {
                        'day': 'Tuesday',
                        'focus': 'Part 2 - Cue card practice',
                        'duration': '60 minutes',
                        'activities': ['Choose topic', 'Plan for 1 minute', 'Speak for 2 minutes']
                    },
                    {
                        'day': 'Wednesday',
                        'focus': 'Part 3 - Abstract discussions',
                        'duration': '60 minutes',
                        'activities': ['Practice complex questions', 'Use advanced vocabulary', 'Give detailed answers']
                    },
                    {
                        'day': 'Thursday',
                        'focus': 'Pronunciation and fluency',
                        'duration': '45 minutes',
                        'activities': ['Shadowing exercises', 'Tongue twisters', 'Word stress practice']
                    },
                    {
                        'day': 'Friday',
                        'focus': 'Full mock test',
                        'duration': '20 minutes',
                        'activities': ['Complete all 3 parts', 'Time yourself', 'Get feedback']
                    },
                    {
                        'day': 'Saturday',
                        'focus': 'Vocabulary building',
                        'duration': '45 minutes',
                        'activities': ['Learn topic vocabulary', 'Practice using new words', 'Create example sentences']
                    },
                    {
                        'day': 'Sunday',
                        'focus': 'Review and rest',
                        'duration': '30 minutes',
                        'activities': ['Review recordings', 'Note improvements', 'Plan next week']
                    }
                ]
            }
        
        elif assessment_type == 'writing':
            return {
                'weekly_hours': 8 if intensity == 'high' else 6,
                'daily_practice': [
                    {
                        'day': 'Monday',
                        'focus': 'Task 1 - Report writing',
                        'duration': '60 minutes',
                        'activities': ['Write one Task 1', 'Review model answers', 'Note key phrases']
                    },
                    {
                        'day': 'Tuesday',
                        'focus': 'Task 2 - Essay planning',
                        'duration': '60 minutes',
                        'activities': ['Practice brainstorming', 'Create essay outlines', 'Develop arguments']
                    },
                    {
                        'day': 'Wednesday',
                        'focus': 'Task 2 - Full essay',
                        'duration': '90 minutes',
                        'activities': ['Write complete essay', 'Check word count', 'Proofread carefully']
                    },
                    {
                        'day': 'Thursday',
                        'focus': 'Grammar and vocabulary',
                        'duration': '60 minutes',
                        'activities': ['Practice complex sentences', 'Learn collocations', 'Review errors']
                    },
                    {
                        'day': 'Friday',
                        'focus': 'Full mock test',
                        'duration': '60 minutes',
                        'activities': ['Task 1 (20 min)', 'Task 2 (40 min)', 'No breaks']
                    },
                    {
                        'day': 'Saturday',
                        'focus': 'Review and improvement',
                        'duration': '90 minutes',
                        'activities': ['Analyze feedback', 'Rewrite weak paragraphs', 'Study model essays']
                    },
                    {
                        'day': 'Sunday',
                        'focus': 'Reading for writing',
                        'duration': '45 minutes',
                        'activities': ['Read academic articles', 'Note useful phrases', 'Build vocabulary']
                    }
                ]
            }
        
        else:  # Reading or Listening
            return {
                'weekly_hours': 6 if intensity == 'high' else 4,
                'practice_frequency': 'Daily 30-40 minutes',
                'weekly_tests': 2 if intensity == 'high' else 1,
                'focus_areas': [area.get('type', area.get('section', '')) for area in weak_areas[:3]]
            }
    
    def _create_milestones(
        self,
        current_band: float,
        target_band: float,
        assessment_type: str
    ) -> List[Dict[str, Any]]:
        """Create progress milestones"""
        gap = target_band - current_band
        weeks = int(gap * 8)  # Rough estimate: 8 weeks per 1.0 band
        
        milestones = []
        for i in range(1, int(gap * 2) + 1):
            milestone_band = current_band + (i * 0.5)
            if milestone_band <= target_band:
                milestones.append({
                    'band_score': milestone_band,
                    'target_week': i * 4,
                    'key_achievements': [
                        f'Consistently score {milestone_band} in practice tests',
                        f'Demonstrate mastery of Band {int(milestone_band)} criteria',
                        f'Show measurable improvement in weak areas'
                    ]
                })
        
        return milestones
    
    def _estimate_time_to_improve(
        self,
        current_band: float,
        target_band: float,
        assessment_type: str
    ) -> Dict[str, Any]:
        """Estimate time needed for improvement"""
        gap = target_band - current_band
        
        # Average time per 0.5 band increase
        weeks_per_half_band = {
            'speaking': 4,
            'writing': 5,
            'reading': 3,
            'listening': 3
        }
        
        weeks = int(gap * 2 * weeks_per_half_band.get(assessment_type, 4))
        
        return {
            'weeks': weeks,
            'months': round(weeks / 4.3, 1),
            'daily_practice_hours': 1 if gap < 1.0 else 1.5,
            'confidence_level': 'high' if gap <= 1.0 else 'medium'
        }
    
    def _prioritize_areas(self, weak_areas: List[Dict]) -> List[str]:
        """Prioritize improvement areas by severity"""
        high_priority = [area.get('area', area.get('type', area.get('section', ''))) 
                        for area in weak_areas if area.get('severity') == 'high']
        medium_priority = [area.get('area', area.get('type', area.get('section', ''))) 
                          for area in weak_areas if area.get('severity') == 'medium']
        
        return high_priority + medium_priority
    
    def _get_speaking_strategies(self, weak_areas: List[Dict], band: float) -> List[str]:
        """Get evidence-based speaking strategies"""
        return [
            "Think in English: Avoid translating from your native language",
            "Use fillers naturally: Well, actually, you know, I mean (don't overuse)",
            "Extend answers: Give examples and reasons for every point",
            "Practice with timer: Get comfortable with 2-minute responses",
            "Record and review: Identify hesitations and errors",
            "Mirror native speakers: Copy their intonation and stress patterns"
        ]
    
    def _get_writing_strategies(self, weak_areas: List[Dict], band: float) -> List[str]:
        """Get evidence-based writing strategies"""
        return [
            "Plan before writing: Spend 5-10 minutes outlining",
            "Use topic sentences: Start each paragraph with main idea",
            "Vary sentence length: Mix short and long sentences",
            "Check coherence: Ensure logical flow between ideas",
            "Proofread systematically: Grammar → Spelling → Punctuation",
            "Meet word count: 150+ for Task 1, 250+ for Task 2"
        ]
    
    def _get_reading_strategies(self, weak_types: List[Dict], band: float) -> List[str]:
        """Get evidence-based reading strategies"""
        return [
            "Skim first: Get overview before reading in detail",
            "Scan for keywords: Find specific information quickly",
            "Underline carefully: Mark key words in questions",
            "Watch time: 20 minutes per passage maximum",
            "Transfer answers: Check spelling and word limits",
            "Guess intelligently: Eliminate wrong answers first"
        ]
    
    def _get_listening_strategies(self, weak_sections: List[Dict], band: float) -> List[str]:
        """Get evidence-based listening strategies"""
        return [
            "Read ahead: Use preparation time to read questions",
            "Predict answers: Guess what information you'll hear",
            "Listen for synonyms: Answers often paraphrase the audio",
            "Write as you hear: Don't wait to write answers",
            "Check spelling: Especially for names and places",
            "Use transfer time: Review and complete any missing answers"
        ]
    
    def _get_example_responses(self, current_band: float, target_band: float) -> List[Dict]:
        """Get example speaking responses at target band level"""
        return [
            {
                'question': 'Describe a memorable journey you have taken',
                'band_level': target_band,
                'example': 'One of the most memorable journeys I\'ve undertaken was a trip to Japan...',
                'key_features': [
                    'Varied vocabulary (undertaken, immersed, captivating)',
                    'Complex structures (relative clauses, passive voice)',
                    'Clear organization and development',
                    'Natural fluency with minimal hesitation'
                ]
            }
        ]
    
    def _get_example_essays(self, current_band: float, target_band: float) -> List[Dict]:
        """Get example essays at target band level"""
        return [
            {
                'task_type': 'Advantage/Disadvantage',
                'band_level': target_band,
                'topic': 'Remote work trend',
                'key_features': [
                    'Clear thesis statement',
                    'Balanced discussion of both sides',
                    'Specific examples provided',
                    'Strong conclusion with opinion'
                ]
            }
        ]
    
    def _get_grammar_focus(self, score: float) -> List[str]:
        """Get grammar focus areas based on score"""
        if score < 6.0:
            return [
                'Master basic tenses: present, past, future',
                'Practice subject-verb agreement',
                'Learn common prepositions',
                'Fix article usage (a, an, the)'
            ]
        elif score < 7.0:
            return [
                'Perfect conditional sentences',
                'Use passive voice correctly',
                'Master relative clauses',
                'Practice participle phrases'
            ]
        else:
            return [
                'Advanced structures: inversion, cleft sentences',
                'Nuanced modal verbs',
                'Perfect aspect in various tenses',
                'Advanced subordination'
            ]
    
    def _get_vocabulary_builders(self, score: float) -> List[str]:
        """Get vocabulary building activities"""
        return [
            'Learn Academic Word List (AWL) - 10 words per week',
            'Study topic-specific vocabulary (education, environment, technology)',
            'Practice collocations and phrasal verbs',
            'Use vocabulary in writing immediately after learning',
            'Create mind maps for word families'
        ]
    
    def _get_common_mistakes(self, assessment_type: str, band: float) -> List[str]:
        """Get common mistakes to avoid"""
        mistakes = {
            'speaking': [
                "Memorized answers sound unnatural",
                "Using complex words incorrectly",
                "Not extending answers with examples",
                "Speaking too fast and making errors"
            ],
            'writing': [
                "Not addressing all parts of the question",
                "Overusing linking words",
                "Writing less than required word count",
                "Not proofreading for basic errors"
            ],
            'reading': [
                "Not managing time effectively",
                "Copying words incorrectly from passage",
                "Exceeding word limits in answers",
                "Not following instructions carefully"
            ],
            'listening': [
                "Writing answers while missing next question",
                "Spelling names and places incorrectly",
                "Not using exact words from audio",
                "Leaving answers blank instead of guessing"
            ]
        }
        return mistakes.get(assessment_type, [])
    
    def _get_resources(self, assessment_type: str, weak_areas: List[Dict]) -> List[Dict]:
        """Get recommended resources"""
        return [
            {
                'type': 'Official Materials',
                'resources': [
                    'Cambridge IELTS Practice Tests (Books 14-18)',
                    'IELTS.org Official Practice Materials',
                    'British Council IELTS Preparation'
                ]
            },
            {
                'type': 'Online Practice',
                'resources': [
                    'IELTS Liz (free tips and examples)',
                    'IELTS Advantage (strategies and practice)',
                    'Road to IELTS (British Council course)'
                ]
            },
            {
                'type': 'Apps',
                'resources': [
                    'IELTS Prep App by British Council',
                    'Magoosh IELTS Prep',
                    'IELTS Word Power by British Council'
                ]
            }
        ]
    
    def _get_time_management_tips(self, test_type: str, band: float) -> List[str]:
        """Get time management tips"""
        return [
            "Spend 2-3 minutes skimming the entire passage",
            "Allocate 20 minutes per passage (including transfer time)",
            "Answer easier questions first to build confidence",
            "Don't spend more than 1.5 minutes per question",
            "Leave difficult questions and return if time permits"
        ]
    
    def _get_academic_vocabulary_plan(self, band: float) -> Dict:
        """Get academic vocabulary building plan"""
        return {
            'focus': 'Academic Word List (AWL) - 570 word families',
            'weekly_target': 20 if band < 6.5 else 15,
            'practice_methods': [
                'Create flashcards with example sentences',
                'Use new words in practice essays',
                'Learn word families (analyze, analysis, analytical)',
                'Study synonyms and antonyms'
            ],
            'high_frequency_words': [
                'analyze, approach, assess, concept, constitute',
                'context, establish, estimate, indicate, principle'
            ]
        }
    
    def _get_reading_techniques(self, band: float) -> Dict:
        """Get skimming and scanning techniques"""
        return {
            'skimming': {
                'purpose': 'Get general idea of passage',
                'technique': 'Read first and last paragraphs, topic sentences',
                'time': '2-3 minutes per passage'
            },
            'scanning': {
                'purpose': 'Find specific information',
                'technique': 'Look for keywords, numbers, capital letters',
                'time': '30 seconds per question'
            },
            'detailed_reading': {
                'purpose': 'Answer specific questions',
                'technique': 'Read relevant sections carefully',
                'time': '1-1.5 minutes per question'
            }
        }
    
    def _get_note_taking_strategies(self, band: float) -> List[str]:
        """Get note-taking strategies for listening"""
        return [
            "Use abbreviations: info (information), govt (government), approx (approximately)",
            "Write key words only, not full sentences",
            "Note numbers, dates, names immediately",
            "Use arrows and symbols for relationships",
            "Leave space to add missed information",
            "Review notes during transfer time"
        ]
    
    def _get_accent_practice_plan(self) -> Dict:
        """Get accent familiarization plan"""
        return {
            'accents_to_practice': ['British', 'American', 'Australian', 'Canadian'],
            'resources': [
                'BBC World Service (British)',
                'NPR/CNN (American)',
                'ABC Australia (Australian)',
                'CBC (Canadian)'
            ],
            'practice_approach': [
                'Listen to 20 minutes daily of different accents',
                'Focus on understanding rather than mimicking',
                'Practice with IELTS-specific audio materials',
                'Watch documentaries with varied speakers'
            ]
        }
    
    def _get_concentration_tips(self) -> List[str]:
        """Get concentration tips"""
        return [
            "Practice in realistic conditions (some background noise)",
            "Build stamina with full-length practice tests",
            "Take brief mental breaks between sections",
            "Stay alert: sit upright, stay hydrated",
            "Focus on keywords in questions before listening",
            "Don't panic if you miss an answer - move on"
        ]
    
    def _get_target_correct_answers(self, target_band: float, test_type: str) -> int:
        """Get number of correct answers needed for target band"""
        # Based on official IELTS conversion tables
        conversion = {
            9.0: 39, 8.5: 37, 8.0: 35, 7.5: 33, 7.0: 30,
            6.5: 27, 6.0: 23, 5.5: 19, 5.0: 15, 4.5: 13
        }
        return conversion.get(target_band, 30)
    
    def _calculate_trend(self, user_history: List[Dict]) -> Optional[str]:
        """Calculate improvement trend from user history"""
        if not user_history or len(user_history) < 2:
            return None
        
        recent_scores = [h.get('overall_band', 0) for h in user_history[-3:]]
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0]:
                return 'improving'
            elif recent_scores[-1] < recent_scores[0]:
                return 'declining'
            else:
                return 'stable'
        return None


# Global singleton instance
_improvement_service = None

def get_improvement_service() -> PersonalizedImprovementService:
    """Get global improvement service instance"""
    global _improvement_service
    if _improvement_service is None:
        _improvement_service = PersonalizedImprovementService()
    return _improvement_service
