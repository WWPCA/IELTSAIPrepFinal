"""
IELTS Writing Assessment Criteria Configuration
This file contains the band descriptors and criteria for IELTS writing assessment for both Task 1 and Task 2.
"""

# IELTS Writing Test Format
WRITING_TEST_FORMAT = {
    "academic": {
        "total_duration": "60 minutes",
        "tasks": [
            {
                "task": 1,
                "words": "at least 150 words",
                "time": "recommended 20 minutes",
                "description": "Describe visual information (graph/table/chart/diagram) or a process. Explain how something works or how it is organized.",
                "assessment_criteria": ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
            },
            {
                "task": 2,
                "words": "at least 250 words",
                "time": "recommended 40 minutes",
                "description": "Present and justify an opinion, discuss a problem, compare and contrast evidence or opinions, evaluate and challenge ideas or arguments.",
                "assessment_criteria": ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
            }
        ]
    },
    "general": {
        "total_duration": "60 minutes",
        "tasks": [
            {
                "task": 1,
                "words": "at least 150 words",
                "time": "recommended 20 minutes",
                "description": "Write a letter requesting information or explaining a situation. There are three possible types: Personal, Semi-formal, or Formal.",
                "assessment_criteria": ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
            },
            {
                "task": 2,
                "words": "at least 250 words",
                "time": "recommended 40 minutes",
                "description": "Write an essay in response to a point of view, argument or problem. Similar to Academic Task 2, but topics are more related to everyday concerns.",
                "assessment_criteria": ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
            }
        ]
    }
}

# IELTS Writing Assessment Criteria Descriptions
WRITING_ASSESSMENT_CRITERIA = {
    "Task Achievement": "This assesses how fully the task has been addressed and whether the format is appropriate.",
    "Task Response": "This assesses how the candidate has responded to the task, developed their position, and provided supporting evidence.",
    "Coherence and Cohesion": "This assesses the overall organization, paragraphing, use of cohesive devices, and logical sequencing of ideas.",
    "Lexical Resource": "This assesses the range and accuracy of vocabulary, including spelling and word formation.",
    "Grammatical Range and Accuracy": "This assesses the range and accuracy of grammatical structures."
}

