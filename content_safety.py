"""
AWS Content Safety Integration for IELTS GenAI Prep
Google Play GenAI Policy Compliance Implementation

This module implements content safety filters and validation for AI-generated content
in accordance with Google Play's GenAI developer policies and AWS responsible AI practices.
"""

import json
import re
import boto3
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

# Configure logging for safety monitoring
logging.basicConfig(level=logging.INFO)
safety_logger = logging.getLogger('content_safety')

class ContentSafetyFilter:
    """
    Comprehensive content safety filter implementing Google Play GenAI policy requirements
    Uses AWS services and industry-standard content moderation techniques
    """
    
    def __init__(self):
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')
        self.translate = boto3.client('translate', region_name='us-east-1')
        
        # Educational context keywords that are acceptable
        self.educational_keywords = {
            'ielts', 'test', 'assessment', 'writing', 'speaking', 'academic', 'general',
            'band', 'score', 'criteria', 'task', 'achievement', 'coherence', 'cohesion',
            'lexical', 'resource', 'grammar', 'accuracy', 'fluency', 'pronunciation',
            'education', 'learning', 'preparation', 'practice', 'examination'
        }
        
        # Content safety patterns for IELTS assessment context
        self.inappropriate_patterns = [
            r'\b(hate|violence|discrimination|harassment)\b',
            r'\b(explicit|sexual|adult)\b',
            r'\b(illegal|criminal|harmful)\b',
            r'\b(scam|fraud|deceptive)\b',
            r'\b(self-harm|suicide|dangerous)\b'
        ]
        
        # Initialize safety metrics tracking
        self.safety_metrics = {
            'total_requests': 0,
            'blocked_requests': 0,
            'flagged_content': 0,
            'educational_content': 0,
            'last_updated': datetime.now().isoformat()
        }
    
    def validate_user_input(self, user_input: str, context: str = "assessment") -> Tuple[bool, str, Dict]:
        """
        Validate user input for safety and appropriateness in IELTS assessment context
        
        Args:
            user_input: User-provided text (speaking response, writing submission, etc.)
            context: Assessment context (writing, speaking, general)
            
        Returns:
            Tuple of (is_safe: bool, sanitized_input: str, safety_report: dict)
        """
        self.safety_metrics['total_requests'] += 1
        
        safety_report = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'original_length': len(user_input),
            'safety_checks': []
        }
        
        # 1. Basic content filtering
        is_safe, violation_type = self._check_inappropriate_content(user_input)
        safety_report['safety_checks'].append({
            'check': 'inappropriate_content',
            'passed': is_safe,
            'violation_type': violation_type
        })
        
        if not is_safe:
            self.safety_metrics['blocked_requests'] += 1
            safety_logger.warning(f"Blocked inappropriate content: {violation_type}")
            return False, "", safety_report
        
        # 2. AWS Comprehend sentiment analysis
        try:
            sentiment_result = self.comprehend.detect_sentiment(
                Text=user_input[:5000],  # AWS limit
                LanguageCode='en'
            )
            
            safety_report['safety_checks'].append({
                'check': 'sentiment_analysis',
                'passed': True,
                'sentiment': sentiment_result['Sentiment'],
                'confidence': sentiment_result['SentimentScore']
            })
            
            # Flag extremely negative sentiment for review
            if sentiment_result['Sentiment'] == 'NEGATIVE' and \
               sentiment_result['SentimentScore']['Negative'] > 0.9:
                self.safety_metrics['flagged_content'] += 1
                safety_logger.info(f"Flagged highly negative content for review")
                
        except Exception as e:
            safety_logger.error(f"Sentiment analysis failed: {e}")
            safety_report['safety_checks'].append({
                'check': 'sentiment_analysis',
                'passed': False,
                'error': str(e)
            })
        
        # 3. Educational content validation
        is_educational = self._validate_educational_context(user_input)
        safety_report['safety_checks'].append({
            'check': 'educational_context',
            'passed': is_educational,
            'educational_score': self._calculate_educational_score(user_input)
        })
        
        if is_educational:
            self.safety_metrics['educational_content'] += 1
        
        # 4. Length and format validation for assessment context
        sanitized_input = self._sanitize_assessment_input(user_input, context)
        safety_report['sanitized_length'] = len(sanitized_input)
        
        safety_logger.info(f"Content safety validation completed: {context}")
        return True, sanitized_input, safety_report
    
    def validate_ai_output(self, ai_output: str, assessment_type: str) -> Tuple[bool, str, Dict]:
        """
        Validate AI-generated content (Maya responses, Nova Micro feedback) for safety
        
        Args:
            ai_output: AI-generated response or feedback
            assessment_type: Type of assessment (writing, speaking, maya_conversation)
            
        Returns:
            Tuple of (is_safe: bool, sanitized_output: str, safety_report: dict)
        """
        safety_report = {
            'timestamp': datetime.now().isoformat(),
            'assessment_type': assessment_type,
            'ai_output_length': len(ai_output),
            'safety_checks': []
        }
        
        # 1. Check for inappropriate AI responses
        is_safe, violation_type = self._check_inappropriate_content(ai_output)
        safety_report['safety_checks'].append({
            'check': 'ai_output_appropriateness',
            'passed': is_safe,
            'violation_type': violation_type
        })
        
        if not is_safe:
            self.safety_metrics['blocked_requests'] += 1
            safety_logger.warning(f"Blocked inappropriate AI output: {violation_type}")
            return False, self._get_safe_fallback_response(assessment_type), safety_report
        
        # 2. Validate educational appropriateness
        is_educational = self._validate_educational_ai_output(ai_output, assessment_type)
        safety_report['safety_checks'].append({
            'check': 'educational_appropriateness',
            'passed': is_educational
        })
        
        # 3. Ensure assessment-specific format compliance
        sanitized_output = self._sanitize_ai_output(ai_output, assessment_type)
        safety_report['sanitized_length'] = len(sanitized_output)
        
        safety_logger.info(f"AI output validation completed: {assessment_type}")
        return True, sanitized_output, safety_report
    
    def _check_inappropriate_content(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check for inappropriate content using pattern matching"""
        text_lower = text.lower()
        
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, text_lower):
                return False, f"Pattern violation: {pattern}"
        
        return True, None
    
    def _validate_educational_context(self, text: str) -> bool:
        """Validate that content is appropriate for educational assessment"""
        text_lower = text.lower()
        educational_matches = sum(1 for keyword in self.educational_keywords if keyword in text_lower)
        
        # Content should have some educational context or be assessment-related
        return educational_matches > 0 or len(text) < 100  # Short responses are generally safe
    
    def _calculate_educational_score(self, text: str) -> float:
        """Calculate educational relevance score"""
        text_lower = text.lower()
        matches = sum(1 for keyword in self.educational_keywords if keyword in text_lower)
        return min(matches / 5.0, 1.0)  # Normalize to 0-1 scale
    
    def _sanitize_assessment_input(self, text: str, context: str) -> str:
        """Sanitize user input for assessment context"""
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', text.strip())
        
        # Limit length based on assessment type
        max_lengths = {
            'writing': 5000,
            'speaking': 2000,
            'general': 1000
        }
        
        max_length = max_lengths.get(context, 1000)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized
    
    def _sanitize_ai_output(self, text: str, assessment_type: str) -> str:
        """Sanitize AI output for safety and appropriateness"""
        # Ensure proper formatting for assessment feedback
        sanitized = text.strip()
        
        # Add educational context if missing
        if assessment_type in ['writing', 'speaking'] and 'assessment' not in sanitized.lower():
            sanitized = f"Assessment feedback: {sanitized}"
        
        return sanitized
    
    def _validate_educational_ai_output(self, text: str, assessment_type: str) -> bool:
        """Validate AI output is educational and assessment-appropriate"""
        text_lower = text.lower()
        
        # Check for assessment-specific keywords
        assessment_keywords = {
            'writing': ['task', 'achievement', 'coherence', 'lexical', 'grammar', 'band'],
            'speaking': ['fluency', 'pronunciation', 'vocabulary', 'grammar', 'part'],
            'maya_conversation': ['part', 'question', 'response', 'continue', 'next']
        }
        
        required_keywords = assessment_keywords.get(assessment_type, [])
        matches = sum(1 for keyword in required_keywords if keyword in text_lower)
        
        return matches > 0 or 'assessment' in text_lower
    
    def _get_safe_fallback_response(self, assessment_type: str) -> str:
        """Provide safe fallback response when content is blocked"""
        fallback_responses = {
            'writing': "I apologize, but I cannot provide feedback on that content. Please ensure your writing relates to the IELTS assessment task.",
            'speaking': "I apologize, but I cannot process that response. Please provide content relevant to the IELTS speaking assessment.",
            'maya_conversation': "I apologize, but I need to keep our conversation focused on the IELTS speaking assessment. Let's continue with the next question."
        }
        
        return fallback_responses.get(assessment_type, "I apologize, but I cannot process that content. Please try again with assessment-related content.")
    
    def get_safety_metrics(self) -> Dict:
        """Get current safety metrics for monitoring and compliance"""
        self.safety_metrics['last_updated'] = datetime.now().isoformat()
        return self.safety_metrics.copy()
    
    def log_safety_incident(self, incident_type: str, details: Dict):
        """Log safety incidents for compliance monitoring"""
        incident_report = {
            'timestamp': datetime.now().isoformat(),
            'incident_type': incident_type,
            'details': details,
            'metrics_snapshot': self.get_safety_metrics()
        }
        
        safety_logger.warning(f"Safety incident logged: {incident_type}")
        
        # In production, this would be sent to AWS CloudWatch or similar monitoring system
        return incident_report

# Global content safety filter instance
content_safety = ContentSafetyFilter()

def validate_user_input_safe(user_input: str, context: str = "assessment") -> Tuple[bool, str, Dict]:
    """Global function for user input validation"""
    return content_safety.validate_user_input(user_input, context)

def validate_ai_output_safe(ai_output: str, assessment_type: str) -> Tuple[bool, str, Dict]:
    """Global function for AI output validation"""
    return content_safety.validate_ai_output(ai_output, assessment_type)

def get_safety_metrics() -> Dict:
    """Get current safety metrics"""
    return content_safety.get_safety_metrics()