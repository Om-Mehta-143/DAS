"""
Report Generator Module

Generates comprehensive HTML and JSON reports from test results.
"""

import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from colorama import Fore, Style


class ReportGenerator:
    """Generates test reports in multiple formats"""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self,
                       target_url: str,
                       crawl_results: Dict,
                       test_results: Dict,
                       test_metadata: Dict) -> Dict[str, str]:
        """
        Generate comprehensive report
        
        Args:
            target_url: The tested target URL
            crawl_results: Results from web crawler
            test_results: Results from credential stuffing test
            test_metadata: Additional metadata
            
        Returns:
            Dictionary with paths to generated reports
        """
        print(f"\n{Fore.CYAN}[*] Generating reports...{Style.RESET_ALL}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = target_url.split("//")[-1].split("/")[0].replace(":", "_")
        base_filename = f"security_test_{domain}_{timestamp}"
        
        # Generate JSON report
        json_path = self._generate_json_report(
            base_filename,
            target_url,
            crawl_results,
            test_results,
            test_metadata
        )
        
        # Generate HTML report
        html_path = self._generate_html_report(
            base_filename,
            target_url,
            crawl_results,
            test_results,
            test_metadata
        )
        
        # Generate executive summary
        summary_path = self._generate_summary(
            base_filename,
            target_url,
            crawl_results,
            test_results
        )
        
        print(f"{Fore.GREEN}[✓] Reports generated successfully:{Style.RESET_ALL}")
        print(f"  - JSON: {json_path}")
        print(f"  - HTML: {html_path}")
        print(f"  - Summary: {summary_path}")
        
        return {
            'json': str(json_path),
            'html': str(html_path),
            'summary': str(summary_path)
        }
    
    def _generate_json_report(self,
                             base_filename: str,
                             target_url: str,
                             crawl_results: Dict,
                             test_results: Dict,
                             test_metadata: Dict) -> Path:
        """Generate JSON report"""
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'target_url': target_url,
                'test_type': 'credential_stuffing',
                **test_metadata
            },
            'discovery': {
                'robots_txt': crawl_results.get('robots_txt'),
                'sitemap_xml': crawl_results.get('sitemap_xml'),
                'login_pages_found': len(crawl_results.get('login_pages', [])),
                'login_pages': crawl_results.get('login_pages', []),
                'pages_crawled': len(crawl_results.get('crawled_pages', []))
            },
            'testing': {
                'total_attempts': test_results.get('total_attempts', 0),
                'successful_logins': test_results.get('successful_logins', []),
                'failed_logins_count': len(test_results.get('failed_logins', [])),
                'blocked_attempts': test_results.get('blocked_attempts', []),
                'rate_limited': test_results.get('rate_limited', False),
                'captcha_detected': test_results.get('captcha_detected', False),
                'errors': test_results.get('errors', [])
            },
            'statistics': self._calculate_statistics(test_results)
        }
        
        json_path = self.output_dir / f"{base_filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return json_path
    
    def _generate_html_report(self,
                             base_filename: str,
                             target_url: str,
                             crawl_results: Dict,
                             test_results: Dict,
                             test_metadata: Dict) -> Path:
        """Generate HTML report"""
        
        # Calculate statistics
        stats = self._calculate_statistics(test_results)
        
        # Determine risk level
        risk_level, risk_color = self._assess_risk(test_results, stats)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Test Report - {target_url}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .section {{
            padding: 30px 40px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .risk-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.2em;
            color: white;
            background: {risk_color};
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .info-card .label {{
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .info-card .value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .alert {{
            padding: 15px 20px;
            border-radius: 6px;
            margin: 15px 0;
        }}
        .alert-success {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            color: #155724;
        }}
        .alert-warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            color: #856404;
        }}
        .alert-danger {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .table th, .table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .table th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        .table tr:hover {{
            background: #f5f5f5;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-success {{
            background: #28a745;
            color: white;
        }}
        .badge-danger {{
            background: #dc3545;
            color: white;
        }}
        .badge-warning {{
            background: #ffc107;
            color: #333;
        }}
        .recommendations {{
            background: #e7f3ff;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
        }}
        .recommendations h3 {{
            color: #1976D2;
            margin-bottom: 15px;
        }}
        .recommendations ul {{
            margin-left: 20px;
        }}
        .recommendations li {{
            margin: 10px 0;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security Test Report</h1>
            <div class="subtitle">Credential Stuffing Vulnerability Assessment</div>
            <div style="margin-top: 20px; font-size: 0.9em;">
                Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="section">
            <div class="section-title">📊 Executive Summary</div>
            <div style="margin: 20px 0;">
                <strong>Target:</strong> <code>{target_url}</code><br>
                <strong>Risk Level:</strong> <span class="risk-badge">{risk_level}</span>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Total Tests</div>
                    <div class="value">{test_results.get('total_attempts', 0)}</div>
                </div>
                <div class="info-card">
                    <div class="label">Successful Logins</div>
                    <div class="value" style="color: #dc3545;">{len(test_results.get('successful_logins', []))}</div>
                </div>
                <div class="info-card">
                    <div class="label">Login Forms Found</div>
                    <div class="value">{len(crawl_results.get('login_pages', []))}</div>
                </div>
                <div class="info-card">
                    <div class="label">Rate Limiting</div>
                    <div class="value">{'✓ Active' if test_results.get('rate_limited') else '✗ Not Detected'}</div>
                </div>
            </div>
        </div>

        <!-- Discovery Results -->
        <div class="section">
            <div class="section-title">🔍 Discovery Phase</div>
            
            <h3>Special Files</h3>
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">robots.txt</div>
                    <div class="value">{'✓ Found' if crawl_results.get('robots_txt', {}).get('exists') else '✗ Not Found'}</div>
                </div>
                <div class="info-card">
                    <div class="label">sitemap.xml</div>
                    <div class="value">{'✓ Found' if crawl_results.get('sitemap_xml', {}).get('exists') else '✗ Not Found'}</div>
                </div>
            </div>

            <h3 style="margin-top: 30px;">Login Pages Discovered</h3>
            {self._generate_login_pages_table(crawl_results.get('login_pages', []))}

            <!-- Tech Stack & Defenses -->
            <div style="margin-top: 40px;">
                {self._generate_tech_stack_section(crawl_results)}
            </div>

            <!-- Detailed Discovery Log -->
            <div style="margin-top: 40px;">
                <div class="section-title" style="font-size: 1.5em; border-bottom: none;">Detailed Discovery Log</div>
                {self._generate_discovery_log_table(crawl_results.get('discovery_log', []))}
            </div>
        </div>

        <!-- Test Results -->
        <div class="section">
            <div class="section-title">🧪 Testing Results</div>
            
            {''.join([f'<div class="alert alert-danger"><strong>⚠️ Critical Finding:</strong> {len(test_results.get("successful_logins", []))} successful login(s) detected with test credentials!</div>' if test_results.get('successful_logins') else ''])}
            
            {''.join([f'<div class="alert alert-success"><strong>✓ Good:</strong> Rate limiting is active.</div>' if test_results.get('rate_limited') else '<div class="alert alert-warning"><strong>⚠️ Warning:</strong> No rate limiting detected during testing.</div>'])}
            
            {''.join([f'<div class="alert alert-warning"><strong>ℹ️ Notice:</strong> CAPTCHA protection detected.</div>' if test_results.get('captcha_detected') else ''])}

            <h3>Performance Statistics</h3>
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Success Rate</div>
                    <div class="value">{stats.get('success_rate', 0):.1f}%</div>
                </div>
                <div class="info-card">
                    <div class="label">Avg Response Time</div>
                    <div class="value">{stats.get('avg_response_time', 0):.2f}s</div>
                </div>
                <div class="info-card">
                    <div class="label">Failed Attempts</div>
                    <div class="value">{len(test_results.get('failed_logins', []))}</div>
                </div>
                <div class="info-card">
                    <div class="label">Errors</div>
                    <div class="value">{len(test_results.get('errors', []))}</div>
                </div>
            </div>

            {self._generate_successful_logins_table(test_results.get('successful_logins', []))}
        </div>

        <!-- Recommendations -->
        <div class="section">
            <div class="section-title">💡 Recommendations</div>
            <div class="recommendations">
                {self._generate_recommendations(test_results, crawl_results)}
            </div>
        </div>

        <div class="footer">
            <p>This report was generated by the Distributed Attack Simulation & Defense Testing Platform</p>
            <p>⚠️ This test was conducted for authorized security assessment purposes only.</p>
        </div>
    </div>
</body>
</html>"""
        
        html_path = self.output_dir / f"{base_filename}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_path
    
    def _generate_summary(self,
                         base_filename: str,
                         target_url: str,
                         crawl_results: Dict,
                         test_results: Dict) -> Path:
        """Generate executive summary in markdown"""
        
        stats = self._calculate_statistics(test_results)
        risk_level, _ = self._assess_risk(test_results, stats)
        
        summary = f"""# Security Test Summary

**Target:** {target_url}  
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Risk Level:** {risk_level}

## Key Findings

- **Login Forms Discovered:** {len(crawl_results.get('login_pages', []))}
- **Credential Tests Performed:** {test_results.get('total_attempts', 0)}
- **Successful Logins:** {len(test_results.get('successful_logins', []))}
- **Rate Limiting:** {'Active ✓' if test_results.get('rate_limited') else 'Not Detected ✗'}
- **CAPTCHA Protection:** {'Active ✓' if test_results.get('captcha_detected') else 'Not Detected ✗'}

## Risk Assessment

{self._get_risk_explanation(risk_level)}

## Immediate Actions Required

{self._get_immediate_actions(test_results, risk_level)}

## Vulnerability Score: {self._calculate_vulnerability_score(test_results, stats):.1f}/10

---
*For detailed findings, see the full HTML report.*
"""
        
        summary_path = self.output_dir / f"{base_filename}_summary.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary_path
    
    def _calculate_statistics(self, test_results: Dict) -> Dict:
        """Calculate test statistics"""
        total = test_results.get('total_attempts', 0)
        successes = len(test_results.get('successful_logins', []))
        
        success_rate = (successes / total * 100) if total > 0 else 0
        
        timing_data = test_results.get('timing_data', [])
        avg_response_time = sum(timing_data) / len(timing_data) if timing_data else 0
        
        return {
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'total_attempts': total,
            'successful_logins': successes
        }
    
    def _assess_risk(self, test_results: Dict, stats: Dict) -> tuple:
        """Assess risk level based on results"""
        successes = len(test_results.get('successful_logins', []))
        rate_limited = test_results.get('rate_limited', False)
        captcha = test_results.get('captcha_detected', False)
        
        if successes > 0:
            if not rate_limited and not captcha:
                return "CRITICAL", "#dc3545"
            else:
                return "HIGH", "#ff6b6b"
        elif not rate_limited and not captcha:
            return "MEDIUM", "#ffc107"
        elif rate_limited or captcha:
            return "LOW", "#28a745"
        else:
            return "MEDIUM", "#ffc107"
    
    def _calculate_vulnerability_score(self, test_results: Dict, stats: Dict) -> float:
        """Calculate vulnerability score out of 10"""
        score = 0.0
        
        # Successful logins (worst)
        if len(test_results.get('successful_logins', [])) > 0:
            score += 5.0
        
        # No rate limiting
        if not test_results.get('rate_limited', False):
            score += 3.0
        
        # No CAPTCHA
        if not test_results.get('captcha_detected', False):
            score += 2.0
        
        return score
    
    def _generate_login_pages_table(self, login_pages: List[Dict]) -> str:
        """Generate HTML table of login pages"""
        if not login_pages:
            return "<p>No login pages found.</p>"
        
        rows = ""
        for idx, page in enumerate(login_pages, 1):
            confidence_badge = f'<span class="badge badge-{"success" if page.get("confidence") == "high" or page.get("confidence") == "verified" else "warning"}">{page.get("confidence", "unknown").upper()}</span>'
            
            screenshot_html = "N/A"
            if page.get("screenshot"):
                # Use relative path for HTML report
                rel_path = Path(page.get("screenshot")).name
                screenshot_html = f'<a href="screenshots/{rel_path}" target="_blank">View Evidence</a>'

            rows += f"""
            <tr>
                <td>{idx}</td>
                <td><code>{page.get('page_url', 'N/A')}</code></td>
                <td>{page.get('form_method', 'N/A')}</td>
                <td>{confidence_badge}</td>
                <td>{screenshot_html}</td>
            </tr>
            """
        
        return f"""
        <table class="table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Page URL</th>
                    <th>Method</th>
                    <th>Confidence</th>
                    <th>Evidence</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_successful_logins_table(self, successful_logins: List[Dict]) -> str:
        """Generate table of successful logins"""
        if not successful_logins:
            return ""
        
        rows = ""
        for idx, login in enumerate(successful_logins, 1):
            rows += f"""
            <tr>
                <td>{idx}</td>
                <td><code>{login.get('username', 'N/A')}</code></td>
                <td>••••••••</td>
                <td>{login.get('response_time', 0):.2f}s</td>
                <td><span class="badge badge-danger">SUCCESS</span></td>
            </tr>
            """
        
        return f"""
        <h3 style="margin-top: 30px; color: #dc3545;">⚠️ Successful Login Attempts</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Response Time</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """
    
    def _generate_recommendations(self, test_results: Dict, crawl_results: Dict) -> str:
        """Generate security recommendations"""
        recommendations = []
        
        if len(test_results.get('successful_logins', [])) > 0:
            recommendations.append("<li><strong>URGENT:</strong> Force password resets for compromised accounts immediately.</li>")
            recommendations.append("<li>Implement strong password policies (min 12 characters, complexity requirements).</li>")
            recommendations.append("<li>Enable multi-factor authentication (MFA) for all user accounts.</li>")
        
        if not test_results.get('rate_limited', False):
            recommendations.append("<li><strong>Implement rate limiting:</strong> Limit login attempts to 5 per minute per IP address.</li>")
            recommendations.append("<li>Add progressive delays after failed attempts (exponential backoff).</li>")
        
        if not test_results.get('captcha_detected', False):
            recommendations.append("<li><strong>Add CAPTCHA protection:</strong> Implement reCAPTCHA or hCaptcha after 3 failed attempts.</li>")
        
        recommendations.append("<li>Monitor for suspicious login patterns and implement alerting.</li>")
        recommendations.append("<li>Consider implementing device fingerprinting and behavioral analysis.</li>")
        recommendations.append("<li>Use Web Application Firewall (WAF) to detect and block automated attacks.</li>")
        recommendations.append("<li>Implement account lockout after multiple failed attempts.</li>")
        recommendations.append("<li>Log all authentication attempts for security analysis.</li>")
        
        if recommendations:
            return f"<h3>Security Measures to Implement:</h3><ul>{''.join(recommendations)}</ul>"
        else:
            return "<h3>✓ Current security posture appears adequate</h3><p>Continue monitoring and testing regularly.</p>"
    
    def _get_risk_explanation(self, risk_level: str) -> str:
        """Get explanation for risk level"""
        explanations = {
            "CRITICAL": "The application is highly vulnerable to credential stuffing attacks. Successful logins were achieved with test credentials, indicating weak or compromised passwords without adequate protection mechanisms.",
            "HIGH": "The application shows significant vulnerability. While some protection mechanisms exist, they are insufficient to prevent credential stuffing attacks effectively.",
            "MEDIUM": "The application has basic security controls but could benefit from additional protective measures against credential stuffing attacks.",
            "LOW": "The application demonstrates good resistance to credential stuffing attacks with active rate limiting and/or CAPTCHA protection."
        }
        return explanations.get(risk_level, "Risk level assessment pending.")
    
    def _get_immediate_actions(self, test_results: Dict, risk_level: str) -> str:
        """Get immediate actions based on risk"""
        if risk_level == "CRITICAL":
            return """1. **IMMEDIATE:** Disable compromised accounts
2. **IMMEDIATE:** Force password reset for all affected users
3. **URGENT:** Implement rate limiting within 24 hours
4. **URGENT:** Add CAPTCHA protection
5. **HIGH:** Enable MFA for all accounts"""
        elif risk_level == "HIGH":
            return """1. **URGENT:** Implement rate limiting
2. **URGENT:** Add CAPTCHA after failed attempts
3. **HIGH:** Review and strengthen password policies
4. **MEDIUM:** Plan MFA rollout"""
        elif risk_level == "MEDIUM":
            return """1. **HIGH:** Enhance rate limiting rules
2. **MEDIUM:** Consider adding CAPTCHA
3. **MEDIUM:** Review authentication logs regularly"""
        else:
            return """1. **LOW:** Continue monitoring authentication patterns
2. **LOW:** Regular security testing recommended
3. **INFO:** Current controls appear adequate"""


    
    def _generate_tech_stack_section(self, crawl_results: Dict) -> str:
        """Generate Tech Stack & Defense Breakdown"""
        stack = crawl_results.get('technology_stack', {})
        defenses = crawl_results.get('defense_mechanisms', [])
        
        stack_html = ""
        for k, v in stack.items():
            if v and v != 'unknown':
                stack_html += f'<div class="info-card"><div class="label">{k.title()}</div><div class="value">{v}</div></div>'
        
        defense_html = ""
        if defenses:
            for d in defenses:
                defense_html += f'<span class="badge badge-warning" style="font-size: 1em; margin: 5px;">🛡️ {d.get("provider", "Generic")} {d.get("type", "WAF")}</span>'
        else:
            defense_html = '<span class="badge badge-success" style="font-size: 1em;">No Active Defenses Detected</span>'

        return f"""
        <h3>Technology Stack</h3>
        <div class="info-grid">
            {stack_html if stack_html else '<div class="info-card"><div class="value">No items detected</div></div>'}
        </div>
        
        <h3 style="margin-top: 20px;">Defense Mechanisms</h3>
        <div style="margin-top: 10px;">
            {defense_html}
        </div>
        """

    def _generate_discovery_log_table(self, logs: List[Dict]) -> str:
        """Generate detailed discovery log table"""
        if not logs:
            return "<p>No discovery logs available.</p>"
            
        rows = ""
        for idx, log in enumerate(logs[:50], 1): # Limit to 50 for readability
            status = log.get('status_code')
            found = log.get('found')
            
            # Style status code
            status_class = "badge-success" if status == 200 else "badge-warning" if status in [403, 429] else "badge-danger" if status == 404 else "badge-info"
            status_badge = f'<span class="badge {status_class}">{status}</span>'
            
            # Style Found
            found_icon = "✅ FOUND" if found else "❌"
            row_style = "background-color: #e8f5e9;" if found else ""
            
            rows += f"""
            <tr style="{row_style}">
                <td>{idx}</td>
                <td><code>{log.get('url')}</code></td>
                <td>{log.get('source').upper()}</td>
                <td>{status_badge}</td>
                <td><strong>{found_icon}</strong></td>
            </tr>
            """
            
        return f"""
        <p><em>Showing last {len(logs[:50])} checks...</em></p>
        <table class="table" style="font-size: 0.9em;">
            <thead>
                <tr>
                    <th>#</th>
                    <th>URL Checked</th>
                    <th>Source</th>
                    <th>Status</th>
                    <th>Outcome</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """


if __name__ == "__main__":
    # Test report generation
    generator = ReportGenerator()
    print("Report generator initialized")
