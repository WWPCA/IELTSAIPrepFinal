"""
IELTS Speaking Assessment Criteria Configuration
This file contains the band descriptors and criteria for IELTS speaking assessment.
"""

# IELTS Speaking Test Format
SPEAKING_TEST_FORMAT = {
    "total_duration": "11-14 minutes",
    "parts": [
        {
            "part": 1,
            "name": "Introduction and Interview",
            "duration": "4-5 minutes",
            "description": "The examiner introduces themselves and asks the candidate to introduce themselves and confirm their identity. The examiner then asks general questions on familiar topics such as home, family, work, studies and interests."
        },
        {
            "part": 2,
            "name": "Individual Long Turn",
            "duration": "3-4 minutes",
            "description": "The examiner gives the candidate a task card which asks the candidate to talk about a particular topic, includes points to cover in their talk, and instructs the candidate to explain one aspect of the topic. Candidates are given 1 minute to prepare their talk, and are given a pencil and paper to make notes. The examiner asks the candidate to talk for 1-2 minutes, stops the candidate after 2 minutes, and asks one or two questions on the same topic."
        },
        {
            "part": 3,
            "name": "Two-way Discussion",
            "duration": "4-5 minutes",
            "description": "The examiner asks further questions which are connected to the topic of Part 2. These questions give the candidate an opportunity to discuss more abstract issues and ideas."
        }
    ]
}

# IELTS Speaking Assessment Criteria
SPEAKING_ASSESSMENT_CRITERIA = [
    {
        "name": "Fluency and Coherence",
        "description": "This refers to the ability to talk with normal levels of continuity, rate and effort and to link ideas and language together to form coherent, connected speech. The key indicators are:- speech rate, continuity, connected ideas, use of cohesive devices, and related functions."
    },
    {
        "name": "Lexical Resource",
        "description": "This refers to the range of vocabulary used and the precision with which meanings and attitudes can be expressed. The key indicators are: the variety of words used, the adequacy and appropriacy of the words used, the ability to circumlocute (get round a vocabulary gap by using other words) with or without noticeable hesitation."
    },
    {
        "name": "Grammatical Range and Accuracy",
        "description": "This refers to the range and accurate use of the candidate's grammatical resource. The key indicators are: the length and complexity of the spoken sentences, the appropriate use of subordinate clauses, the range of sentence structures, the ability to use complex structures flexibly, the frequency of grammatical errors, and the effect of errors on communication."
    },
    {
        "name": "Pronunciation",
        "description": "This refers to the ability to produce comprehensible speech to fulfill the speaking test requirements. The key indicators are: the amount of strain caused to the listener, the amount of unintelligible speech, the noticeability of L1 influence, and related features such as stress, intonation, and clarity of articulation."
    }
]

