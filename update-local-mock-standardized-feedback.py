#!/usr/bin/env python3
"""
Update local AWS mock configuration to use standardized feedback format
"""

import random
import uuid
from datetime import datetime, timezone

def generate_standardized_writing_feedback(assessment_type: str, user_input: str) -> dict:
    """Generate standardized writing feedback using the new format"""
    
    # Base scores with some randomization
    base_score = random.uniform(6.0, 8.5)
    
    # Generate individual criterion scores around the base
    task_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    coherence_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    lexical_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    grammar_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    
    # Overall score is average of criteria
    overall_score = (task_score + coherence_score + lexical_score + grammar_score) / 4
    
    # Standardized feedback format
    feedback = {
        "overall_band": round(overall_score, 1),
        "criteria": {
            "task_achievement": {
                "score": round(task_score, 1),
                "feedback": "Good task response with clear position and relevant examples. Consider developing arguments more thoroughly."
            },
            "coherence_cohesion": {
                "score": round(coherence_score, 1),
                "feedback": "Well-organized ideas with appropriate linking devices. Some transitions could be smoother."
            },
            "lexical_resource": {
                "score": round(lexical_score, 1),
                "feedback": "Good range of vocabulary with some sophisticated usage. Avoid repetition of key terms."
            },
            "grammatical_range": {
                "score": round(grammar_score, 1),
                "feedback": "Variety of sentence structures with good accuracy. Some complex structures need refinement."
            }
        },
        "detailed_feedback": f"Your {assessment_type} demonstrates solid understanding with clear argumentation. The essay shows good command of English with appropriate academic register. Focus on expanding examples and using more varied sentence structures for higher band scores.",
        "word_count": len(user_input.split()) if user_input else 0,
        "strengths": [
            "Clear thesis statement and logical structure",
            "Appropriate academic vocabulary usage"
        ],
        "areas_for_improvement": [
            "Develop supporting examples more thoroughly",
            "Use more sophisticated linking devices"
        ],
        "assessment_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return feedback

def generate_standardized_speaking_feedback(assessment_type: str, conversation_duration: int = 14) -> dict:
    """Generate standardized speaking feedback using the new format"""
    
    # Base scores with some randomization
    base_score = random.uniform(6.0, 8.5)
    
    # Generate individual criterion scores around the base
    fluency_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    lexical_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    grammar_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    pronunciation_score = max(4.0, min(9.0, base_score + random.uniform(-0.5, 0.5)))
    
    # Overall score is average of criteria
    overall_score = (fluency_score + lexical_score + grammar_score + pronunciation_score) / 4
    
    # Standardized feedback format
    feedback = {
        "overall_band": round(overall_score, 1),
        "criteria": {
            "fluency_coherence": {
                "score": round(fluency_score, 1),
                "feedback": "Natural conversation flow with appropriate hesitation patterns. Some topic development could be more coherent."
            },
            "lexical_resource": {
                "score": round(lexical_score, 1),
                "feedback": "Good range of vocabulary with flexibility. Occasional imprecise word choices but generally effective communication."
            },
            "grammatical_range": {
                "score": round(grammar_score, 1),
                "feedback": "Variety of sentence structures with generally good control. Some complex structures need refinement."
            },
            "pronunciation": {
                "score": round(pronunciation_score, 1),
                "feedback": "Generally clear pronunciation with effective use of stress and intonation. Some individual sounds need attention."
            }
        },
        "detailed_feedback": f"Your {assessment_type} performance demonstrates good communicative ability with natural interaction patterns. Maya noted your ability to maintain conversation flow and respond appropriately to questions. Focus on expanding vocabulary range and refining complex grammar structures.",
        "conversation_duration": f"{conversation_duration} minutes",
        "strengths": [
            "Natural conversation flow and appropriate responses",
            "Clear pronunciation and effective communication"
        ],
        "areas_for_improvement": [
            "Expand vocabulary range for abstract topics",
            "Refine complex grammatical structures"
        ],
        "assessment_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return feedback

def create_mock_assessment_function():
    """Create mock assessment function with standardized feedback"""
    
    mock_functions = """
# Updated mock assessment functions with standardized feedback format

def call_nova_micro_api(prompt: str, assessment_type: str) -> Dict[str, Any]:
    \"\"\"Call AWS Nova Micro for writing assessment evaluation with standardized feedback\"\"\"
    
    # Import the standardized feedback generator
    from update_local_mock_standardized_feedback import generate_standardized_writing_feedback
    
    # Generate standardized feedback
    result = generate_standardized_writing_feedback(assessment_type, prompt)
    
    print(f"Nova Micro assessment completed for {assessment_type}")
    print(f"Overall band: {result['overall_band']}")
    
    return result

def call_nova_sonic_api(conversation_data: Dict[str, Any], assessment_type: str) -> Dict[str, Any]:
    \"\"\"Call AWS Nova Sonic for speaking assessment evaluation with standardized feedback\"\"\"
    
    # Import the standardized feedback generator
    from update_local_mock_standardized_feedback import generate_standardized_speaking_feedback
    
    # Generate standardized feedback
    result = generate_standardized_speaking_feedback(assessment_type, conversation_data.get('duration', 14))
    
    print(f"Nova Sonic assessment completed for {assessment_type}")
    print(f"Overall band: {result['overall_band']}")
    
    return result
"""
    
    return mock_functions

def main():
    """Main function to show standardized feedback format"""
    print("=== Standardized Nova Feedback Format ===")
    print()
    
    # Example writing feedback
    print("📝 Writing Assessment Feedback Example:")
    writing_feedback = generate_standardized_writing_feedback("academic_writing", "Sample essay content here")
    print(f"Overall Band: {writing_feedback['overall_band']}")
    print(f"Task Achievement: {writing_feedback['criteria']['task_achievement']['score']}")
    print(f"Strengths: {', '.join(writing_feedback['strengths'])}")
    print()
    
    # Example speaking feedback
    print("🗣️ Speaking Assessment Feedback Example:")
    speaking_feedback = generate_standardized_speaking_feedback("academic_speaking", 14)
    print(f"Overall Band: {speaking_feedback['overall_band']}")
    print(f"Fluency & Coherence: {speaking_feedback['criteria']['fluency_coherence']['score']}")
    print(f"Strengths: {', '.join(speaking_feedback['strengths'])}")
    print()
    
    print("✅ Standardized format provides:")
    print("  • Consistent JSON structure across all assessments")
    print("  • Detailed criterion-specific feedback")
    print("  • Actionable strengths and improvement areas")
    print("  • Unique assessment IDs for tracking")
    print("  • Timestamp for analytics")
    print()
    
    print("📋 Mock functions created for local testing")
    print("   These functions can be integrated into app.py for development")

if __name__ == "__main__":
    main()