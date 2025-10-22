"""
Conversation Data Retention System
Manages cleanup of conversation data after assessment completion while preserving
scores and feedback in user profiles for 1 year as required by data storage policies
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from question_bank_dal import get_question_bank_dal

logger = logging.getLogger(__name__)

class ConversationDataRetentionManager:
    """Manages conversation data cleanup and user profile storage"""
    
    def __init__(self):
        self.question_dal = get_question_bank_dal()
        
    def cleanup_after_assessment_completion(
        self, 
        session_id: str, 
        user_email: str, 
        assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Clean up conversation data after assessment completion
        Preserves only score and feedback in user profile for 1 year
        
        Args:
            session_id: Assessment session ID
            user_email: User's email address
            assessment_data: Complete assessment data including conversation history
            
        Returns:
            Dict with cleanup results
        """
        try:
            logger.info(f"Starting data retention cleanup for session {session_id}")
            
            # Extract what to preserve (score and feedback only)
            preserved_data = self._extract_preserved_data(assessment_data)
            
            # Store preserved data in user profile with 1-year expiration
            profile_result = self._store_in_user_profile(
                user_email, 
                session_id, 
                preserved_data
            )
            
            if not profile_result['success']:
                logger.error(f"Failed to store preserved data in profile: {profile_result.get('error')}")
                return {
                    'success': False,
                    'error': 'Failed to preserve assessment data in user profile'
                }
            
            # Clean up conversation data from Maya engine
            cleanup_result = self._cleanup_conversation_data(session_id)
            
            if not cleanup_result['success']:
                logger.warning(f"Conversation cleanup had issues: {cleanup_result.get('error')}")
            
            # Remove detailed conversation data from session storage
            session_cleanup = self._cleanup_session_conversation_data(session_id)
            
            logger.info(f"Data retention cleanup completed for session {session_id}")
            logger.info(f"Preserved: Score and feedback stored in user profile for 1 year")
            logger.info(f"Deleted: All conversation history and audio data")
            
            return {
                'success': True,
                'message': 'Conversation data cleaned up successfully',
                'preserved_data_location': 'user_profile',
                'retention_period': '1_year',
                'cleanup_details': {
                    'conversation_data_removed': cleanup_result['success'],
                    'session_data_cleaned': session_cleanup['success'],
                    'profile_data_stored': profile_result['success']
                }
            }
            
        except Exception as e:
            logger.error(f"Data retention cleanup error for session {session_id}: {e}")
            return {
                'success': False,
                'error': f'Cleanup failed: {str(e)}'
            }
    
    def _extract_preserved_data(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only score and feedback data to preserve"""
        preserved = {
            'assessment_date': datetime.utcnow().isoformat(),
            'overall_band_score': assessment_data.get('overall_band_score'),
            'criterion_scores': assessment_data.get('criterion_scores', {}),
            'feedback_summary': assessment_data.get('feedback_summary', ''),
            'assessment_type': assessment_data.get('assessment_type'),
            'session_id': assessment_data.get('session_id'),
            'expiry_date': (datetime.utcnow() + timedelta(days=365)).isoformat()
        }
        
        # Remove any conversation history or personal conversation data
        # Only keep the scoring and structured feedback
        if 'detailed_feedback' in assessment_data:
            feedback = assessment_data['detailed_feedback']
            # Keep only structured feedback, not conversation excerpts
            preserved['structured_feedback'] = {
                'fluency_feedback': feedback.get('fluency_feedback', ''),
                'lexical_feedback': feedback.get('lexical_feedback', ''),
                'grammatical_feedback': feedback.get('grammatical_feedback', ''),
                'pronunciation_feedback': feedback.get('pronunciation_feedback', '')
            }
        
        return preserved
    
    def _store_in_user_profile(
        self, 
        user_email: str, 
        session_id: str, 
        preserved_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store preserved assessment data in user profile with 1-year retention"""
        try:
            # Get or create user profile
            profile_result = self.question_dal.get_user_profile(user_email)
            
            if not profile_result.get('success'):
                # Create new profile if doesn't exist
                profile_data = {
                    'user_email': user_email,
                    'assessment_history': [],
                    'created_date': datetime.utcnow().isoformat(),
                    'last_updated': datetime.utcnow().isoformat()
                }
            else:
                profile_data = profile_result['profile']
                if 'assessment_history' not in profile_data:
                    profile_data['assessment_history'] = []
            
            # Add preserved assessment data
            assessment_record = {
                'session_id': session_id,
                'stored_date': datetime.utcnow().isoformat(),
                'expiry_date': preserved_data['expiry_date'],
                **preserved_data
            }
            
            profile_data['assessment_history'].append(assessment_record)
            profile_data['last_updated'] = datetime.utcnow().isoformat()
            
            # Clean up expired records (older than 1 year)
            self._cleanup_expired_profile_data(profile_data)
            
            # Store updated profile
            store_result = self.question_dal.store_user_profile(user_email, profile_data)
            
            if store_result.get('success'):
                logger.info(f"Assessment data preserved in user profile for {user_email}")
                return {
                    'success': True,
                    'message': 'Assessment data stored in user profile for 1 year'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store profile data'
                }
                
        except Exception as e:
            logger.error(f"Error storing preserved data in profile: {e}")
            return {
                'success': False,
                'error': f'Profile storage failed: {str(e)}'
            }
    
    def _cleanup_conversation_data(self, session_id: str) -> Dict[str, Any]:
        """Clean up conversation data from Maya engine"""
        try:
            from maya_conversation_engine import get_maya_engine
            
            maya_engine = get_maya_engine()
            
            # Clear conversation state if session exists
            if hasattr(maya_engine, 'conversation_state'):
                if maya_engine.conversation_state.get('session_id') == session_id:
                    # Keep only essential non-conversation data
                    maya_engine.conversation_state = {
                        'session_id': None,
                        'stage': None,
                        'conversation_history': [],  # Clear all conversation history
                        'user_context': {},  # Clear user context data
                        'current_topics': [],  # Clear topics discussed
                        'evaluation_notes': []  # Clear evaluation notes
                    }
            
            logger.info(f"Maya conversation data cleared for session {session_id}")
            return {
                'success': True,
                'message': 'Maya conversation data cleared'
            }
            
        except Exception as e:
            logger.warning(f"Maya conversation cleanup warning: {e}")
            return {
                'success': False,
                'error': f'Maya cleanup failed: {str(e)}'
            }
    
    def _cleanup_session_conversation_data(self, session_id: str) -> Dict[str, Any]:
        """Remove conversation data from session storage"""
        try:
            # Get session data
            session_result = self.question_dal.get_assessment_session(session_id)
            
            if session_result.get('success'):
                session_data = session_result['session']
                
                # Remove conversation-related data while keeping assessment structure
                conversation_keys_to_remove = [
                    'conversation_history',
                    'audio_recordings',
                    'transcript_data',
                    'user_responses',
                    'maya_responses',
                    'conversation_context',
                    'speech_analysis',
                    'detailed_conversation_log'
                ]
                
                for key in conversation_keys_to_remove:
                    if key in session_data:
                        del session_data[key]
                
                # Mark as data-cleaned and preserve only completion status
                session_data['conversation_data_cleaned'] = True
                session_data['data_cleanup_date'] = datetime.utcnow().isoformat()
                session_data['retention_policy_applied'] = True
                
                # Update session without conversation data
                update_result = self.question_dal.update_assessment_session(session_id, session_data)
                
                if update_result.get('success'):
                    logger.info(f"Session conversation data cleaned for {session_id}")
                    return {
                        'success': True,
                        'message': 'Session conversation data removed'
                    }
            
            return {
                'success': False,
                'error': 'Session not found or update failed'
            }
            
        except Exception as e:
            logger.warning(f"Session cleanup warning: {e}")
            return {
                'success': False,
                'error': f'Session cleanup failed: {str(e)}'
            }
    
    def _cleanup_expired_profile_data(self, profile_data: Dict[str, Any]):
        """Remove expired assessment records from user profile"""
        if 'assessment_history' not in profile_data:
            return
        
        current_time = datetime.utcnow()
        active_records = []
        
        for record in profile_data['assessment_history']:
            expiry_date_str = record.get('expiry_date')
            if expiry_date_str:
                try:
                    expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
                    if expiry_date > current_time:
                        active_records.append(record)
                    else:
                        logger.info(f"Removed expired assessment record: {record.get('session_id')}")
                except ValueError:
                    # Keep records with invalid dates to be safe
                    active_records.append(record)
            else:
                # Keep records without expiry dates
                active_records.append(record)
        
        profile_data['assessment_history'] = active_records
    
    def get_user_assessment_history(self, user_email: str, limit: int = 10) -> Dict[str, Any]:
        """Get user's preserved assessment history (scores and feedback only)"""
        try:
            profile_result = self.question_dal.get_user_profile(user_email)
            
            if not profile_result.get('success'):
                return {
                    'success': True,
                    'assessment_history': [],
                    'message': 'No assessment history found'
                }
            
            profile_data = profile_result['profile']
            assessment_history = profile_data.get('assessment_history', [])
            
            # Sort by assessment date (most recent first) and limit results
            sorted_history = sorted(
                assessment_history,
                key=lambda x: x.get('assessment_date', ''),
                reverse=True
            )[:limit]
            
            # Remove internal fields from response
            clean_history = []
            for record in sorted_history:
                clean_record = {
                    'session_id': record.get('session_id'),
                    'assessment_date': record.get('assessment_date'),
                    'assessment_type': record.get('assessment_type'),
                    'overall_band_score': record.get('overall_band_score'),
                    'criterion_scores': record.get('criterion_scores', {}),
                    'feedback_summary': record.get('feedback_summary', ''),
                    'structured_feedback': record.get('structured_feedback', {})
                }
                clean_history.append(clean_record)
            
            return {
                'success': True,
                'assessment_history': clean_history,
                'total_assessments': len(clean_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting user assessment history: {e}")
            return {
                'success': False,
                'error': f'Failed to get assessment history: {str(e)}'
            }

# Singleton instance
_retention_manager = None

def get_retention_manager() -> ConversationDataRetentionManager:
    """Get conversation data retention manager instance"""
    global _retention_manager
    if _retention_manager is None:
        _retention_manager = ConversationDataRetentionManager()
    return _retention_manager