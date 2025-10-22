#!/usr/bin/env python3
"""
Comprehensive Test Scenarios for QR Authentication System
Simulates various user flows and edge cases for Lambda backend testing
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

class QRTestScenarios:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        result = {
            'test': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def test_valid_purchase_flow(self):
        """Test 1: Complete valid purchase to assessment access flow"""
        try:
            # Step 1: Generate QR token after mock purchase
            purchase_data = {
                'user_email': 'test.scenario1@example.com',
                'product_id': 'academic_speaking_assessment',
                'purchase_verified': True,
                'receipt_data': 'mock_receipt_12345',
                'transaction_id': f'mock_{uuid.uuid4()}'
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/generate-qr", 
                                       json=purchase_data)
            
            if response.status_code != 200:
                self.log_result("Valid Purchase Flow", False, f"QR generation failed: {response.status_code}")
                return
                
            qr_data = response.json()
            token = qr_data['token_id']
            
            # Step 2: Verify QR token (simulate website scan)
            verify_response = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                              json={'token': token})
            
            if verify_response.status_code != 200:
                self.log_result("Valid Purchase Flow", False, f"QR verification failed: {verify_response.status_code}")
                return
                
            verify_data = verify_response.json()
            session_id = verify_data['session_id']
            
            # Step 3: Access purchased assessment
            self.session.cookies.set('qr_session_id', session_id)
            assessment_response = self.session.get(f"{BASE_URL}/assessment/academic_speaking_assessment")
            
            if assessment_response.status_code == 200:
                self.log_result("Valid Purchase Flow", True, "Complete flow successful")
            else:
                self.log_result("Valid Purchase Flow", False, f"Assessment access failed: {assessment_response.status_code}")
                
        except Exception as e:
            self.log_result("Valid Purchase Flow", False, f"Exception: {str(e)}")
    
    def test_expired_token_scenario(self):
        """Test 2: Expired QR token handling"""
        try:
            # Generate token and manually expire it
            purchase_data = {
                'user_email': 'test.scenario2@example.com',
                'product_id': 'academic_writing_assessment',
                'purchase_verified': True
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/generate-qr", json=purchase_data)
            qr_data = response.json()
            token = qr_data['token_id']
            
            # Simulate token expiry by waiting or manually expiring
            # For testing, we'll modify the token's expiry time in the backend
            # In real scenario, we'd wait 10+ minutes
            
            time.sleep(1)  # Brief delay to simulate time passage
            
            # Try to verify expired token
            verify_response = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                              json={'token': token})
            
            # Should fail with 401 for expired token
            if verify_response.status_code == 401:
                error_data = verify_response.json()
                if 'expired' in error_data.get('error', '').lower():
                    self.log_result("Expired Token Scenario", True, "Correctly rejected expired token")
                else:
                    self.log_result("Expired Token Scenario", False, "Wrong error message for expired token")
            else:
                self.log_result("Expired Token Scenario", False, f"Unexpected response: {verify_response.status_code}")
                
        except Exception as e:
            self.log_result("Expired Token Scenario", False, f"Exception: {str(e)}")
    
    def test_invalid_token_scenario(self):
        """Test 3: Invalid/fake token handling"""
        try:
            fake_token = str(uuid.uuid4())
            
            verify_response = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                              json={'token': fake_token})
            
            if verify_response.status_code == 401:
                error_data = verify_response.json()
                if 'invalid' in error_data.get('error', '').lower():
                    self.log_result("Invalid Token Scenario", True, "Correctly rejected invalid token")
                else:
                    self.log_result("Invalid Token Scenario", False, "Wrong error message for invalid token")
            else:
                self.log_result("Invalid Token Scenario", False, f"Unexpected response: {verify_response.status_code}")
                
        except Exception as e:
            self.log_result("Invalid Token Scenario", False, f"Exception: {str(e)}")
    
    def test_used_token_scenario(self):
        """Test 4: Already used token handling"""
        try:
            # Generate and use token once
            purchase_data = {
                'user_email': 'test.scenario4@example.com',
                'product_id': 'general_speaking_assessment',
                'purchase_verified': True
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/generate-qr", json=purchase_data)
            qr_data = response.json()
            token = qr_data['token_id']
            
            # Use token first time (should succeed)
            first_verify = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                           json={'token': token})
            
            if first_verify.status_code != 200:
                self.log_result("Used Token Scenario", False, "First token use failed")
                return
            
            # Try to use same token again (should fail)
            second_verify = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                            json={'token': token})
            
            if second_verify.status_code == 401:
                error_data = second_verify.json()
                if 'used' in error_data.get('error', '').lower():
                    self.log_result("Used Token Scenario", True, "Correctly rejected already used token")
                else:
                    self.log_result("Used Token Scenario", False, "Wrong error message for used token")
            else:
                self.log_result("Used Token Scenario", False, f"Unexpected response: {second_verify.status_code}")
                
        except Exception as e:
            self.log_result("Used Token Scenario", False, f"Exception: {str(e)}")
    
    def test_multiple_product_purchases(self):
        """Test 5: User with multiple purchased products"""
        try:
            user_email = 'test.scenario5@example.com'
            products = ['academic_speaking_assessment', 'academic_writing_assessment']
            
            tokens = []
            for product in products:
                purchase_data = {
                    'user_email': user_email,
                    'product_id': product,
                    'purchase_verified': True
                }
                
                response = self.session.post(f"{BASE_URL}/api/auth/generate-qr", json=purchase_data)
                if response.status_code != 200:
                    self.log_result("Multiple Products", False, f"Failed to generate QR for {product}")
                    return
                
                qr_data = response.json()
                tokens.append(qr_data['token_id'])
            
            # Use latest token to authenticate
            verify_response = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                              json={'token': tokens[-1]})
            
            if verify_response.status_code != 200:
                self.log_result("Multiple Products", False, "Authentication failed")
                return
            
            verify_data = verify_response.json()
            session_id = verify_data['session_id']
            self.session.cookies.set('qr_session_id', session_id)
            
            # Test access to both purchased assessments
            success_count = 0
            for product in products:
                assessment_response = self.session.get(f"{BASE_URL}/assessment/{product}")
                if assessment_response.status_code == 200:
                    success_count += 1
            
            if success_count == len(products):
                self.log_result("Multiple Products", True, f"Access granted to all {len(products)} purchased assessments")
            else:
                self.log_result("Multiple Products", False, f"Access granted to only {success_count}/{len(products)} assessments")
                
        except Exception as e:
            self.log_result("Multiple Products", False, f"Exception: {str(e)}")
    
    def test_unpurchased_assessment_access(self):
        """Test 6: Attempt to access unpurchased assessment"""
        try:
            # Purchase only one product
            purchase_data = {
                'user_email': 'test.scenario6@example.com',
                'product_id': 'academic_speaking_assessment',
                'purchase_verified': True
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/generate-qr", json=purchase_data)
            qr_data = response.json()
            token = qr_data['token_id']
            
            # Authenticate with valid token
            verify_response = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                              json={'token': token})
            verify_data = verify_response.json()
            session_id = verify_data['session_id']
            self.session.cookies.set('qr_session_id', session_id)
            
            # Try to access unpurchased assessment
            assessment_response = self.session.get(f"{BASE_URL}/assessment/general_writing_assessment")
            
            if assessment_response.status_code == 200:
                content = assessment_response.text
                if 'access_restricted' in content or 'requires a purchase' in content.lower():
                    self.log_result("Unpurchased Access", True, "Correctly blocked access to unpurchased assessment")
                else:
                    self.log_result("Unpurchased Access", False, "Allowed access to unpurchased assessment")
            else:
                self.log_result("Unpurchased Access", True, "Correctly redirected unpurchased assessment access")
                
        except Exception as e:
            self.log_result("Unpurchased Access", False, f"Exception: {str(e)}")
    
    def test_session_persistence(self):
        """Test 7: Session persistence across requests"""
        try:
            # Create session
            purchase_data = {
                'user_email': 'test.scenario7@example.com',
                'product_id': 'general_speaking_assessment',
                'purchase_verified': True
            }
            
            response = self.session.post(f"{BASE_URL}/api/auth/generate-qr", json=purchase_data)
            qr_data = response.json()
            token = qr_data['token_id']
            
            verify_response = self.session.post(f"{BASE_URL}/api/auth/verify-qr",
                                              json={'token': token})
            verify_data = verify_response.json()
            session_id = verify_data['session_id']
            self.session.cookies.set('qr_session_id', session_id)
            
            # Test multiple assessment accesses with same session
            access_count = 0
            for _ in range(3):
                assessment_response = self.session.get(f"{BASE_URL}/assessment/general_speaking_assessment")
                if assessment_response.status_code == 200:
                    access_count += 1
                time.sleep(0.5)
            
            if access_count == 3:
                self.log_result("Session Persistence", True, "Session persisted across multiple requests")
            else:
                self.log_result("Session Persistence", False, f"Session failed after {3-access_count} requests")
                
        except Exception as e:
            self.log_result("Session Persistence", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Execute all test scenarios"""
        print("🧪 Starting QR Authentication Test Suite")
        print("=" * 50)
        
        test_methods = [
            self.test_valid_purchase_flow,
            self.test_expired_token_scenario,
            self.test_invalid_token_scenario,
            self.test_used_token_scenario,
            self.test_multiple_product_purchases,
            self.test_unpurchased_assessment_access,
            self.test_session_persistence
        ]
        
        for test_method in test_methods:
            print(f"\n🔄 Running {test_method.__name__}...")
            test_method()
            time.sleep(1)  # Brief pause between tests
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n📝 Detailed test log saved with {len(self.test_results)} entries")
        
        # Save detailed results to file
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)

if __name__ == "__main__":
    tester = QRTestScenarios()
    tester.run_all_tests()