# Example Test Script
# This script demonstrates how to run the agent programmatically

"""
This example shows how to use the agent as a Python module
rather than from the command line.
"""

from agent import AttackAgent
from pathlib import Path

def run_test_example():
    """Run a simple test example"""
    
    print("="*70)
    print("CREDENTIAL STUFFING AGENT - EXAMPLE TEST")
    print("="*70)
    print()
    
    # Configuration
    target_url = "https://example.com"
    credentials_file = "credentials_example.csv"
    
    # Verify credentials file exists
    if not Path(credentials_file).exists():
        print(f"❌ Credentials file not found: {credentials_file}")
        print("   Please create it or use the example file.")
        return
    
    print(f"🎯 Target: {target_url}")
    print(f"📄 Credentials: {credentials_file}")
    print(f"⚙️  Max attempts: 10")
    print(f"⏱️  Delay: 1.0s")
    print()
    
    # Create agent
    agent = AttackAgent(
        target_url=target_url,
        credentials_file=credentials_file,
        max_attempts=10,  # Limited for testing
        delay=1.0,
        crawl_depth=2  # Shallow crawl for speed
    )
    
    # Run the agent
    success = agent.run()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("📊 Check the reports/ folder for results")
    else:
        print("\n⚠️ Test completed with warnings")
        print("📊 Check the reports/ folder for partial results")


def run_custom_test():
    """Example of custom test configuration"""
    
    print("\n" + "="*70)
    print("CUSTOM TEST CONFIGURATION EXAMPLE")
    print("="*70 + "\n")
    
    # This is how you might configure for different scenarios
    
    scenarios = {
        "quick_check": {
            "max_attempts": 10,
            "delay": 0.5,
            "crawl_depth": 1,
            "description": "Fast security check"
        },
        "thorough_test": {
            "max_attempts": 100,
            "delay": 2.0,
            "crawl_depth": 4,
            "description": "Comprehensive security assessment"
        },
        "stealth_mode": {
            "max_attempts": 50,
            "delay": 5.0,
            "crawl_depth": 3,
            "description": "Slow, stealthy testing"
        }
    }
    
    print("Available test scenarios:\n")
    for name, config in scenarios.items():
        print(f"📋 {name}:")
        print(f"   {config['description']}")
        print(f"   Attempts: {config['max_attempts']}, "
              f"Delay: {config['delay']}s, "
              f"Depth: {config['crawl_depth']}")
        print()
    
    print("To use a scenario, modify the agent initialization:")
    print()
    print("agent = AttackAgent(")
    print("    target_url='https://your-site.com',")
    print("    credentials_file='your_creds.csv',")
    print("    **scenarios['thorough_test']  # Use specific scenario")
    print(")")


if __name__ == "__main__":
    import sys
    
    print("\n🚀 Credential Stuffing Agent - Test Examples\n")
    
    # Show available examples
    print("Available examples:")
    print("  1. Basic test (example.com)")
    print("  2. Show custom configuration options")
    print()
    
    choice = input("Select example (1 or 2, or 'q' to quit): ").strip()
    
    if choice == "1":
        print()
        confirm = input("⚠️  This will test example.com. Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            run_test_example()
        else:
            print("Test cancelled.")
    elif choice == "2":
        run_custom_test()
    elif choice.lower() == 'q':
        print("Goodbye!")
    else:
        print("Invalid choice.")
    
    print("\n" + "="*70)
    print("Remember: Only test systems you own or have permission to test!")
    print("="*70 + "\n")
