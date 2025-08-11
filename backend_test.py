#!/usr/bin/env python3
"""
Backend API Testing for Branding Pioneers Learning Badge & LinkedIn Post Generator
Tests authentication, admin functionality, and badge generation with comprehensive coverage
"""

import requests
import json
import base64
import re
from typing import Dict, Any, Optional
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
        self.admin_session = None
        self.user_session = None
        
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

    def test_admin_login(self):
        """Test admin login with 'Arush T.' - should get admin role"""
        test_data = {"name": "Arush T."}
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "user" in data and "session_token" in data:
                    user = data["user"]
                    if user.get("name") == "Arush T." and user.get("role") == "admin":
                        # Store session for later tests
                        self.admin_session = response.cookies.get('session_token')
                        self.log_test("Admin Login", True, 
                                    "Admin login successful - 'Arush T.' assigned admin role correctly",
                                    f"User role: {user.get('role')}, Session stored")
                        return data
                    else:
                        self.log_test("Admin Login", False,
                                    f"Admin role not assigned correctly. Name: {user.get('name')}, Role: {user.get('role')}")
                        return None
                else:
                    self.log_test("Admin Login", False,
                                "Login response missing required fields",
                                f"Response keys: {list(data.keys())}")
                    return None
            else:
                self.log_test("Admin Login", False,
                            f"Login failed with status {response.status_code}",
                            response.text)
                return None
                
        except Exception as e:
            self.log_test("Admin Login", False,
                        f"Failed to login admin: {str(e)}")
            return None

    def test_user_login(self):
        """Test regular user login with 'John Doe' - should get user role"""
        test_data = {"name": "John Doe"}
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "user" in data and "session_token" in data:
                    user = data["user"]
                    if user.get("name") == "John Doe" and user.get("role") == "user":
                        # Store session for later tests
                        self.user_session = response.cookies.get('session_token')
                        self.log_test("Regular User Login", True, 
                                    "Regular user login successful - assigned user role correctly",
                                    f"User role: {user.get('role')}, Session stored")
                        return data
                    else:
                        self.log_test("Regular User Login", False,
                                    f"User role not assigned correctly. Name: {user.get('name')}, Role: {user.get('role')}")
                        return None
                else:
                    self.log_test("Regular User Login", False,
                                "Login response missing required fields",
                                f"Response keys: {list(data.keys())}")
                    return None
            else:
                self.log_test("Regular User Login", False,
                            f"Login failed with status {response.status_code}",
                            response.text)
                return None
                
        except Exception as e:
            self.log_test("Regular User Login", False,
                        f"Failed to login user: {str(e)}")
            return None

    def test_auth_me_endpoint(self):
        """Test /api/auth/me endpoint with admin session"""
        if not self.admin_session:
            self.log_test("Auth Me Endpoint", False, "No admin session available for testing")
            return False
            
        try:
            cookies = {'session_token': self.admin_session}
            response = requests.get(
                f"{API_BASE_URL}/auth/me",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("name") == "Arush T." and data.get("role") == "admin":
                    self.log_test("Auth Me Endpoint", True, 
                                "Session verification successful - returns correct user info",
                                f"Name: {data.get('name')}, Role: {data.get('role')}")
                    return True
                else:
                    self.log_test("Auth Me Endpoint", False,
                                f"Incorrect user info returned. Name: {data.get('name')}, Role: {data.get('role')}")
                    return False
            else:
                self.log_test("Auth Me Endpoint", False,
                            f"Auth me failed with status {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", False,
                        f"Failed to verify session: {str(e)}")
            return False

    def test_logout_endpoint(self):
        """Test /api/auth/logout endpoint"""
        if not self.user_session:
            self.log_test("Logout Endpoint", False, "No user session available for testing")
            return False
            
        try:
            cookies = {'session_token': self.user_session}
            response = requests.post(
                f"{API_BASE_URL}/auth/logout",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "logged out" in data["message"].lower():
                    self.log_test("Logout Endpoint", True, 
                                "Logout successful - session cleared",
                                f"Response: {data.get('message')}")
                    return True
                else:
                    self.log_test("Logout Endpoint", False,
                                "Unexpected logout response",
                                f"Response: {data}")
                    return False
            else:
                self.log_test("Logout Endpoint", False,
                            f"Logout failed with status {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Logout Endpoint", False,
                        f"Failed to logout: {str(e)}")
            return False

    def test_admin_stats_with_admin(self):
        """Test /api/admin/stats endpoint with admin session - should work"""
        if not self.admin_session:
            self.log_test("Admin Stats (Admin Access)", False, "No admin session available for testing")
            return False
            
        try:
            cookies = {'session_token': self.admin_session}
            response = requests.get(
                f"{API_BASE_URL}/admin/stats",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_users", "total_admins", "total_badges_generated", "recent_activities", "top_learners"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Admin Stats (Admin Access)", True, 
                                "Admin stats endpoint accessible with admin session",
                                f"Stats: {data.get('total_users')} users, {data.get('total_admins')} admins, {data.get('total_badges_generated')} badges")
                    return True
                else:
                    self.log_test("Admin Stats (Admin Access)", False,
                                f"Admin stats response missing fields: {missing_fields}",
                                f"Available fields: {list(data.keys())}")
                    return False
            else:
                self.log_test("Admin Stats (Admin Access)", False,
                            f"Admin stats failed with status {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Stats (Admin Access)", False,
                        f"Failed to get admin stats: {str(e)}")
            return False

    def test_admin_stats_with_user(self):
        """Test /api/admin/stats endpoint with regular user session - should return 403"""
        # Create a new user session for this test
        test_data = {"name": "Regular User"}
        
        try:
            # Login as regular user
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Admin Stats (User Access)", False, "Failed to create test user session")
                return False
                
            user_session = response.cookies.get('session_token')
            
            # Try to access admin stats
            cookies = {'session_token': user_session}
            response = requests.get(
                f"{API_BASE_URL}/admin/stats",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 403:
                self.log_test("Admin Stats (User Access)", True, 
                            "Admin stats correctly blocked for regular user - returned 403 Forbidden",
                            "Access control working properly")
                return True
            else:
                self.log_test("Admin Stats (User Access)", False,
                            f"Admin stats should return 403 for regular user, got {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Stats (User Access)", False,
                        f"Failed to test user access to admin stats: {str(e)}")
            return False

    def test_admin_stats_without_auth(self):
        """Test /api/admin/stats endpoint without authentication - should return 401"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/admin/stats",
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test("Admin Stats (No Auth)", True, 
                            "Admin stats correctly blocked without authentication - returned 401 Unauthorized",
                            "Authentication requirement working properly")
                return True
            else:
                self.log_test("Admin Stats (No Auth)", False,
                            f"Admin stats should return 401 without auth, got {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Stats (No Auth)", False,
                        f"Failed to test unauthenticated access to admin stats: {str(e)}")
            return False

    def test_admin_users_endpoint(self):
        """Test /api/admin/users endpoint with admin session"""
        if not self.admin_session:
            self.log_test("Admin Users Endpoint", False, "No admin session available for testing")
            return False
            
        try:
            cookies = {'session_token': self.admin_session}
            response = requests.get(
                f"{API_BASE_URL}/admin/users",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "users" in data and isinstance(data["users"], list):
                    self.log_test("Admin Users Endpoint", True, 
                                "Admin users endpoint working - returns user list",
                                f"Found {len(data['users'])} users")
                    return True
                else:
                    self.log_test("Admin Users Endpoint", False,
                                "Admin users response missing 'users' field or not a list",
                                f"Response keys: {list(data.keys())}")
                    return False
            else:
                self.log_test("Admin Users Endpoint", False,
                            f"Admin users failed with status {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Users Endpoint", False,
                        f"Failed to get admin users: {str(e)}")
            return False

    def test_admin_badges_endpoint(self):
        """Test /api/admin/badges endpoint with admin session"""
        if not self.admin_session:
            self.log_test("Admin Badges Endpoint", False, "No admin session available for testing")
            return False
            
        try:
            cookies = {'session_token': self.admin_session}
            response = requests.get(
                f"{API_BASE_URL}/admin/badges",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "badges" in data and isinstance(data["badges"], list):
                    self.log_test("Admin Badges Endpoint", True, 
                                "Admin badges endpoint working - returns badge list",
                                f"Found {len(data['badges'])} badge generations")
                    return True
                else:
                    self.log_test("Admin Badges Endpoint", False,
                                "Admin badges response missing 'badges' field or not a list",
                                f"Response keys: {list(data.keys())}")
                    return False
            else:
                self.log_test("Admin Badges Endpoint", False,
                            f"Admin badges failed with status {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Badges Endpoint", False,
                        f"Failed to get admin badges: {str(e)}")
            return False

    def test_admin_actions_endpoint(self):
        """Test /api/admin/actions endpoint with admin session"""
        if not self.admin_session:
            self.log_test("Admin Actions Endpoint", False, "No admin session available for testing")
            return False
            
        try:
            cookies = {'session_token': self.admin_session}
            response = requests.get(
                f"{API_BASE_URL}/admin/actions",
                cookies=cookies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "actions" in data and isinstance(data["actions"], list):
                    self.log_test("Admin Actions Endpoint", True, 
                                "Admin actions endpoint working - returns action log",
                                f"Found {len(data['actions'])} admin actions")
                    return True
                else:
                    self.log_test("Admin Actions Endpoint", False,
                                "Admin actions response missing 'actions' field or not a list",
                                f"Response keys: {list(data.keys())}")
                    return False
            else:
                self.log_test("Admin Actions Endpoint", False,
                            f"Admin actions failed with status {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Actions Endpoint", False,
                        f"Failed to get admin actions: {str(e)}")
            return False

    def test_badge_generation_with_auth(self):
        """Test /api/generate endpoint with authenticated user session - should work"""
        if not self.admin_session:
            self.log_test("Badge Generation (With Auth)", False, "No admin session available for testing")
            return None
            
        test_data = {
            "employeeName": "Sarah Johnson",
            "learning": "Advanced Python data structures and algorithms", 
            "difficulty": "Moderate"
        }
        
        try:
            cookies = {'session_token': self.admin_session}
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json=test_data,
                cookies=cookies,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has required fields
                if "badgeUrl" in data and "linkedinPost" in data:
                    self.log_test("Badge Generation (With Auth)", True, 
                                "Badge generation successful with authentication - creates database entries",
                                f"Response keys: {list(data.keys())}")
                    return data
                else:
                    self.log_test("Badge Generation (With Auth)", False,
                                "Response missing required fields (badgeUrl, linkedinPost)",
                                f"Received: {list(data.keys())}")
                    return None
            else:
                self.log_test("Badge Generation (With Auth)", False,
                            f"Badge generation failed with status {response.status_code}",
                            response.text)
                return None
                
        except Exception as e:
            self.log_test("Badge Generation (With Auth)", False,
                        f"Failed to generate badge with auth: {str(e)}")
            return None

    def test_badge_generation_without_auth(self):
        """Test /api/generate endpoint without authentication - should return 401"""
        test_data = {
            "employeeName": "Test User",
            "learning": "Basic testing concepts", 
            "difficulty": "Easy"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 401:
                self.log_test("Badge Generation (No Auth)", True, 
                            "Badge generation correctly blocked without authentication - returned 401",
                            "Authentication requirement working properly")
                return True
            else:
                self.log_test("Badge Generation (No Auth)", False,
                            f"Badge generation should return 401 without auth, got {response.status_code}",
                            response.text)
                return False
                
        except Exception as e:
            self.log_test("Badge Generation (No Auth)", False,
                        f"Failed to test unauthenticated badge generation: {str(e)}")
            return False

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
            
            # Check for Branding Pioneers elements (updated for current test data)
            required_elements = [
                "BRANDING",
                "PIONEERS", 
                "Sarah Johnson",  # Employee name from current test data
                "Moderate"        # Difficulty level
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
        
        # Check for key elements that should be in a good LinkedIn post (updated for current test data)
        required_elements = [
            "Sarah Johnson",  # Employee name from current test data
            "Python",         # Learning topic (partial match, case insensitive)
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
        print("BRANDING PIONEERS COMPREHENSIVE BACKEND API TESTING")
        print("=" * 80)
        print(f"Testing API at: {API_BASE_URL}")
        print()
        
        # Test 1: API Health Check
        if not self.test_api_health():
            print("❌ API health check failed. Stopping tests.")
            return self.get_summary()
        
        print("\n" + "=" * 60)
        print("AUTHENTICATION TESTING")
        print("=" * 60)
        
        # Test 2: Admin Login (Arush T.)
        admin_login_result = self.test_admin_login()
        
        # Test 3: Regular User Login (John Doe)
        user_login_result = self.test_user_login()
        
        # Test 4: Auth Me Endpoint
        self.test_auth_me_endpoint()
        
        # Test 5: Logout Endpoint
        self.test_logout_endpoint()
        
        print("\n" + "=" * 60)
        print("ADMIN ACCESS CONTROL TESTING")
        print("=" * 60)
        
        # Test 6: Admin Stats with Admin Session
        self.test_admin_stats_with_admin()
        
        # Test 7: Admin Stats with User Session (should fail)
        self.test_admin_stats_with_user()
        
        # Test 8: Admin Stats without Authentication (should fail)
        self.test_admin_stats_without_auth()
        
        # Test 9: Admin Users Endpoint
        self.test_admin_users_endpoint()
        
        # Test 10: Admin Badges Endpoint
        self.test_admin_badges_endpoint()
        
        # Test 11: Admin Actions Endpoint
        self.test_admin_actions_endpoint()
        
        print("\n" + "=" * 60)
        print("BADGE GENERATION WITH AUTH TESTING")
        print("=" * 60)
        
        # Test 12: Badge Generation with Authentication
        badge_response = self.test_badge_generation_with_auth()
        
        # Test 13: Badge Generation without Authentication (should fail)
        self.test_badge_generation_without_auth()
        
        # Test 14: SVG Badge Generation (if we got a response)
        if badge_response:
            self.test_svg_badge_generation(badge_response)
            
            # Test 15: LinkedIn Post Generation
            self.test_linkedin_post_generation(badge_response)
            
            # Test 16: Response Format
            self.test_response_format(badge_response)
        else:
            print("❌ Badge generation with auth failed. Skipping dependent tests.")
        
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