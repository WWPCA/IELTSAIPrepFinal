"""
IELTS Context Data Loader
This module loads and prepares IELTS assessment context data from provided context files.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

def load_writing_context_data():
    """
    Load context data from the IELTS Writing Context File.
    
    Returns:
        dict: Structured IELTS Writing assessment context data
    """
    context_data = {
        "academic": {
            "task1": {
                "band_descriptors": {},
                "examples": [],
                "assessment_guidance": ""
            },
            "task2": {
                "band_descriptors": {},
                "examples": [],
                "assessment_guidance": ""
            }
        },
        "general": {
            "task1": {
                "band_descriptors": {},
                "examples": [],
                "assessment_guidance": ""
            },
            "task2": {
                "band_descriptors": {},
                "examples": [],
                "assessment_guidance": ""
            }
        }
    }
    
    try:
        # The context data is stored in writing_criteria.py as band descriptors
        from assessment_criteria.writing_criteria import (
            WRITING_TASK1_BAND_DESCRIPTORS, 
            WRITING_TASK2_BAND_DESCRIPTORS,
            WRITING_TEST_FORMAT
        )
        
        # Academic Task 1 context
        context_data["academic"]["task1"]["band_descriptors"] = WRITING_TASK1_BAND_DESCRIPTORS
        context_data["academic"]["task1"]["assessment_guidance"] = """
When assessing an IELTS Academic Task 1 essay, focus on:
1. Task Achievement: How well the candidate addresses all parts of the task, provides an overview, selects key features, and uses appropriate data.
2. Coherence and Cohesion: How well-organized the response is, with paragraphing, linking devices, and logical progression.
3. Lexical Resource: Vocabulary range, precision, spelling, and appropriateness.
4. Grammatical Range and Accuracy: Sentence structures, grammar, and punctuation.

For graph/chart descriptions, candidates should:
- Include an introduction that describes what the visual shows
- Provide an overview of main trends/features
- Select key data points to highlight (not describe every detail)
- Group related information logically
- Make appropriate comparisons
- NOT include opinions or causes not shown in the data
"""
        
        # Academic Task 2 context
        context_data["academic"]["task2"]["band_descriptors"] = WRITING_TASK2_BAND_DESCRIPTORS
        context_data["academic"]["task2"]["assessment_guidance"] = """
When assessing an IELTS Academic Task 2 essay, focus on:
1. Task Response: How well the candidate addresses all parts of the question, develops a position, presents relevant ideas, and reaches a conclusion.
2. Coherence and Cohesion: How well-organized the essay is, with paragraphing, linking devices, and logical progression.
3. Lexical Resource: Vocabulary range, precision, spelling, and appropriateness.
4. Grammatical Range and Accuracy: Sentence structures, grammar, and punctuation.

A well-structured Task 2 essay should have:
- Introduction that addresses the question
- Body paragraphs with clear topic sentences and supporting details
- A conclusion that restates the position/summarizes key points
- Balanced argument (if asked to discuss both sides)
- Clear stance (if asked for an opinion)
"""

        # General Training Task 1 context (letter writing)
        context_data["general"]["task1"]["band_descriptors"] = WRITING_TASK1_BAND_DESCRIPTORS
        context_data["general"]["task1"]["assessment_guidance"] = """
When assessing an IELTS General Training Task 1 letter, focus on:
1. Task Achievement: How well the candidate addresses the purpose of the letter, covers all three bullet points, and uses appropriate tone/format.
2. Coherence and Cohesion: How well-organized the letter is, with paragraphing, linking devices, and logical progression.
3. Lexical Resource: Vocabulary range, precision, spelling, and appropriateness for the letter context.
4. Grammatical Range and Accuracy: Sentence structures, grammar, and punctuation.

A well-structured letter should have:
- Proper opening salutation (Dear Sir/Madam or Dear [Name])
- Clear purpose in the opening paragraph
- Body paragraphs addressing each of the 3 required bullet points
- A polite closing paragraph with any necessary request or action point
- Appropriate closing expression (Yours faithfully/Yours sincerely)
- Consistent tone throughout (formal, semi-formal, or informal as appropriate)
"""
        
        # General Training Task 2 context (essay)
        context_data["general"]["task2"]["band_descriptors"] = WRITING_TASK2_BAND_DESCRIPTORS
        context_data["general"]["task2"]["assessment_guidance"] = """
