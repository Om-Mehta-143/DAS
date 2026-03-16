import os
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    """Manages persistent storage for Distribution-Attack-Sim via Supabase."""
    
    def __init__(self):
        self.url: Optional[str] = os.getenv("SUPABASE_URL")
        self.key: Optional[str] = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        
        # Local fallback state
        self._local_logs: List[Dict] = []
        self._local_banned: Set[str] = set()
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                print("DEBUG: Connected to Supabase successfully.")
            except Exception as e:
                print(f"ERROR: Failed to connect to Supabase: {e}")
        else:
            print("WARNING: Supabase credentials missing. Running in local-only mode.")

    def log_attack(self, data: Dict):
        """Insert a tactical attack log entry."""
        if not self.client:
            self._local_logs.append(data)
            if len(self._local_logs) > 1000: self._local_logs.pop(0)
            return
            
        try:
            # Flatten or format data for Supabase table structure
            entry = {
                "method": data.get("method"),
                "url": data.get("url"),
                "ip": data.get("ip"),
                "status_code": data.get("status_code"),
                "duration_ms": data.get("duration_ms"),
                "user_agent": data.get("user_agent"),
                "behavioral_score": data.get("behavioral_score", "NORMAL"),
                "headers": data.get("headers", {})
            }
            self.client.table("attack_logs").insert(entry).execute()
        except Exception as e:
            print(f"ERROR logging to Supabase: {e}")

    def ban_ip(self, ip: str, reason: str = "Automated defense"):
        """Ban an IP address persistently."""
        if not self.client:
            self._local_banned.add(ip)
            return
            
        try:
            self.client.table("banned_ips").upsert({
                "ip": ip,
                "reason": reason
            }).execute()
        except Exception as e:
            print(f"ERROR banning IP in Supabase: {e}")

    def unban_ip(self, ip: str):
        """Remove an IP block."""
        if not self.client:
            if ip in self._local_banned:
                self._local_banned.remove(ip)
            return
            
        try:
            self.client.table("banned_ips").delete().eq("ip", ip).execute()
        except Exception as e:
            print(f"ERROR unbanning IP in Supabase: {e}")

    def unban_all_ips(self):
        """Clear all entries from the banned_ips table."""
        if not self.client:
            self._local_banned.clear()
            return
            
        try:
            # Delete all rows where ip is not null (effectively all)
            self.client.table("banned_ips").delete().neq("ip", "null").execute()
        except Exception as e:
            print(f"ERROR clearing all bans in Supabase: {e}")

    def get_banned_ips(self) -> List[str]:
        """Fetch all banned IPs from Supabase."""
        if not self.client:
            return list(self._local_banned)
            
        try:
            response = self.client.table("banned_ips").select("ip").execute()
            return [item['ip'] for item in response.data]
        except Exception as e:
            print(f"ERROR fetching banned IPs: {e}")
            return []

    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Fetch recent attack logs for SITREP."""
        if not self.client:
            return self._local_logs[-limit:]
            
        try:
            response = self.client.table("attack_logs") \
                .select("*") \
                .order("timestamp", desc=True) \
                .limit(limit) \
                .execute()
            return response.data
        except Exception as e:
            print(f"ERROR fetching logs: {e}")
            return []
