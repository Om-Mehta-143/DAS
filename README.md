# Credential Stuffing Attack Agent

## 🎯 Overview

The **Credential Stuffing Attack Agent** is the first module of our **Distributed Attack Simulation & Defense Testing Platform**. This agent helps organizations assess their vulnerability to credential stuffing attacks by simulating realistic attack patterns in a controlled, ethical manner.

## ⚠️ Important Legal Notice

**THIS TOOL IS FOR AUTHORIZED SECURITY TESTING ONLY**

- ✅ Only test systems you own or have explicit written permission to test
- ❌ Unauthorized testing is illegal and unethical
- ⚠️ You are responsible for ensuring compliance with all applicable laws
- 📋 Always obtain proper authorization before running tests

## 🚀 Features

### What This Agent Does

1. **URL Validation & Correction**
   - Validates target URLs
   - Automatically corrects common URL formatting issues
   - Checks if target is accessible

2. **Intelligent Web Crawling**
   - Discovers `robots.txt` and `sitemap.xml`
   - Finds login pages automatically
   - Identifies login forms with high confidence
   - Respects crawl depth limits

3. **Credential Stuffing Testing**
   - Tests discovered login forms with provided credentials
   - Implements rate limiting for safety
   - Detects defense mechanisms (rate limiting, CAPTCHA)
   - Tracks successful/failed attempts

4. **Comprehensive Reporting**
   - Beautiful HTML reports
   - JSON data exports
   - Executive summaries in Markdown
   - Risk assessment and recommendations

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Verify installation:**
```powershell
python agent.py --help
```

## 🎮 Usage

### Basic Usage

```powershell
python agent.py <target-url> <credentials-file>
```

### Example

```powershell
python agent.py https://example.com credentials_example.csv
```

### Advanced Options

```powershell
# Custom number of attempts
python agent.py https://example.com creds.csv --max-attempts 50

# Increase delay between attempts (slower, more stealthy)
python agent.py https://example.com creds.csv --delay 2.0

# Deep crawl (more thorough discovery)
python agent.py https://example.com creds.csv --crawl-depth 5

# Combine options
python agent.py https://example.com creds.csv --max-attempts 30 --delay 1.5 --crawl-depth 4
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `target` | Target website URL (required) | - |
| `credentials` | Path to credentials CSV file (required) | - |
| `--max-attempts` | Maximum credential attempts | 100 |
| `--delay` | Delay between attempts (seconds) | 1.0 |
| `--crawl-depth` | Maximum crawl depth | 3 |

## 📁 Credentials File Format

Create a CSV file with `username` and `password` columns:

```csv
username,password
admin,admin123
user@example.com,password123
testuser,test12345
```

**Example file:** [`credentials_example.csv`](credentials_example.csv)

## 📊 Output

The agent generates three types of reports in the `reports/` directory:

### 1. HTML Report
- Visual, interactive report
- Color-coded risk levels
- Detailed findings and recommendations
- **Open in browser for best experience**

### 2. JSON Report
- Machine-readable format
- Complete test data
- Suitable for automation/parsing

### 3. Markdown Summary
- Executive summary
- Quick overview of findings
- Immediate action items

### Example Output Structure

```
reports/
├── security_test_example.com_20240211_143052.html
├── security_test_example.com_20240211_143052.json
└── security_test_example.com_20240211_143052_summary.md
```

## 🔍 How It Works

### Workflow

```
┌─────────────────────────────────────────┐
│  1. URL Validation                      │
│  - Validate format                      │
│  - Check accessibility                  │
│  - Correct common issues                │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  2. Web Crawling                        │
│  - Find robots.txt, sitemap.xml         │
│  - Discover login pages                 │
│  - Identify form fields                 │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  3. Credential Stuffing Test            │
│  - Load credential pairs                │
│  - Test login forms                     │
│  - Detect defenses                      │
│  - Track results                        │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  4. Report Generation                   │
│  - Risk assessment                      │
│  - Security recommendations             │
│  - Multiple output formats              │
└─────────────────────────────────────────┘
```

## 🛡️ Safety Features

1. **Rate Limiting**
   - Configurable delays between attempts
   - Prevents accidental DDoS

2. **Automatic Defense Detection**
   - Stops when rate limiting is detected
   - Stops when CAPTCHA appears
   - Respects target defenses

3. **Limited Scope**
   - Configurable maximum attempts
   - Configurable crawl depth
   - Stays on target domain only

## 🧪 Testing the Agent

### Test Against Your Own Application

**Safe Testing Steps:**

1. Set up a test environment (not production!)
2. Deploy your application
3. Create test credentials
4. Run the agent:
```powershell
python agent.py http://localhost:3000 test_credentials.csv
```

### Example Test Scenario

```powershell
# Create test credentials
echo "username,password
testuser,wrongpass
admin,wrongpass
user@test.com,wrongpass" > test_creds.csv

