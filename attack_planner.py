"""
AI-Powered Attack Strategy Planner

Analyzes website profile and creates intelligent attack strategy:
- Determines best attack vectors
- Calculates optimal bot count and distribution
- Plans attack timing and intensity
- Adapts strategy based on defenses detected
"""

from typing import Dict, List
from colorama import Fore, Style
import json


class AttackPlanner:
    """AI-powered attack strategy planner"""
    
    def __init__(self, website_profile: Dict):
        self.profile = website_profile
        self.strategy = {
            'attack_vectors': [],
            'bot_configuration': {},
            'timing_strategy': {},
            'risk_assessment': {},
            'success_probability': 0.0
        }
    
    def plan_attack(self, max_bots: int = 50) -> Dict:
        """
        Create comprehensive attack strategy
        
        Args:
            max_bots: Maximum number of bots available
            
        Returns:
            Complete attack strategy
        """
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}🎯 AI-POWERED ATTACK PLANNING{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")
        
        # Step 1: Identify attack vectors
        self._identify_attack_vectors()
        
        # Step 2: Assess defenses
        self._assess_defenses()
        
        # Step 3: Calculate bot distribution
        self._calculate_bot_distribution(max_bots)
        
        # Step 4: Plan timing strategy
        self._plan_timing_strategy()
        
        # Step 5: Estimate success probability
        self._estimate_success_probability()
        
        # Step 6: Generate attack plan
        self._generate_attack_plan()
        
        return self.strategy
    
    def _identify_attack_vectors(self):
        """Identify all possible attack vectors"""
        print(f"{Fore.CYAN}[1/6] Identifying Attack Vectors...{Style.RESET_ALL}")
        
        vectors = []
        
        # Analyze login methods
        for login_method in self.profile.get('login_methods', []):
            vector = {
                'type': 'credential_stuffing',
                'target': login_method['url'],
                'form_action': login_method['form_action'],
                'method': login_method['method'],
                'priority': 'high',
                'complexity': 'low'
            }
            
            # Adjust complexity based on features
            if login_method.get('has_2fa'):
                vector['complexity'] = 'high'
                vector['priority'] = 'low'
                vector['note'] = '2FA detected - success unlikely'
            
            if login_method.get('type') == 'phone_based':
                vector['complexity'] = 'very_high'
                vector['note'] = 'Phone-based auth - requires SMS'
            
            vectors.append(vector)
        
        # Analyze signup methods (for account creation attacks)
        for signup_method in self.profile.get('signup_methods', []):
            vector = {
                'type': 'account_creation',
                'target': signup_method['url'],
                'form_action': signup_method['form_action'],
                'priority': 'medium',
                'complexity': 'medium'
            }
            
            if 'email_required' in signup_method.get('requirements', []):
                vector['note'] = 'Email verification required'
                vector['complexity'] = 'high'
            
            vectors.append(vector)
        
        # Analyze API endpoints
        for api_endpoint in self.profile.get('api_endpoints', []):
            vector = {
                'type': 'api_abuse',
                'target': api_endpoint['url'],
                'priority': 'medium',
                'complexity': 'medium',
                'note': 'API endpoint - may have different defenses'
            }
            vectors.append(vector)
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        vectors.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        self.strategy['attack_vectors'] = vectors
        
        print(f"{Fore.GREEN}  [✓] Identified {len(vectors)} attack vector(s){Style.RESET_ALL}")
        for i, vector in enumerate(vectors, 1):
            print(f"{Fore.YELLOW}      {i}. {vector['type'].upper()} - Priority: {vector['priority'].upper()}{Style.RESET_ALL}")
    
    def _assess_defenses(self):
        """Assess defensive capabilities"""
        print(f"\n{Fore.CYAN}[2/6] Assessing Defenses...{Style.RESET_ALL}")
        
        defenses = self.profile.get('defense_mechanisms', [])
        
        defense_score = 0  # 0 = no defenses, 100 = maximum defenses
        
        has_rate_limiting = any(d['type'] == 'rate_limiting' for d in defenses)
        has_waf = any(d['type'] == 'waf' for d in defenses)
        has_captcha = any(d['type'] == 'captcha' for d in defenses)
        
        if has_rate_limiting:
            defense_score += 40
            print(f"{Fore.YELLOW}  [!] Rate limiting detected - will slow attack{Style.RESET_ALL}")
        
        if has_waf:
            defense_score += 35
            print(f"{Fore.YELLOW}  [!] WAF detected - may block suspicious patterns{Style.RESET_ALL}")
        
        if has_captcha:
            defense_score += 25
            print(f"{Fore.YELLOW}  [!] CAPTCHA detected - may trigger on automation{Style.RESET_ALL}")
        
        if defense_score == 0:
            print(f"{Fore.GREEN}  [✓] Weak defenses - attack likely to succeed{Style.RESET_ALL}")
        
        self.strategy['risk_assessment'] = {
            'defense_score': defense_score,
            'has_rate_limiting': has_rate_limiting,
            'has_waf': has_waf,
            'has_captcha': has_captcha,
            'difficulty': 'hard' if defense_score > 60 else 'medium' if defense_score > 30 else 'easy'
        }
    
    def _calculate_bot_distribution(self, max_bots: int):
        """Calculate optimal bot count and distribution"""
        print(f"\n{Fore.CYAN}[3/6] Calculating Bot Distribution...{Style.RESET_ALL}")
        
        defense_score = self.strategy['risk_assessment']['defense_score']
        num_vectors = len(self.strategy['attack_vectors'])
        
        # Adjust bot count based on defenses
        if defense_score > 60:
            # Strong defenses - use fewer bots, slower rate
            recommended_bots = min(10, max_bots)
            requests_per_bot = 5  # per minute
            strategy_type = 'stealth'
        elif defense_score > 30:
            # Medium defenses - moderate approach
            recommended_bots = min(25, max_bots)
            requests_per_bot = 10
            strategy_type = 'balanced'
        else:
            # Weak defenses - aggressive approach
            recommended_bots = min(max_bots, 50)
            requests_per_bot = 20
            strategy_type = 'aggressive'
        
        # Distribute bots across vectors
        bots_per_vector = recommended_bots // max(num_vectors, 1)
        
        bot_config = {
            'total_bots': recommended_bots,
            'max_available': max_bots,
            'strategy_type': strategy_type,
            'requests_per_bot_per_minute': requests_per_bot,
            'distribution': {}
        }
        
        for i, vector in enumerate(self.strategy['attack_vectors']):
            if vector['priority'] == 'high':
                allocation = int(bots_per_vector * 1.5)
            elif vector['priority'] == 'medium':
                allocation = bots_per_vector
            else:
                allocation = max(1, bots_per_vector // 2)
            
            bot_config['distribution'][vector['target']] = {
                'bots': min(allocation, recommended_bots),
                'rate': requests_per_bot
            }
        
        self.strategy['bot_configuration'] = bot_config
        
        print(f"{Fore.GREEN}  [✓] Bot Configuration:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}      Total Bots: {recommended_bots} / {max_bots} available{Style.RESET_ALL}")
        print(f"{Fore.CYAN}      Strategy: {strategy_type.upper()}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}      Rate: {requests_per_bot} requests/bot/minute{Style.RESET_ALL}")
    
    def _plan_timing_strategy(self):
        """Plan attack timing and phases"""
        print(f"\n{Fore.CYAN}[4/6] Planning Timing Strategy...{Style.RESET_ALL}")
        
        strategy_type = self.strategy['bot_configuration']['strategy_type']
        
        if strategy_type == 'stealth':
            timing = {
                'phase_1': {
                    'name': 'reconnaissance',
                    'duration_seconds': 30,
                    'bots_active': '10%',
                    'purpose': 'Test defenses with minimal traffic'
                },
                'phase_2': {
                    'name': 'gradual_ramp',
                    'duration_seconds': 60,
                    'bots_active': '50%',
                    'purpose': 'Slowly increase load to avoid detection'
                },
                'phase_3': {
                    'name': 'main_attack',
                    'duration_seconds': 300,
                    'bots_active': '100%',
                    'purpose': 'Full credential testing'
                }
            }
        elif strategy_type == 'balanced':
            timing = {
                'phase_1': {
                    'name': 'warm_up',
                    'duration_seconds': 20,
                    'bots_active': '25%',
                    'purpose': 'Initial probe'
                },
                'phase_2': {
                    'name': 'main_attack',
                    'duration_seconds': 180,
                    'bots_active': '100%',
                    'purpose': 'Full attack'
                }
            }
        else:  # aggressive
            timing = {
                'phase_1': {
                    'name': 'blitz',
                    'duration_seconds': 120,
                    'bots_active': '100%',
                    'purpose': 'Fast, aggressive testing'
                }
            }
        
        self.strategy['timing_strategy'] = timing
        
        print(f"{Fore.GREEN}  [✓] Attack Phases:{Style.RESET_ALL}")
        for phase_num, phase in timing.items():
            print(f"{Fore.YELLOW}      {phase['name'].upper()}: {phase['duration_seconds']}s ({phase['bots_active']} bots){Style.RESET_ALL}")
    
    def _estimate_success_probability(self):
        """Estimate probability of successful attack"""
        print(f"\n{Fore.CYAN}[5/6] Estimating Success Probability...{Style.RESET_ALL}")
        
        # Base probability
        probability = 50.0
        
        # Adjust based on defenses
        defense_score = self.strategy['risk_assessment']['defense_score']
        probability -= (defense_score * 0.5)  # Defense score reduces success chance
        
        # Adjust based on number of attack vectors
        if len(self.strategy['attack_vectors']) > 2:
            probability += 15  # More targets = more chances
        
        # Adjust based on vulnerabilities
        critical_vulns = [v for v in self.profile.get('vulnerabilities', []) 
                         if v['severity'] in ['critical', 'high']]
        probability += (len(critical_vulns) * 10)
        
        # Cap between 0 and 100
        probability = max(0, min(100, probability))
        
        self.strategy['success_probability'] = probability
        
        color = Fore.GREEN if probability > 60 else Fore.YELLOW if probability > 30 else Fore.RED
        print(f"{color}  [!] Estimated Success Probability: {probability:.1f}%{Style.RESET_ALL}")
    
    def _generate_attack_plan(self):
        """Generate human-readable attack plan"""
        print(f"\n{Fore.CYAN}[6/6] Generating Attack Plan...{Style.RESET_ALL}")
        
        plan = {
            'summary': self._generate_summary(),
            'recommendations': self._generate_recommendations(),
            'execution_order': self._generate_execution_order()
        }
        
        self.strategy['attack_plan'] = plan
        
        print(f"{Fore.GREEN}  [✓] Attack plan generated{Style.RESET_ALL}")
    
    def _generate_summary(self) -> str:
        """Generate attack summary"""
        bot_count = self.strategy['bot_configuration']['total_bots']
        strategy = self.strategy['bot_configuration']['strategy_type']
        probability = self.strategy['success_probability']
        
        return (f"Deploy {bot_count} bots using {strategy} strategy. "
                f"Estimated success probability: {probability:.1f}%. "
                f"Target {len(self.strategy['attack_vectors'])} attack vector(s).")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate tactical recommendations"""
        recommendations = []
        
        if self.strategy['risk_assessment']['has_rate_limiting']:
            recommendations.append("Use slow, distributed approach to avoid rate limits")
        
        if self.strategy['risk_assessment']['has_captcha']:
            recommendations.append("CAPTCHA may trigger - be prepared to stop")
        
        if self.strategy['risk_assessment']['has_waf']:
            recommendations.append("Rotate User-Agents and IPs to avoid WAF detection")
        
        if not recommendations:
            recommendations.append("No special precautions needed - defenses are weak")
        
        return recommendations
    
    def _generate_execution_order(self) -> List[Dict]:
        """Generate step-by-step execution order"""
        execution = []
        
        for i, vector in enumerate(self.strategy['attack_vectors'][:3], 1):  # Top 3 vectors
            execution.append({
                'step': i,
                'action': f"Attack {vector['type']} at {vector['target']}",
                'bots': self.strategy['bot_configuration']['distribution'].get(vector['target'], {}).get('bots', 0),
                'priority': vector['priority']
            })
        
        return execution
    
    def print_strategy(self):
        """Print formatted strategy"""
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📋 ATTACK STRATEGY SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.CYAN}Summary:{Style.RESET_ALL}")
        print(f"  {self.strategy['attack_plan']['summary']}\n")
        
        print(f"{Fore.CYAN}Execution Order:{Style.RESET_ALL}")
        for step in self.strategy['attack_plan']['execution_order']:
            print(f"  {step['step']}. {step['action']}")
            print(f"     Bots: {step['bots']} | Priority: {step['priority'].upper()}")
        
        print(f"\n{Fore.CYAN}Recommendations:{Style.RESET_ALL}")
        for rec in self.strategy['attack_plan']['recommendations']:
            print(f"  • {rec}")
        
        print(f"\n{Fore.CYAN}Risk Assessment:{Style.RESET_ALL}")
        risk = self.strategy['risk_assessment']
        print(f"  Difficulty: {risk['difficulty'].upper()}")
        print(f"  Defense Score: {risk['defense_score']}/100")
        print(f"  Success Probability: {self.strategy['success_probability']:.1f}%")


if __name__ == "__main__":
    # Example usage
    mock_profile = {
        'login_methods': [{'url': 'https://example.com/login', 'form_action': '/auth', 'method': 'POST'}],
        'signup_methods': [],
        'defense_mechanisms': [],
        'vulnerabilities': [{'severity': 'high', 'issue': 'No rate limiting'}]
    }
    
    planner = AttackPlanner(mock_profile)
    strategy = planner.plan_attack(max_bots=50)
    planner.print_strategy()
