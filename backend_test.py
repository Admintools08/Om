#!/usr/bin/env python3
"""
Backend API Testing for Branding Pioneers Learning Badge & LinkedIn Post Generator
Tests Gemini API integration and SVG badge generation functionality
"""

import requests
import json
import base64
import re
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_api_health(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Branding Pioneers" in data.get("message", ""):
                    self.log_test("API Health Check", True, "API is accessible and responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, "API responding but unexpected message", str(data))
                    return False
            else:
                self.log_test("API Health Check", False, f"API returned status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Failed to connect to API: {str(e)}")
            return False

    def test_gemini_api_integration(self):
        """Test Gemini API integration with the /api/generate endpoint"""
        test_data = {
            "employeeName": "John Smith",
            "learning": "Advanced React hooks and state management patterns", 
            "difficulty": "Hard"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has required fields
                if "badgeUrl" in data and "linkedinPost" in data:
                    self.log_test("Gemini API Integration", True, 
                                "Successfully called Gemini API and received structured response",
                                f"Response keys: {list(data.keys())}")
                    return data
                else:
                    self.log_test("Gemini API Integration", False,
                                "Response missing required fields (badgeUrl, linkedinPost)",
                                f"Received: {list(data.keys())}")
                    return None
            else:
                self.log_test("Gemini API Integration", False,
                            f"API returned status {response.status_code}",
                            response.text)
                return None
                
        except Exception as e:
            self.log_test("Gemini API Integration", False,
                        f"Failed to call Gemini API: {str(e)}")
            return None

    def test_svg_badge_generation(self, api_response: Dict[Any, Any]):
        """Test SVG badge generation and base64 encoding"""
        if not api_response or "badgeUrl" not in api_response:
            self.log_test("SVG Badge Generation", False, "No badge URL in API response")
            return False
            
        badge_url = api_response["badgeUrl"]
        
        # Check if it's a proper data URL
        if not badge_url.startswith("data:image/svg+xml;base64,"):
            self.log_test("SVG Badge Generation", False,
                        "Badge URL is not a proper base64 SVG data URL",
                        f"URL starts with: {badge_url[:50]}...")
            return False
        
        try:
            # Extract base64 content
            base64_content = badge_url.split("data:image/svg+xml;base64,")[1]
            
            # Decode base64 to get SVG content
            svg_content = base64.b64decode(base64_content).decode('utf-8')
            
            # Validate SVG structure
            if not svg_content.strip().startswith('<svg'):
                self.log_test("SVG Badge Generation", False,
                            "Decoded content is not valid SVG",
                            f"Content starts with: {svg_content[:100]}...")
                return False
            
            # Check for Branding Pioneers elements
            required_elements = [
                "BRANDING",
                "PIONEERS", 
                "John Smith",  # Employee name from test data
                "#FF416C",     # Branding Pioneers gradient color
                "#FF4B2B"      # Branding Pioneers gradient color
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in svg_content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log_test("SVG Badge Generation", False,
                            f"SVG missing required branding elements: {missing_elements}",
                            f"SVG length: {len(svg_content)} chars")
                return False
            
            self.log_test("SVG Badge Generation", True,
                        "SVG badge generated correctly with Branding Pioneers branding and base64 encoding",
                        f"SVG contains all required elements, length: {len(svg_content)} chars")
            return True
            
        except Exception as e:
            self.log_test("SVG Badge Generation", False,
                        f"Failed to decode or validate SVG: {str(e)}")
            return False

    def test_linkedin_post_generation(self, api_response: Dict[Any, Any]):
        """Test LinkedIn post generation quality"""
        if not api_response or "linkedinPost" not in api_response:
            self.log_test("LinkedIn Post Generation", False, "No LinkedIn post in API response")
            return False
            
        linkedin_post = api_response["linkedinPost"]
        
        if not linkedin_post or len(linkedin_post.strip()) < 50:
            self.log_test("LinkedIn Post Generation", False,
                        "LinkedIn post is too short or empty",
                        f"Post length: {len(linkedin_post)} chars")
            return False
        
        # Check for key elements that should be in a good LinkedIn post
        required_elements = [
            "John Smith",  # Employee name
            "React",       # Learning topic (partial match, case insensitive)
        ]
        
        missing_elements = []
        for element in required_elements:
            if element.lower() not in linkedin_post.lower():
                missing_elements.append(element)
        
        # Check for hashtags (optional - AI might not always include them)
        has_hashtags = "#" in linkedin_post
        hashtag_note = " (includes hashtags)" if has_hashtags else " (no hashtags - minor AI generation variance)"
        
        if missing_elements:
            self.log_test("LinkedIn Post Generation", False,
                        f"LinkedIn post missing key elements: {missing_elements}",
                        f"Post preview: {linkedin_post[:200]}...")
            return False
        
        # Check post length (should be reasonable length for LinkedIn)
        word_count = len(linkedin_post.split())
        if word_count < 20:
            self.log_test("LinkedIn Post Generation", False,
                        f"LinkedIn post too short: {word_count} words",
                        f"Post preview: {linkedin_post[:200]}...")
            return False
        
        self.log_test("LinkedIn Post Generation", True,
                    f"LinkedIn post generated successfully with {word_count} words and required elements{hashtag_note}",
                    f"Post preview: {linkedin_post[:150]}...")
        return True

    def test_response_format(self, api_response: Dict[Any, Any]):
        """Test that API response format matches expected structure"""
        if not api_response:
            self.log_test("API Response Format", False, "No API response to validate")
            return False
        
        expected_fields = ["badgeUrl", "linkedinPost"]
        actual_fields = list(api_response.keys())
        
        missing_fields = [field for field in expected_fields if field not in actual_fields]
        extra_fields = [field for field in actual_fields if field not in expected_fields]
        
        if missing_fields:
            self.log_test("API Response Format", False,
                        f"Response missing required fields: {missing_fields}",
                        f"Actual fields: {actual_fields}")
            return False
        
        if extra_fields:
            # Extra fields are not necessarily bad, just note them
            self.log_test("API Response Format", True,
                        f"Response format correct (with extra fields: {extra_fields})",
                        f"All required fields present: {expected_fields}")
        else:
            self.log_test("API Response Format", True,
                        "Response format matches expected structure exactly",
                        f"Fields: {actual_fields}")
        
        return True

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 80)
        print("BRANDING PIONEERS BACKEND API TESTING")
        print("=" * 80)
        print(f"Testing API at: {API_BASE_URL}")
        print()
        
        # Test 1: API Health Check
        if not self.test_api_health():
            print("❌ API health check failed. Stopping tests.")
            return self.get_summary()
        
        # Test 2: Gemini API Integration (main test)
        api_response = self.test_gemini_api_integration()
        
        if api_response:
            # Test 3: SVG Badge Generation
            self.test_svg_badge_generation(api_response)
            
            # Test 4: LinkedIn Post Generation  
            self.test_linkedin_post_generation(api_response)
            
            # Test 5: Response Format
            self.test_response_format(api_response)
        else:
            print("❌ Gemini API integration failed. Skipping dependent tests.")
        
        return self.get_summary()

    def get_summary(self):
        """Get test summary"""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌" in result['status']:
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        return {
            'total_tests': self.passed_tests + self.failed_tests,
            'passed': self.passed_tests,
            'failed': self.failed_tests,
            'success_rate': self.passed_tests / (self.passed_tests + self.failed_tests) * 100 if (self.passed_tests + self.failed_tests) > 0 else 0,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = BackendTester()
    summary = tester.run_all_tests()
    
    if summary['failed'] == 0:
        print("🎉 All tests passed! Backend API is working correctly.")
        exit(0)
    else:
        print(f"⚠️  {summary['failed']} test(s) failed. Check the details above.")
        exit(1)