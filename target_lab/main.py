from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from target_lab.core.pow import PoWController
from target_lab.core.limiter import LocalLimiter
from target_lab.core.database import SupabaseManager
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
import os

# Configure robust attack logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

attack_logger = logging.getLogger("attack_monitor")
attack_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "attacks.json"))
attack_logger.addHandler(file_handler)

app = FastAPI(title="Pentest Target Lab - Fortress Edition")

# Security State
pow_manager = PoWController(difficulty=4)
db_manager = SupabaseManager()

# IP Banning / Limiting State
limiter = LocalLimiter()
failed_attempts: Dict[str, int] = {} 
global_traffic_count = 0
security_stats = {
    "pow_passed": 0,
    "honey_triggered": 0,
    "behavioral_blocked": 0
}

# Helper to get current banned IPs (Sync with DB if possible)
def get_current_banned_ips() -> Set[str]:
    db_ips = db_manager.get_banned_ips()
    return set(db_ips)

class SITREPMiddleware:
    """System for Intelligence and Tactical Response (SITREP)"""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        # Extract Real IP (Handle Cloudflare/Proxies)
        client_ip = request.headers.get("cf-connecting-ip") or \
                    request.headers.get("x-forwarded-for", "").split(",")[0].strip() or \
                    request.client.host
        
        # Track global traffic before any rate limits or bans short-circuit the request
        whitelist_paths = ["/api/stats", "/api/sitrep", "/dashboard", "/dashboard_assets", "/favicon.ico", "/api/unban", "/api/unban_all"]
        if not any(path in str(request.url) for path in whitelist_paths):
            global global_traffic_count
            global_traffic_count += 1

        # Block Banned IPs instantly
        current_banned = get_current_banned_ips()
        if client_ip in current_banned:
            response = JSONResponse(
                status_code=403, 
                content={"status": "blocked", "message": "Access denied due to suspicious activity"}
            )
            await response(scope, receive, send)
            return

        # Global Rate Limit check
        if not any(path in str(request.url) for path in whitelist_paths):
            if not limiter.is_allowed(key=f"global:{client_ip}", limit=20, window=60):
                security_stats["behavioral_blocked"] += 1
                db_manager.ban_ip(client_ip, "Global rate limit exceeded")
                attack_logger.warning(f"BAN: Global rate limit exceeded by {client_ip}")
                response = JSONResponse(status_code=429, content={"status": "blocked", "message": "Too many requests. IP banned."})
                await response(scope, receive, send)
                return

        start_time = time.time()
        
        # Capture Tactical Data
        tactical_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "ip": client_ip,
            "headers": dict(request.headers),
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        # WAF Logic - Basic Structural Check
        is_blocked = False
        block_reason = None

        # Behavioral Identity Verification (JA3 Simulation)
        ua = tactical_data["user_agent"].lower()
        headers = tactical_data["headers"]
        
        # Check for discrepancies: Chrome UA but missing Sec-CH-UA headers
        is_suspicious = False
        if "chrome" in ua or "chromium" in ua:
            if "sec-ch-ua" not in headers:
                is_suspicious = True
        
        # Check for known automation libs
        if any(lib in ua for lib in ["curl-cffi", "python-requests", "aiohttp", "go-http-client"]):
            is_suspicious = True

        if is_suspicious:
            tactical_data["behavioral_score"] = "HIGH_RISK"
            # attack_logger.warning(f"SUSPICIOUS: Behavioral anomaly detected from {client_ip}")

        # Basic Rate Limiting Simulation (Granular logic would go in separate middleware)
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                tactical_data["status_code"] = message["status"]
                tactical_data["duration_ms"] = round(duration * 1000, 2)
                
                # Ignore dashboard polling so it doesn't pollute the logs
                if not any(path in tactical_data["url"] for path in whitelist_paths):
                    # Log the encounter
                    log_entry = json.dumps(tactical_data)
                    attack_logger.info(log_entry)
                    db_manager.log_attack(tactical_data)

            await send(message)

        await self.app(scope, receive, send_wrapper)

app.add_middleware(SITREPMiddleware)

