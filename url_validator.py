"""
URL Validator Module

Validates and corrects target URLs before testing.
Ensures URLs are well-formed and accessible.
"""

import re
import validators
from urllib.parse import urlparse, urlunparse
from typing import Tuple, Optional
import requests
from colorama import Fore, Style

class URLValidator:
    """Validates and corrects target URLs"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def validate_and_correct(self, url: str) -> Tuple[bool, str, str]:
        """
        Validate and correct a URL
        
        Args:
            url: The URL to validate
            
        Returns:
            Tuple of (is_valid, corrected_url, message)
        """
        print(f"\n{Fore.CYAN}[*] Validating URL: {url}{Style.RESET_ALL}")
        
        # Step 1: Clean the URL
        url = url.strip()
        
        # Step 2: Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            print(f"{Fore.YELLOW}[!] No scheme detected, trying https://{Style.RESET_ALL}")
            url = f"https://{url}"
        
        # Step 3: Parse URL
        try:
            parsed = urlparse(url)
            
            # Ensure we have a valid domain
            if not parsed.netloc:
                return False, url, "Invalid URL: No domain found"
            
            # Reconstruct URL with proper formatting
            corrected_url = urlunparse((
                parsed.scheme,
                parsed.netloc.lower(),  # Lowercase domain
                parsed.path or '/',
                parsed.params,
                parsed.query,
                ''  # Remove fragment
            ))
            
        except Exception as e:
            return False, url, f"URL parsing error: {str(e)}"
        
        # Step 4: Validate URL format
        # Patch: allow localhost or valid URL
        is_url_valid = validators.url(corrected_url)
        if not is_url_valid and 'localhost' not in corrected_url:
            return False, corrected_url, "Invalid URL format"
        
        # Step 5: Check if URL is accessible
        print(f"{Fore.CYAN}[*] Checking accessibility...{Style.RESET_ALL}")
        is_accessible, access_message = self._check_accessibility(corrected_url)
        
        if is_accessible:
            print(f"{Fore.GREEN}[✓] URL is valid and accessible: {corrected_url}{Style.RESET_ALL}")
            return True, corrected_url, "URL is valid and accessible"
        else:
            # Try http:// if https:// failed
            if corrected_url.startswith('https://'):
                http_url = corrected_url.replace('https://', 'http://')
                print(f"{Fore.YELLOW}[!] HTTPS failed, trying HTTP...{Style.RESET_ALL}")
                is_accessible, access_message = self._check_accessibility(http_url)
                
                if is_accessible:
                    print(f"{Fore.GREEN}[✓] URL is accessible via HTTP: {http_url}{Style.RESET_ALL}")
                    return True, http_url, "URL accessible via HTTP"
            
            return False, corrected_url, f"URL not accessible: {access_message}"
    
    def _check_accessibility(self, url: str) -> Tuple[bool, str]:
        """
        Check if a URL is accessible
        
        Returns:
            Tuple of (is_accessible, message)
        """
        try:
            response = requests.head(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                verify=False  # For testing purposes - in production, handle SSL properly
            )
            
            if response.status_code < 400:
                return True, f"HTTP {response.status_code}"
            else:
                # Try GET if HEAD fails
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=False
                )
                
                if response.status_code < 400:
                    return True, f"HTTP {response.status_code}"
                else:
                    return False, f"HTTP {response.status_code}"
                    
        except requests.exceptions.SSLError:
            return False, "SSL Certificate Error"
        except requests.exceptions.ConnectionError:
            return False, "Connection Error - Host unreachable"
        except requests.exceptions.Timeout:
            return False, "Request Timeout"
        except requests.exceptions.TooManyRedirects:
            return False, "Too many redirects"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc


if __name__ == "__main__":
    # Test the validator
    validator = URLValidator()
    
    test_urls = [
        "example.com",
        "https://www.google.com",
        "http://invalid-domain-that-doesnt-exist-12345.com",
        "https://github.com",
    ]
    
    for test_url in test_urls:
        is_valid, corrected, message = validator.validate_and_correct(test_url)
        print(f"Result: {is_valid} - {message}\n")
