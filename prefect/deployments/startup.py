#!/usr/bin/env python3
"""
Prefect Deployment Startup Script

This script handles the initialization and startup of Prefect deployments.
Run this once to set up all scheduled flows, then start the Prefect agent.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

def run_command(cmd: list, description: str) -> bool:
    """Execute a command and return success status."""
    print(f"\n{'='*60}")
    print(f"► {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            return True
        else:
            print(f"✗ {description} - FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"✗ {description} - ERROR: {e}")
        return False

def check_prefect() -> bool:
    """Check if Prefect is installed."""
    try:
        result = subprocess.run(
            ["prefect", "version"],
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.decode().strip()
            print(f"✓ Prefect is installed: {version}")
            return True
        else:
            print("✗ Prefect is not properly installed")
            return False
    except FileNotFoundError:
        print("✗ Prefect command not found. Install with: pip install prefect")
        return False

def check_python_env() -> bool:
    """Check if Python environment has required packages."""
    required = ['psycopg2', 'click', 'yaml']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All required Python packages installed")
    return True

def setup_prefect_cloud() -> bool:
    """Configure Prefect Cloud/Server connection."""
    print(f"\n{'='*60}")
    print("► Prefect Cloud/Server Configuration")
    print(f"{'='*60}\n")
    
    choice = input("Use Prefect Cloud or Local Server? (cloud/local) [local]: ").strip().lower() or "local"
    
    if choice == "cloud":
        api_key = input("Enter your Prefect Cloud API Key: ").strip()
        workspace = input("Enter Prefect workspace (username/workspace_name): ").strip()
        
        os.environ['PREFECT_API_KEY'] = api_key
        os.environ['PREFECT_API_URL'] = f"https://api.prefect.cloud/api/accounts/workspaces/{workspace}"
        print("✓ Prefect Cloud configured")
        return True
    else:
        # Local server - ensure it's running
        print("\nMake sure Prefect Server is running:")
        print("  1. In another terminal: prefect server start")
        print("  2. Or use existing running instance")
        input("Press Enter once Prefect Server is ready...")
        return True

def deploy_flows() -> bool:
    """Deploy flows to Prefect."""
    cwd = Path(__file__).parent.parent
    
    return run_command(
        [sys.executable, str(cwd / "manage_deployments.py"), "setup"],
        "Deploy Prefect flows and deployments"
    )

def create_work_queue() -> bool:
    """Create default work queue if it doesn't exist."""
    print(f"\n{'='*60}")
    print("► Work Queue Configuration")
    print(f"{'='*60}\n")
    
    # Check if default queue exists
    result = subprocess.run(
        ["prefect", "work-queue", "ls"],
        capture_output=True,
        check=False
    )
    
    if "default" in result.stdout.decode():
        print("✓ Default work queue exists")
        return True
    else:
        return run_command(
            ["prefect", "work-queue", "create", "default"],
            "Create default work queue"
        )

def start_agent(background: bool = False) -> bool:
    """Start Prefect agent."""
    print(f"\n{'='*60}")
    print("► Starting Prefect Agent")
    print(f"{'='*60}\n")
    
    cmd = ["prefect", "agent", "start", "--work-queue", "default"]
    
    if background:
        print("Starting agent in background...")
        try:
            subprocess.Popen(cmd)
            print("✓ Agent started in background")
            return True
        except Exception as e:
            print(f"✗ Failed to start agent: {e}")
            return False
    else:
        print("Starting agent in foreground (press Ctrl+C to stop)...")
        print(f"Command: {' '.join(cmd)}\n")
        try:
            subprocess.run(cmd)
            return True
        except KeyboardInterrupt:
            print("\n✓ Agent stopped")
            return True

def view_dashboard() -> bool:
    """View Prefect dashboard."""
    cwd = Path(__file__).parent.parent
    
    return run_command(
        [sys.executable, str(cwd / "manage_deployments.py"), "dashboard"],
        "Display Prefect dashboard"
    )

def print_next_steps() -> None:
    """Print next steps for user."""
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}\n")
    
    print("""
1. MONITOR DEPLOYMENTS (in new terminal):
   python prefect/manage_deployments.py dashboard
   
2. CHECK EXECUTION HISTORY:
   python prefect/manage_deployments.py history --days 7
   
3. TEST INCREMENTAL FLOW MANUALLY:
   python prefect/manage_deployments.py test-incremental
   
4. VIEW DEPLOYMENT STATISTICS:
   python prefect/manage_deployments.py stats

5. ENABLE NOTIFICATIONS (optional):
   - Slack: Set SLACK_WEBHOOK_URL environment variable
   - Email: Update recipients in schedule_config.yaml
   
SCHEDULED TIMES (UTC):
   - Daily Incremental: 2:00 AM UTC
   - Weekly Full Refresh: 3:00 AM UTC (Sundays)

MONITORING:
   - Check dbt_refresh_log table for execution history
   - Review logs in logs/prefect/ directory
   - Monitor alerts in Slack/Email as configured
""")

def main():
    """Main startup routine."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║      PREFECT INCREMENTAL REFRESH - STARTUP SCRIPT          ║
    ║                                                            ║
    ║  This script will initialize and start Prefect scheduling  ║
    ║  for automated dBT incremental refresh operations.         ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Pre-flight checks
    print("\n" + "="*60)
    print("PRE-FLIGHT CHECKS")
    print("="*60)
    
    if not check_prefect():
        print("\n✗ Prefect installation required. Exiting.")
        return False
    
    if not check_python_env():
        print("\n✗ Missing Python dependencies. Exiting.")
        return False
    
    # Configuration steps
    if not setup_prefect_cloud():
        print("\n✗ Prefect configuration failed. Exiting.")
        return False
    
    # Deployment steps
    print("\n" + "="*60)
    print("DEPLOYMENT STEPS")
    print("="*60)
    
    if not create_work_queue():
        print("\n⚠ Work queue creation failed, continuing anyway...")
    
    if not deploy_flows():
        print("\n✗ Deployment failed. Exiting.")
        return False
    
    # Agent startup
    print("\n" + "="*60)
    print("AGENT STARTUP")
    print("="*60)
    
    choice = input("\nStart Prefect agent now? (yes/no) [yes]: ").strip().lower() or "yes"
    if choice in ["yes", "y"]:
        background = input("Run in background? (yes/no) [no]: ").strip().lower() in ["yes", "y"]
        start_agent(background=background)
    else:
        print("\nAgent not started. You can start it manually with:")
        print("  prefect agent start --work-queue default")
    
    # View dashboard
    choice = input("\nView dashboard now? (yes/no) [yes]: ").strip().lower() or "yes"
    if choice in ["yes", "y"]:
        view_dashboard()
    
    print_next_steps()
    
    print(f"\n{'='*60}")
    print("✓ STARTUP COMPLETE")
    print(f"{'='*60}\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