# IELTS Writing Band Descriptors - Task 1
WRITING_TASK1_BAND_DESCRIPTORS = {
    9: {
        "Task Achievement": "Fully satisfies all the requirements of the task. Clearly presents a fully developed response. The response is a full and relevant exploration of the key features.",
        "Coherence and Cohesion": "Uses cohesion in such a way that it attracts no attention. Skillfully manages paragraphing. Sequences information and ideas logically.",
        "Lexical Resource": "Uses a wide range of vocabulary with very natural and sophisticated control of lexical features. Minor errors in spelling and word formation occur rarely, if at all.",
        "Grammatical Range and Accuracy": "Uses a wide range of structures with full flexibility and accuracy. Rare minor errors occur only as 'slips'."
    },
    8: {
        "Task Achievement": "Covers all requirements of the task sufficiently. Presents, highlights and illustrates key features clearly and appropriately.",
        "Coherence and Cohesion": "Manages all aspects of cohesion well. Uses paragraphing sufficiently and appropriately. Presents a clear central topic within each paragraph.",
        "Lexical Resource": "Uses a wide range of vocabulary fluently and flexibly to convey precise meanings. Skillfully uses uncommon lexical items but there may be occasional inaccuracies in word choice and collocation. Produces rare errors in spelling and/or word formation.",
        "Grammatical Range and Accuracy": "Uses a wide range of structures. The majority of sentences are error-free. Makes only very occasional errors or inappropriacies."
    },
    7: {
        "Task Achievement": "Covers the requirements of the task. Presents a clear overview of main trends, differences or stages. Clearly presents and highlights key features but could be more fully extended.",
        "Coherence and Cohesion": "Logically organizes information and ideas; there is clear progression throughout. Uses a range of cohesive devices appropriately although there may be some under-/over-use. Presents a clear central topic within each paragraph.",
        "Lexical Resource": "Uses a sufficient range of vocabulary to allow some flexibility and precision. Uses less common lexical items with some awareness of style and collocation. May produce occasional errors in word choice, spelling and/or word formation.",
        "Grammatical Range and Accuracy": "Uses a variety of complex structures. Produces frequent error-free sentences. Has good control of grammar and punctuation but may make a few errors."
    },
    6: {
        "Task Achievement": "Addresses the requirements of the task. Presents an overview with information appropriately selected. Presents and adequately highlights key features but details may be irrelevant, inappropriate or inaccurate.",
        "Coherence and Cohesion": "Arranges information and ideas coherently and there is a clear overall progression. Uses cohesive devices effectively, but cohesion within and/or between sentences may be faulty or mechanical. May not always use referencing clearly or appropriately. Uses paragraphing, but not always logically.",
        "Lexical Resource": "Uses an adequate range of vocabulary for the task. Attempts to use less common vocabulary but with some inaccuracy. Makes some errors in spelling and/or word formation, but they do not impede communication.",
        "Grammatical Range and Accuracy": "Uses a mix of simple and complex sentence forms. Makes some errors in grammar and punctuation but they rarely reduce communication."
    },
    5: {
        "Task Achievement": "Generally addresses the task. The format may be inappropriate in places. Recounts detail mechanically with no clear overview. Presents, but inadequately covers, key features. There may be a tendency to focus on details.",
        "Coherence and Cohesion": "Presents information with some organization but there may be a lack of overall progression. Makes inadequate, inaccurate or over-use of cohesive devices. May be repetitive because of lack of referencing and substitution. May not write in paragraphs, or paragraphing may be inadequate.",
        "Lexical Resource": "Uses a limited range of vocabulary, but this is minimally adequate for the task. May make noticeable errors in spelling and/or word formation that may cause some difficulty for the reader.",
        "Grammatical Range and Accuracy": "Uses only a limited range of structures. Attempts complex sentences but these tend to be less accurate than simple sentences. May make frequent grammatical errors and punctuation may be faulty; errors can cause some difficulty for the reader."
    },
    4: {
        "Task Achievement": "Attempts to address the task but does not cover all key features. The format may be inappropriate. Fails to present a clear overview of main trends, differences or stages. May confuse key features with detail; parts may be unclear, irrelevant, repetitive or inaccurate.",
        "Coherence and Cohesion": "Presents information and ideas but these are not arranged coherently and there is no clear progression in the response. Uses some basic cohesive devices but these may be inaccurate or repetitive. May not write in paragraphs or their use may be confusing.",
        "Lexical Resource": "Uses only basic vocabulary which may be used repetitively or which may be inappropriate for the task. Has limited control of word formation and/or spelling; errors may cause strain for the reader.",
        "Grammatical Range and Accuracy": "Uses only a very limited range of structures with only rare use of subordinate clauses. Some structures are accurate but errors predominate, and punctuation is often faulty."
    },
    3: {
        "Task Achievement": "Fails to address the task adequately. Fails to present a clear overview. The information and ideas are poorly organized; there is no clear progression in the response.",
        "Coherence and Cohesion": "Does not organize ideas logically. May use a very limited range of cohesive devices, and those used may not indicate a logical relationship between ideas.",
        "Lexical Resource": "Uses only a very limited range of words and expressions with very limited control of word formation and/or spelling. Errors may severely distort the message.",
        "Grammatical Range and Accuracy": "Attempts sentence forms but errors in grammar and punctuation predominate and distort the meaning."
    },
    2: {
        "Task Achievement": "Answer is barely related to the task. Fails to communicate any message.",
        "Coherence and Cohesion": "Has very little control of organizational features.",
        "Lexical Resource": "Uses an extremely limited range of vocabulary; essentially no control of word formation and/or spelling.",
        "Grammatical Range and Accuracy": "Cannot use sentence forms except in memorized phrases."
    },
    1: {
        "Task Achievement": "Answer is completely unrelated to the task.",
        "Coherence and Cohesion": "Fails to communicate any message.",
        "Lexical Resource": "Can only use a few isolated words.",
        "Grammatical Range and Accuracy": "Cannot use sentence forms at all."
    },
    0: {
        "Task Achievement": "Candidate did not attend or did not attempt the task in any way.",
        "Coherence and Cohesion": "Candidate did not attend or did not attempt the task in any way.",
        "Lexical Resource": "Candidate did not attend or did not attempt the task in any way.",
        "Grammatical Range and Accuracy": "Candidate did not attend or did not attempt the task in any way."
    }
}