# Static files for dashboard
app.mount("/dashboard_assets", StaticFiles(directory="target_lab/static"), name="static")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    with open("target_lab/static/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Fortress | Security Hub</title>
            <link rel="stylesheet" href="/dashboard_assets/fortress.css">
            <style>
                .nav-links {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 20px;
                }
                .secondary-btn {
                    background: transparent;
                    border: 1px solid var(--primary);
                    padding: 12px 24px;
                    text-decoration: none;
                    color: var(--primary);
                    border-radius: 12px;
                    font-weight: 600;
                    transition: all 0.2s;
                }
                .secondary-btn:hover {
                    background: var(--primary-glow);
                }
            </style>
        </head>
        <body>
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            
            <div class="fortress-container" style="text-align: center;">
                <h2>SECURITY HUB</h2>
                <p class="subtitle">Advanced Pentesting Target Environment</p>
                
                <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 12px; margin-bottom: 30px; border: 1px solid rgba(255,255,255,0.05);">
                    <p style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.6;">
                        This node is protected by multi-layered defenses including Proof-of-Work, 
                        Behavioral Analysis, and Honey-pot traps.
                    </p>
                </div>

                <a href="/login" style="display: block; width: 100%; padding: 14px; background: var(--primary); color: #fff; text-decoration: none; border-radius: 12px; font-weight: 600; transition: all 0.2s;">
                    Access Restricted Area
                </a>
                
                <div class="nav-links">
                    <a href="/dashboard" class="secondary-btn">SITREP Dashboard</a>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    challenge_token, difficulty = pow_manager.generate_challenge()
    return f"""
    <html>
        <head>
            <title>Fortress | Restricted Access</title>
            <link rel="stylesheet" href="/dashboard_assets/fortress.css">
            <script>
                async function solvePoW(token, difficulty) {{
                    const [salt, ts, sig] = token.split('.');
                    let nonce = 0;
                    const prefix = "0".repeat(difficulty);
                    while (true) {{
                        const data = new TextEncoder().encode(salt + nonce);
                        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
                        const hashArray = Array.from(new Uint8Array(hashBuffer));
                        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                        if (hashHex.startsWith(prefix)) return nonce;
                        nonce++;
                    }}
                }}

                async function handleSubmit(e) {{
                    e.preventDefault();
                    const btn = document.getElementById('login-btn');
                    const status = document.getElementById('status');
                    btn.disabled = true;
                    status.innerHTML = '<span class="status-solving">Validating Neural Link...</span>';
                    
                    try {{
                        const nonce = await solvePoW("{challenge_token}", {difficulty});
                        
                        const formData = new FormData(e.target);
                        formData.set('pow_nonce', nonce);

                        const response = await fetch('/api/login', {{
                            method: 'POST',
                            body: formData
                        }});

                        if (response.ok) {{
                            const result = await response.json();
                            status.innerHTML = `<span style="color: #10b981;">${{result.message}}</span>`;
                            setTimeout(() => window.location.href = "/dashboard", 1000);
                        }} else {{
                            const errorText = await response.text();
                            status.innerHTML = `<span style="color: var(--danger);">Access Denied: ${{errorText}}</span>`;
                            btn.disabled = false;
                        }}
                    }} catch (err) {{
                        status.innerHTML = `<span style="color: var(--danger);">Challenge failed. Please refresh.</span>`;
                        btn.disabled = false;
                    }}
                }}
            </script>
        </head>
        <body>
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            
            <div class="fortress-container">
                <h2>FORTRESS NODE</h2>
                <p class="subtitle">Secure Authentication Interface</p>
                
                <form action="/api/login" method="post" onsubmit="handleSubmit(event)">
                    <div class="input-group">
                        <label>Identifier</label>
                        <input type="text" name="username" placeholder="Enter identity..." required autocomplete="off">
                    </div>
                    
                    <div class="input-group">
                        <label>Access Key</label>
                        <input type="password" name="password" placeholder="••••••••" required>
                    </div>
                    
                    <!-- Honey Pot Fields -->
                    <div class="hidden">
                        <input type="text" name="confirm_account_id" tabindex="-1" autocomplete="off">
                    </div>

                    <!-- PoW Fields -->
                    <input type="hidden" name="pow_token" value="{challenge_token}">
                    <input type="hidden" name="pow_nonce" id="pow_nonce">

                    <button type="submit" id="login-btn">Initialize Connection</button>
                    <div id="status"></div>
                </form>
            </div>
        </body>
    </html>
    """

@app.post("/api/login")
async def login_api(request: Request):
    form_data = await request.form()
    client_ip = request.client.host
    
    # 0. Fast-Reject Banned IPs
    current_banned = get_current_banned_ips()
    if client_ip in current_banned:
        raise HTTPException(status_code=403, detail="Your IP has been banned due to malicious activity.")
        
    # Rate Limiting via custom local limiter logic
    # Limits users to 10 login requests per minute (60 seconds)
    if not limiter.is_allowed(key=f"login:{client_ip}", limit=20, window=60):
        security_stats["behavioral_blocked"] += 1
        db_manager.ban_ip(client_ip, "Login rate limit exceeded")
        attack_logger.warning(f"BAN: Rate limit exceeded by {client_ip}")
        raise HTTPException(status_code=429, detail="Too many attempts. IP banned.")

    # 1. Honey Pot Check
    if form_data.get("confirm_account_id"):
        banned_ips.add(client_ip)
        security_stats["honey_triggered"] += 1
        attack_logger.warning(f"BAN: Honey-pot triggered by {client_ip}")
        raise HTTPException(status_code=403, detail="Suspicious activity detected")

    # 2. PoW / Bot Check
    token = form_data.get("pow_token")
    nonce = form_data.get("pow_nonce")
    
    # If the JS variables are entirely missing, it's a headless bot
    if not token or nonce is None:
        db_manager.ban_ip(client_ip, "Bot detected (No PoW payload)")
        security_stats["behavioral_blocked"] += 1
        attack_logger.warning(f"BAN: Bot detected (No PoW payload) from {client_ip}")
        raise HTTPException(status_code=403, detail="Automated access blocked")
        
    print(f"DEBUG API: Received token='{token}', nonce='{nonce}'")
    
    if not pow_manager.verify_solution(str(token), str(nonce)):
        attack_logger.warning(f"BLOCK: Invalid PoW from {client_ip}")
        raise HTTPException(status_code=400, detail="Secure challenge failed")
    
    security_stats["pow_passed"] += 1

    # 3. Standard Login Logic
    username = form_data.get("username")
    password = form_data.get("password")
    
    valid_credentials = {
        "admin": "p@ssword123",
        "testuser": "testpass1",
        "developer": "dev@cces5",
        "security": "securesystem99"
    }
    
    if username in valid_credentials and valid_credentials[username] == password:
        # Reset their failed attempts if they get it right
        if client_ip in failed_attempts:
            failed_attempts[client_ip] = 0
        return JSONResponse({"status": "success", "message": f"Welcome back, {username}!"})
    
    # Track Failed Login
    failed_attempts[client_ip] = failed_attempts.get(client_ip, 0) + 1
    if failed_attempts[client_ip] > 10:
        banned_ips.add(client_ip)
        attack_logger.warning(f"BAN: Too many failed logins from {client_ip}")
        raise HTTPException(status_code=403, detail="Too many failed attempts. IP banned.")
        
    time.sleep(0.1)  # Security delay
    return JSONResponse(status_code=401, content={"status": "failed", "message": "Access denied"})

@app.get("/api/sitrep")
async def get_sitrep():
    """Return the recent attack events from Supabase"""
    return db_manager.get_recent_logs(limit=50)

@app.get("/api/stats")
async def get_stats():
    return {
        "banned": db_manager.get_banned_ips(),
        "pow_total": security_stats["pow_passed"],
        "honey_total": security_stats["honey_triggered"],
        "global_traffic": global_traffic_count
    }

@app.post("/api/unban")
async def unban_ip(request: Request):
    try:
        data = await request.json()
        ip_to_unban = data.get("ip")
        if ip_to_unban:
            db_manager.unban_ip(ip_to_unban)
            if ip_to_unban in failed_attempts:
                failed_attempts.pop(ip_to_unban, None)
            attack_logger.info(f"UNBAN: {ip_to_unban} has been manually unbanned from the dashboard.")
            return JSONResponse({"status": "success", "message": f"Successfully unbanned {ip_to_unban}"})
    except Exception as e:
        pass
    return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid unban request"})

@app.post("/api/unban_all")
async def unban_all_ips():
    try:
        db_manager.unban_all_ips()
        failed_attempts.clear()
        attack_logger.info("UNBAN ALL: All IPs have been manually unbanned from the dashboard.")
        return JSONResponse({"status": "success", "message": "Successfully unbanned all IPs"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# Catch-all for POST attacks hitting the root or other invalid paths correctly
@app.post("/{full_path:path}")
async def catch_all_post(request: Request, full_path: str):
    client_ip = request.client.host
    
    # Track malicious blind POST attempts
    failed_attempts[client_ip] = failed_attempts.get(client_ip, 0) + 1
    if failed_attempts[client_ip] > 10:
        banned_ips.add(client_ip)
        attack_logger.warning(f"BAN: Malicious route sweeping from {client_ip} on /{full_path}")
        raise HTTPException(status_code=403, detail="Too many invalid requests. IP banned.")
        
    return JSONResponse(status_code=403, content={"status": "failed", "message": "Invalid API endpoint hit."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
