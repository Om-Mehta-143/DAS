from core.network import NetworkClient
import asyncio

async def simple_test():
    print("Initializing Network Client (Async Wrapper)...")
    client = NetworkClient()
    
    print("\n[Test 1] TLS Fingerprint Verification:")
    try:
        # Request to a TLS analysis API
        response = await client.request("GET", "https://tls.peet.ws/api/all")
        data = response.json()
        
        # Check if the fingerprint looks like a browser (not python-requests)
        ja3 = data.get('tls', {}).get('ja3', 'Unknown')
        user_agent = data.get('http', {}).get('user_agent', 'Unknown')
        headers = data.get('http', {}).get('headers', {})
        
        print(f"  > JA3 Hash: {ja3}")
        print(f"  > User-Agent: {user_agent}")
        try:
             # Handle different header casing from server
             sec_ch_ua = headers.get('sec-ch-ua') or headers.get('Sec-Ch-Ua') or 'Missing'
             print(f"  > Sec-CH-UA: {sec_ch_ua}")
        except:
             print("  > Sec-CH-UA: Error parsing")
        print("  > Result: SUCCESS (Fingerprint received)")
    except Exception as e:
        print(f"  > Result: FAILED ({str(e)})")

    print("\n[Test 2] Header Verification (httpbin):")
    try:
        response = await client.request("GET", "https://httpbin.org/headers")
        headers = response.json().get('headers', {})
        
        print(f"  > User-Agent: {headers.get('User-Agent', 'MISSING')}")
        print(f"  > Sec-Ch-Ua: {headers.get('Sec-Ch-Ua', 'MISSING')}")
        print(f"  > Upgrade-Insecure-Requests: {headers.get('Upgrade-Insecure-Requests', 'MISSING')}")
        
    except Exception as e:
        print(f"  > Result: FAILED ({str(e)})")

if __name__ == "__main__":
    asyncio.run(simple_test())