When assessing an IELTS General Training Task 2 essay, focus on:
1. Task Response: How well the candidate addresses all parts of the question, develops a position, presents relevant ideas, and reaches a conclusion.
2. Coherence and Cohesion: How well-organized the essay is, with paragraphing, linking devices, and logical progression.
3. Lexical Resource: Vocabulary range, precision, spelling, and appropriateness.
4. Grammatical Range and Accuracy: Sentence structures, grammar, and punctuation.

A well-structured General Training Task 2 essay should have:
- Introduction that addresses the question
- Body paragraphs with clear topic sentences and supporting details
- A conclusion that restates the position/summarizes key points
- Personal examples relevant to everyday contexts (more common than in Academic Task 2)
- Slightly less formal tone than Academic Task 2 is acceptable
"""
        
        return context_data
        
    except Exception as e:
        logger.error(f"Error loading writing context data: {str(e)}")
        return context_data

def load_speaking_context_data():
    """
    Load context data from the IELTS Speaking Context File.
    
    Returns:
        dict: Structured IELTS Speaking assessment context data
    """
    context_data = {
        "band_descriptors": {},
        "part_guidance": {
            "part1": "",
            "part2": "",
            "part3": ""
        },
        "examples": []
    }
    
    try:
        # The context data is stored in speaking_criteria.py as band descriptors
        from assessment_criteria.speaking_criteria import (
            SPEAKING_BAND_DESCRIPTORS,
            SPEAKING_TEST_FORMAT
        )
        
        context_data["band_descriptors"] = SPEAKING_BAND_DESCRIPTORS
        
        # Part guidance
        context_data["part_guidance"]["part1"] = """
IELTS Speaking Part 1 (Introduction and Interview):
- Duration: 4-5 minutes
- Question types: Personal topics, familiar everyday themes
- Format: Examiner asks direct questions about everyday topics

Assessment focus:
- Ability to provide information about familiar topics
- Use of appropriate tense and grammar for personal responses
- Pronunciation and fluency in short responses
- Range of vocabulary for everyday topics
"""
        
        context_data["part_guidance"]["part2"] = """
IELTS Speaking Part 2 (Individual Long Turn):
- Duration: 3-4 minutes (including 1 minute preparation)
- Format: Candidate speaks for 1-2 minutes on a given topic using a task card
- Preparation time: 1 minute with note-taking allowed

Assessment focus:
- Ability to speak at length coherently
- Organization and connection of ideas
- Use of descriptive language and specific details
- Range of grammatical structures and vocabulary
- Ability to maintain fluency without excessive hesitation
"""
        
        context_data["part_guidance"]["part3"] = """
IELTS Speaking Part 3 (Two-way Discussion):
- Duration: 4-5 minutes
- Format: Examiner asks questions related to Part 2 topic but more abstract
- Question types: Analytical, evaluative, speculative

Assessment focus:
- Ability to express and justify opinions
- Ability to analyze, discuss and speculate on issues
- Use of complex language and appropriate discourse markers
- Development of ideas and coherent argumentation
- Handling of abstract concepts
"""
        
        return context_data
        
    except Exception as e:
        logger.error(f"Error loading speaking context data: {str(e)}")
        return context_data

def get_ielts_context_for_assessment(assessment_type, test_type="academic", task_number=1):
    """
    Get the appropriate IELTS context data for a specific assessment.
    
    Args:
        assessment_type (str): "writing" or "speaking"
        test_type (str): "academic" or "general"
        task_number (int): 1, 2, or 3 (for speaking parts)
        
    Returns:
        dict: Context data for the specified assessment
    """
    try:
        if assessment_type.lower() == "writing":
            context_data = load_writing_context_data()
            task_key = f"task{task_number}"
            return context_data[test_type.lower()][task_key]
        
        elif assessment_type.lower() == "speaking":
            context_data = load_speaking_context_data()
            part_key = f"part{task_number}"
            part_context = {
                "band_descriptors": context_data["band_descriptors"],
                "guidance": context_data["part_guidance"][part_key]
            }
            return part_context
        
        else:
            logger.error(f"Unknown assessment type: {assessment_type}")
            return {}
            
    except Exception as e:
        logger.error(f"Error getting context for {assessment_type} assessment: {str(e)}")
        return {}