# IELTS Writing Band Descriptors - Task 2
WRITING_TASK2_BAND_DESCRIPTORS = {
    9: {
        "Task Response": "Fully addresses all parts of the task. Presents a fully developed position in answer to the question with relevant, fully extended and well supported ideas.",
        "Coherence and Cohesion": "Uses cohesion in such a way that it attracts no attention. Skillfully manages paragraphing.",
        "Lexical Resource": "Uses a wide range of vocabulary with very natural and sophisticated control of lexical features; rare minor errors occur only as 'slips'.",
        "Grammatical Range and Accuracy": "Uses a wide range of structures with full flexibility and accuracy; rare minor errors occur only as 'slips'."
    },
    8: {
        "Task Response": "Sufficiently addresses all parts of the task. Presents a well-developed response to the question with relevant, extended and supported ideas.",
        "Coherence and Cohesion": "Sequences information and ideas logically. Manages all aspects of cohesion well. Uses paragraphing sufficiently and appropriately.",
        "Lexical Resource": "Uses a wide range of vocabulary fluently and flexibly to convey precise meanings. Skillfully uses uncommon lexical items but there may be occasional inaccuracies in word choice and collocation. Produces rare errors in spelling and/or word formation.",
        "Grammatical Range and Accuracy": "Uses a wide range of structures. The majority of sentences are error-free. Makes only very occasional errors or inappropriacies."
    },
    7: {
        "Task Response": "Addresses all parts of the task. Presents a clear position throughout the response. Presents, extends and supports main ideas, but there may be a tendency to over-generalize and/or supporting ideas may lack focus.",
        "Coherence and Cohesion": "Logically organizes information and ideas; there is clear progression throughout. Uses a range of cohesive devices appropriately although there may be some under-/over-use. Presents a clear central topic within each paragraph.",
        "Lexical Resource": "Uses a sufficient range of vocabulary to allow some flexibility and precision. Uses less common lexical items with some awareness of style and collocation. May produce occasional errors in word choice, spelling and/or word formation.",
        "Grammatical Range and Accuracy": "Uses a variety of complex structures. Produces frequent error-free sentences. Has good control of grammar and punctuation but may make a few errors."
    },
    6: {
        "Task Response": "Addresses all parts of the task although some parts may be more fully covered than others. Presents a relevant position although the conclusions may become unclear or repetitive. Presents relevant main ideas but some may be inadequately developed/unclear.",
        "Coherence and Cohesion": "Arranges information and ideas coherently and there is a clear overall progression. Uses cohesive devices effectively, but cohesion within and/or between sentences may be faulty or mechanical. May not always use referencing clearly or appropriately. Uses paragraphing, but not always logically.",
        "Lexical Resource": "Uses an adequate range of vocabulary for the task. Attempts to use less common vocabulary but with some inaccuracy. Makes some errors in spelling and/or word formation, but they do not impede communication.",
        "Grammatical Range and Accuracy": "Uses a mix of simple and complex sentence forms. Makes some errors in grammar and punctuation but they rarely reduce communication."
    },
    5: {
        "Task Response": "Addresses the task only partially; the format may be inappropriate in places. Expresses a position but the development is not always clear and there may be no conclusions drawn. Presents some main ideas but these are limited and not sufficiently developed; there may be irrelevant detail.",
        "Coherence and Cohesion": "Presents information with some organization but there may be a lack of overall progression. Makes inadequate, inaccurate or over-use of cohesive devices. May be repetitive because of lack of referencing and substitution. May not write in paragraphs, or paragraphing may be inadequate.",
        "Lexical Resource": "Uses a limited range of vocabulary, but this is minimally adequate for the task. May make noticeable errors in spelling and/or word formation that may cause some difficulty for the reader.",
        "Grammatical Range and Accuracy": "Uses only a limited range of structures. Attempts complex sentences but these tend to be less accurate than simple sentences. May make frequent grammatical errors and punctuation may be faulty; errors can cause some difficulty for the reader."
    },
    4: {
        "Task Response": "Responds to the task only in a minimal way or the answer is tangential; the format may be inappropriate. Presents a position but this is unclear. Presents some main ideas but these are difficult to identify and may be repetitive, irrelevant or not well supported.",
        "Coherence and Cohesion": "Presents information and ideas but these are not arranged coherently and there is no clear progression in the response. Uses some basic cohesive devices but these may be inaccurate or repetitive. May not write in paragraphs or their use may be confusing.",
        "Lexical Resource": "Uses only basic vocabulary which may be used repetitively or which may be inappropriate for the task. Has limited control of word formation and/or spelling; errors may cause strain for the reader.",
        "Grammatical Range and Accuracy": "Uses only a very limited range of structures with only rare use of subordinate clauses. Some structures are accurate but errors predominate, and punctuation is often faulty."
    },
    3: {
        "Task Response": "Does not adequately address any part of the task. Does not express a clear position. Presents few ideas, which are largely undeveloped or irrelevant.",
        "Coherence and Cohesion": "Does not organize ideas logically. May use a very limited range of cohesive devices, and those used may not indicate a logical relationship between ideas.",
        "Lexical Resource": "Uses only a very limited range of words and expressions with very limited control of word formation and/or spelling. Errors may severely distort the message.",
        "Grammatical Range and Accuracy": "Attempts sentence forms but errors in grammar and punctuation predominate and distort the meaning."
    },
    2: {
        "Task Response": "Barely responds to the task. Does not express a position. May attempt to present one or two ideas but there is no development.",
        "Coherence and Cohesion": "Has very little control of organizational features.",
        "Lexical Resource": "Uses an extremely limited range of vocabulary; essentially no control of word formation and/or spelling.",
        "Grammatical Range and Accuracy": "Cannot use sentence forms except in memorized phrases."
    },
    1: {
        "Task Response": "Answer is completely unrelated to the task.",
        "Coherence and Cohesion": "Fails to communicate any message.",
        "Lexical Resource": "Can only use a few isolated words.",
        "Grammatical Range and Accuracy": "Cannot use sentence forms at all."
    },
    0: {
        "Task Response": "Candidate did not attend or did not attempt the task in any way.",
        "Coherence and Cohesion": "Candidate did not attend or did not attempt the task in any way.",
        "Lexical Resource": "Candidate did not attend or did not attempt the task in any way.",
        "Grammatical Range and Accuracy": "Candidate did not attend or did not attempt the task in any way."
    }
}

