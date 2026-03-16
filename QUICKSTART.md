# Quick Start Guide

## Get Started in 5 Minutes! 🚀

### Step 1: Install Dependencies (2 minutes)

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

**Expected output:** Installation messages for aiohttp, requests, beautifulsoup4, etc.

### Step 2: Test the Agent (1 minute)

Test against a public example site:

```powershell
python agent.py https://example.com credentials_example.csv --max-attempts 5
```

**What happens:**
- ✅ Validates the URL
- ✅ Crawls the website
- ⚠️ Won't find login pages (example.com has none)
- ✅ Generates a discovery report

### Step 3: View Your Report (1 minute)

```powershell
# Open the reports folder
cd reports

# Find the latest HTML file
dir *.html | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

Open the HTML file in your browser to see the beautiful report!

### Step 4: Test Your Own Application (ongoing)

**CRITICAL: Only test systems you own or have permission to test!**

1. **Set up a test environment** (not production!)

2. **Create test credentials:**

```powershell
# Create a test credentials file
@"
username,password
testuser1,wrongpassword111
testuser2,wrongpassword222
admin,admin123
"@ | Out-File -Encoding utf8 my_test_creds.csv
```

3. **Run the agent:**

```powershell
# Example: Testing local development server
python agent.py http://localhost:3000 my_test_creds.csv

# Example: Testing staging environment
python agent.py https://staging.yourcompany.com my_test_creds.csv --max-attempts 20 --delay 2.0
```

4. **Review findings:**
   - Check the `reports/` folder
   - Open the HTML report
   - Review the security recommendations
   - Implement suggested improvements

---

## Common Use Cases

### Use Case 1: Pre-Production Security Check

**When:** Before deploying new authentication features

```powershell
# Run against staging environment
python agent.py https://staging.myapp.com test_credentials.csv --max-attempts 50 --delay 1.5

# Review report
# Verify rate limiting works
# Verify CAPTCHA triggers
# Fix any issues before production
```

### Use Case 2: Penetration Testing

**When:** Annual security audit

```powershell
# Comprehensive test with deep crawl
python agent.py https://myapp.com pentest_credentials.csv --max-attempts 200 --crawl-depth 5 --delay 2.0

# Document findings
# Create remediation plan
# Retest after fixes
```

### Use Case 3: Continuous Security Testing

**When:** Regular automated checks (weekly/monthly)

```powershell
# Quick health check
python agent.py https://myapp.com basic_test_creds.csv --max-attempts 20 --delay 1.0

# Compare with previous reports
# Monitor for regressions
# Alert on critical findings
```

---

## Interpreting Results

### ✅ Good Signs (Low Risk)

- Rate limiting activated after few attempts
- CAPTCHA protection detected
- No successful logins with test credentials
- Fast detection times

**Example Finding:**
```
✓ Rate limiting triggered after 5 attempts
✓ CAPTCHA required after 3 failed attempts
✓ No successful logins
Risk Level: LOW
```

### ⚠️ Warning Signs (Medium Risk)

- Slow detection (>30 seconds)
- Weak rate limiting (>100 attempts)
- No CAPTCHA protection
- Inconsistent blocking

**Example Finding:**
```
⚠️ Rate limiting after 50 attempts (weak)
⚠️ No CAPTCHA detected
✓ No successful logins
Risk Level: MEDIUM
```

### 🚨 Critical Issues (High/Critical Risk)

- Successful logins with test credentials
- No rate limiting detected
- No CAPTCHA protection
- Weak password policies

**Example Finding:**
```
🚨 3 successful logins with common passwords!
✗ No rate limiting detected
✗ No CAPTCHA protection
Risk Level: CRITICAL
```

---

## Next Steps After Testing

### If Risk is LOW ✅
1. Continue regular testing (quarterly)
2. Monitor authentication logs
3. Keep defenses updated

### If Risk is MEDIUM ⚠️
1. Implement recommendations from report
2. Add stricter rate limiting
3. Consider adding CAPTCHA
4. Retest within 1 week

### If Risk is HIGH/CRITICAL 🚨
1. **URGENT:** Review all user accounts
2. Force password resets if needed
3. Implement rate limiting immediately
4. Add CAPTCHA protection
5. Enable MFA for all accounts
6. Retest within 24 hours
7. Consider external security audit

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| "No login pages found" | Increase `--crawl-depth` or check if login is JavaScript-based |
| Connection timeout | Target is slow; increase `--delay` |
| SSL errors | Tool disables SSL verification for testing |
| Reports not generated | Check `reports/` folder was created; create it manually if needed |
| Agent stops immediately | Check if credentials file exists and is formatted correctly |

---

## Safety Reminders 🛡️

Before EVERY test run, ask yourself:

1. ✅ Do I own this system?
2. ✅ Do I have written permission to test?
3. ✅ Is this a test/staging environment?
4. ✅ Have I configured reasonable rate limits?
5. ✅ Am I documenting my findings properly?

**If you answered NO to any question, DO NOT proceed!**

---

## Getting Help

1. **Read the README:** [README.md](README.md)
2. **Check architecture docs:** [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Review project overview:** [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
4. **Examine the code:** All modules are well-commented

---

## What's Next?

After mastering the credential stuffing agent, the full platform will include:

- 🔄 **Distributed Attack Nodes** - Multi-origin testing
- 📊 **Real-time Dashboard** - Live monitoring
- 🤖 **Multiple Attack Modules** - Brute force, API abuse, scraping
- 📈 **Trend Analysis** - Track improvements over time
- 🔗 **CI/CD Integration** - Automated security testing

Stay tuned! 🚀

---

**Happy (Ethical) Hacking! 🎯**
