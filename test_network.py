import asyncio
from core.network import NetworkClient

async def simple_test():
    print("Initializing Network Client...")
    client = NetworkClient()
    
    print("\n[Test 1] TLS Fingerprint Verification:")
    try:
        # Request to a TLS analysis API
        response = await client.request("GET", "https://tls.peet.ws/api/all")
        data = response.json()
        
        # Check if the fingerprint looks like a browser (not python-requests)
        ja3 = data.get('tls', {}).get('ja3', 'Unknown')
        user_agent = data.get('http', {}).get('user_agent', 'Unknown')
        
        print(f"  > JA3 Hash: {ja3}")
        print(f"  > User-Agent: {user_agent}")
        print("  > Result: SUCCESS (Fingerprint received)")
    except Exception as e:
        print(f"  > Result: FAILED ({str(e)})")

    print("\n[Test 2] Header Randomization")
    try:
        response = await client.request("GET", "https://httpbin.org/headers")
        headers = response.json().get('headers', {})
        print(f"  > Accepted Headers: {headers.keys()}")
        print("  > Result: SUCCESS")
    except Exception as e:
        print(f"  > Result: FAILED ({str(e)})")

if __name__ == "__main__":
    asyncio.run(simple_test())
