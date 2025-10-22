"""
Maya Conversation Engine
Natural speaking triggers and evaluation flow for authentic IELTS examiner experience
"""

import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

from nova_sonic_service import get_nova_sonic_service, NovaSonicService

logger = logging.getLogger(__name__)

class ConversationStage(Enum):
    """Maya conversation stages"""
    INITIAL_GREETING = "initial_greeting"
    IDENTITY_CONFIRMATION = "identity_confirmation" 
    PART1_INTRODUCTION = "part1_introduction"
    PART1_QUESTIONS = "part1_questions"
    PART2_BRIEFING = "part2_briefing"
    PART2_PREPARATION = "part2_preparation"
    PART2_SPEAKING = "part2_speaking"
    PART2_FOLLOWUP = "part2_followup"
    PART3_INTRODUCTION = "part3_introduction"
    PART3_DISCUSSION = "part3_discussion"
    CLOSING = "closing"

class ResponseType(Enum):
    """Maya response types for natural flow"""
    ENCOURAGEMENT = "encouragement"
    CLARIFICATION = "clarification"
    TRANSITION = "transition"
    PROMPT = "prompt"
    FOLLOW_UP = "follow_up"
    TIME_CHECK = "time_check"

class MayaConversationEngine:
    """
    Maya AI Examiner Conversation Engine
    Provides natural, human-like conversation flow and evaluation triggers
    """
    
    def __init__(self):
        # Initialize Nova Sonic service for voice synthesis
        self.nova_sonic = get_nova_sonic_service()
        
        # AI Conversation System - No more pre-written scripts!
        # Maya will generate contextual responses using Nova Sonic's conversational AI
        
        # Time tracking for natural conversation flow
        self.time_limits = {
            ConversationStage.PART1_QUESTIONS: {"per_question": 60, "total": 300},  # 5 minutes total
            ConversationStage.PART2_PREPARATION: {"preparation": 60},  # 1 minute prep
            ConversationStage.PART2_SPEAKING: {"speaking": 120},  # 2 minutes speaking  
            ConversationStage.PART3_DISCUSSION: {"total": 300}  # 5 minutes total
        }
        
        # IELTS conversation structure for AI context
        self.ielts_structure = {
            "part1_topics": ["work/study", "hometown", "family", "hobbies", "daily_routine"],
            "part2_format": "long_turn_monologue_with_topic_card",
            "part3_focus": "abstract_discussion_related_to_part2"
        }
        
        # Enhanced conversation state with AI context tracking
        self.conversation_state = {
            "stage": ConversationStage.INITIAL_GREETING,
            "part1_questions_asked": 0,
            "part2_prep_time": 0,
            "part2_speaking_time": 0,
            "part3_questions_asked": 0,
            "total_time": 0,
            "start_time": None,
            "stage_start_time": None,
            "user_responses": [],
            "conversation_history": [],  # Full conversation context for AI
            "user_context": {},  # What we've learned about the user
            "current_topics": [],  # Active discussion topics
            "evaluation_notes": [],
            "streaming_session": None  # Active Nova Sonic session
        }
    
    async def initialize_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize Maya conversation session"""
        try:
            session_id = session_data.get('session_id')
            assessment_type = session_data.get('assessment_type')
            questions = session_data.get('questions', {})
            
            # Reset conversation state
            self.conversation_state = {
                "session_id": session_id,
                "assessment_type": assessment_type,
                "stage": ConversationStage.INITIAL_GREETING,
                "questions": questions,
                "part1_questions_asked": 0,
                "part2_prep_time": 0,
                "part2_speaking_time": 0,
                "part3_questions_asked": 0,
                "total_time": 0,
                "started_at": datetime.utcnow().isoformat(),
                "user_responses": [],
                "evaluation_notes": []
            }
            
            # Initialize Nova Sonic session for streaming (if available)
            streaming_context = None
            try:
                import asyncio
                # Attempt to initialize streaming session
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                streaming_result = loop.run_until_complete(
                    self.nova_sonic.start_maya_conversation(
                        system_prompt=self.nova_sonic.get_maya_ielts_system_prompt(assessment_type or "academic_speaking"),
                        voice_id="matthew"
                    )
                )
                
                if streaming_result.get('success'):
                    streaming_context = {
                        'stream': streaming_result.get('stream'),
                        'session_id': streaming_result.get('session_id'),
                        'voice_id': streaming_result.get('voice_id'),
                        'status': streaming_result.get('status')
                    }
                    logger.info(f"Nova Sonic streaming session initialized: {streaming_result.get('session_id')}")
                else:
                    logger.warning(f"Nova Sonic streaming failed: {streaming_result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"Failed to initialize Nova Sonic streaming: {e}")
            
            # Set start times for time management
            self.conversation_state["start_time"] = time.time()
            self.conversation_state["stage_start_time"] = time.time()
            self.conversation_state["streaming_session"] = streaming_context
            
            # Generate initial greeting using AI
            initial_message = await self.generate_contextual_response(
                user_input="",
                stage=ConversationStage.INITIAL_GREETING
            )
            
            # Create response with audio synthesis using proper streaming context
            return await self._create_maya_response_with_audio(
                text=initial_message,
                stage=ConversationStage.INITIAL_GREETING,
                expected_response="user_greeting",
                instructions="Respond naturally to Maya's greeting. Tell her how you're feeling today.",
                session_context=streaming_context
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Maya session: {e}")
            return {
                "success": False,
                "error": "Failed to initialize conversation"
            }
    
    async def process_user_response(self, user_input: str, audio_duration: float = 0) -> Dict[str, Any]:
        """
        Process user response and generate Maya's next natural response
        
        Args:
            user_input: User's spoken text (transcribed)
            audio_duration: Duration of user's audio in seconds
            
        Returns:
            Dict with Maya's response and conversation state
        """
        try:
            current_stage = self.conversation_state["stage"]
            
            # Record user response
            response_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "stage": current_stage.value,
                "text": user_input,
                "duration": audio_duration,
                "word_count": len(user_input.split()) if user_input else 0
            }
            self.conversation_state["user_responses"].append(response_record)
            
            # Generate evaluation notes
            evaluation_notes = self.evaluate_response(user_input, audio_duration, current_stage)
            self.conversation_state["evaluation_notes"].extend(evaluation_notes)
            
            # Determine next stage and response using AI
            next_response = await self.determine_next_response(user_input, current_stage)
            
            return next_response
            
        except Exception as e:
            logger.error(f"Failed to process user response: {e}")
            return {
                "success": False,
                "error": "Failed to process response"
            }
    
    async def generate_contextual_response(self, 
                                          user_input: str = "", 
                                          stage: ConversationStage = None,
                                          time_remaining: Optional[int] = None) -> str:
        """Generate contextual AI response using Nova Sonic conversation capabilities"""
        try:
            # Build conversation context for AI
            context = self._build_conversation_context(user_input, stage, time_remaining)
            
            # Use Nova Sonic's AI to generate contextual response
            if self.conversation_state.get('streaming_session'):
                # Use active streaming session for real-time conversation
                response = await self._generate_streaming_response(context)
            else:
                # Generate response using Nova Sonic's conversation AI
                response = await self._generate_ai_response(context)
            
            # Update conversation history with AI-generated response
            self._update_conversation_history(user_input, response)
            
            return response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            # Fallback to stage-appropriate response if AI fails
            return self._get_fallback_response(stage or self.conversation_state['stage'])
    
    def _build_conversation_context(self, 
                                  user_input: str, 
                                  stage: ConversationStage, 
                                  time_remaining: Optional[int]) -> Dict[str, Any]:
        """Build comprehensive context for AI response generation"""
        return {
            "current_stage": stage.value if stage else self.conversation_state['stage'].value,
            "user_input": user_input,
            "conversation_history": self.conversation_state['conversation_history'][-10:],  # Last 10 exchanges
            "user_context": self.conversation_state['user_context'],
            "current_topics": self.conversation_state['current_topics'],
            "time_remaining": time_remaining,
            "total_time_elapsed": self._get_elapsed_time(),
            "ielts_requirements": self._get_stage_requirements(stage),
            "questions_asked": self.conversation_state.get('part1_questions_asked', 0),
            "assessment_type": self.conversation_state.get('assessment_type', 'academic_speaking')
        }
    
    async def _generate_ai_response(self, context: Dict[str, Any]) -> str:
        """Generate AI response using Nova Sonic's conversational capabilities"""
        # Create conversation prompt for Nova Sonic
        conversation_prompt = self._create_conversation_prompt(context)
        
        # Use Nova Sonic to generate contextual response
        # This would use the actual bidirectional streaming or conversation API
        # For now, this is the architecture - implementation depends on Nova Sonic's API
        
        # Placeholder for Nova Sonic conversation API call
        # In production, this would be: await self.nova_sonic.generate_conversation_response(conversation_prompt)
        
        return self._create_contextual_response(context)
    
    def _create_conversation_prompt(self, context: Dict[str, Any]) -> str:
        """Create AI prompt with full conversation context"""
        stage = context['current_stage']
        user_input = context['user_input']
        history = context['conversation_history']
        time_remaining = context['time_remaining']
        
        prompt = f"""You are Maya, an experienced IELTS examiner. Current situation:

**Stage**: {stage}
**User just said**: "{user_input}"
**Time remaining**: {time_remaining}s
**What you know about the user**: {context['user_context']}
**Recent conversation**: {history[-3:] if history else 'Beginning of assessment'}

Generate a natural, contextual response that:
1. Acknowledges what the user said specifically
2. Shows genuine interest in their response
3. Follows IELTS examination standards
4. Manages time appropriately
5. Asks relevant follow-up questions when needed

Respond as Maya would, naturally and professionally."""
        
        return prompt
    
    def _create_contextual_response(self, context: Dict[str, Any]) -> str:
        """Create contextual response based on conversation context (temporary implementation)"""
        stage = context['current_stage']
        user_input = context['user_input']
        time_remaining = context['time_remaining']
        
        # Extract context from user input to generate relevant responses
        user_context = self._extract_user_context(user_input)
        self.conversation_state['user_context'].update(user_context)
        
        if stage == 'initial_greeting':
            return "Hello! I'm Maya, your IELTS examiner today. I can see you're ready to begin - that's wonderful! Before we start, could you please tell me your full name?"
        
        elif stage == 'identity_confirmation':
            name = user_context.get('name', 'there')
            return f"Thank you, {name}. Now, I'd like to ask you some questions about yourself and your interests. Let's start with something familiar."
        
        elif stage == 'part1_questions':
            # Generate contextual follow-ups based on what user said
            if 'work' in user_input.lower():
                if 'engineer' in user_input.lower():
                    return "That sounds fascinating! Engineering is such a diverse field. What specifically drew you to that type of work, and how long have you been doing it?"
                elif 'teacher' in user_input.lower():
                    return "Teaching is such an important profession! What subjects do you teach, and what do you find most rewarding about working with students?"
                else:
                    return "That's interesting work! Can you tell me more about what a typical day looks like for you?"
            
            elif 'study' in user_input.lower():
                return "Your studies sound engaging! What aspects of your subject do you find most interesting, and what are your future plans?"
            
            elif 'home' in user_input.lower() or 'live' in user_input.lower():
                return "That sounds like a nice place to live! What do you particularly like about your area, and how long have you been there?"
            
            # Time-aware responses
            if time_remaining and time_remaining < 30:
                return "That's really interesting. Let me ask you about something different now..."
            
            return "That's really interesting to hear. Can you tell me a bit more about how that influences your daily life?"
        
        elif stage == 'part2_speaking':
            if time_remaining and time_remaining > 30:
                return "You're doing very well. Please continue - I'd love to hear more details about that."
            else:
                return "Thank you for that detailed description. Can you tell me briefly why this topic is particularly meaningful to you?"
        
        return "Thank you for sharing that with me. That's very interesting."
    
    def _synthesize_maya_response(self, text: str, session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Synthesize Maya's text response to audio using Nova Sonic
        
        Args:
            text: Maya's text response
            session_context: Optional streaming session context
            
        Returns:
            Dict with both text and audio synthesis result
        """
        try:
            # Use Nova Sonic service to synthesize Maya's speech
            synthesis_result = self.nova_sonic.synthesize_maya_speech(
                text=text,
                voice_id="matthew",  # Nova Sonic compatible voice
                session_context=session_context
            )
            
            if synthesis_result.get('success'):
                return {
                    "text": text,
                    "audio_synthesis": {
                        "success": True,
                        "audio_base64": synthesis_result.get('audio_base64', ''),
                        "format": synthesis_result.get('format', 'audio/lpcm'),
                        "sample_rate": synthesis_result.get('sample_rate', 24000),
                        "voice_id": synthesis_result.get('voice_id', 'matthew'),
                        "duration_ms": synthesis_result.get('duration_ms', 0),
                        "streaming": synthesis_result.get('streaming', False),
                        "fallback_mode": synthesis_result.get('fallback_mode', False)
                    }
                }
            else:
                logger.warning(f"Voice synthesis failed: {synthesis_result.get('error', 'Unknown error')}")
                return {
                    "text": text,
                    "audio_synthesis": {
                        "success": False,
                        "error": synthesis_result.get('error', 'Synthesis failed'),
                        "fallback_text": text
                    }
                }
                
        except Exception as e:
            logger.error(f"Maya voice synthesis error: {e}")
            return {
                "text": text,
                "audio_synthesis": {
                    "success": False,
                    "error": str(e),
                    "fallback_text": text
                }
            }
    
    async def _create_maya_response_with_audio(self, 
                                       text: str, 
                                       stage: ConversationStage, 
                                       expected_response: str,
                                       session_context: Optional[Dict[str, Any]] = None,
                                       time_remaining: Optional[int] = None,
                                       stage_transition: bool = False,
                                       **kwargs) -> Dict[str, Any]:
        """
        Create Maya response with both text and audio synthesis
        
        Args:
            text: Maya's text message
            stage: Current conversation stage
            expected_response: Expected type of user response
            session_context: Optional streaming session context
            **kwargs: Additional response fields
            
        Returns:
            Complete Maya response with text and audio
        """
        # Update conversation state if transitioning
        if stage_transition:
            self.conversation_state["stage"] = stage
            self.conversation_state["stage_start_time"] = time.time()
        
        # Synthesize Maya's speech using streaming session if available
        session_context = session_context or self.conversation_state.get('streaming_session')
        synthesis_data = self._synthesize_maya_response(text, session_context)
        
        # Build complete response with time awareness
        response = {
            "success": True,
            "maya_message": synthesis_data["text"],
            "maya_audio": synthesis_data["audio_synthesis"],
            "stage": stage.value,
            "expected_response": expected_response,
            "time_remaining": time_remaining,
            "stage_transition": stage_transition,
            "conversation_context": {
                "topics_discussed": self.conversation_state["current_topics"],
                "user_context": self.conversation_state["user_context"]
            },
            **kwargs
        }
        
        return response
    
    async def determine_next_response(self, user_input: str, current_stage: ConversationStage) -> Dict[str, Any]:
        """Generate Maya's contextual response using AI conversation capabilities"""
        try:
            # Calculate time remaining for this stage
            time_remaining = self._calculate_time_remaining(current_stage)
            
            # Generate AI-powered contextual response
            maya_response = await self.generate_contextual_response(
                user_input=user_input,
                stage=current_stage, 
                time_remaining=time_remaining
            )
            
            # Determine next stage based on conversation flow and time
            next_stage, should_transition = self._should_transition_stage(current_stage, time_remaining)
            
            # Create complete response with audio synthesis
            return await self._create_maya_response_with_audio(
                text=maya_response,
                stage=next_stage if should_transition else current_stage,
                expected_response=self._get_expected_response_type(next_stage if should_transition else current_stage),
                time_remaining=time_remaining,
                stage_transition=should_transition
            )
            
        except Exception as e:
            logger.error(f"Failed to determine next response: {e}")
            # Fallback to simple progression
            return await self._handle_fallback_progression(current_stage)
    
    def _calculate_time_remaining(self, stage: ConversationStage) -> Optional[int]:
        """Calculate remaining time for current stage"""
        if not self.conversation_state.get('stage_start_time'):
            return None
            
        elapsed = time.time() - self.conversation_state['stage_start_time']
        time_limits = self.time_limits.get(stage, {})
        
        if stage == ConversationStage.PART1_QUESTIONS:
            total_limit = time_limits.get('total', 300)  # 5 minutes
            return max(0, total_limit - int(elapsed))
        elif stage == ConversationStage.PART2_PREPARATION:
            prep_limit = time_limits.get('preparation', 60)  # 1 minute
            return max(0, prep_limit - int(elapsed))
        elif stage == ConversationStage.PART2_SPEAKING:
            speaking_limit = time_limits.get('speaking', 120)  # 2 minutes
            return max(0, speaking_limit - int(elapsed))
        elif stage == ConversationStage.PART3_DISCUSSION:
            total_limit = time_limits.get('total', 300)  # 5 minutes
            return max(0, total_limit - int(elapsed))
            
        return None
    
    def _should_transition_stage(self, current_stage: ConversationStage, time_remaining: Optional[int]) -> Tuple[ConversationStage, bool]:
        """Determine if we should transition to next stage based on time and conversation flow"""
        # Time-based transitions
        if time_remaining is not None and time_remaining <= 0:
            return self._get_next_stage(current_stage), True
        
        # Content-based transitions (e.g., enough Part 1 questions asked)
        if current_stage == ConversationStage.PART1_QUESTIONS:
            questions_asked = self.conversation_state.get('part1_questions_asked', 0)
            if questions_asked >= 5:  # Standard IELTS Part 1 has 4-6 questions
                return ConversationStage.PART2_BRIEFING, True
        
        return current_stage, False
    
    def _get_next_stage(self, current_stage: ConversationStage) -> ConversationStage:
        """Get the next logical stage in IELTS assessment"""
        stage_progression = {
            ConversationStage.INITIAL_GREETING: ConversationStage.IDENTITY_CONFIRMATION,
            ConversationStage.IDENTITY_CONFIRMATION: ConversationStage.PART1_INTRODUCTION,
            ConversationStage.PART1_INTRODUCTION: ConversationStage.PART1_QUESTIONS,
            ConversationStage.PART1_QUESTIONS: ConversationStage.PART2_BRIEFING,
            ConversationStage.PART2_BRIEFING: ConversationStage.PART2_PREPARATION,
            ConversationStage.PART2_PREPARATION: ConversationStage.PART2_SPEAKING,
            ConversationStage.PART2_SPEAKING: ConversationStage.PART2_FOLLOWUP,
            ConversationStage.PART2_FOLLOWUP: ConversationStage.PART3_INTRODUCTION,
            ConversationStage.PART3_INTRODUCTION: ConversationStage.PART3_DISCUSSION,
            ConversationStage.PART3_DISCUSSION: ConversationStage.CLOSING
        }
        return stage_progression.get(current_stage, ConversationStage.CLOSING)
    
    def _extract_user_context(self, user_input: str) -> Dict[str, Any]:
        """Extract context information from user's response"""
        context = {}
        user_lower = user_input.lower()
        
        # Extract occupation/work
        if 'work' in user_lower or 'job' in user_lower:
            if 'engineer' in user_lower:
                context['occupation'] = 'engineer'
            elif 'teacher' in user_lower:
                context['occupation'] = 'teacher'
            elif 'doctor' in user_lower:
                context['occupation'] = 'doctor'
            elif 'student' in user_lower:
                context['occupation'] = 'student'
        
        # Extract location references
        cities = ['london', 'paris', 'tokyo', 'sydney', 'new york', 'beijing']
        for city in cities:
            if city in user_lower:
                context['location'] = city
                break
        
        # Extract interests/hobbies
        hobbies = ['music', 'sports', 'reading', 'travel', 'cooking', 'photography']
        for hobby in hobbies:
            if hobby in user_lower:
                context.setdefault('interests', []).append(hobby)
        
        # Extract name if mentioned
        if 'my name is' in user_lower or "i'm " in user_lower:
            # Simple name extraction - in production would use NLP
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() in ['name', "i'm", 'called']:
                    if i + 1 < len(words):
                        context['name'] = words[i + 1].strip('.,!?')
                        break
        
        return context
    
    def _update_conversation_history(self, user_input: str, maya_response: str):
        """Update conversation history with new exchange"""
        exchange = {
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_input,
            "maya": maya_response
        }
        self.conversation_state['conversation_history'].append(exchange)
        
        # Keep only last 20 exchanges to manage memory
        if len(self.conversation_state['conversation_history']) > 20:
            self.conversation_state['conversation_history'] = \
                self.conversation_state['conversation_history'][-20:]
    
    def _get_elapsed_time(self) -> int:
        """Get total elapsed time since assessment start"""
        if self.conversation_state.get('start_time'):
            return int(time.time() - self.conversation_state['start_time'])
        return 0
    
    def _get_stage_requirements(self, stage: Optional[ConversationStage]) -> Dict[str, Any]:
        """Get IELTS requirements for specific stage"""
        if not stage:
            return {}
        
        requirements = {
            ConversationStage.PART1_QUESTIONS: {
                "duration": "4-5 minutes",
                "questions": "4-6 familiar topics",
                "focus": "personal information, daily life, interests"
            },
            ConversationStage.PART2_SPEAKING: {
                "duration": "1-2 minutes speaking",
                "preparation": "1 minute preparation time", 
                "format": "long turn monologue with topic card"
            },
            ConversationStage.PART3_DISCUSSION: {
                "duration": "4-5 minutes",
                "focus": "abstract discussion related to Part 2 topic",
                "style": "two-way discussion with examiner"
            }
        }
        
        return requirements.get(stage, {})
    
    def _get_expected_response_type(self, stage: ConversationStage) -> str:
        """Get expected type of user response for stage"""
        response_types = {
            ConversationStage.INITIAL_GREETING: "greeting_response",
            ConversationStage.IDENTITY_CONFIRMATION: "full_name",
            ConversationStage.PART1_QUESTIONS: "detailed_personal_answer",
            ConversationStage.PART2_SPEAKING: "extended_monologue",
            ConversationStage.PART3_DISCUSSION: "analytical_discussion"
        }
        return response_types.get(stage, "general_response")
    
    def _get_fallback_response(self, stage: ConversationStage) -> str:
        """Get fallback response if AI generation fails"""
        fallbacks = {
            ConversationStage.INITIAL_GREETING: "Hello! I'm Maya, your IELTS examiner. How are you today?",
            ConversationStage.IDENTITY_CONFIRMATION: "Could you please tell me your full name?",
            ConversationStage.PART1_QUESTIONS: "That's interesting. Can you tell me more about that?",
            ConversationStage.PART2_SPEAKING: "Please continue with your response.",
            ConversationStage.PART3_DISCUSSION: "That's a good point. What do you think about that?"
        }
        return fallbacks.get(stage, "Thank you. Please continue.")
    
    async def _handle_fallback_progression(self, current_stage: ConversationStage) -> Dict[str, Any]:
        """Handle conversation progression if AI generation fails"""
        fallback_text = self._get_fallback_response(current_stage)
        
        return {
            "success": True,
            "maya_message": fallback_text,
            "maya_audio": {"success": False, "error": "AI generation failed"},
            "stage": current_stage.value,
            "expected_response": self._get_expected_response_type(current_stage),
            "fallback_mode": True
        }
    
    async def _generate_streaming_response(self, context: Dict[str, Any]) -> str:
        """Generate response using active Nova Sonic streaming session"""
        # This would use the bidirectional streaming session
        # For now, fall back to AI response generation
        return await self._generate_ai_response(context)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get comprehensive conversation summary for evaluation"""
        return {
            "session_id": self.conversation_state.get('session_id'),
            "total_duration": self._get_elapsed_time(),
            "conversation_history": self.conversation_state['conversation_history'],
            "user_context": self.conversation_state['user_context'],
            "stages_completed": self.conversation_state['stage'].value,
            "questions_asked": {
                "part1": self.conversation_state.get('part1_questions_asked', 0),
                "part3": self.conversation_state.get('part3_questions_asked', 0)
            },
            "evaluation_notes": self.conversation_state['evaluation_notes'],
            "assessment_complete": self.conversation_state['stage'] == ConversationStage.CLOSING
        }
    
    def handle_identity_confirmation(self) -> Dict[str, Any]:
        """Handle identity confirmation stage"""
        self.conversation_state["stage"] = ConversationStage.IDENTITY_CONFIRMATION
        
        message = self.get_stage_response(ConversationStage.IDENTITY_CONFIRMATION)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.IDENTITY_CONFIRMATION.value,
            "expected_response": "full_name",
            "instructions": "Please state your full name clearly."
        }
    
    def handle_part1_start(self) -> Dict[str, Any]:
        """Handle Part 1 introduction"""
        self.conversation_state["stage"] = ConversationStage.PART1_INTRODUCTION
        
        message = self.get_stage_response(ConversationStage.PART1_INTRODUCTION)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.PART1_INTRODUCTION.value,
            "expected_response": "acknowledgment",
            "instructions": "Listen to Maya's instructions for Part 1."
        }
    
    def handle_part1_questions(self) -> Dict[str, Any]:
        """Handle Part 1 questions"""
        self.conversation_state["stage"] = ConversationStage.PART1_QUESTIONS
        
        # Get first Part 1 question
        part1_questions = self.conversation_state["questions"].get("speaking_part1", [])
        
        if not part1_questions:
            # Fallback question
            question_text = "Tell me about yourself and your background."
        else:
            question_text = part1_questions[0].get("content", {}).get("text", "Tell me about yourself.")
        
        self.conversation_state["part1_questions_asked"] = 1
        
        return {
            "success": True,
            "maya_message": question_text,
            "stage": ConversationStage.PART1_QUESTIONS.value,
            "expected_response": "detailed_answer",
            "instructions": "Give a detailed answer (2-3 sentences). Avoid yes/no responses."
        }
    
    def handle_part1_progression(self, user_input: str) -> Dict[str, Any]:
        """Handle progression through Part 1 questions"""
        questions_asked = self.conversation_state["part1_questions_asked"]
        part1_questions = self.conversation_state["questions"].get("speaking_part1", [])
        
        # Natural encouragement
        encouragement = random.choice(self.encouragement_phrases)
        
        # Check if we should ask more questions (typically 4-6 in Part 1)
        if questions_asked < min(6, len(part1_questions)):
            # Ask next question
            next_question = part1_questions[questions_asked]
            question_text = next_question.get("content", {}).get("text", "Tell me more about that.")
            
            self.conversation_state["part1_questions_asked"] += 1
            
            # Natural transition
            transition = random.choice(self.transition_phrases)
            full_message = f"{encouragement} {transition} {question_text}"
            
            return {
                "success": True,
                "maya_message": full_message,
                "stage": ConversationStage.PART1_QUESTIONS.value,
                "expected_response": "detailed_answer",
                "instructions": "Continue with detailed answers about your experiences and opinions."
            }
        else:
            # Move to Part 2
            return self.handle_part2_briefing()
    
    def handle_part2_briefing(self) -> Dict[str, Any]:
        """Handle Part 2 briefing and topic card presentation"""
        self.conversation_state["stage"] = ConversationStage.PART2_BRIEFING
        
        # Get Part 2 topic
        part2_questions = self.conversation_state["questions"].get("speaking_part2", [])
        if part2_questions:
            topic_card = part2_questions[0].get("content", {}).get("text", "Describe something important to you.")
        else:
            topic_card = "Describe a place that is special to you. You should say: where it is, when you go there, what you do there, and explain why this place is special to you."
        
        briefing_message = self.get_stage_response(ConversationStage.PART2_BRIEFING)
        full_message = f"{briefing_message}\n\nHere's your topic card:\n\n{topic_card}\n\nRemember, you have one minute to prepare. Your preparation time starts now."
        
        return {
            "success": True,
            "maya_message": full_message,
            "stage": ConversationStage.PART2_BRIEFING.value,
            "expected_response": "preparation",
            "instructions": "Use this minute to organize your thoughts. Make notes if needed.",
            "preparation_time": 60,  # 60 seconds preparation
            "topic_card": topic_card
        }
    
    def handle_part2_preparation(self) -> Dict[str, Any]:
        """Handle Part 2 preparation time"""
        self.conversation_state["stage"] = ConversationStage.PART2_PREPARATION
        
        return {
            "success": True,
            "maya_message": "Your preparation time is up. Please begin speaking about your topic. Remember, you should speak for 1-2 minutes.",
            "stage": ConversationStage.PART2_PREPARATION.value,
            "expected_response": "long_turn_speech",
            "instructions": "Speak for 1-2 minutes about your topic. Cover all the points on the card.",
            "speaking_time": 120  # 2 minutes maximum
        }
    
    def handle_part2_speaking(self) -> Dict[str, Any]:
        """Handle Part 2 speaking phase"""
        self.conversation_state["stage"] = ConversationStage.PART2_SPEAKING
        
        # Generate follow-up questions
        follow_up_questions = [
            "Thank you. Can you tell me a bit more about why this is important to you?",
            "That's interesting. How do you think this has influenced you?",
            "Thank you for that detailed description."
        ]
        
        follow_up = random.choice(follow_up_questions)
        
        return {
            "success": True,
            "maya_message": follow_up,
            "stage": ConversationStage.PART2_FOLLOWUP.value,
            "expected_response": "brief_elaboration",
            "instructions": "Give a brief response to Maya's follow-up question."
        }
    
    def handle_part2_completion(self, user_input: str) -> Dict[str, Any]:
        """Handle Part 2 completion"""
        self.conversation_state["stage"] = ConversationStage.PART2_FOLLOWUP
        
        return {
            "success": True,
            "maya_message": random.choice(self.encouragement_phrases),
            "stage": ConversationStage.PART2_FOLLOWUP.value,
            "transition_to_part3": True
        }
    
    def handle_part3_start(self) -> Dict[str, Any]:
        """Handle Part 3 introduction"""
        self.conversation_state["stage"] = ConversationStage.PART3_INTRODUCTION
        
        message = self.get_stage_response(ConversationStage.PART3_INTRODUCTION)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.PART3_INTRODUCTION.value,
            "expected_response": "acknowledgment",
            "instructions": "Part 3 involves more abstract discussion. Give thoughtful, extended answers."
        }
    
    def handle_part3_questions(self) -> Dict[str, Any]:
        """Handle Part 3 questions"""
        self.conversation_state["stage"] = ConversationStage.PART3_DISCUSSION
        
        # Get first Part 3 question
        part3_questions = self.conversation_state["questions"].get("speaking_part3", [])
        
        if part3_questions:
            question_text = part3_questions[0].get("content", {}).get("text", "What are your thoughts on this topic in general?")
        else:
            question_text = "What do you think about the role this plays in modern society?"
        
        self.conversation_state["part3_questions_asked"] = 1
        
        return {
            "success": True,
            "maya_message": question_text,
            "stage": ConversationStage.PART3_DISCUSSION.value,
            "expected_response": "analytical_response",
            "instructions": "Give detailed, analytical responses. Consider different perspectives."
        }
    
    def handle_part3_progression(self, user_input: str) -> Dict[str, Any]:
        """Handle progression through Part 3 discussion"""
        questions_asked = self.conversation_state["part3_questions_asked"]
        part3_questions = self.conversation_state["questions"].get("speaking_part3", [])
        
        # Natural encouragement
        encouragement = random.choice(self.encouragement_phrases)
        
        # Check if we should ask more questions (typically 4-5 in Part 3)
        if questions_asked < min(4, len(part3_questions)):
            # Ask next question
            next_question = part3_questions[questions_asked]
            question_text = next_question.get("content", {}).get("text", "What's your opinion on this?")
            
            self.conversation_state["part3_questions_asked"] += 1
            
            # Natural transition for abstract discussion
            transitions = [
                "That's a good point. How about this:",
                "I see your perspective. Let me ask you:",
                "Interesting. What would you say about:",
                "That raises another question:"
            ]
            transition = random.choice(transitions)
            full_message = f"{encouragement} {transition} {question_text}"
            
            return {
                "success": True,
                "maya_message": full_message,
                "stage": ConversationStage.PART3_DISCUSSION.value,
                "expected_response": "analytical_response",
                "instructions": "Continue discussing these abstract concepts in detail."
            }
        else:
            # End the assessment
            return self.handle_closing()
    
    def handle_closing(self) -> Dict[str, Any]:
        """Handle assessment closing"""
        self.conversation_state["stage"] = ConversationStage.CLOSING
        
        message = self.get_stage_response(ConversationStage.CLOSING)
        
        return {
            "success": True,
            "maya_message": message,
            "stage": ConversationStage.CLOSING.value,
            "assessment_complete": True,
            "instructions": "Your speaking assessment is now complete. Thank you!"
        }
    
    def evaluate_response(self, user_input: str, audio_duration: float, stage: ConversationStage) -> List[Dict[str, Any]]:
        """
        Evaluate user response for IELTS criteria
        
        Returns evaluation notes for band scoring
        """
        evaluation_notes = []
        
        if not user_input or len(user_input.strip()) < 3:
            evaluation_notes.append({
                "criterion": "Fluency and Coherence",
                "note": "Very brief response - limited assessment possible",
                "stage": stage.value
            })
            return evaluation_notes
        
        word_count = len(user_input.split())
        
        # Fluency and Coherence evaluation
        if audio_duration > 0:
            words_per_minute = (word_count / audio_duration) * 60
            if words_per_minute < 100:
                evaluation_notes.append({
                    "criterion": "Fluency and Coherence",
                    "note": f"Slow speech rate ({words_per_minute:.0f} wpm) - may indicate hesitation",
                    "stage": stage.value
                })
            elif words_per_minute > 200:
                evaluation_notes.append({
                    "criterion": "Fluency and Coherence",
                    "note": f"Very rapid speech ({words_per_minute:.0f} wpm) - check for coherence",
                    "stage": stage.value
                })
        
        # Lexical Resource evaluation
        unique_words = set(user_input.lower().split())
        lexical_variety = len(unique_words) / word_count if word_count > 0 else 0
        
        if lexical_variety > 0.8:
            evaluation_notes.append({
                "criterion": "Lexical Resource",
                "note": "Good vocabulary variety demonstrated",
                "stage": stage.value
            })
        elif lexical_variety < 0.5:
            evaluation_notes.append({
                "criterion": "Lexical Resource",
                "note": "Limited vocabulary range - repetitive word use",
                "stage": stage.value
            })
        
        # Response length appropriateness
        expected_lengths = {
            ConversationStage.PART1_QUESTIONS: (10, 50),  # 10-50 words
            ConversationStage.PART2_SPEAKING: (150, 300), # 150-300 words for 2 minutes
            ConversationStage.PART3_DISCUSSION: (30, 100) # 30-100 words
        }
        
        if stage in expected_lengths:
            min_words, max_words = expected_lengths[stage]
            if word_count < min_words:
                evaluation_notes.append({
                    "criterion": "Task Response",
                    "note": f"Response too brief ({word_count} words) for {stage.value}",
                    "stage": stage.value
                })
            elif word_count > max_words * 1.5:  # 50% over is concerning
                evaluation_notes.append({
                    "criterion": "Task Response", 
                    "note": f"Very lengthy response ({word_count} words) - may lack focus",
                    "stage": stage.value
                })
        
        return evaluation_notes
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get complete conversation summary for evaluation"""
        return {
            "session_id": self.conversation_state.get("session_id"),
            "assessment_type": self.conversation_state.get("assessment_type"),
            "conversation_flow": {
                "total_responses": len(self.conversation_state["user_responses"]),
                "part1_responses": len([r for r in self.conversation_state["user_responses"] if "part1" in r["stage"]]),
                "part2_responses": len([r for r in self.conversation_state["user_responses"] if "part2" in r["stage"]]),
                "part3_responses": len([r for r in self.conversation_state["user_responses"] if "part3" in r["stage"]]),
            },
            "user_responses": self.conversation_state["user_responses"],
            "evaluation_notes": self.conversation_state["evaluation_notes"],
            "completion_status": self.conversation_state["stage"] == ConversationStage.CLOSING
        }

# Global instance
_maya_engine = None

def get_maya_engine() -> MayaConversationEngine:
    """Get global Maya conversation engine instance"""
    global _maya_engine
    if _maya_engine is None:
        _maya_engine = MayaConversationEngine()
    return _maya_engine

# Export
__all__ = [
    'MayaConversationEngine',
    'ConversationStage',
    'ResponseType', 
    'get_maya_engine'
]