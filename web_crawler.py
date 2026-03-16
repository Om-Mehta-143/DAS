"""
Web Crawler Module

Crawls target website to discover:
- robots.txt
- sitemap.xml
- Login pages
- Important endpoints
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import re
from typing import List, Set, Dict, Optional
from colorama import Fore, Style
import time


class WebCrawler:
    """Crawls websites to discover login pages and important files"""
    
    # Common login page indicators
    LOGIN_INDICATORS = [
        'login', 'signin', 'sign-in', 'log-in', 'authenticate',
        'auth', 'session', 'account', 'user', 'member',
        'portal', 'admin', 'dashboard'
    ]
    
    # Common login form indicators
    LOGIN_FORM_FIELDS = ['username', 'password', 'email', 'user', 'pass', 'pwd']
    
    def __init__(self, base_url: str, max_depth: int = 3, max_pages: int = 100):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.login_pages: List[Dict] = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl(self) -> Dict:
        """
        Main crawl method
        
        Returns:
            Dictionary containing discovered resources
        """
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] Starting Web Crawl{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        results = {
            'robots_txt': None,
            'sitemap_xml': None,
            'login_pages': [],
            'forms_found': [],
            'crawled_pages': []
        }
        
        # Step 1: Check robots.txt
        print(f"{Fore.YELLOW}[1/4] Checking robots.txt...{Style.RESET_ALL}")
        results['robots_txt'] = self._check_robots_txt()
        
        # Step 2: Check sitemap.xml
        print(f"{Fore.YELLOW}[2/4] Checking sitemap.xml...{Style.RESET_ALL}")
        results['sitemap_xml'] = self._check_sitemap()
        
        # Step 3: Crawl for login pages
        print(f"{Fore.YELLOW}[3/4] Crawling for login pages...{Style.RESET_ALL}")
        self._crawl_recursive(self.base_url, depth=0)
        
        # Step 4: Analyze findings
        print(f"{Fore.YELLOW}[4/4] Analyzing findings...{Style.RESET_ALL}")
        results['login_pages'] = self.login_pages
        results['crawled_pages'] = list(self.visited_urls)
        
        print(f"\n{Fore.GREEN}[✓] Crawl complete!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    - Pages crawled: {len(self.visited_urls)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    - Login pages found: {len(self.login_pages)}{Style.RESET_ALL}\n")
        
        return results
    
    def _check_robots_txt(self) -> Optional[Dict]:
        """Check for robots.txt"""
        robots_url = urljoin(self.base_url, '/robots.txt')
        try:
            response = requests.get(robots_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                print(f"{Fore.GREEN}  [✓] Found robots.txt{Style.RESET_ALL}")
                
                # Parse for interesting paths
                content = response.text
                disallowed_paths = re.findall(r'Disallow:\s*(.+)', content)
                
                return {
                    'url': robots_url,
                    'exists': True,
                    'content': content[:500],  # First 500 chars
                    'disallowed_paths': disallowed_paths[:10]  # Top 10
                }
            else:
                print(f"{Fore.RED}  [✗] robots.txt not found (HTTP {response.status_code}){Style.RESET_ALL}")
                return {'exists': False}
        except Exception as e:
            print(f"{Fore.RED}  [✗] Error checking robots.txt: {str(e)}{Style.RESET_ALL}")
            return {'exists': False, 'error': str(e)}
    
    def _check_sitemap(self) -> Optional[Dict]:
        """Check for sitemap.xml"""
        sitemap_urls = ['/sitemap.xml', '/sitemap_index.xml', '/sitemap1.xml']
        
        for sitemap_path in sitemap_urls:
            sitemap_url = urljoin(self.base_url, sitemap_path)
            try:
                response = requests.get(sitemap_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}  [✓] Found sitemap: {sitemap_path}{Style.RESET_ALL}")
                    
                    # Parse URLs from sitemap
                    urls = re.findall(r'<loc>(.+?)</loc>', response.text)
                    
                    return {
                        'url': sitemap_url,
                        'exists': True,
                        'urls_count': len(urls),
                        'sample_urls': urls[:10]  # First 10 URLs
                    }
            except Exception:
                continue
        
        print(f"{Fore.RED}  [✗] sitemap.xml not found{Style.RESET_ALL}")
        return {'exists': False}
    
    def _crawl_recursive(self, url: str, depth: int):
        """Recursively crawl pages"""
        # Stop conditions
        if depth > self.max_depth:
            return
        if len(self.visited_urls) >= self.max_pages:
            return
        if url in self.visited_urls:
            return
        
        # Only crawl same domain
        if urlparse(url).netloc != self.domain:
            return
        
        try:
            print(f"{Fore.CYAN}  [*] Crawling [{depth}/{self.max_depth}]: {url[:80]}...{Style.RESET_ALL}")
            
            self.visited_urls.add(url)
            response = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                return
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if this page has login forms
            self._analyze_page_for_login(url, soup)
            
            # Find links to crawl
            if depth < self.max_depth:
                links = self._extract_links(soup, url)
                for link in links:
                    time.sleep(0.1)  # Be polite
                    self._crawl_recursive(link, depth + 1)
                    
        except Exception as e:
            print(f"{Fore.RED}  [✗] Error crawling {url}: {str(e)}{Style.RESET_ALL}")
    
    def _analyze_page_for_login(self, url: str, soup: BeautifulSoup):
        """Analyze page for login forms"""
        # Check URL for login indicators
        url_lower = url.lower()
        url_has_login_indicator = any(indicator in url_lower for indicator in self.LOGIN_INDICATORS)
        
        # Check page title
        title = soup.title.string if soup.title else ""
        title_has_login_indicator = any(indicator in title.lower() for indicator in self.LOGIN_INDICATORS)
        
        # Find forms
        forms = soup.find_all('form')
        
        for form_idx, form in enumerate(forms):
            form_action = form.get('action', '')
            form_method = form.get('method', 'get').upper()
            
            # Get form inputs
            inputs = form.find_all('input')
            input_types = {}
            
            for inp in inputs:
                input_name = inp.get('name', '').lower()
                input_type = inp.get('type', 'text').lower()
                input_types[input_name] = input_type
            
            # Check if form looks like a login form
            has_password_field = any(inp_type == 'password' for inp_type in input_types.values())
            has_username_field = any(
                field in input_types.keys() 
                for field in ['username', 'email', 'user', 'login', 'account']
            )
            
            # If it looks like a login form
            if has_password_field and (has_username_field or url_has_login_indicator):
                form_action_url = urljoin(url, form_action)
                
                login_info = {
                    'page_url': url,
                    'form_action': form_action_url,
                    'form_method': form_method,
                    'fields': list(input_types.keys()),
                    'confidence': 'high' if (has_username_field and has_password_field) else 'medium'
                }
                
                # Avoid duplicates
                if not any(lp['form_action'] == form_action_url for lp in self.login_pages):
                    self.login_pages.append(login_info)
                    print(f"{Fore.GREEN}  [✓] Login form found: {url}{Style.RESET_ALL}")
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links from page"""
        links = []
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Convert to absolute URL
            full_url = urljoin(base_url, href)
            
            # Parse URL
            parsed = urlparse(full_url)
            
            # Only include same domain, http/https, and not files
            if (parsed.netloc == self.domain and 
                parsed.scheme in ['http', 'https'] and
                not parsed.path.endswith(('.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.zip'))):
                
                # Remove fragment
                clean_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    ''
                ))
                
                links.append(clean_url)
        
        return links


if __name__ == "__main__":
    # Test the crawler
    crawler = WebCrawler("https://example.com", max_depth=2, max_pages=20)
    results = crawler.crawl()
    
    print("\n=== Results ===")
    print(f"Login pages found: {len(results['login_pages'])}")
    for login_page in results['login_pages']:
        print(f"  - {login_page['page_url']}")
