"""
Intelligent Website Profiler (Deterministic Upgraded)

Analyzes target website using structural DOM analysis to identify:
- Login/Signup forms (by input types, not just regex)
- Defense mechanisms (WAF, rate limiting, CAPTCHA)
- Technology stack
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Set, Optional
from colorama import Fore, Style
import time
from core.network import NetworkClient
import asyncio
from core.browser import BrowserManager

class WebsiteProfiler:
    """Deterministic website analysis and profiling"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.client = NetworkClient() # Use our enhanced client
        self.browser_manager = BrowserManager(headless=True)
        
        self.profile = {
            'technology_stack': {},
            'authentication_methods': [],
            'defense_mechanisms': [],
            'api_endpoints': [],
            'login_methods': [],
            'signup_methods': [],
            'social_auth': [],
            'security_features': [],
            'security_features': [],
            'vulnerabilities': [],
            'discovery_log': []  # [NEW] Log of all checked URLs
        }
    
    async def analyze(self) -> Dict:
        """
        Perform complete website profiling
        """
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🔍 DETERMINISTIC STRUCTURAL ANALYSIS{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")
        
        # Phase 1: Technology Detection
        await self._detect_technology_stack()
        
        # Phase 2: Authentication Analysis (DOM Based)
        await self._analyze_authentication_methods()

        # Phase 3: Defense Detection
        await self._detect_defense_mechanisms()
        
        # Cleanup
        await self.browser_manager.close()
        
        return self.profile

    async def _detect_technology_stack(self):
        """Detect what technologies the site uses via Headers & HTML fingerprints"""
        print(f"{Fore.CYAN}[1/3] Detecting Technology Stack...{Style.RESET_ALL}")
        try:
            response = await self.client.request("GET", self.base_url, timeout=10)
            
            headers_lower = {k.lower(): v for k, v in response.headers.items()}
            tech_stack = {
                'framework': 'unknown',
                'server': headers_lower.get('server', 'unknown'),
                'powered_by': headers_lower.get('x-powered-by', 'unknown'),
                'cms': 'unknown'
            }

            if 'x-aspnet-version' in headers_lower:
                tech_stack['framework'] = 'ASP.NET'
            elif 'php' in tech_stack['powered_by'].lower():
                tech_stack['framework'] = 'PHP'
            
            # HTML Analysis
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find('meta', {'name': 'generator', 'content': re.compile('WordPress', re.I)}):
                tech_stack['cms'] = 'WordPress'
            
            self.profile['technology_stack'] = tech_stack
            print(f"{Fore.GREEN}  [✓] Server: {tech_stack['server']}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}  [✓] Framework: {tech_stack['framework']}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}  [✗] Error detecting technology: {str(e)}{Style.RESET_ALL}")

    async def _analyze_authentication_methods(self):
        """Analyze authentication using Structural DOM Analysis"""
        print(f"\n{Fore.CYAN}[2/3] Analyzing Auth Forms (Structural)...{Style.RESET_ALL}")
        
        try:
            # Check base URL and common paths
            candidates = [self.base_url, urljoin(self.base_url, "/login"), urljoin(self.base_url, "/signin")]
            
            # Crawl homepage for other potential login links
            try:
                home_resp = await self.client.request("GET", self.base_url, timeout=10)
                if home_resp.status_code == 200:
                    found_links = self._find_candidate_links(home_resp.text, self.base_url)
                    candidates.extend(found_links)
                    print(f"{Fore.CYAN}  [+] Discovered {len(found_links)} potential login links from homepage{Style.RESET_ALL}")
            except Exception:
                pass
            
            # Remove duplicates
            candidates = list(set(candidates))
            
            # 3. Fuzzing Common Paths
            common_paths = [
                '/login', '/signin', '/user/login', '/auth/login', 
                '/admin', '/admin/login', '/wp-login.php', '/login.php'
            ]
            for path in common_paths:
                candidates.append(urljoin(self.base_url, path))
            
            # Remove duplicates
            candidates = list(set(candidates))
            
            print(f"{Fore.CYAN}  [+] Checking {len(candidates)} potential login URLs...{Style.RESET_ALL}")
            seen_actions = set()

            for url in candidates:
                # 1. Try Fast HTTP Request first
                try:
                    status_code = 0
                    found = False
                    
                    try:
                        resp = await self.client.request("GET", url, timeout=10, allow_redirects=True)
                        status_code = resp.status_code
                        
                        # If 200 OK, we must VERIFY it's a login page (Browser or DOM)
                        if resp.status_code == 200:
                            # Quick DOM check
                            if self._analyze_page_structure(url, resp.text, seen_actions):
                                found = True
                            else:
                                # Hybrid Verification: If text unclear, use Browser to render & check visibility
                                # This avoids "404 softpages" or JS-only forms being missed
                                print(f"{Fore.YELLOW}  [?] Verifying candidate with Browser: {url}{Style.RESET_ALL}")
                                if await self._analyze_with_browser(url, seen_actions):
                                    found = True

                        elif resp.status_code in [403, 503]:
                            print(f"{Fore.YELLOW}  [!] WAF/Bot Protection detected at {url}. Switching to Browser...{Style.RESET_ALL}")
                            if await self._analyze_with_browser(url, seen_actions):
                                found = True
                            
                    except Exception as e:
                        # If HTTP fails, try Browser as backup
                        try:
                            if await self._analyze_with_browser(url, seen_actions):
                                found = True
                        except:
                            pass
                    
                    # Log the attempt
                    self.profile['discovery_log'].append({
                        'url': url,
                        'status_code': status_code if status_code else 'Err',
                        'found': found,
                        'source': 'fuzz' if any(p in url for p in common_paths) else 'crawl'
                    })

                except Exception as e:
                    pass

            # 4. Interactive Discovery (Human-Like)
            print(f"{Fore.CYAN}  [+] Attempting Interactive Discovery (Human-Like)...{Style.RESET_ALL}")
            try:
                result = await self.browser_manager.find_login_interactively(self.base_url)
                if result['found']:
                    print(f"{Fore.GREEN}  [✓] Interactive Discovery Validated Login!{Style.RESET_ALL}")
                    print(f"      URL: {result['url']}")
                    if result['screenshot_path']:
                        print(f"      Proof: {result['screenshot_path']}")
                    
                    self.profile['login_methods'].append({
                        'url': self.base_url,
                        'form_action': result['url'], # Often the page itself
                        'method': 'INTERACTIVE',
                        'type': 'interactive_login',
                        'confidence': 'verified',
                        'screenshot': result['screenshot_path']
                    })
                    
                    # Log it
                    self.profile['discovery_log'].append({
                        'url': result['url'],
                        'status_code': 200,
                        'found': True,
                        'source': 'interactive'
                    })
            except Exception as e:
                print(f"{Fore.RED}  [!] Interactive Discovery Failed: {e}{Style.RESET_ALL}")

        except Exception as e:
             print(f"{Fore.RED}  [✗] Error: {str(e)}{Style.RESET_ALL}")

    async def _analyze_with_browser(self, url: str, seen_actions: Set[str]) -> bool:
        """Fallback analysis using Playwright"""
        try:
            content = await self.browser_manager.get_page_content(url)
            # Only count as found if structure matches
            if self._analyze_page_structure(url, content, seen_actions):
                 print(f"{Fore.GREEN}  [✓] Confirmed via Browser: {url}{Style.RESET_ALL}")
                 return True
        except Exception as e:
             # print(f"{Fore.RED}  [✗] Browser Analysis Failed: {str(e)}{Style.RESET_ALL}")
             pass
        return False

    def _analyze_page_structure(self, url: str, html: str, seen_actions: Set[str]) -> bool:
        """
        Identifies forms by structure:
        - Login: Form with exactly 1 password field and 1 text/email field
        Returns True if relevant forms were found.
        """
        soup = BeautifulSoup(html, 'html.parser')
        forms = soup.find_all('form')
        found_any = False
        
        for form in forms:
            inputs = form.find_all('input')
            text_inputs = [i for i in inputs if i.get('type') in ['text', 'email', 'tel']]
            password_inputs = [i for i in inputs if i.get('type') == 'password']
            
            action = form.get('action') or ''
            full_action = urljoin(url, action)

            if full_action in seen_actions:
                continue

            # Heuristic: Login Form
            if len(password_inputs) == 1 and len(text_inputs) >= 1:
                seen_actions.add(full_action)
                found_any = True
                
                print(f"{Fore.GREEN}  [✓] FOUND LOGIN FORM at {url}")
                print(f"      Source: {'Browser' if 'headless' in str(self.browser_manager) else 'NetworkClient'}")
                print(f"      Action: {full_action}")
                print(f"      Method: {form.get('method', 'POST').upper()}")
                
                self.profile['login_methods'].append({
                    'url': url,
                    'form_action': full_action,
                    'method': form.get('method', 'POST').upper(),
                    'type': 'structural_login',
                    'confidence': 'high'
                })
        
        return found_any

    async def _detect_defense_mechanisms(self):
        """Detect defenses via header analysis and WAF signatures"""
        print(f"\n{Fore.CYAN}[3/3] Detecting Defense Mechanisms...{Style.RESET_ALL}")
        try:
            resp = await self.client.request("GET", self.base_url)
            
            # WAF Headers
            waf_headers = ['cf-ray', 'server', 'x-firewall', 'x-sucuri-id']
            for h in waf_headers:
                val = resp.headers.get(h, '').lower()
                if 'cloudflare' in val:
                    self.profile['defense_mechanisms'].append({'type': 'waf', 'provider': 'Cloudflare'})
                    print(f"{Fore.YELLOW}  [!] Cloudflare WAF Detected{Style.RESET_ALL}")
                elif 'sucuri' in val:
                    self.profile['defense_mechanisms'].append({'type': 'waf', 'provider': 'Sucuri'})
                    print(f"{Fore.YELLOW}  [!] Sucuri WAF Detected{Style.RESET_ALL}")

        except Exception:
            pass

    def _find_candidate_links(self, html: str, base_url: str) -> List[str]:
        """Find potential login links in HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        candidates = []
        keywords = ['login', 'signin', 'sign-in', 'log-in', 'account', 'user', 'member']
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().lower()
            url_lower = href.lower()
            
            # Check if keyword in URL or Link Text
            if any(k in url_lower or k in text for k in keywords):
                full_url = urljoin(base_url, href)
                # Ensure it's internal
                if self.domain in urlparse(full_url).netloc:
                    candidates.append(full_url)
                    
        return candidates[:5] # Limit to top 5 to avoid spam
