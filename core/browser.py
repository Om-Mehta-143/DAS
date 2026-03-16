"""
Headless Browser Manager using Playwright
"""

import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class BrowserManager:
    """
    Manages headless browser instances for:
    1. JavaScript execution
    2. CAPTCHA solving
    3. Dynamic content rendering
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def start(self):
        """Initialize browser engine"""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']  # Basic evasion
            )
            
    async def get_page(self) -> Page:
        """Get a fresh page with realistic context"""
        if not self.browser:
            await self.start()
            
        if not self.context:
            # Create context with realistic viewport and locale
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US'
            )
            
            # Add stealth scripts
            await self.context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
        return await self.context.new_page()

    async def close(self):
        """Cleanup resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_page_content(self, url: str) -> str:
        """Navigate to URL and return rendered HTML"""
        page = await self.get_page()
        try:
            await page.goto(url, wait_until='networkidle')
            content = await page.content()
            return content
        finally:
            await page.close()

    async def find_login_interactively(self, url: str) -> Dict[str, Any]:
        """
        Interactively find login forms by clicking 'Login' buttons.
        Returns: {
            'found': bool,
            'url': str,       # Final URL where form was found
            'html': str,      # Page content
            'screenshot_path': str (optional)
        }
        """
        page = await self.get_page()
        result = {'found': False, 'url': url, 'html': '', 'screenshot_path': None}
        
        try:
            print(f"  [Browser] Navigating to {url}...")
            await page.goto(url, wait_until='networkidle', timeout=15000)
            
            # 1. Check current page first
            if await self._has_login_form(page):
                 print(f"  [Browser] Login form detected on homepage.")
                 result['found'] = True
                 result['url'] = page.url
                 result['html'] = await page.content()
                 result['screenshot_path'] = await self._take_screenshot(page, "login_found")
                 return result

            # 2. Look for "Login" / "Sign In" buttons and click
            # Heuristic: Buttons often have text specific to aux-nav
            selectors = [
                "a:text-is('Login')", "button:text-is('Login')",
                "a:text-is('Sign In')", "button:text-is('Sign In')",
                "a:text-is('Log In')", "button:text-is('Log In')",
                "a[href*='login']", "a[href*='signin']"
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        print(f"  [Browser] Clicking candidate element: {selector}")
                        # visual feedback
                        await element.highlight()
                        await asyncio.sleep(0.5) # Human-like pause
                        
                        # Click and wait for navigation or modal
                        await element.click()
                        await page.wait_for_load_state('networkidle', timeout=5000)
                        
                        # Check again
                        if await self._has_login_form(page):
                             print(f"  [Browser] Login form detected after interaction!")
                             result['found'] = True
                             result['url'] = page.url
                             result['html'] = await page.content()
                             result['screenshot_path'] = await self._take_screenshot(page, "login_found_interactive")
                             return result
                except Exception:
                    continue
                    
        except Exception as e:
            # print(f"  [Browser Error] {e}")
            pass
        finally:
            await self.close_page(page)
            
        return result

    async def _has_login_form(self, page: Page) -> bool:
        """Check if page has a password field visible"""
        try:
            # Low-level check for password input
            pwd = page.locator("input[type='password']")
            return await pwd.count() > 0 and await pwd.first.is_visible()
        except:
            return False

    async def _take_screenshot(self, page: Page, name: str) -> str:
        """Save screenshot to reports folder"""
        import os
        from datetime import datetime
        
        reports_dir = "reports/screenshots"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{reports_dir}/{name}_{timestamp}.png"
        await page.screenshot(path=filename)
        return filename

    async def close_page(self, page: Page):
        try:
            await page.close()
        except:
            pass
