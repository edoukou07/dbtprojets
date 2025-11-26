"""
Prefect Deployment Configuration for Incremental Refresh Scheduling
Defines deployment parameters and scheduling rules
"""

from datetime import datetime, timedelta
from prefect.schedules import IntervalSchedule, CronSchedule
from prefect.deployments import Deployment
from prefect.infrastructure import Process
from prefect.task_runs import TaskRunPolicy
from prefect.utilities.asyncutils import sync_compatible

# Import flows
from flows.incremental_refresh import (
    incremental_refresh_flow,
    full_refresh_flow
)


# Incremental Refresh Deployment - Daily at 2 AM UTC
incremental_deployment = Deployment(
    flow=incremental_refresh_flow,
    name="daily-incremental-refresh",
    description="Daily incremental refresh of fact tables - runs at 2 AM UTC",
    version="1.0.0",
    tags=["production", "incremental", "daily"],
    schedule=CronSchedule(
        cron="0 2 * * *",  # 2 AM UTC daily
        timezone="UTC"
    ),
    infrastructure=Process(
        working_dir=str(Path(__file__).parent.parent.parent),
        env={
            "PREFECT_LOGGING_LEVEL": "INFO",
            "DBT_PROFILES_DIR": str(Path(__file__).parent.parent.parent)
        }
    ),
    parameters={},
    work_queue_name="default"
)


# Full Refresh Deployment - Weekly on Sunday at 3 AM UTC
full_refresh_deployment = Deployment(
    flow=full_refresh_flow,
    name="weekly-full-refresh",
    description="Weekly full refresh of all models - runs Sundays at 3 AM UTC",
    version="1.0.0",
    tags=["production", "full-refresh", "weekly"],
    schedule=CronSchedule(
        cron="0 3 * * 0",  # 3 AM UTC on Sundays
        timezone="UTC"
    ),
    infrastructure=Process(
        working_dir=str(Path(__file__).parent.parent.parent),
        env={
            "PREFECT_LOGGING_LEVEL": "INFO",
            "DBT_PROFILES_DIR": str(Path(__file__).parent.parent.parent)
        }
    ),
    parameters={},
    work_queue_name="default"
)


if __name__ == "__main__":
    # Deploy both flows
    print("Deploying incremental refresh flow...")
    incremental_deployment.apply()
    print("✓ Daily incremental refresh deployed")
    
    print("Deploying full refresh flow...")
    full_refresh_deployment.apply()
    print("✓ Weekly full refresh deployed")
    
    print("\nDeployments configured successfully!")
    print("\nSchedule Summary:")
    print("  - Daily Incremental: 2:00 AM UTC (Monday-Sunday)")
    print("  - Weekly Full Refresh: 3:00 AM UTC (Sundays)")
