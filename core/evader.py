"""
Evader Module - Advanced Deception & Fingerprint Management
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class BrowserProfile:
    user_agent: str
    sec_ch_ua: str
    sec_ch_ua_platform: str
    sec_ch_ua_mobile: str
    accept_language: str
    upgrade_insecure_requests: str
    impersonate: str

class Evader:
    """
    Manages realistic browser fingerprints and headers to evade detection.
    """
    
    def __init__(self):
        self.profiles = [
            # Chrome 120 on Windows
            BrowserProfile(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                sec_ch_ua='"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                sec_ch_ua_platform='"Windows"',
                sec_ch_ua_mobile='?0',
                accept_language='en-US,en;q=0.9',
                upgrade_insecure_requests='1',
                impersonate='chrome120'
            ),
            # Chrome 120 on macOS
            BrowserProfile(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                sec_ch_ua='"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                sec_ch_ua_platform='"macOS"',
                sec_ch_ua_mobile='?0',
                accept_language='en-US,en;q=0.9',
                upgrade_insecure_requests='1',
                impersonate='chrome120'
            ),
            # Safari 17 on macOS
            BrowserProfile(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
                sec_ch_ua='', # Safari usually doesn't send this
                sec_ch_ua_platform='"macOS"',
                sec_ch_ua_mobile='?0',
                accept_language='en-US,en;q=0.9',
                upgrade_insecure_requests='1',
                impersonate='safari17_0'
            )
        ]

    def get_profile(self) -> BrowserProfile:
        """Get a random realistic browser profile"""
        return random.choice(self.profiles)

    def get_headers(self, profile: BrowserProfile) -> Dict[str, str]:
        """Generate consistent headers for a profile"""
        headers = {
            'User-Agent': profile.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': profile.accept_language,
            'Upgrade-Insecure-Requests': profile.upgrade_insecure_requests,
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
        }
        
        # Add Client Hints only if they exist (Chrome/Edge)
        if profile.sec_ch_ua:
            headers['sec-ch-ua'] = profile.sec_ch_ua
        if profile.sec_ch_ua_mobile:
            headers['sec-ch-ua-mobile'] = profile.sec_ch_ua_mobile
        if profile.sec_ch_ua_platform:
            headers['sec-ch-ua-platform'] = profile.sec_ch_ua_platform
            
        return headers
