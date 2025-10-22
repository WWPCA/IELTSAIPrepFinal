"""
IELTS Band Scoring and Detailed Feedback System
Comprehensive evaluation and improvement recommendations based on official IELTS rubrics
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import statistics

from assessment_criteria.speaking_criteria import (
    SPEAKING_BAND_DESCRIPTORS,
    SPEAKING_ASSESSMENT_CRITERIA,
    calculate_speaking_band_score
)

logger = logging.getLogger(__name__)

class ScoringCriterion(Enum):
    """IELTS Speaking assessment criteria"""
    FLUENCY_COHERENCE = "Fluency and Coherence"
    LEXICAL_RESOURCE = "Lexical Resource" 
    GRAMMATICAL_RANGE = "Grammatical Range and Accuracy"
    PRONUNCIATION = "Pronunciation"

class BandLevel(Enum):
    """IELTS Band levels"""
    BAND_9 = 9.0
    BAND_8_5 = 8.5
    BAND_8 = 8.0
    BAND_7_5 = 7.5
    BAND_7 = 7.0
    BAND_6_5 = 6.5
    BAND_6 = 6.0
    BAND_5_5 = 5.5
    BAND_5 = 5.0
    BAND_4_5 = 4.5
    BAND_4 = 4.0

class IELTSBandScorer:
    """
    Comprehensive IELTS Band Scoring System
    Provides detailed feedback and improvement recommendations
    """
    
    def __init__(self):
        # Improvement suggestions database
        self.improvement_suggestions = {
            ScoringCriterion.FLUENCY_COHERENCE: {
                "low": [
                    "Practice speaking without long pauses by rehearsing common topics daily",
                    "Use linking words like 'however', 'therefore', 'in addition' to connect ideas",
                    "Practice reading aloud to improve natural rhythm and flow",
                    "Record yourself speaking and identify where you hesitate most",
                    "Use conversation starters to practice spontaneous speaking"
                ],
                "medium": [
                    "Work on reducing self-correction by planning your responses better", 
                    "Practice using discourse markers more naturally and accurately",
                    "Focus on maintaining coherence when discussing complex topics",
                    "Develop your ideas more fully before moving to the next point",
                    "Practice topic development through extended speaking exercises"
                ],
                "high": [
                    "Fine-tune your use of cohesive devices for more sophisticated connections",
                    "Practice maintaining fluency even when discussing unfamiliar topics",
                    "Work on situational appropriateness in your responses",
                    "Develop skills in managing interruptions or redirecting topics naturally"
                ]
            },
            
            ScoringCriterion.LEXICAL_RESOURCE: {
                "low": [
                    "Build vocabulary by learning 10 new words daily with example sentences",
                    "Practice paraphrasing using synonyms and different word forms",
                    "Use vocabulary journals to track and review new words regularly",
                    "Focus on topic-specific vocabulary for common IELTS themes",
                    "Practice explaining words when you don't know specific terms"
                ],
                "medium": [
                    "Work on using less common vocabulary items appropriately",
                    "Practice collocations (word partnerships) to sound more natural",
                    "Focus on idiomatic expressions and their appropriate usage",
                    "Develop skills in using different word forms (noun/verb/adjective)",
                    "Practice precision in word choice to convey exact meanings"
                ],
                "high": [
                    "Master sophisticated vocabulary and precise usage in all contexts",
                    "Practice using idiomatic language naturally and appropriately",
                    "Develop skills in subtle meaning distinctions and word choice",
                    "Work on style variation for different speaking contexts"
                ]
            },
            
            ScoringCriterion.GRAMMATICAL_RANGE: {
                "low": [
                    "Practice basic sentence structures until they become automatic",
                    "Focus on subject-verb agreement and verb tense consistency",
                    "Learn common sentence patterns for expressing opinions and ideas",
                    "Practice forming questions and using conditional sentences",
                    "Work on using articles (a, an, the) correctly"
                ],
                "medium": [
                    "Practice complex sentence structures with subordinate clauses",
                    "Work on using a variety of verb tenses accurately",
                    "Focus on reducing grammatical errors in complex structures",
                    "Practice using passive voice and reported speech appropriately",
                    "Develop skills in using relative clauses effectively"
                ],
                "high": [
                    "Master flexible use of complex grammatical structures",
                    "Focus on achieving native-like accuracy in all structures",
                    "Practice sophisticated grammar for advanced communication",
                    "Work on error-free production in spontaneous speech"
                ]
            },
            
            ScoringCriterion.PRONUNCIATION: {
                "low": [
                    "Practice individual sounds that are difficult in your native language",
                    "Work on word stress patterns using online pronunciation dictionaries",
                    "Practice sentence rhythm and basic intonation patterns",
                    "Focus on clear articulation of consonant clusters",
                    "Record and compare your pronunciation with native speakers"
                ],
                "medium": [
                    "Develop natural rhythm and stress timing in connected speech",
                    "Practice intonation patterns for different sentence types",
                    "Work on pronunciation of less common words and technical terms",
                    "Focus on maintaining clarity even when speaking quickly",
                    "Practice chunking speech into appropriate thought groups"
                ],
                "high": [
                    "Master subtle pronunciation features for conveying precise meaning",
                    "Develop flexible use of stress and intonation for emphasis",
                    "Work on accent modification if it affects intelligibility",
                    "Practice effortless intelligibility in all speaking contexts"
                ]
            }
        }
        
        # Assessment prompts for detailed evaluation
        self.assessment_prompts = {
            ScoringCriterion.FLUENCY_COHERENCE: [
                "How smoothly does the candidate speak without noticeable pauses?",
                "Are ideas connected logically and coherently?", 
                "Does the candidate use appropriate linking devices?",
                "Is there natural rhythm and flow in the speech?",
                "How well does the candidate develop topics?"
            ],
            
            ScoringCriterion.LEXICAL_RESOURCE: [
                "What is the range and variety of vocabulary used?",
                "How appropriately and accurately is vocabulary used?",
                "Can the candidate paraphrase effectively when needed?",
                "Are collocations and word partnerships used naturally?",
                "Does the candidate use idiomatic language appropriately?"
            ],
            
            ScoringCriterion.GRAMMATICAL_RANGE: [
                "What range of grammatical structures does the candidate use?",
                "How accurate are the grammatical structures produced?",
                "Are complex structures used flexibly and appropriately?",
                "How frequent are grammatical errors?",
                "Do errors interfere with communication?"
            ],
            
            ScoringCriterion.PRONUNCIATION: [
                "How clear and intelligible is the candidate's speech?",
                "Are individual sounds produced accurately?",
                "How appropriate are stress, rhythm, and intonation?",
                "Does pronunciation interfere with understanding?",
                "How much effort is required to understand the candidate?"
            ]
        }
    
    def evaluate_speaking_assessment(self, conversation_data: Dict[str, Any], 
                                   ai_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation of speaking assessment
        
        Args:
            conversation_data: Complete conversation data from Maya
            ai_analysis: Optional AI analysis results
            
        Returns:
            Dict with detailed band scores and feedback
        """
        try:
            logger.info(f"Evaluating speaking assessment for session: {conversation_data.get('session_id')}")
            
            # Extract conversation details
            user_responses = conversation_data.get('user_responses', [])
            evaluation_notes = conversation_data.get('evaluation_notes', [])
            conversation_flow = conversation_data.get('conversation_flow', {})
            
            if not user_responses:
                return {
                    'success': False,
                    'error': 'No user responses found for evaluation'
                }
            
            # Analyze each criterion
            criterion_scores = {}
            detailed_feedback = {}
            
            for criterion in ScoringCriterion:
                score, feedback = self.evaluate_criterion(
                    criterion, user_responses, evaluation_notes, ai_analysis
                )
                criterion_scores[criterion.value] = score
                detailed_feedback[criterion.value] = feedback
            
            # Calculate overall band score
            overall_score = calculate_speaking_band_score(criterion_scores)
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report(
                overall_score, criterion_scores, detailed_feedback, 
                conversation_flow, user_responses
            )
            
            return {
                'success': True,
                'overall_band_score': overall_score,
                'criterion_scores': criterion_scores,
                'detailed_feedback': detailed_feedback,
                'comprehensive_report': report,
                'assessment_date': datetime.utcnow().isoformat(),
                'session_id': conversation_data.get('session_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate speaking assessment: {e}")
            return {
                'success': False,
                'error': 'Failed to complete evaluation'
            }
    
    def evaluate_criterion(self, criterion: ScoringCriterion, user_responses: List[Dict[str, Any]], 
                         evaluation_notes: List[Dict[str, Any]], ai_analysis: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate specific IELTS criterion
        
        Returns:
            Tuple of (band_score, detailed_feedback)
        """
        try:
            # Base evaluation from conversation analysis
            base_score = self.analyze_criterion_from_responses(criterion, user_responses, evaluation_notes)
            
            # Adjust with AI analysis if available
            if ai_analysis and criterion.value.lower().replace(' ', '_') in ai_analysis:
                ai_score = ai_analysis[criterion.value.lower().replace(' ', '_')].get('score', base_score)
                # Weight: 70% AI analysis, 30% conversation analysis
                adjusted_score = (ai_score * 0.7) + (base_score * 0.3)
            else:
                adjusted_score = base_score
            
            # Round to nearest 0.5
            final_score = round(adjusted_score * 2) / 2
            
            # Generate detailed feedback
            feedback = self.generate_criterion_feedback(criterion, final_score, user_responses, evaluation_notes)
            
            return final_score, feedback
            
        except Exception as e:
            logger.error(f"Failed to evaluate criterion {criterion.value}: {e}")
            # Return middle band with generic feedback
            return 5.0, {"score": 5.0, "feedback": "Unable to provide detailed evaluation for this criterion."}
    
    def analyze_criterion_from_responses(self, criterion: ScoringCriterion, 
                                       user_responses: List[Dict[str, Any]], 
                                       evaluation_notes: List[Dict[str, Any]]) -> float:
        """Analyze criterion based on conversation responses"""
        
        if criterion == ScoringCriterion.FLUENCY_COHERENCE:
            return self.analyze_fluency_coherence(user_responses, evaluation_notes)
        elif criterion == ScoringCriterion.LEXICAL_RESOURCE:
            return self.analyze_lexical_resource(user_responses, evaluation_notes) 
        elif criterion == ScoringCriterion.GRAMMATICAL_RANGE:
            return self.analyze_grammatical_range(user_responses, evaluation_notes)
        elif criterion == ScoringCriterion.PRONUNCIATION:
            return self.analyze_pronunciation(user_responses, evaluation_notes)
        else:
            return 5.0  # Default middle band
    
    def analyze_fluency_coherence(self, responses: List[Dict[str, Any]], notes: List[Dict[str, Any]]) -> float:
        """Analyze fluency and coherence from responses"""
        scores = []
        
        for response in responses:
            score = 5.0  # Base score
            
            # Check response length appropriateness
            word_count = response.get('word_count', 0)
            duration = response.get('duration', 0)
            stage = response.get('stage', '')
            
            # Fluency indicators
            if duration > 0 and word_count > 0:
                words_per_minute = (word_count / duration) * 60
                if 120 <= words_per_minute <= 180:  # Natural speaking rate
                    score += 1.0
                elif words_per_minute < 100 or words_per_minute > 200:
                    score -= 1.0
            
            # Response appropriateness
            if 'part1' in stage and 10 <= word_count <= 50:
                score += 0.5
            elif 'part2' in stage and 150 <= word_count <= 300:
                score += 1.0
            elif 'part3' in stage and 30 <= word_count <= 100:
                score += 0.5
            elif word_count < 5:  # Very brief responses
                score -= 1.5
            
            # Check evaluation notes for fluency issues
            fluency_notes = [n for n in notes if n.get('criterion') == 'Fluency and Coherence']
            if any('hesitation' in n.get('note', '').lower() for n in fluency_notes):
                score -= 0.5
            if any('slow speech' in n.get('note', '').lower() for n in fluency_notes):
                score -= 0.5
                
            scores.append(max(1.0, min(9.0, score)))  # Keep within band range
        
        return statistics.mean(scores) if scores else 5.0
    
    def analyze_lexical_resource(self, responses: List[Dict[str, Any]], notes: List[Dict[str, Any]]) -> float:
        """Analyze lexical resource from responses"""
        scores = []
        all_words = []
        
        for response in responses:
            score = 5.0  # Base score
            text = response.get('text', '')
            words = text.lower().split() if text else []
            all_words.extend(words)
            
            if not words:
                scores.append(3.0)  # No vocabulary to assess
                continue
                
            # Vocabulary variety
            unique_words = set(words)
            variety_ratio = len(unique_words) / len(words) if words else 0
            
            if variety_ratio > 0.8:
                score += 1.5  # High variety
            elif variety_ratio > 0.6:
                score += 0.5  # Good variety
            elif variety_ratio < 0.4:
                score -= 1.0  # Poor variety
            
            # Response length bonus (more words = more vocabulary demonstrated)
            word_count = len(words)
            if word_count > 100:
                score += 0.5
            elif word_count < 10:
                score -= 0.5
            
            scores.append(max(1.0, min(9.0, score)))
        
        # Overall vocabulary variety across all responses
        if all_words:
            total_unique = len(set(all_words))
            total_words = len(all_words)
            overall_variety = total_unique / total_words
            
            variety_bonus = 0
            if overall_variety > 0.7:
                variety_bonus = 1.0
            elif overall_variety > 0.5:
                variety_bonus = 0.5
            elif overall_variety < 0.3:
                variety_bonus = -0.5
                
            scores = [s + variety_bonus for s in scores]
        
        return statistics.mean(scores) if scores else 5.0
    
    def analyze_grammatical_range(self, responses: List[Dict[str, Any]], notes: List[Dict[str, Any]]) -> float:
        """Analyze grammatical range and accuracy from responses"""
        scores = []
        
        for response in responses:
            score = 5.0  # Base score
            text = response.get('text', '')
            
            if not text:
                scores.append(3.0)
                continue
            
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            # Sentence variety
            if len(sentences) > 1:
                score += 0.5  # Multiple sentences show structure variety
            
            # Word count indicates complexity potential
            word_count = response.get('word_count', 0)
            if word_count > 50:
                score += 0.5  # Longer responses suggest complex structures
            elif word_count > 100:
                score += 1.0
            
            # Check for complex sentence indicators
            complex_indicators = ['because', 'although', 'however', 'therefore', 'which', 'that', 'when', 'if']
            complex_count = sum(1 for indicator in complex_indicators if indicator in text.lower())
            
            if complex_count >= 3:
                score += 1.0
            elif complex_count >= 1:
                score += 0.5
            
            scores.append(max(1.0, min(9.0, score)))
        
        return statistics.mean(scores) if scores else 5.0
    
    def analyze_pronunciation(self, responses: List[Dict[str, Any]], notes: List[Dict[str, Any]]) -> float:
        """Analyze pronunciation from responses (basic analysis without audio)"""
        # Note: Full pronunciation analysis requires audio processing
        # This provides baseline scoring that can be enhanced with AI audio analysis
        
        base_score = 6.0  # Assume reasonable pronunciation without audio analysis
        
        # Check evaluation notes for pronunciation issues
        pronunciation_notes = [n for n in notes if n.get('criterion') == 'Pronunciation']
        
        for note in pronunciation_notes:
            note_text = note.get('note', '').lower()
            if 'unclear' in note_text or 'unintelligible' in note_text:
                base_score -= 1.0
            elif 'strain' in note_text or 'effort' in note_text:
                base_score -= 0.5
        
        # Response length can indicate confidence in pronunciation
        total_words = sum(r.get('word_count', 0) for r in responses)
        if total_words > 500:  # Confident speaking suggests better pronunciation
            base_score += 0.5
        elif total_words < 100:  # Very brief may indicate pronunciation concerns
            base_score -= 0.5
        
        return max(3.0, min(8.0, base_score))  # Conservative range without audio
    
    def generate_criterion_feedback(self, criterion: ScoringCriterion, score: float, 
                                  responses: List[Dict[str, Any]], notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate detailed feedback for specific criterion"""
        
        # Determine performance level
        if score >= 7.0:
            level = "high"
        elif score >= 5.5:
            level = "medium"
        else:
            level = "low"
        
        # Get appropriate suggestions
        suggestions = self.improvement_suggestions[criterion][level]
        
        # Get band descriptor
        band_level = int(score) if score == int(score) else int(score)
        descriptor = SPEAKING_BAND_DESCRIPTORS.get(band_level, {}).get(criterion.value, "")
        
        # Analyze specific strengths and weaknesses
        strengths, weaknesses = self.identify_strengths_weaknesses(criterion, responses, notes, score)
        
        return {
            "score": score,
            "level": level.title(),
            "band_descriptor": descriptor,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": suggestions[:3],  # Top 3 suggestions
            "specific_examples": self.get_specific_examples(criterion, responses),
        }
    
    def identify_strengths_weaknesses(self, criterion: ScoringCriterion, responses: List[Dict[str, Any]], 
                                    notes: List[Dict[str, Any]], score: float) -> Tuple[List[str], List[str]]:
        """Identify specific strengths and weaknesses for criterion"""
        
        strengths = []
        weaknesses = []
        
        if criterion == ScoringCriterion.FLUENCY_COHERENCE:
            # Analyze fluency patterns
            avg_length = statistics.mean([r.get('word_count', 0) for r in responses]) if responses else 0
            
            if score >= 6.0:
                if avg_length > 30:
                    strengths.append("Produces extended responses showing willingness to communicate")
                strengths.append("Maintains conversation flow across different topics")
            
            if score < 6.0:
                if avg_length < 15:
                    weaknesses.append("Responses tend to be brief, limiting assessment opportunities")
                # Check notes for specific issues
                fluency_issues = [n.get('note', '') for n in notes if n.get('criterion') == 'Fluency and Coherence']
                for issue in fluency_issues:
                    if 'hesitation' in issue.lower():
                        weaknesses.append("Frequent hesitation affects speech flow")
                    if 'slow' in issue.lower():
                        weaknesses.append("Speech rate slower than natural conversation")
        
        elif criterion == ScoringCriterion.LEXICAL_RESOURCE:
            total_words = sum(r.get('word_count', 0) for r in responses)
            
            if score >= 6.0:
                if total_words > 300:
                    strengths.append("Demonstrates substantial vocabulary range across topics")
                strengths.append("Shows flexibility in expressing ideas with available vocabulary")
            
            if score < 6.0:
                weaknesses.append("Limited vocabulary range restricts expression of complex ideas")
                if total_words < 150:
                    weaknesses.append("Brief responses limit demonstration of lexical resource")
        
        elif criterion == ScoringCriterion.GRAMMATICAL_RANGE:
            if score >= 6.0:
                strengths.append("Uses a mix of simple and complex sentence structures")
                strengths.append("Grammar errors rarely impede communication")
            
            if score < 6.0:
                weaknesses.append("Limited range of grammatical structures")
                weaknesses.append("Frequent grammatical errors may affect clarity")
        
        elif criterion == ScoringCriterion.PRONUNCIATION:
            if score >= 6.0:
                strengths.append("Generally intelligible despite some pronunciation features")
                strengths.append("Pronunciation rarely interferes with understanding")
            
            if score < 6.0:
                weaknesses.append("Pronunciation issues may require listener effort")
                weaknesses.append("Some features of first language affect clarity")
        
        return strengths, weaknesses
    
    def get_specific_examples(self, criterion: ScoringCriterion, responses: List[Dict[str, Any]]) -> List[str]:
        """Get specific examples from user responses for criterion"""
        examples = []
        
        for response in responses[:3]:  # Analyze first 3 responses
            text = response.get('text', '')
            if not text:
                continue
                
            if criterion == ScoringCriterion.FLUENCY_COHERENCE:
                if len(text.split()) > 25:  # Substantial response
                    examples.append(f"Extended response in {response.get('stage', 'conversation')}: \"{text[:100]}{'...' if len(text) > 100 else ''}\"")
            
            elif criterion == ScoringCriterion.LEXICAL_RESOURCE:
                words = text.split()
                if len(set(words)) > len(words) * 0.6:  # Good vocabulary variety
                    examples.append(f"Vocabulary variety demonstrated: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
            
            elif criterion == ScoringCriterion.GRAMMATICAL_RANGE:
                complex_indicators = ['because', 'although', 'however', 'when', 'if', 'which']
                if any(indicator in text.lower() for indicator in complex_indicators):
                    examples.append(f"Complex structure usage: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
        
        return examples[:2]  # Return top 2 examples
    
    def generate_comprehensive_report(self, overall_score: float, criterion_scores: Dict[str, float], 
                                    detailed_feedback: Dict[str, Dict[str, Any]], 
                                    conversation_flow: Dict[str, Any], 
                                    user_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive IELTS assessment report"""
        
        # Performance summary
        performance_level = self.get_performance_level(overall_score)
        
        # Key strengths across all criteria
        all_strengths = []
        all_weaknesses = []
        priority_improvements = []
        
        for criterion, feedback in detailed_feedback.items():
            all_strengths.extend(feedback.get('strengths', []))
            all_weaknesses.extend(feedback.get('weaknesses', []))
            
            # Get priority improvements from lowest scoring criteria
            score = criterion_scores.get(criterion, 5.0)
            if score < overall_score - 0.5:  # Significantly below overall
                priority_improvements.extend(feedback.get('improvement_suggestions', [])[:2])
        
        # Assessment statistics
        total_responses = len(user_responses)
        total_words = sum(r.get('word_count', 0) for r in user_responses)
        avg_response_length = total_words / total_responses if total_responses > 0 else 0
        
        # Next steps recommendation
        next_steps = self.generate_next_steps(overall_score, criterion_scores, priority_improvements)
        
        return {
            "overall_assessment": {
                "band_score": overall_score,
                "performance_level": performance_level,
                "description": self.get_overall_description(overall_score)
            },
            
            "detailed_breakdown": {
                "criterion_scores": criterion_scores,
                "strengths": all_strengths[:5],  # Top 5 strengths
                "areas_for_improvement": all_weaknesses[:5],  # Top 5 areas
            },
            
            "assessment_statistics": {
                "total_responses": total_responses,
                "total_words_spoken": total_words,
                "average_response_length": round(avg_response_length, 1),
                "conversation_completeness": self.assess_completeness(conversation_flow)
            },
            
            "improvement_plan": {
                "priority_areas": priority_improvements[:3],
                "immediate_next_steps": next_steps,
                "practice_recommendations": self.get_practice_recommendations(overall_score)
            },
            
            "assessment_validity": {
                "sufficient_evidence": total_responses >= 10 and total_words >= 200,
                "balanced_assessment": self.check_assessment_balance(conversation_flow),
                "reliability_notes": self.generate_reliability_notes(total_responses, total_words)
            }
        }
    
    def get_performance_level(self, score: float) -> str:
        """Get performance level description"""
        if score >= 8.0:
            return "Very Good User"
        elif score >= 7.0:
            return "Good User"
        elif score >= 6.0:
            return "Competent User"
        elif score >= 5.0:
            return "Modest User"
        elif score >= 4.0:
            return "Limited User"
        else:
            return "Extremely Limited User"
    
    def get_overall_description(self, score: float) -> str:
        """Get overall performance description"""
        descriptions = {
            9.0: "Exceptional command of English with full operational proficiency",
            8.0: "Very good command with only occasional unsystematic inaccuracies", 
            7.0: "Good operational command with occasional inaccuracies in unfamiliar situations",
            6.0: "Generally effective command with some inaccuracies in complex situations",
            5.0: "Partial command with frequent problems, but basic communication in familiar situations",
            4.0: "Limited command with frequent breakdown in communication",
            3.0: "Extremely limited command with frequent breakdown in basic communication"
        }
        
        # Find closest band description
        band_level = round(score)
        return descriptions.get(band_level, "Assessment requires additional evaluation")
    
    def generate_next_steps(self, overall_score: float, criterion_scores: Dict[str, float], 
                          priority_improvements: List[str]) -> List[str]:
        """Generate immediate next steps for improvement"""
        
        next_steps = []
        
        # Find weakest criterion
        weakest_criterion = min(criterion_scores.items(), key=lambda x: x[1])
        criterion_name = weakest_criterion[0]
        criterion_score = weakest_criterion[1]
        
        next_steps.append(f"Focus on {criterion_name} - your weakest area (Band {criterion_score})")
        
        # Add specific immediate actions
        if overall_score < 6.0:
            next_steps.extend([
                "Practice daily speaking on familiar topics for 15-20 minutes",
                "Record yourself and identify specific areas needing improvement",
                "Work with English speaking practice materials or conversation partners"
            ])
        elif overall_score < 7.0:
            next_steps.extend([
                "Focus on complex topics and abstract discussions",
                "Practice using advanced vocabulary and complex sentence structures",
                "Work on maintaining fluency when discussing unfamiliar topics"
            ])
        else:
            next_steps.extend([
                "Fine-tune pronunciation for subtle meaning distinctions", 
                "Practice sophisticated vocabulary in academic/professional contexts",
                "Work on perfect accuracy in complex grammatical structures"
            ])
        
        return next_steps[:4]  # Top 4 next steps
    
    def get_practice_recommendations(self, overall_score: float) -> List[str]:
        """Get practice recommendations based on overall score"""
        
        if overall_score < 5.0:
            return [
                "Daily conversation practice with basic topics",
                "Vocabulary building with common words and phrases",
                "Pronunciation practice with individual sounds and word stress",
                "Basic grammar exercises focusing on sentence structure"
            ]
        elif overall_score < 6.5:
            return [
                "Extended speaking practice on IELTS topics",
                "Vocabulary expansion with academic and formal language",
                "Complex sentence structure practice", 
                "Pronunciation refinement for clarity and natural rhythm"
            ]
        else:
            return [
                "Advanced discussion on abstract and complex topics",
                "Sophisticated vocabulary and idiomatic expression practice",
                "Precision in grammatical accuracy and flexibility",
                "Fine-tuning pronunciation for subtle meaning conveyance"
            ]
    
    def assess_completeness(self, conversation_flow: Dict[str, Any]) -> str:
        """Assess completeness of conversation"""
        part1_responses = conversation_flow.get('part1_responses', 0)
        part2_responses = conversation_flow.get('part2_responses', 0)
        part3_responses = conversation_flow.get('part3_responses', 0)
        
        if part1_responses >= 4 and part2_responses >= 1 and part3_responses >= 3:
            return "Complete - All parts adequately covered"
        elif part1_responses >= 2 and (part2_responses >= 1 or part3_responses >= 2):
            return "Mostly Complete - Sufficient evidence for evaluation"
        else:
            return "Incomplete - Additional assessment recommended"
    
    def check_assessment_balance(self, conversation_flow: Dict[str, Any]) -> bool:
        """Check if assessment covered all parts appropriately"""
        part1 = conversation_flow.get('part1_responses', 0)
        part2 = conversation_flow.get('part2_responses', 0) 
        part3 = conversation_flow.get('part3_responses', 0)
        
        return part1 >= 2 and part2 >= 1 and part3 >= 2
    
    def generate_reliability_notes(self, total_responses: int, total_words: int) -> List[str]:
        """Generate reliability notes for assessment"""
        notes = []
        
        if total_responses < 8:
            notes.append("Limited number of responses - consider additional assessment")
        if total_words < 150:
            notes.append("Brief responses limit comprehensive evaluation")
        if total_responses >= 12 and total_words >= 400:
            notes.append("Sufficient evidence for reliable band score assessment")
        
        return notes

# Global instance
_band_scorer = None

def get_band_scorer() -> IELTSBandScorer:
    """Get global IELTS band scorer instance"""
    global _band_scorer
    if _band_scorer is None:
        _band_scorer = IELTSBandScorer()
    return _band_scorer

# Export
__all__ = [
    'IELTSBandScorer',
    'ScoringCriterion',
    'BandLevel',
    'get_band_scorer'
]