# IELTS Speaking Band Descriptors
SPEAKING_BAND_DESCRIPTORS = {
    9: {
        "Fluency and Coherence": "Fluent with only very occasional repetition or self correction. Any hesitation that occurs is used only to prepare the content of the next utterance and not to find words or grammar. Speech is situationally appropriate and cohesive features are fully acceptable. Topic development is fully coherent and appropriately extended.",
        "Lexical Resource": "Total flexibility and precise use in all contexts. Sustained use of accurate and idiomatic language.",
        "Grammatical Range and Accuracy": "Structures are precise and accurate at all times, apart from 'mistakes' characteristic of native speaker speech.",
        "Pronunciation": "Uses a full range of phonological features to convey precise and/or subtle meaning. Flexible use of features of connected speech is sustained throughout. Can be effortlessly understood throughout. Accent has no effect on intelligibility."
    },
    8: {
        "Fluency and Coherence": "Fluent with only very occasional repetition or self correction. Hesitation may occasionally be used to find words or grammar, but most will be content related. Topic development is coherent, appropriate and relevant.",
        "Lexical Resource": "Wide resource, readily and flexibly used to discuss all topics and convey precise meaning. Skilful use of less common and idiomatic items despite occasional inaccuracies in word choice and collocation. Effective use of paraphrase as required.",
        "Grammatical Range and Accuracy": "Wide range of structures, flexibly used. The majority of sentences are error free. Occasional inappropriacies and non systematic errors occur. A few basic errors may persist.",
        "Pronunciation": "Uses a wide range of phonological features to convey precise and/or subtle meaning. Can sustain appropriate rhythm. Flexible use of stress and intonation across long utterances, despite occasional lapses. Can be easily understood throughout. Accent has minimal effect on intelligibility."
    },
    7: {
        "Fluency and Coherence": "Able to keep going and readily produce long turns without noticeable effort. Some hesitation, repetition and/or self correction may occur, often mid sentence and indicate problems with accessing appropriate language. However, these will not affect coherence. Flexible use of spoken discourse markers, connectives and cohesive features.",
        "Lexical Resource": "Resource flexibly used to discuss a variety of topics. Some ability to use less common and idiomatic items and an awareness of style and collocation is evident though inappropriacies occur. Effective use of paraphrase as required.",
        "Grammatical Range and Accuracy": "A range of structures flexibly used. Error free sentences are frequent. Both simple and complex sentences are used effectively despite some errors. A few basic errors persist.",
        "Pronunciation": "Displays all the positive features of band 6, and some, but not all, of the positive features of band 8."
    },
    6: {
        "Fluency and Coherence": "Able to keep going and demonstrates a willingness to produce long turns. Coherence may be lost at times as a result of hesitation, repetition and/or self correction. Uses a range of spoken discourse markers, connectives and cohesive features though not always appropriately.",
        "Lexical Resource": "Resource sufficient to discuss topics at length. Vocabulary use may be inappropriate but meaning is clear. Generally able to paraphrase successfully.",
        "Grammatical Range and Accuracy": "Produces a mix of short and complex sentence forms and a variety of structures with limited flexibility. Though errors frequently occur in complex structures, these rarely impede communication.",
        "Pronunciation": "Uses a range of phonological features, but control is variable. Chunking is generally appropriate, but rhythm may be affected by a lack of stress timing and/or a rapid speech rate. Some effective use of intonation and stress, but this is not sustained. Individual words or phonemes may be mispronounced but this causes only occasional lack of clarity. Can generally be understood throughout without much effort."
    },
    5: {
        "Fluency and Coherence": "Usually able to keep going, but relies on repetition and self correction to do so and/or on slow speech. Hesitations are often associated with mid sentence searches for fairly basic lexis and grammar. Overuse of certain discourse markers, connectives and other cohesive features. More complex speech usually causes disfluency but simpler language may be produced fluently.",
        "Lexical Resource": "Resource sufficient to discuss familiar and unfamiliar topics but there is limited flexibility. Attempts paraphrase but not always with success.",
        "Grammatical Range and Accuracy": "Basic sentence forms are fairly well controlled for accuracy. Complex structures are attempted but these are limited in range, nearly always contain errors and may lead to the need for reformulation.",
        "Pronunciation": "Displays all the positive features of band 4, and some, but not all, of the positive features of band 6."
    },
    4: {
        "Fluency and Coherence": "Unable to keep going without noticeable pauses. Speech may be slow with frequent repetition. Often self corrects. Can link simple sentences but often with repetitious use of connectives. Some breakdowns in coherence.",
        "Lexical Resource": "Resource sufficient for familiar topics but only basic meaning can be conveyed on unfamiliar topics. Frequent inappropriacies and errors in word choice. Rarely attempts paraphrase.",
        "Grammatical Range and Accuracy": "Can produce basic sentence forms and some short utterances are error free. Subordinate clauses are rare and, overall, turns are short, structures are repetitive and errors are frequent.",
        "Pronunciation": "Uses some acceptable phonological features, but the range is limited. Produces some acceptable chunking, but there are frequent lapses in overall rhythm. Attempts to use intonation and stress, but control is limited. Individual words or phonemes are frequently mispronounced, causing lack of clarity. Understanding requires some effort and there may be patches of speech that cannot be understood."
    },
    3: {
        "Fluency and Coherence": "Frequent, sometimes long, pauses occur while candidate searches for words. Limited ability to link simple sentences and go beyond simple responses to questions. Frequently unable to convey basic message.",
        "Lexical Resource": "Resource limited to simple vocabulary used primarily to convey personal information. Vocabulary inadequate for unfamiliar topics.",
        "Grammatical Range and Accuracy": "Basic sentence forms are attempted but grammatical errors are numerous except in apparently memorised utterances.",
        "Pronunciation": "Displays some features of band 2, and some, but not all, of the positive features of band 4."
    },
    2: {
        "Fluency and Coherence": "Lengthy pauses before nearly every word. Isolated words may be recognisable but speech is of virtually no communicative significance.",
        "Lexical Resource": "Very limited resource. Utterances consist of isolated words or memorised utterances. Little communication possible without the support of mime or gesture.",
        "Grammatical Range and Accuracy": "No evidence of basic sentence forms.",
        "Pronunciation": "Uses few acceptable phonological features (possibly because sample is Overall problems with delivery impair attempts at connected speech. Individual words and phonemes are mainly mispronounced and little meaning is conveyed. Often unintelligible."
    },
    1: {
        "Fluency and Coherence": "Essentially none. Speech is totally incoherent.",
        "Lexical Resource": "No resource bar a few isolated words. No communication possible.",
        "Grammatical Range and Accuracy": "No rateable language unless memorised.",
        "Pronunciation": "Can produce occasional individual words and phonemes that are recognisable, but no overall meaning is conveyed. Unintelligible."
    },
    0: {
        "Fluency and Coherence": "Does not attend or attempt test at all",
        "Lexical Resource": "Does not attend or attempt test at all",
        "Grammatical Range and Accuracy": "Does not attend or attempt test at all",
        "Pronunciation": "Does not attend or attempt test at all"
    }
}

# Function to calculate overall band score
def calculate_speaking_band_score(scores):
    """
    Calculate the overall IELTS speaking band score based on the four criteria scores.
    
    Args:
        scores (dict): Dictionary with scores for each criterion
            {
                "Fluency and Coherence": float,
                "Lexical Resource": float,
                "Grammatical Range and Accuracy": float,
                "Pronunciation": float
            }
    
    Returns:
        float: Overall band score (rounded to nearest 0.5 or whole number)
    """
    if not all(key in scores for key in ["Fluency and Coherence", "Lexical Resource", 
                                        "Grammatical Range and Accuracy", "Pronunciation"]):
        raise ValueError("Missing required criteria in scores dictionary")
    
    # Calculate mean score
    total = sum(scores.values())
    mean = total / 4
    
    # Round to nearest 0.5 or whole number
    return round(mean * 2) / 2