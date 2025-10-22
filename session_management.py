"""
Section-Timed Session Management for IELTS GenAI Prep
Implements assessment-specific timing with auto-advance functionality
"""
import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from flask import session, g
from dynamodb_dal import get_dal
from assessment_encryption import get_assessment_encryption

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Assessment session status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class SectionStatus(Enum):
    """Individual section status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    SKIPPED = "skipped"

@dataclass
class AssessmentSection:
    """Assessment section configuration"""
    section_id: str
    name: str
    duration_minutes: int
    instructions: str
    auto_advance: bool = True
    allow_return: bool = False
    required: bool = True

@dataclass
class SessionTimer:
    """Session timing information"""
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    paused_duration: int = 0  # seconds
    time_remaining: int = 0  # seconds
    auto_advance_at: Optional[datetime] = None

@dataclass
class SessionState:
    """Complete session state"""
    session_id: str
    user_id: str
    assessment_type: str
    status: SessionStatus
    current_section: Optional[str] = None
    section_progress: Dict[str, SectionStatus] = None
    timers: Dict[str, SessionTimer] = None
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Assessment section configurations
ASSESSMENT_SECTIONS = {
    'academic_writing': [
        AssessmentSection(
            section_id='task1',
            name='Academic Writing Task 1',
            duration_minutes=20,
            instructions='Describe the information shown in the diagram, graph, or chart.',
            auto_advance=True,
            allow_return=False,
            required=True
        ),
        AssessmentSection(
            section_id='task2',
            name='Academic Writing Task 2',
            duration_minutes=40,
            instructions='Write an essay in response to the given argument or problem.',
            auto_advance=True,
            allow_return=False,
            required=True
        )
    ],
    
    'general_writing': [
        AssessmentSection(
            section_id='task1',
            name='General Writing Task 1',
            duration_minutes=20,
            instructions='Write a letter in response to the given situation.',
            auto_advance=True,
            allow_return=False,
            required=True
        ),
        AssessmentSection(
            section_id='task2',
            name='General Writing Task 2',
            duration_minutes=40,
            instructions='Write an essay in response to the given topic.',
            auto_advance=True,
            allow_return=False,
            required=True
        )
    ],
    
    'academic_speaking': [
        AssessmentSection(
            section_id='introduction',
            name='Introduction and Interview',
            duration_minutes=5,
            instructions='Introduce yourself and answer questions about familiar topics.',
            auto_advance=True,
            allow_return=False,
            required=True
        ),
        AssessmentSection(
            section_id='long_turn',
            name='Individual Long Turn',
            duration_minutes=4,
            instructions='Speak about the given topic for 2 minutes after 1 minute preparation.',
            auto_advance=True,
            allow_return=False,
            required=True
        ),
        AssessmentSection(
            section_id='discussion',
            name='Two-way Discussion',
            duration_minutes=5,
            instructions='Discuss abstract ideas related to the Part 2 topic.',
            auto_advance=True,
            allow_return=False,
            required=True
        )
    ],
    
    'general_speaking': [
        AssessmentSection(
            section_id='introduction',
            name='Introduction and Interview',
            duration_minutes=5,
            instructions='Introduce yourself and answer questions about familiar topics.',
            auto_advance=True,
            allow_return=False,
            required=True
        ),
        AssessmentSection(
            section_id='long_turn',
            name='Individual Long Turn',
            duration_minutes=4,
            instructions='Speak about the given topic for 2 minutes after 1 minute preparation.',
            auto_advance=True,
            allow_return=False,
            required=True
        ),
        AssessmentSection(
            section_id='discussion',
            name='Two-way Discussion',
            duration_minutes=5,
            instructions='Discuss abstract ideas related to the Part 2 topic.',
            auto_advance=True,
            allow_return=False,
            required=True
        )
    ]
}

class AssessmentSessionManager:
    """Manages assessment sessions with section-based timing"""
    
    def __init__(self):
        self.dal = get_dal()
        self.encryption = get_assessment_encryption()
    
    def create_session(self, user_id: str, assessment_type: str, 
                      entitlement_id: str = None) -> Optional[SessionState]:
        """
        Create a new assessment session
        
        Args:
            user_id: User ID
            assessment_type: Type of assessment
            entitlement_id: Entitlement ID for verification
            
        Returns:
            SessionState or None if creation failed
        """
        try:
            # Validate assessment type
            if assessment_type not in ASSESSMENT_SECTIONS:
                logger.error(f"Invalid assessment type: {assessment_type}")
                return None
            
            # Verify user entitlement
            if entitlement_id and not self._verify_entitlement(user_id, assessment_type, entitlement_id):
                logger.warning(f"Entitlement verification failed for user: {user_id}")
                return None
            
            # Generate session ID
            session_id = self._generate_session_id(user_id, assessment_type)
            
            # Get sections for this assessment
            sections = ASSESSMENT_SECTIONS[assessment_type]
            
            # Initialize section progress and timers
            section_progress = {section.section_id: SectionStatus.NOT_STARTED for section in sections}
            timers = {}
            
            for section in sections:
                timers[section.section_id] = SessionTimer(
                    time_remaining=section.duration_minutes * 60
                )
            
            # Create session state
            session_state = SessionState(
                session_id=session_id,
                user_id=user_id,
                assessment_type=assessment_type,
                status=SessionStatus.NOT_STARTED,
                current_section=None,
                section_progress=section_progress,
                timers=timers,
                metadata={
                    'entitlement_id': entitlement_id,
                    'sections': [{'id': s.section_id, 'name': s.name, 'duration': s.duration_minutes} for s in sections],
                    'total_duration': sum(s.duration_minutes for s in sections),
                    'created_by': 'session_manager_v1.0'
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in DynamoDB
            if self._store_session_state(session_state):
                logger.info(f"Created assessment session: {session_id}")
                return session_state
            else:
                logger.error(f"Failed to store session: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return None
    
    def start_session(self, session_id: str, user_id: str) -> bool:
        """
        Start an assessment session
        
        Args:
            session_id: Session ID
            user_id: User ID for verification
            
        Returns:
            True if started successfully
        """
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state:
                return False
            
            if session_state.status != SessionStatus.NOT_STARTED:
                logger.warning(f"Session {session_id} already started or completed")
                return False
            
            # Start the session
            session_state.status = SessionStatus.IN_PROGRESS
            session_state.updated_at = datetime.utcnow()
            
            # Start first section
            sections = ASSESSMENT_SECTIONS[session_state.assessment_type]
            first_section = sections[0]
            
            success = self.start_section(session_id, user_id, first_section.section_id)
            
            logger.info(f"Started assessment session: {session_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to start session {session_id}: {e}")
            return False
    
    def start_section(self, session_id: str, user_id: str, section_id: str) -> bool:
        """
        Start a specific section
        
        Args:
            session_id: Session ID
            user_id: User ID
            section_id: Section to start
            
        Returns:
            True if started successfully
        """
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state:
                return False
            
            # Validate section
            sections = ASSESSMENT_SECTIONS[session_state.assessment_type]
            section_config = next((s for s in sections if s.section_id == section_id), None)
            
            if not section_config:
                logger.error(f"Invalid section ID: {section_id}")
                return False
            
            # Check if section can be started
            if session_state.section_progress[section_id] != SectionStatus.NOT_STARTED:
                logger.warning(f"Section {section_id} already started or completed")
                return session_state.section_progress[section_id] == SectionStatus.IN_PROGRESS
            
            # Start the section
            now = datetime.utcnow()
            session_state.current_section = section_id
            session_state.section_progress[section_id] = SectionStatus.IN_PROGRESS
            
            # Initialize timer
            timer = session_state.timers[section_id]
            timer.started_at = now
            timer.expires_at = now + timedelta(minutes=section_config.duration_minutes)
            
            if section_config.auto_advance:
                timer.auto_advance_at = timer.expires_at
            
            session_state.updated_at = now
            
            # Store updated state
            success = self._store_session_state(session_state)
            
            if success:
                logger.info(f"Started section {section_id} in session {session_id}")
                
                # Set up auto-advance if enabled
                if section_config.auto_advance:
                    self._schedule_auto_advance(session_id, section_id, timer.expires_at)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to start section {section_id}: {e}")
            return False
    
    def complete_section(self, session_id: str, user_id: str, section_id: str) -> bool:
        """
        Complete a section and advance to next
        
        Args:
            session_id: Session ID
            user_id: User ID
            section_id: Section to complete
            
        Returns:
            True if completed successfully
        """
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state:
                return False
            
            # Validate section is in progress
            if session_state.section_progress[section_id] != SectionStatus.IN_PROGRESS:
                logger.warning(f"Section {section_id} not in progress")
                return False
            
            # Complete the section
            session_state.section_progress[section_id] = SectionStatus.COMPLETED
            timer = session_state.timers[section_id]
            
            if timer.started_at:
                elapsed = (datetime.utcnow() - timer.started_at).total_seconds()
                timer.time_remaining = max(0, timer.time_remaining - elapsed)
            
            # Find next section
            sections = ASSESSMENT_SECTIONS[session_state.assessment_type]
            current_index = next(i for i, s in enumerate(sections) if s.section_id == section_id)
            
            if current_index < len(sections) - 1:
                # Start next section
                next_section = sections[current_index + 1]
                session_state.current_section = next_section.section_id
                self.start_section(session_id, user_id, next_section.section_id)
            else:
                # All sections completed
                session_state.current_section = None
                session_state.status = SessionStatus.COMPLETED
            
            session_state.updated_at = datetime.utcnow()
            
            success = self._store_session_state(session_state)
            
            if success:
                logger.info(f"Completed section {section_id} in session {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to complete section {section_id}: {e}")
            return False
    
    def get_session_state(self, session_id: str, user_id: str) -> Optional[SessionState]:
        """Get current session state"""
        return self._load_session_state(session_id, user_id)
    
    def get_time_remaining(self, session_id: str, user_id: str, 
                          section_id: str = None) -> Optional[int]:
        """
        Get time remaining for session or specific section
        
        Args:
            session_id: Session ID
            user_id: User ID
            section_id: Optional section ID (current section if not provided)
            
        Returns:
            Seconds remaining or None if error
        """
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state:
                return None
            
            target_section = section_id or session_state.current_section
            if not target_section:
                return None
            
            timer = session_state.timers.get(target_section)
            if not timer or not timer.started_at:
                return timer.time_remaining if timer else None
            
            # Calculate real-time remaining
            elapsed = (datetime.utcnow() - timer.started_at).total_seconds()
            elapsed -= timer.paused_duration
            
            remaining = max(0, timer.time_remaining - elapsed)
            
            # Auto-advance if time expired
            if remaining == 0 and session_state.section_progress[target_section] == SectionStatus.IN_PROGRESS:
                self._auto_advance_section(session_id, user_id, target_section)
            
            return int(remaining)
            
        except Exception as e:
            logger.error(f"Failed to get time remaining: {e}")
            return None
    
    def pause_session(self, session_id: str, user_id: str) -> bool:
        """Pause the current session"""
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state or session_state.status != SessionStatus.IN_PROGRESS:
                return False
            
            session_state.status = SessionStatus.PAUSED
            
            # Pause current section timer
            if session_state.current_section:
                timer = session_state.timers[session_state.current_section]
                timer.paused_at = datetime.utcnow()
            
            session_state.updated_at = datetime.utcnow()
            
            return self._store_session_state(session_state)
            
        except Exception as e:
            logger.error(f"Failed to pause session: {e}")
            return False
    
    def resume_session(self, session_id: str, user_id: str) -> bool:
        """Resume a paused session"""
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state or session_state.status != SessionStatus.PAUSED:
                return False
            
            session_state.status = SessionStatus.IN_PROGRESS
            
            # Resume current section timer
            if session_state.current_section:
                timer = session_state.timers[session_state.current_section]
                if timer.paused_at:
                    pause_duration = (datetime.utcnow() - timer.paused_at).total_seconds()
                    timer.paused_duration += pause_duration
                    timer.paused_at = None
            
            session_state.updated_at = datetime.utcnow()
            
            return self._store_session_state(session_state)
            
        except Exception as e:
            logger.error(f"Failed to resume session: {e}")
            return False
    
    def _auto_advance_section(self, session_id: str, user_id: str, section_id: str):
        """Auto-advance when section time expires"""
        try:
            session_state = self._load_session_state(session_id, user_id)
            if not session_state:
                return
            
            # Mark section as expired and advance
            session_state.section_progress[section_id] = SectionStatus.EXPIRED
            
            logger.info(f"Auto-advancing from expired section {section_id}")
            
            self.complete_section(session_id, user_id, section_id)
            
        except Exception as e:
            logger.error(f"Auto-advance failed: {e}")
    
    def _schedule_auto_advance(self, session_id: str, section_id: str, advance_time: datetime):
        """Schedule auto-advance (implementation depends on job scheduler)"""
        # In a real implementation, this would use AWS Lambda scheduled events
        # or a job queue like Celery for auto-advance functionality
        logger.info(f"Scheduled auto-advance for {session_id}/{section_id} at {advance_time}")
    
    def _generate_session_id(self, user_id: str, assessment_type: str) -> str:
        """Generate unique session ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"session_{assessment_type}_{user_id}_{timestamp}"
    
    def _verify_entitlement(self, user_id: str, assessment_type: str, entitlement_id: str) -> bool:
        """Verify user has valid entitlement for assessment"""
        try:
            # Implementation would check entitlements table
            logger.info(f"Verifying entitlement {entitlement_id} for user {user_id}")
            return True  # Simplified for now
        except Exception as e:
            logger.error(f"Entitlement verification failed: {e}")
            return False
    
    def _store_session_state(self, session_state: SessionState) -> bool:
        """Store session state in DynamoDB"""
        try:
            # Convert to dict for storage
            state_dict = {
                'session_id': session_state.session_id,
                'user_id': session_state.user_id,
                'assessment_type': session_state.assessment_type,
                'status': session_state.status.value,
                'current_section': session_state.current_section,
                'section_progress': {k: v.value for k, v in session_state.section_progress.items()},
                'timers': {
                    k: {
                        'started_at': v.started_at.isoformat() if v.started_at else None,
                        'expires_at': v.expires_at.isoformat() if v.expires_at else None,
                        'paused_at': v.paused_at.isoformat() if v.paused_at else None,
                        'paused_duration': v.paused_duration,
                        'time_remaining': v.time_remaining,
                        'auto_advance_at': v.auto_advance_at.isoformat() if v.auto_advance_at else None
                    } for k, v in session_state.timers.items()
                },
                'metadata': session_state.metadata,
                'created_at': session_state.created_at.isoformat(),
                'updated_at': session_state.updated_at.isoformat()
            }
            
            # Encrypt sensitive data
            encrypted_state = self.encryption.encrypt_assessment_metadata(
                state_dict, session_state.user_id, session_state.session_id
            )
            
            if encrypted_state.success:
                # Store in DynamoDB (implementation would go here)
                logger.info(f"Stored session state: {session_state.session_id}")
                return True
            else:
                logger.error(f"Failed to encrypt session state: {encrypted_state.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to store session state: {e}")
            return False
    
    def _load_session_state(self, session_id: str, user_id: str) -> Optional[SessionState]:
        """Load session state from DynamoDB"""
        try:
            # Load from DynamoDB and decrypt (implementation would go here)
            # For now, return a mock state for development
            logger.info(f"Loading session state: {session_id}")
            return None  # Simplified for now
            
        except Exception as e:
            logger.error(f"Failed to load session state: {e}")
            return None

# Global session manager instance
session_manager = None

def get_session_manager() -> AssessmentSessionManager:
    """Get global session manager instance"""
    global session_manager
    if session_manager is None:
        session_manager = AssessmentSessionManager()
    return session_manager

def create_assessment_session(user_id: str, assessment_type: str, 
                            entitlement_id: str = None) -> Optional[SessionState]:
    """Convenience function to create assessment session"""
    return get_session_manager().create_session(user_id, assessment_type, entitlement_id)

def get_session_time_remaining(session_id: str, user_id: str, 
                             section_id: str = None) -> Optional[int]:
    """Convenience function to get time remaining"""
    return get_session_manager().get_time_remaining(session_id, user_id, section_id)