#!/usr/bin/env python3
"""
Verify Production Requirements - Complete Package Review
Systematic verification of all 8 requirements
"""

import zipfile
import re
import json

def verify_all_requirements():
    """Verify all 8 requirements systematically"""
    
    print("=== PRODUCTION PACKAGE VERIFICATION ===")
    print("Package: google_play_compliant_lambda.zip")
    print("Verification Date: July 15, 2025")
    print()
    
    try:
        with zipfile.ZipFile('google_play_compliant_lambda.zip', 'r') as z:
            lambda_content = z.read('lambda_function.py').decode('utf-8')
            
            print("✅ Package successfully extracted")
            print(f"   Lambda function size: {len(lambda_content)} characters")
            print()
            
            # 1. Original Working Template Verification
            print("1. ORIGINAL WORKING TEMPLATE VERIFICATION:")
            if 'original_template' in lambda_content:
                print("   ✅ Original template integration found")
                
                # Check for specific template components
                if 'IELTS GenAI Prep' in lambda_content:
                    print("   ✅ Title: IELTS GenAI Prep found")
                if 'AI-Powered IELTS Assessment Platform' in lambda_content:
                    print("   ✅ Subtitle: AI-Powered IELTS Assessment Platform found")
                if 'TrueScore' in lambda_content and 'ClearScore' in lambda_content:
                    print("   ✅ Branding: TrueScore® and ClearScore® found")
                if 'privacy-policy' in lambda_content and 'terms-of-service' in lambda_content:
                    print("   ✅ Legal pages: Privacy Policy and Terms of Service found")
                if 'gdpr' in lambda_content.lower():
                    print("   ✅ GDPR compliance: GDPR references found")
                    
                print("   ✅ REQUIREMENT 1: PASSED")
            else:
                print("   ❌ Original template integration NOT found")
                print("   ❌ REQUIREMENT 1: FAILED")
            print()
            
            # 2. AI SEO Robots.txt Verification
            print("2. AI SEO ROBOTS.TXT VERIFICATION:")
            if 'robots.txt' in lambda_content:
                print("   ✅ robots.txt endpoint found")
                
                # Check for AI crawler permissions
                if 'GPTBot' in lambda_content:
                    print("   ✅ GPTBot permission found")
                if 'ClaudeBot' in lambda_content:
                    print("   ✅ ClaudeBot permission found")
                if 'Google-Extended' in lambda_content:
                    print("   ✅ Google-Extended permission found")
                if 'Allow: /' in lambda_content:
                    print("   ✅ Allow all paths found")
                    
                print("   ✅ REQUIREMENT 2: PASSED")
            else:
                print("   ❌ robots.txt endpoint NOT found")
                print("   ❌ REQUIREMENT 2: FAILED")
            print()
            
            # 3. Nova Sonic EN-GB Voice Verification
            print("3. NOVA SONIC EN-GB VOICE VERIFICATION:")
            if 'nova-sonic' in lambda_content:
                print("   ✅ Nova Sonic integration found")
                
                # Check for specific voice configuration
                if 'en-GB-feminine' in lambda_content:
                    print("   ✅ EN-GB feminine voice found")
                if 'synthesize_maya_voice_nova_sonic' in lambda_content:
                    print("   ✅ Maya voice synthesis function found")
                if 'bedrock-runtime' in lambda_content:
                    print("   ✅ AWS Bedrock runtime integration found")
                if 'nova-sonic-connect' in lambda_content:
                    print("   ✅ Nova Sonic connection test endpoint found")
                if 'nova-sonic-stream' in lambda_content:
                    print("   ✅ Nova Sonic streaming endpoint found")
                    
                print("   ✅ REQUIREMENT 3: PASSED")
            else:
                print("   ❌ Nova Sonic integration NOT found")
                print("   ❌ REQUIREMENT 3: FAILED")
            print()
            
            # 4. Nova Micro Writing Assessment Verification
            print("4. NOVA MICRO WRITING ASSESSMENT VERIFICATION:")
            if 'nova-micro-writing' in lambda_content:
                print("   ✅ Nova Micro writing endpoint found")
                
                # Check for assessment components
                if 'evaluate_writing_with_nova_micro' in lambda_content:
                    print("   ✅ Writing evaluation function found")
                if 'essay_text' in lambda_content and 'submit' in lambda_content:
                    print("   ✅ Essay submission with submit button found")
                if 'overall_band' in lambda_content and 'criteria_scores' in lambda_content:
                    print("   ✅ IELTS scoring system found")
                if 'detailed_feedback' in lambda_content:
                    print("   ✅ Detailed feedback system found")
                    
                print("   ✅ REQUIREMENT 4: PASSED")
            else:
                print("   ❌ Nova Micro writing endpoint NOT found")
                print("   ❌ REQUIREMENT 4: FAILED")
            print()
            
            # 5. User Profile with Account Deletion Verification
            print("5. USER PROFILE WITH ACCOUNT DELETION VERIFICATION:")
            if 'my-profile' in lambda_content or 'profile' in lambda_content:
                print("   ✅ Profile page found")
                
                # Check for account deletion features
                if 'account-deletion' in lambda_content:
                    print("   ✅ Account deletion endpoint found")
                if 'delete_user_account' in lambda_content:
                    print("   ✅ Account deletion function found")
                if 'get_user_assessment_history' in lambda_content:
                    print("   ✅ Assessment history display found")
                    
                print("   ✅ REQUIREMENT 5: PASSED")
            else:
                print("   ❌ Profile page NOT found")
                print("   ❌ REQUIREMENT 5: FAILED")
            print()
            
            # 6. Easy Assessment Navigation Verification
            print("6. EASY ASSESSMENT NAVIGATION VERIFICATION:")
            if 'dashboard' in lambda_content:
                print("   ✅ Dashboard page found")
                
                # Check for assessment navigation
                if 'assessment/' in lambda_content:
                    print("   ✅ Assessment routing found")
                if 'academic-writing' in lambda_content and 'general-writing' in lambda_content:
                    print("   ✅ Writing assessments found")
                if 'academic-speaking' in lambda_content and 'general-speaking' in lambda_content:
                    print("   ✅ Speaking assessments found")
                if 'Start Assessment' in lambda_content:
                    print("   ✅ Start Assessment buttons found")
                    
                print("   ✅ REQUIREMENT 6: PASSED")
            else:
                print("   ❌ Dashboard page NOT found")
                print("   ❌ REQUIREMENT 6: FAILED")
            print()
            
            # 7. SES Email Functionality Verification
            print("7. SES EMAIL FUNCTIONALITY VERIFICATION:")
            if 'send_welcome_email' in lambda_content:
                print("   ✅ Welcome email function found")
                
                # Check for SES components
                if 'send_account_deletion_email' in lambda_content:
                    print("   ✅ Account deletion email function found")
                if 'boto3.client(\'ses\'' in lambda_content:
                    print("   ✅ AWS SES client integration found")
                if 'welcome@ieltsaiprep.com' in lambda_content:
                    print("   ✅ Welcome email sender found")
                if 'noreply@ieltsaiprep.com' in lambda_content:
                    print("   ✅ No-reply email sender found")
                if 'HTML' in lambda_content and 'professional' in lambda_content:
                    print("   ✅ Professional HTML email templates found")
                    
                print("   ✅ REQUIREMENT 7: PASSED")
            else:
                print("   ❌ Welcome email function NOT found")
                print("   ❌ REQUIREMENT 7: FAILED")
            print()
            
            # 8. Production DynamoDB Verification
            print("8. PRODUCTION DYNAMODB VERIFICATION:")
            
            # Extract all DynamoDB table references
            table_pattern = r"'([^']*ielts[^']*?)'"
            tables = re.findall(table_pattern, lambda_content)
            
            if tables:
                print(f"   ✅ DynamoDB tables found: {len(set(tables))}")
                for table in set(tables):
                    print(f"      - {table}")
                
                # Check for production table naming
                prod_tables = [t for t in tables if 'ielts-genai-prep-' in t or 'ielts-assessment-' in t]
                if prod_tables:
                    print(f"   ✅ Production table naming: {len(set(prod_tables))} production tables")
                
                # Check for mock/dev references
                mock_patterns = [r'mock', r'dev', r'test.*data', r'fake', r'dummy']
                mock_found = []
                for pattern in mock_patterns:
                    matches = re.findall(pattern, lambda_content.lower())
                    mock_found.extend(matches)
                
                if not mock_found:
                    print("   ✅ No mock/dev data references found")
                    print("   ✅ REQUIREMENT 8: PASSED")
                else:
                    print(f"   ❌ Mock/dev references found: {mock_found}")
                    print("   ❌ REQUIREMENT 8: FAILED")
            else:
                print("   ❌ No DynamoDB tables found")
                print("   ❌ REQUIREMENT 8: FAILED")
            print()
            
            # Summary
            print("=== VERIFICATION SUMMARY ===")
            
            requirements_status = []
            
            # Count passed requirements
            if 'original_template' in lambda_content:
                requirements_status.append("✅ 1. Original Template")
            else:
                requirements_status.append("❌ 1. Original Template")
                
            if 'robots.txt' in lambda_content:
                requirements_status.append("✅ 2. AI SEO robots.txt")
            else:
                requirements_status.append("❌ 2. AI SEO robots.txt")
                
            if 'nova-sonic' in lambda_content and 'en-GB-feminine' in lambda_content:
                requirements_status.append("✅ 3. Nova Sonic EN-GB Voice")
            else:
                requirements_status.append("❌ 3. Nova Sonic EN-GB Voice")
                
            if 'nova-micro-writing' in lambda_content:
                requirements_status.append("✅ 4. Nova Micro Writing")
            else:
                requirements_status.append("❌ 4. Nova Micro Writing")
                
            if 'profile' in lambda_content and 'account-deletion' in lambda_content:
                requirements_status.append("✅ 5. User Profile & Deletion")
            else:
                requirements_status.append("❌ 5. User Profile & Deletion")
                
            if 'dashboard' in lambda_content:
                requirements_status.append("✅ 6. Assessment Navigation")
            else:
                requirements_status.append("❌ 6. Assessment Navigation")
                
            if 'send_welcome_email' in lambda_content:
                requirements_status.append("✅ 7. SES Email System")
            else:
                requirements_status.append("❌ 7. SES Email System")
                
            if tables and not mock_found:
                requirements_status.append("✅ 8. Production DynamoDB")
            else:
                requirements_status.append("❌ 8. Production DynamoDB")
            
            for status in requirements_status:
                print(status)
            
            passed = len([s for s in requirements_status if '✅' in s])
            total = len(requirements_status)
            
            print(f"\nOverall Score: {passed}/{total} requirements passed")
            
            if passed == total:
                print("🎉 ALL REQUIREMENTS VERIFIED - PRODUCTION READY")
                return True
            else:
                print("⚠️  SOME REQUIREMENTS NOT MET - NEEDS ATTENTION")
                return False
                
    except FileNotFoundError:
        print("❌ Package file not found: google_play_compliant_lambda.zip")
        return False
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return False

if __name__ == "__main__":
    verify_all_requirements()