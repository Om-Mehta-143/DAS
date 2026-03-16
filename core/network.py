"""
High-Performance Network Client with TLS Impersonation and Evasion
"""

from curl_cffi import requests as crequests
from curl_cffi.requests import AsyncSession
from typing import Dict, Optional, Any, List
import asyncio
import random
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

@dataclass
class ProxyConfig:
    url: str
    auth: Optional[Dict[str, str]] = None

from core.evader import Evader, BrowserProfile

class NetworkClient:
    """
    Advanced Network Client with:
    1. TLS Fingerprint Impersonation (mimics Chrome/Safari via Evader)
    2. Automatic Proxy Rotation
    3. Realistic Browser Profile Rotation
    4. HTTP/2 & HTTP/3 Support
    """

    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.current_proxy_index = 0
        self.evader = Evader()

    def _get_proxy(self) -> Optional[str]:
        """Get next proxy URL from rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def request(self, 
                     method: str, 
                     url: str, 
                     **kwargs) -> crequests.Response:
        """
        Execute HTTP request with evasion techniques
        """
        # 1. Get a consistent browser profile
        profile = self.evader.get_profile()
        
        # 2. Select Impersonation Profile matched to User-Agent
        impersonate = kwargs.pop('impersonate', profile.impersonate)
        
        # 3. Rotate Proxy
        proxy = self._get_proxy()
        
        # 4. Generate Realistic Headers
        # Merge with provided headers, but prioritize Evader's structural headers
        generated_headers = self.evader.get_headers(profile)
        provided_headers = kwargs.get('headers', {})
        
        # Update generated with provided (so user can override specific fields)
        generated_headers.update(provided_headers)
        kwargs['headers'] = generated_headers

        # 5. Execute with curl_cffi
        # We use AsyncSession for connection pooling if we were doing many requests,
        # but for individual request flow this wrapper is fine.
        # For high-concurrency, we might want to pass a session in.
        
        # Note: When using impersonate, some headers might be overridden.
        # We need to ensure our critical headers (UA, Sec-CH-UA) are respected.
        
        async with AsyncSession(impersonate=impersonate, headers=generated_headers) as s:
            if proxy:
                s.proxies = {"http": proxy, "https": proxy}
            
            # We already passed headers to AsyncSession, but passing them again to request
            # ensures they are used for this specific request if keyword arg is used.
            # But here kwargs['headers'] includes them, so we just pass kwargs.
            response = await s.request(method, url, **kwargs)
            return response

    async def check_ip(self) -> Dict:
        """Debug method to verify IP and capabilities"""
        try:
            resp = await self.request("GET", "https://httpbin.org/ip")
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    async def check_tls(self) -> Dict:
        """Debug method to verify TLS fingerprint"""
        try:
            # tls.peet.ws is a good fingerprint analyzer
            resp = await self.request("GET", "https://tls.peet.ws/api/all")
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
