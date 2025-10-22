#!/usr/bin/env python3
"""
Update Speaking Question Bank with Complete 3-Part IELTS Structure
Integrate Part 1, Part 2, and Part 3 questions from knowledge base export files
"""

import json
import time
from aws_mock_config import AWSMockServices

def load_part_1_questions():
    """Load Part 1 questions from knowledge base export"""
    questions = [
        "Tell me about your favorite hobby and why you enjoy it.",
        "Tell me about your job. What responsibilities do you have?",
        "What do you like or dislike about your studies?",
        "Would you prefer to work in a large company or a small company? Why?",
        "Can you describe the place where you live?",
        "What kind of accommodation do you live in?",
        "What changes would you like to make to your home?",
        "Describe your hometown. What is it known for?",
        "Is your hometown a good place for tourists to visit? Why or why not?",
        "How has your hometown changed in recent years?",
        "What activities do you enjoy doing in your free time?",
        "Do you prefer indoor or outdoor activities? Why?",
        "How important is it to have hobbies?",
        "How often do you use computers or technology in your daily life?",
        "What impact does technology have on your work or studies?",
        "Do you think people rely too much on technology nowadays?",
        "What kind of places do you like to visit on vacation?",
        "Do you prefer traveling alone or with other people? Why?",
        "What's the most interesting journey you've ever taken?"
    ]
    return questions

def load_part_2_questions():
    """Load Part 2 questions from knowledge base export"""
    questions = [
        "Describe a place you have visited that had a significant impact on you. You should say: where the place is, when you went there, what you did there, and explain why this place had such an impact on you.",
        "Describe a person who has had a significant influence on your life. You should say: who this person is, how you know them, what they do, and explain why they have influenced you so much.",
        "Describe a teacher who has influenced you. You should say: when you met them, what subject they taught, what was special about them, and explain how they influenced your life.",
        "Describe a friend who is a good leader. You should say: who the person is, how you know this person, what leadership qualities they have, and explain why you think they are a good leader.",
        "Describe a public place you like to visit. You should say: where it is, when you usually go there, what you do there, and explain why you like this place.",
        "Describe a historic building you have visited. You should say: where it is, when you visited it, what the building looks like, and explain why you visited this building.",
        "Describe a place in your country that you would recommend someone visit. You should say: where it is, what people can do there, when is the best time to visit, and explain why you would recommend this place.",
        "Describe an important object in your life. You should say: what it is, how long you've had it, where you got it from, and explain why it's important to you.",
        "Describe a piece of technology that you find useful. You should say: what it is, what you use it for, how often you use it, and explain why it is so useful to you.",
        "Describe a book that has influenced you. You should say: what kind of book it is, what it is about, when you first read it, and explain how it has influenced you.",
        "Describe a skill you would like to learn. You should say: what this skill is, why you want to learn it, how you would learn it, and explain how this skill would be useful to you in the future.",
        "Describe a time when you helped someone. You should say: who you helped, what you did, why they needed help, and explain how you felt about helping this person.",
        "Describe an important decision you have made. You should say: what the decision was, when you made it, why you made this decision, and explain how this decision changed your life.",
        "Describe a special event you attended. You should say: what the event was, where and when it was held, who was there with you, and explain why it was special to you.",
        "Describe a tradition in your country. You should say: what the tradition is, when and how people celebrate it, how people prepare for it, and explain what you like or dislike about this tradition.",
        "Describe a time when you had to work with a group. You should say: what you were working on, who you worked with, how long you worked together, and explain how you felt about this experience."
    ]
    return questions

def load_part_3_questions():
    """Load Part 3 questions from knowledge base export"""
    questions = [
        "Do you think travel is an important part of education? Why or why not?",
        "What changes do you think will happen in education in the future?",
        "Do you think students should be able to choose what they study at school?",
        "How important do you think it is for people to continue learning throughout their lives?",
        "What factors should people consider when choosing a career?",
        "Do you think it's better to have one job for life or to change jobs regularly?",
        "How has technology changed the way people work in your country?",
        "What environmental problems does your country face today?",
        "Do you think individuals or governments should be responsible for protecting the environment?",
        "How can we encourage more people to use public transportation instead of cars?",
        "How might technology change the way we live in the future?",
        "Do social media platforms bring people together or push them further apart?",
        "Should there be more regulation of technology and the internet?",
        "How has family life changed in your country in recent decades?",
        "What role should governments play in healthcare and social services?",
        "Is it better to live in a city or in the countryside? Why?",
        "How can countries work together more effectively to solve global problems?",
        "What do you think are the biggest challenges facing young people today?",
        "Do you think international tourism is mostly positive or negative for local communities?"
    ]
    return questions

