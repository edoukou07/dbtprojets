#!/usr/bin/env python
"""
Prefect Setup and Management Script
Initialize deployments, manage schedules, and monitor incremental refresh
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import click
import psycopg2
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

PROJECT_DIR = Path(__file__).parent.parent.parent


class PrefectManager:
    """Manage Prefect deployments and schedules"""
    
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.db_host = os.getenv('DWH_DB_HOST', 'localhost')
        self.db_port = os.getenv('DWH_DB_PORT', '5432')
        self.db_name = os.getenv('DWH_DB_NAME', 'sigeti_node_db')
        self.db_user = os.getenv('DWH_DB_USER', 'postgres')
        self.db_password = os.getenv('DWH_DB_PASSWORD', 'postgres')
    
    def setup_deployments(self):
        """Initialize Prefect deployments"""
        click.echo("Setting up Prefect deployments...")
        
        try:
            os.chdir(str(self.project_dir))
            
            # Create deployments
            cmd = [
                'prefect',
                'deployment',
                'build',
                '-f', './prefect/deployments/deployment_config.py',
                '-o', './prefect/deployments/deployments.yaml'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                click.secho("✓ Deployments built successfully", fg='green')
                
                # Apply deployments
                cmd = [
                    'prefect',
                    'deployment',
                    'apply',
                    './prefect/deployments/deployments.yaml'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    click.secho("✓ Deployments applied successfully", fg='green')
                    return True
                else:
                    click.secho(f"✗ Failed to apply deployments: {result.stderr}", fg='red')
                    return False
            else:
                click.secho(f"✗ Failed to build deployments: {result.stderr}", fg='red')
                return False
        
        except Exception as e:
            click.secho(f"✗ Error during setup: {e}", fg='red')
            return False
    
    def list_deployments(self):
        """List all active deployments"""
        click.echo("\nActive Deployments:")
        click.echo("=" * 60)
        
        try:
            cmd = ['prefect', 'deployment', 'ls']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                click.echo(result.stdout)
                return True
            else:
                click.secho(f"✗ Failed to list deployments: {result.stderr}", fg='red')
                return False
        
        except Exception as e:
            click.secho(f"✗ Error: {e}", fg='red')
            return False
    
    def get_refresh_history(self, days: int = 7) -> List[Dict]:
        """Get incremental refresh execution history"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=int(self.db_port),
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT 
                    refresh_id,
                    run_date,
                    success,
                    models_updated,
                    rows_inserted,
                    execution_time_seconds,
                    notes
                FROM dbt_refresh_log
                WHERE run_date >= NOW() - INTERVAL '{days} days'
                ORDER BY run_date DESC
                LIMIT 50
            """)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'run_date': row[1],
                    'success': row[2],
                    'models_updated': row[3],
                    'rows_inserted': row[4],
                    'execution_time': row[5],
                    'notes': row[6]
                })
            
            return history
        
        except Exception as e:
            click.secho(f"✗ Failed to get history: {e}", fg='red')
            return []
    
    def get_execution_stats(self) -> Dict:
        """Get execution statistics"""
        try:
            history = self.get_refresh_history(days=30)
            
            if not history:
                return {
                    'total_runs': 0,
                    'successful': 0,
                    'failed': 0,
                    'success_rate': 0,
                    'avg_execution_time': 0,
                    'total_rows_inserted': 0
                }
            
            successful = sum(1 for h in history if h['success'])
            failed = len(history) - successful
            total_time = sum(h['execution_time'] or 0 for h in history)
            total_rows = sum(h['rows_inserted'] or 0 for h in history)
            
            return {
                'total_runs': len(history),
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / len(history) * 100) if history else 0,
                'avg_execution_time': total_time / len(history) if history else 0,
                'total_rows_inserted': total_rows
            }
        
        except Exception as e:
            click.secho(f"✗ Error calculating stats: {e}", fg='red')
            return {}
    
    def show_dashboard(self):
        """Display execution dashboard"""
        click.clear()
        click.secho("=" * 70, fg='blue')
        click.secho("  PREFECT INCREMENTAL REFRESH DASHBOARD", fg='blue', bold=True)
        click.secho("=" * 70, fg='blue')
        
        # Show recent runs
        click.echo("\n📋 Recent Execution History (Last 7 Days):")
        click.echo("-" * 70)
        
        history = self.get_refresh_history(days=7)
        if history:
            for run in history[:10]:
                status_icon = "✓" if run['success'] else "✗"
                status_color = 'green' if run['success'] else 'red'
                
                click.secho(
                    f"{status_icon} {run['run_date']} | {run['models_updated']} models | "
                    f"{run['rows_inserted'] or 0} rows | {run['execution_time']:.1f}s",
                    fg=status_color
                )
        else:
            click.echo("No execution history found")
        
        # Show statistics
        click.echo("\n📊 Execution Statistics (Last 30 Days):")
        click.echo("-" * 70)
        
        stats = self.get_execution_stats()
        click.echo(f"Total Runs:              {stats.get('total_runs', 0)}")
        click.secho(f"Successful:             {stats.get('successful', 0)}", fg='green')
        click.secho(f"Failed:                 {stats.get('failed', 0)}", fg='red' if stats.get('failed', 0) > 0 else 'white')
        click.secho(
            f"Success Rate:           {stats.get('success_rate', 0):.1f}%",
            fg='green' if stats.get('success_rate', 0) >= 95 else 'yellow'
        )
        click.echo(f"Avg Execution Time:     {stats.get('avg_execution_time', 0):.1f}s")
        click.echo(f"Total Rows Inserted:    {stats.get('total_rows_inserted', 0):,}")
        
        # Show scheduled deployments
        click.echo("\n⏰ Scheduled Deployments:")
        click.echo("-" * 70)
        click.echo("Daily Incremental:      2:00 AM UTC (Monday-Sunday)")
        click.echo("Weekly Full Refresh:    3:00 AM UTC (Sundays)")
        
        click.echo("\n" + "=" * 70)


@click.group()
def cli():
    """Prefect Incremental Refresh Management CLI"""
    pass


@cli.command()
def setup():
    """Initialize Prefect deployments"""
    manager = PrefectManager()
    success = manager.setup_deployments()
    
    if success:
        click.secho("\n✓ Setup completed successfully!", fg='green', bold=True)
        manager.list_deployments()
    else:
        click.secho("\n✗ Setup failed. See errors above.", fg='red', bold=True)
        sys.exit(1)


@cli.command()
def list():
    """List all active deployments"""
    manager = PrefectManager()
    manager.list_deployments()


@cli.command()
def dashboard():
    """Display execution dashboard"""
    manager = PrefectManager()
    
    while True:
        manager.show_dashboard()
        
        try:
            click.echo("\nPress 'q' to quit, 'r' to refresh (auto-refresh in 60s)...")
            # Could add interactive prompt here
            break
        except KeyboardInterrupt:
            click.echo("Exiting...")
            break


@cli.command()
@click.option('--days', default=7, help='Number of days to display')
def history(days):
    """Show execution history"""
    manager = PrefectManager()
    history = manager.get_refresh_history(days=days)
    
    click.echo(f"\nExecution History (Last {days} Days):")
    click.echo("=" * 80)
    click.echo(f"{'ID':<5} {'Date':<20} {'Status':<8} {'Models':<8} {'Rows':<10} {'Time':<8}")
    click.echo("-" * 80)
    
    for run in history:
        status = "✓ OK" if run['success'] else "✗ FAIL"
        click.echo(
            f"{run['id']:<5} {str(run['run_date']):<20} {status:<8} "
            f"{run['models_updated']:<8} {run['rows_inserted'] or 0:<10} "
            f"{run['execution_time']:.1f}s"
        )
    
    click.echo("\n" + "=" * 80)
    stats = manager.get_execution_stats()
    click.echo(f"Success Rate: {stats.get('success_rate', 0):.1f}% | "
               f"Avg Time: {stats.get('avg_execution_time', 0):.1f}s")


@cli.command()
def stats():
    """Show execution statistics"""
    manager = PrefectManager()
    stats = manager.get_execution_stats()
    
    click.echo("\nExecution Statistics (Last 30 Days):")
    click.echo("=" * 50)
    click.echo(f"Total Runs:           {stats.get('total_runs', 0)}")
    click.secho(f"Successful:           {stats.get('successful', 0)}", fg='green')
    click.secho(f"Failed:               {stats.get('failed', 0)}", fg='red' if stats.get('failed', 0) > 0 else 'white')
    click.echo(f"Success Rate:         {stats.get('success_rate', 0):.1f}%")
    click.echo(f"Avg Execution Time:   {stats.get('avg_execution_time', 0):.1f}s")
    click.echo(f"Total Rows Inserted:  {stats.get('total_rows_inserted', 0):,}")


@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be done without running')
def test_incremental(dry_run):
    """Test incremental refresh flow"""
    click.echo("Testing incremental refresh flow...")
    
    try:
        os.chdir(str(PROJECT_DIR))
        
        if dry_run:
            click.echo("Dry-run mode: Would execute incremental flow")
        else:
            from prefect.flows.incremental_refresh import incremental_refresh_flow
            
            click.echo("Running incremental refresh flow...")
            state = incremental_refresh_flow()
            
            click.secho("✓ Test completed successfully", fg='green')
    
    except Exception as e:
        click.secho(f"✗ Test failed: {e}", fg='red')
        sys.exit(1)


if __name__ == "__main__":
    cli()