# Function to calculate overall band score for writing
def calculate_writing_band_score(task1_scores, task2_scores):
    """
    Calculate the overall IELTS writing band score based on the Task 1 and Task 2 scores.
    Task 2 is weighted more heavily than Task 1 (twice the weight).
    
    Args:
        task1_scores (dict): Dictionary with Task 1 scores for each criterion
            {
                "Task Achievement": float,
                "Coherence and Cohesion": float,
                "Lexical Resource": float,
                "Grammatical Range and Accuracy": float
            }
        task2_scores (dict): Dictionary with Task 2 scores for each criterion
            {
                "Task Response": float,
                "Coherence and Cohesion": float,
                "Lexical Resource": float,
                "Grammatical Range and Accuracy": float
            }
    
    Returns:
        float: Overall band score (rounded to nearest 0.5 or whole number)
    """
    # Validate task1_scores
    if not all(key in task1_scores for key in ["Task Achievement", "Coherence and Cohesion", 
                                             "Lexical Resource", "Grammatical Range and Accuracy"]):
        raise ValueError("Missing required criteria in task1_scores dictionary")
    
    # Validate task2_scores
    if not all(key in task2_scores for key in ["Task Response", "Coherence and Cohesion", 
                                             "Lexical Resource", "Grammatical Range and Accuracy"]):
        raise ValueError("Missing required criteria in task2_scores dictionary")
    
    # Calculate average for Task 1
    task1_avg = sum(task1_scores.values()) / 4
    
    # Calculate average for Task 2
    task2_avg = sum(task2_scores.values()) / 4
    
    # Apply weighting (Task 2 is weighted at twice Task 1)
    weighted_avg = (task1_avg + (task2_avg * 2)) / 3
    
    # Round to nearest 0.5 or whole number
    return round(weighted_avg * 2) / 2