def create_complete_speaking_questions():
    """Create complete 3-part IELTS speaking questions"""
    aws_mock = AWSMockServices()
    
    part_1_questions = load_part_1_questions()
    part_2_questions = load_part_2_questions()
    part_3_questions = load_part_3_questions()
    
    # Create Academic Speaking Questions with complete 3-part structure
    academic_questions = []
    for i in range(10):
        question = {
            "question_id": f"as_complete_{i+1:03d}",
            "assessment_type": "academic_speaking",
            "parts": [
                {
                    "part": 1,
                    "duration": "4-5 minutes",
                    "topic": "Introduction and Interview",
                    "questions": part_1_questions[i*2:(i*2)+2]  # 2 questions per assessment
                },
                {
                    "part": 2,
                    "duration": "3-4 minutes",
                    "topic": "Individual Long Turn",
                    "prompt": part_2_questions[i],
                    "prep_time": 60,
                    "talk_time": 120
                },
                {
                    "part": 3,
                    "duration": "4-5 minutes", 
                    "topic": "Two-way Discussion",
                    "questions": part_3_questions[i*2:(i*2)+2]  # 2 questions per assessment
                }
            ],
            "total_duration": "11-14 minutes",
            "created_at": int(time.time())
        }
        academic_questions.append(question)
    
    # Create General Speaking Questions with complete 3-part structure
    general_questions = []
    for i in range(10):
        question = {
            "question_id": f"gs_complete_{i+1:03d}",
            "assessment_type": "general_speaking",
            "parts": [
                {
                    "part": 1,
                    "duration": "4-5 minutes",
                    "topic": "Introduction and Interview",
                    "questions": part_1_questions[i*2:(i*2)+2]  # 2 questions per assessment
                },
                {
                    "part": 2,
                    "duration": "3-4 minutes",
                    "topic": "Individual Long Turn",
                    "prompt": part_2_questions[i],
                    "prep_time": 60,
                    "talk_time": 120
                },
                {
                    "part": 3,
                    "duration": "4-5 minutes",
                    "topic": "Two-way Discussion", 
                    "questions": part_3_questions[i*2:(i*2)+2]  # 2 questions per assessment
                }
            ],
            "total_duration": "11-14 minutes",
            "created_at": int(time.time())
        }
        general_questions.append(question)
    
    return academic_questions, general_questions

def update_question_bank():
    """Update the question bank with complete 3-part structure"""
    print("🔄 Updating Speaking Question Bank with Complete 3-Part Structure")
    print("=" * 70)
    
    academic_questions, general_questions = create_complete_speaking_questions()
    
    print(f"✅ Created {len(academic_questions)} complete Academic Speaking assessments")
    print(f"✅ Created {len(general_questions)} complete General Speaking assessments")
    
    # Show sample structure
    print("\n📋 Sample Academic Speaking Structure:")
    sample = academic_questions[0]
    for part in sample['parts']:
        part_num = part['part']
        topic = part['topic']
        duration = part['duration']
        print(f"  Part {part_num}: {topic} ({duration})")
        if 'questions' in part:
            print(f"    Questions: {len(part['questions'])} questions")
        if 'prompt' in part:
            print(f"    Prompt: {part['prompt'][:50]}...")
    
    print(f"\n🎯 Total Questions Available:")
    print(f"   Academic Speaking: {len(academic_questions)} complete assessments")
    print(f"   General Speaking: {len(general_questions)} complete assessments")
    print(f"   Each assessment has proper 3-part IELTS structure")
    
    return academic_questions, general_questions

if __name__ == "__main__":
    update_question_bank()