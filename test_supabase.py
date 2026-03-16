import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"Connecting to: {url}")
try:
    client = create_client(url, key)
    print("Connection successful!")
    
    test_data = {
        "method": "TEST",
        "url": "/test-connection",
        "ip": "127.0.0.1",
        "status_code": 200,
        "duration_ms": 1.0,
        "user_agent": "DiagnosticScript",
        "behavioral_score": "TEST"
    }
    
    print("Attempting to insert test log...")
    res = client.table("attack_logs").insert(test_data).execute()
    print("Insert response:", res)
    print("SUCCESS: Data sent to Supabase!")
except Exception as e:
    print(f"FAILED: {e}")
