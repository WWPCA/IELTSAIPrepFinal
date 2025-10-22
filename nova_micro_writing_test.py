#!/usr/bin/env python3
"""
Nova Micro Writing Assessment Test
Tests AWS Nova Micro functionality for writing assessments including:
- Text ingestion after user clicks submit
- IELTS rubric processing
- Band result generation with feedback
"""

import requests
import json
import time
import sys

def test_nova_micro_writing_assessment():
    """Test complete Nova Micro writing assessment flow"""
    
    print("🔍 AWS Nova Micro Writing Assessment Test")
    print("Testing text ingestion, IELTS rubric processing, and feedback generation")
    print("=" * 80)
    
    # Test configurations
    base_url = "http://localhost:5000"
    
    # Sample IELTS writing task and response
    sample_task = """
    You should spend about 20 minutes on this task.

    The chart below shows the percentage of households in owned and rented accommodation in England and Wales between 1918 and 2011.

    Summarise the information by selecting and reporting the main features, and make comparisons where relevant.

    Write at least 150 words.
    """
    
    sample_essay = """
    The chart illustrates the proportion of households in owned and rented accommodation in England and Wales from 1918 to 2011.

    Overall, there was a significant shift from rented to owned accommodation over the period. In 1918, approximately 77% of households rented their homes, while only 23% owned them. This trend completely reversed by 2011, when owned accommodation reached about 68% and rented accommodation fell to 32%.

    The most dramatic change occurred between 1953 and 1971, when owned accommodation increased from around 32% to 50%, while rented accommodation decreased correspondingly. This crossing point marked the beginning of owned accommodation becoming the dominant housing type.

    From 1971 onwards, owned accommodation continued to rise steadily, peaking at approximately 69% in 2001 before slightly declining to 68% in 2011. Conversely, rented accommodation reached its lowest point of 31% in 2001 before marginally increasing to 32% in 2011.

    In conclusion, the data shows a clear long-term trend towards home ownership in England and Wales, with owned accommodation becoming the predominant form of housing by the end of the period.
    """
    
    test_cases = [
        {
            "assessment_type": "academic-writing",
            "task": sample_task,
            "essay": sample_essay,
            "expected_criteria": ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
        },
        {
            "assessment_type": "general-writing",
            "task": "Write a letter to your local council about a problem in your neighbourhood.",
            "essay": "Dear Council Members,\n\nI am writing to bring to your attention a persistent problem in our neighbourhood that requires immediate action. The streetlights on Oak Street have been malfunctioning for the past three weeks, creating safety concerns for residents.\n\nThe problem began after the recent storm, when several streetlights were damaged. Since then, the street has been poorly lit during evening hours, making it dangerous for pedestrians and drivers alike. Many residents, particularly elderly people, are reluctant to go out after dark.\n\nI would like to request that the council prioritize the repair of these streetlights as soon as possible. This is not only a matter of convenience but also public safety. I believe this issue affects the entire community and deserves prompt attention.\n\nThank you for your consideration of this matter. I look forward to your prompt response and action.\n\nYours sincerely,\nJohn Smith",
            "expected_criteria": ["Task Achievement", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
        }
    ]
    
    # Test each assessment type
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['assessment_type'].replace('-', ' ').title()}")
        print("=" * 50)
        
        # Test Nova Micro API endpoint
        nova_micro_url = f"{base_url}/api/nova-micro/writing"
        
        payload = {
            "essay_text": test_case["essay"],
            "prompt": test_case["task"],
            "assessment_type": test_case["assessment_type"],
            "session_id": f"test_session_{i}",
            "user_email": "test@ieltsgenaiprep.com"
        }
        
        print(f"📝 Submitting {len(test_case['essay'])} word essay...")
        print(f"📋 Assessment Type: {test_case['assessment_type']}")
        
        try:
            response = requests.post(nova_micro_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Nova Micro Response: Success")
                
                # Check if result contains expected IELTS criteria
                if "assessment_result" in result:
                    assessment = result["assessment_result"]
                    print(f"📊 Overall Band Score: {assessment.get('overall_band', 'Not provided')}")
                    
                    # Check for IELTS criteria breakdown
                    if "criteria_scores" in assessment:
                        print("\n📈 IELTS Criteria Breakdown:")
                        for criterion, score in assessment["criteria_scores"].items():
                            print(f"   • {criterion}: {score}")
                    
                    # Check for detailed feedback
                    if "detailed_feedback" in assessment:
                        print(f"\n💬 Detailed Feedback Available: {len(assessment['detailed_feedback'])} characters")
                        
                    # Check for strengths and improvements
                    if "strengths" in assessment:
                        print(f"   ✅ Strengths: {len(assessment['strengths'])} items")
                    if "areas_for_improvement" in assessment:
                        print(f"   📝 Areas for Improvement: {len(assessment['areas_for_improvement'])} items")
                        
                    # Verify all expected criteria are present
                    missing_criteria = []
                    if "criteria_scores" in assessment:
                        for expected_criterion in test_case["expected_criteria"]:
                            found = False
                            for actual_criterion in assessment["criteria_scores"]:
                                if expected_criterion.lower() in actual_criterion.lower():
                                    found = True
                                    break
                            if not found:
                                missing_criteria.append(expected_criterion)
                    
                    if missing_criteria:
                        print(f"⚠️  Missing Criteria: {', '.join(missing_criteria)}")
                    else:
                        print("✅ All IELTS Criteria Present")
                        
                else:
                    print("❌ No assessment_result in response")
                    
            else:
                print(f"❌ Nova Micro Request Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Raw Response: {response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print("❌ Request Timeout (30 seconds)")
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error - Server not accessible")
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")

def test_nova_micro_rubric_system():
    """Test Nova Micro rubric system and prompt configuration"""
    
    print("\n🔍 Nova Micro Rubric System Test")
    print("Testing IELTS rubric configuration and prompt system")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test rubric retrieval
    assessment_types = ["academic-writing", "general-writing"]
    
    for assessment_type in assessment_types:
        print(f"\n📋 Testing {assessment_type} rubric...")
        
        # Test direct rubric access through health endpoint
        health_url = f"{base_url}/api/health"
        try:
            response = requests.get(health_url)
            if response.status_code == 200:
                health_data = response.json()
                if "rubrics_available" in health_data:
                    print(f"✅ Rubric System: {health_data['rubrics_available']}")
                else:
                    print("ℹ️  Rubric status not in health check")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")

def test_writing_assessment_page_integration():
    """Test writing assessment page integration with Nova Micro"""
    
    print("\n🔍 Writing Assessment Page Integration Test")
    print("Testing HTML page integration with Nova Micro submit functionality")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    assessment_pages = [
        "/assessment/academic-writing",
        "/assessment/general-writing"
    ]
    
    for page in assessment_pages:
        print(f"\n📄 Testing {page}...")
        
        try:
            # Test page accessibility
            response = requests.get(f"{base_url}{page}")
            
            if response.status_code == 200:
                page_content = response.text
                print("✅ Page accessible")
                
                # Check for Nova Micro integration
                integration_checks = [
                    ("Nova Micro API", "/api/nova-micro/writing" in page_content),
                    ("Submit Button", "submitAssessment" in page_content),
                    ("Essay Text Area", "essayText" in page_content),
                    ("Word Count", "updateWordCount" in page_content),
                    ("Timer", "updateTimer" in page_content),
                    ("Assessment Type", "assessment_type" in page_content)
                ]
                
                for check_name, check_result in integration_checks:
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}: {'Found' if check_result else 'Not Found'}")
                    
            else:
                print(f"❌ Page not accessible: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Page test error: {str(e)}")

if __name__ == "__main__":
    print("🚀 AWS Nova Micro Writing Assessment Functionality Test")
    print("Testing complete writing assessment flow with IELTS rubric processing")
    print("=" * 80)
    
    # Run all tests
    test_nova_micro_writing_assessment()
    test_nova_micro_rubric_system()
    test_writing_assessment_page_integration()
    
    print("\n📊 Nova Micro Writing Assessment Test Complete")
    print("=" * 50)
    print("✅ Text ingestion, IELTS rubric processing, and feedback generation tested")
    print("📋 Check results above for detailed Nova Micro functionality status")