# Run agent
python agent.py http://localhost:8080 test_creds.csv --max-attempts 10 --delay 0.5
```

## 📈 Understanding Results

### Risk Levels

| Risk Level | Meaning |
|------------|---------|
| 🔴 **CRITICAL** | Successful logins with test credentials + no protection |
| 🟠 **HIGH** | Successful logins but some protection exists |
| 🟡 **MEDIUM** | No successful logins but weak protections |
| 🟢 **LOW** | Strong protections (rate limiting + CAPTCHA) |

### Key Metrics

- **Success Rate**: % of credential attempts that succeeded
- **Response Time**: Average time per login attempt
- **Rate Limiting**: Whether rate limiting was detected
- **CAPTCHA**: Whether CAPTCHA protection was encountered

## 🔧 Troubleshooting

### Common Issues

**1. SSL Certificate Errors**
```
Solution: The agent disables SSL verification for testing.
In production, ensure SSL certificates are valid.
```

**2. Connection Timeouts**
```
Solution: Target may be slow or blocking requests.
Increase --delay or check if target is accessible.
```

**3. No Login Pages Found**
```
Solution: Login might be behind JavaScript.
Future versions will support browser automation.
```

**4. "Permission Denied" on reports folder**
```powershell
# Create reports directory manually
mkdir reports
```

## 🔮 Future Enhancements

### Planned Features

- [ ] Browser-based testing (Playwright) for JavaScript-heavy sites
- [ ] Multi-page login flows (e.g., username → password on separate pages)
- [ ] Support for 2FA/MFA testing
- [ ] Distributed node support (multiple IPs)
- [ ] API endpoint testing
- [ ] Custom attack patterns
- [ ] Real-time dashboard
- [ ] Integration with bug bounty platforms

## 🏗️ Project Structure

```
GPTMAKING-TRIAL/
├── agent.py                    # Main entry point
├── url_validator.py            # Step 1: URL validation
├── web_crawler.py              # Step 2: Crawling & discovery
├── credential_tester.py        # Step 3: Credential stuffing
├── report_generator.py         # Step 4: Report generation
├── requirements.txt            # Python dependencies
├── credentials_example.csv     # Example credentials file
├── .env.example               # Configuration template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── reports/                   # Generated reports (created automatically)
```

## 📚 Additional Documentation

- [Project Overview](PROJECT_OVERVIEW.md) - High-level architecture
- [Technical Architecture](ARCHITECTURE.md) - Detailed technical design

## 🤝 Contributing

This is part of a larger security testing platform. Contributions are welcome!

### Development Setup

1. Install development dependencies:
```powershell
pip install -r requirements.txt
pip install pytest pytest-asyncio black
```

2. Run tests:
```powershell
pytest
```

3. Format code:
```powershell
black *.py
```

## 📝 License

This tool is provided for educational and authorized security testing purposes only.

## ⚖️ Ethical Use Guidelines

By using this tool, you agree to:

1. ✅ Only test systems you own or have written permission to test
2. ✅ Respect rate limits and website capacity
3. ✅ Report vulnerabilities responsibly
4. ✅ Use findings to improve security, not exploit weaknesses
5. ❌ Never use against systems without authorization
6. ❌ Never use for malicious purposes
7. ❌ Never share or sell discovered vulnerabilities

## 🆘 Support

For issues, questions, or contributions:

1. Check existing documentation
2. Review troubleshooting section
3. Open an issue with detailed information

## ⭐ Acknowledgments

Built as part of the **Distributed Attack Simulation & Defense Testing Platform** project.

---

**Remember: With great power comes great responsibility. Use ethically! 🛡️**
