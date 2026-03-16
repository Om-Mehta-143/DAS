"""
Credential Stuffing Attack Agent
Main entry point for security testing

This agent performs:
1. URL validation and correction
2. Web crawling to discover login pages
3. Credential stuffing vulnerability testing
4. Comprehensive report generation
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
import warnings

# Initialize colorama for Windows
init(autoreset=True)

# Suppress SSL warnings for testing
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Import our modules
from url_validator import URLValidator
from web_crawler import WebCrawler
from credential_tester import CredentialStuffingTester
from report_generator import ReportGenerator


class AttackAgent:
    """Main attack agent orchestrator"""
    
    def __init__(self, 
                 target_url: str,
                 credentials_file: str,
                 max_attempts: int = 100,
                 delay: float = 1.0,
                 crawl_depth: int = 3):
        """
        Initialize the attack agent
        
        Args:
            target_url: Target website URL
            credentials_file: Path to credentials CSV file
            max_attempts: Maximum credential attempts
            delay: Delay between attempts (seconds)
            crawl_depth: Maximum crawl depth
        """
        self.target_url = target_url
        self.credentials_file = credentials_file
        self.max_attempts = max_attempts
        self.delay = delay
        self.crawl_depth = crawl_depth
        
        # Initialize components
        self.validator = URLValidator()
        self.crawler = None
        self.tester = None
        self.reporter = ReportGenerator()
        
        # Results storage
        self.validated_url = None
        self.crawl_results = {}
        self.test_results = {}
    
    def run(self):
        """Execute the full attack simulation workflow"""
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}   CREDENTIAL STUFFING ATTACK AGENT{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}   Distributed Attack Simulation & Defense Testing Platform{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⚠️  AUTHORIZED TESTING ONLY - Ensure you have permission!{Style.RESET_ALL}\n")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Validate URL
            if not self._step1_validate_url():
                return False
            
            # Step 2: Crawl website
            if not self._step2_crawl_website():
                return False
            
            # Step 3: Test credential stuffing
            if not self._step3_test_credentials():
                return False
            
            # Step 4: Generate report
            if not self._step4_generate_report():
                return False
            
            # Success summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ ATTACK SIMULATION COMPLETE{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
            print(f"\nTotal duration: {duration:.2f} seconds")
            print(f"Reports generated in: ./reports/\n")
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[!] Test interrupted by user{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"\n\n{Fore.RED}[✗] Fatal error: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False
    
    def _step1_validate_url(self) -> bool:
        """Step 1: Validate and correct target URL"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}STEP 1: URL Validation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        is_valid, corrected_url, message = self.validator.validate_and_correct(self.target_url)
        
        if not is_valid:
            print(f"\n{Fore.RED}[✗] URL validation failed: {message}{Style.RESET_ALL}")
            print(f"{Fore.RED}[✗] Cannot proceed with testing{Style.RESET_ALL}")
            return False
        
        self.validated_url = corrected_url
        print(f"\n{Fore.GREEN}[✓] URL validated successfully{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    Target: {self.validated_url}{Style.RESET_ALL}")
        return True
    
    def _step2_crawl_website(self) -> bool:
        """Step 2: Crawl website to discover login pages"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}STEP 2: Web Crawling & Discovery{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        self.crawler = WebCrawler(
            self.validated_url,
            max_depth=self.crawl_depth,
            max_pages=50
        )
        
        self.crawl_results = self.crawler.crawl()
        
        if not self.crawl_results.get('login_pages'):
            print(f"\n{Fore.YELLOW}[!] No login pages discovered{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Cannot proceed with credential testing{Style.RESET_ALL}")
            
            # Still generate a report for crawl results
            print(f"\n{Fore.CYAN}[*] Generating discovery report...{Style.RESET_ALL}")
            self.reporter.generate_report(
                self.validated_url,
                self.crawl_results,
                {},
                {'status': 'no_login_pages_found'}
            )
            return False
        
        print(f"\n{Fore.GREEN}[✓] Discovery complete{Style.RESET_ALL}")
        print(f"{Fore.GREEN}    Found {len(self.crawl_results['login_pages'])} login page(s){Style.RESET_ALL}")
        return True
    
    def _step3_test_credentials(self) -> bool:
        """Step 3: Test credential stuffing on discovered login pages"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}STEP 3: Credential Stuffing Test{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        # Initialize tester
        self.tester = CredentialStuffingTester(
            max_attempts=self.max_attempts,
            delay_between_attempts=self.delay
        )
        
        # Load credentials
        credentials = self.tester.load_credentials(self.credentials_file)
        
        if not credentials:
            print(f"\n{Fore.RED}[✗] No credentials loaded{Style.RESET_ALL}")
            return False
        
        # Test first login page (could be extended to test all)
        first_login_page = self.crawl_results['login_pages'][0]
        print(f"\n{Fore.YELLOW}[*] Testing first login page: {first_login_page['page_url']}{Style.RESET_ALL}")
        
        if len(self.crawl_results['login_pages']) > 1:
            print(f"{Fore.YELLOW}[*] Note: {len(self.crawl_results['login_pages']) - 1} other login page(s) found but not tested{Style.RESET_ALL}")
        
        # Run the test
        self.test_results = self.tester.test_login_form(first_login_page, credentials)
        
        print(f"\n{Fore.GREEN}[✓] Testing complete{Style.RESET_ALL}")
        return True
    
    def _step4_generate_report(self) -> bool:
        """Step 4: Generate comprehensive report"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}STEP 4: Report Generation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        test_metadata = {
            'agent_version': '1.0',
            'max_attempts_configured': self.max_attempts,
            'delay_configured': self.delay,
            'crawl_depth': self.crawl_depth
        }
        
        report_paths = self.reporter.generate_report(
            self.validated_url,
            self.crawl_results,
            self.test_results,
            test_metadata
        )
        
        print(f"\n{Fore.GREEN}[✓] Reports generated:{Style.RESET_ALL}")
        for report_type, path in report_paths.items():
            print(f"{Fore.GREEN}    {report_type.upper()}: {path}{Style.RESET_ALL}")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Credential Stuffing Attack Agent - Security Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic test:
    python agent.py https://example.com credentials.csv

  Custom settings:
    python agent.py https://example.com creds.csv --max-attempts 50 --delay 2.0

  Deep crawl:
    python agent.py https://example.com creds.csv --crawl-depth 5

⚠️  WARNING: Only use on systems you own or have explicit permission to test!
        """
    )
    
    parser.add_argument(
        'target',
        help='Target website URL (e.g., https://example.com)'
    )
    
    parser.add_argument(
        'credentials',
        help='Path to credentials CSV file (with username,password columns)'
    )
    
    parser.add_argument(
        '--max-attempts',
        type=int,
        default=100,
        help='Maximum number of credential attempts (default: 100)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between attempts in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--crawl-depth',
        type=int,
        default=3,
        help='Maximum crawl depth (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Validate credentials file exists
    if not Path(args.credentials).exists():
        print(f"{Fore.RED}Error: Credentials file not found: {args.credentials}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Create and run agent
    agent = AttackAgent(
        target_url=args.target,
        credentials_file=args.credentials,
        max_attempts=args.max_attempts,
        delay=args.delay,
        crawl_depth=args.crawl_depth
    )
    
    success = agent.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
