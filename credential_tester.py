"""
Credential Stuffing Tester Module

Tests login forms with provided credentials to assess vulnerability.
Includes rate limiting and safety checks.
"""

import requests
import pandas as pd
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style
from tqdm import tqdm
import asyncio
import aiohttp
from datetime import datetime


class CredentialStuffingTester:
    """Tests credential stuffing vulnerability on login forms"""
    
    def __init__(self, 
                 max_attempts: int = 100,
                 delay_between_attempts: float = 1.0,
                 max_concurrent: int = 5,
                 timeout: int = 10):
        """
        Initialize the tester
        
        Args:
            max_attempts: Maximum number of credential pairs to test
            delay_between_attempts: Delay in seconds between attempts
            max_concurrent: Maximum concurrent requests (for async)
            timeout: Request timeout in seconds
        """
        self.max_attempts = max_attempts
        self.delay_between_attempts = delay_between_attempts
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Results tracking
        self.test_results = {
            'total_attempts': 0,
            'successful_logins': [],
            'failed_logins': [],
            'blocked_attempts': [],
            'errors': [],
            'rate_limited': False,
            'captcha_detected': False,
            'timing_data': []
        }
    
    def load_credentials(self, credential_file: str) -> List[Dict[str, str]]:
        """
        Load credentials from CSV file
        
        Args:
            credential_file: Path to CSV file with username,password columns
            
        Returns:
            List of credential dictionaries
        """
        print(f"\n{Fore.CYAN}[*] Loading credentials from: {credential_file}{Style.RESET_ALL}")
        
        try:
            df = pd.read_csv(credential_file)
            
            # Validate columns
            if 'username' not in df.columns or 'password' not in df.columns:
                raise ValueError("CSV must have 'username' and 'password' columns")
            
            # Convert to list of dicts
            credentials = df[['username', 'password']].to_dict('records')
            
            # Limit to max_attempts
            if len(credentials) > self.max_attempts:
                print(f"{Fore.YELLOW}[!] Limiting to {self.max_attempts} credentials (from {len(credentials)}){Style.RESET_ALL}")
                credentials = credentials[:self.max_attempts]
            
            print(f"{Fore.GREEN}[✓] Loaded {len(credentials)} credential pairs{Style.RESET_ALL}")
            return credentials
            
        except Exception as e:
            print(f"{Fore.RED}[✗] Error loading credentials: {str(e)}{Style.RESET_ALL}")
            return []
    
    def test_login_form(self, 
                       login_page: Dict,
                       credentials: List[Dict[str, str]]) -> Dict:
        """
        Test a login form with credential stuffing
        
        Args:
            login_page: Dictionary with form details from crawler
            credentials: List of username/password pairs
            
        Returns:
            Dictionary with test results
        """
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Testing Login Form{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Target: {login_page['form_action']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Method: {login_page['form_method']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Credentials to test: {len(credentials)}{Style.RESET_ALL}\n")
        
        # Identify username and password field names
        username_field, password_field = self._identify_form_fields(login_page['fields'])
        
        if not username_field or not password_field:
            print(f"{Fore.RED}[✗] Could not identify username/password fields{Style.RESET_ALL}")
            return self.test_results
        
        print(f"{Fore.GREEN}[✓] Identified fields: {username_field} / {password_field}{Style.RESET_ALL}\n")
        
        # Create session for cookies/session handling
        session = requests.Session()
        session.headers.update(self.headers)
        
        # Test credentials with progress bar
        print(f"{Fore.CYAN}[*] Starting credential stuffing test...{Style.RESET_ALL}\n")
        
        for idx, cred in enumerate(tqdm(credentials, desc="Testing credentials", unit="attempt")):
            attempt_start = time.time()
            
            # Prepare login data
            login_data = {
                username_field: cred['username'],
                password_field: cred['password']
            }
            
            # Attempt login
            try:
                response = session.post(
                    login_page['form_action'],
                    data=login_data,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                attempt_time = time.time() - attempt_start
                
                # Analyze response
                result = self._analyze_response(
                    response, 
                    cred,
                    login_page,
                    attempt_time
                )
                
                self.test_results['total_attempts'] += 1
                self.test_results['timing_data'].append(attempt_time)
                
                # Categorize result
                if result['status'] == 'success':
                    self.test_results['successful_logins'].append(result)
                    print(f"\n{Fore.GREEN}[!] POTENTIAL SUCCESS: {cred['username']}{Style.RESET_ALL}")
                elif result['status'] == 'blocked':
                    self.test_results['blocked_attempts'].append(result)
                    print(f"\n{Fore.YELLOW}[!] BLOCKED/RATE LIMITED{Style.RESET_ALL}")
                    self.test_results['rate_limited'] = True
                    break  # Stop testing if blocked
                elif result['status'] == 'captcha':
                    self.test_results['captcha_detected'] = True
                    print(f"\n{Fore.YELLOW}[!] CAPTCHA DETECTED{Style.RESET_ALL}")
                    break  # Stop if CAPTCHA appears
                else:
                    self.test_results['failed_logins'].append(result)
                
                # Rate limiting delay
                time.sleep(self.delay_between_attempts)
                
            except requests.exceptions.Timeout:
                self.test_results['errors'].append({
                    'username': cred['username'],
                    'error': 'Timeout'
                })
            except Exception as e:
                self.test_results['errors'].append({
                    'username': cred['username'],
                    'error': str(e)
                })
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Test Complete{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"Total attempts: {self.test_results['total_attempts']}")
        print(f"{Fore.GREEN}Potential successes: {len(self.test_results['successful_logins'])}{Style.RESET_ALL}")
        print(f"Failed logins: {len(self.test_results['failed_logins'])}")
        print(f"{Fore.YELLOW}Blocked/Rate Limited: {len(self.test_results['blocked_attempts'])}{Style.RESET_ALL}")
        print(f"Errors: {len(self.test_results['errors'])}")
        
        if self.test_results['timing_data']:
            avg_time = sum(self.test_results['timing_data']) / len(self.test_results['timing_data'])
            print(f"Average response time: {avg_time:.2f}s")
        
        return self.test_results
    
    def _identify_form_fields(self, fields: List[str]) -> tuple:
        """Identify which fields are username and password"""
        username_field = None
        password_field = None
        
        # Common username field names
        username_patterns = ['username', 'user', 'email', 'login', 'account', 'userid']
        password_patterns = ['password', 'pass', 'pwd', 'passwd']
        
        for field in fields:
            field_lower = field.lower()
            
            # Check for username
            if not username_field:
                for pattern in username_patterns:
                    if pattern in field_lower:
                        username_field = field
                        break
            
            # Check for password
            if not password_field:
                for pattern in password_patterns:
                    if pattern in field_lower:
                        password_field = field
                        break
        
        return username_field, password_field
    
    def _analyze_response(self, 
                         response: requests.Response,
                         credentials: Dict,
                         login_page: Dict,
                         response_time: float) -> Dict:
        """
        Analyze login response to determine success/failure
        
        Returns:
            Dictionary with result details
        """
        result = {
            'username': credentials['username'],
            'password': credentials['password'],
            'status_code': response.status_code,
            'response_time': response_time,
            'url_after_redirect': response.url,
            'status': 'failed'
        }
        
        response_text = response.text.lower()
        response_url = response.url.lower()
        
        # Check for rate limiting / blocking
        rate_limit_indicators = [
            'rate limit', 'too many attempts', 'try again later',
            'temporarily blocked', 'suspicious activity', '429'
        ]
        if any(indicator in response_text for indicator in rate_limit_indicators) or response.status_code == 429:
            result['status'] = 'blocked'
            result['reason'] = 'Rate limited or blocked'
            return result
        
        # Check for CAPTCHA
        captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'challenge']
        if any(indicator in response_text for indicator in captcha_indicators):
            result['status'] = 'captcha'
            result['reason'] = 'CAPTCHA detected'
            return result
        
        # Check for successful login indicators
        success_indicators = [
            'dashboard', 'welcome', 'logout', 'profile', 'account',
            'successfully logged in', 'sign out'
        ]
        failure_indicators = [
            'invalid', 'incorrect', 'failed', 'error', 'wrong',
            'try again', 'login again'
        ]
        
        # URL changed significantly (likely redirected to dashboard)
        if response.url != login_page['form_action'] and response.url != login_page['page_url']:
            if any(indicator in response_url for indicator in success_indicators):
                result['status'] = 'success'
                result['reason'] = 'Redirected to protected page'
                return result
        
        # Check response content
        has_success_indicator = any(indicator in response_text for indicator in success_indicators)
        has_failure_indicator = any(indicator in response_text for indicator in failure_indicators)
        
        if has_success_indicator and not has_failure_indicator:
            result['status'] = 'success'
            result['reason'] = 'Success indicators in response'
        elif has_failure_indicator:
            result['status'] = 'failed'
            result['reason'] = 'Failure indicators in response'
        else:
            # Ambiguous - mark as uncertain
            result['status'] = 'uncertain'
            result['reason'] = 'Could not definitively determine'
        
        return result


if __name__ == "__main__":
    # Test the credential stuffing tester
    tester = CredentialStuffingTester(max_attempts=5, delay_between_attempts=0.5)
    
    # Mock login page
    mock_login_page = {
        'page_url': 'https://example.com/login',
        'form_action': 'https://example.com/login',
        'form_method': 'POST',
        'fields': ['username', 'password', 'submit']
    }
    
    # Mock credentials
    mock_credentials = [
        {'username': 'test1@example.com', 'password': 'password123'},
        {'username': 'test2@example.com', 'password': 'admin123'},
    ]
    
    print("Note: This is a test run with mock data")
