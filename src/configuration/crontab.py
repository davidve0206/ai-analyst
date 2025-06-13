import sys
from pathlib import Path

from crontab import CronTab

from src.configuration.settings import BASE_DIR


def set_crontab():
    """
    Set the crontab for the application.

    TODO: Implement variable to set the frequency of the cron job.
    """

    cron = CronTab(user="root")
    for job in cron:
        if "agent" in job.command:
            cron.remove(job)

    python_path = Path(sys.executable)
    agent_main_path = BASE_DIR / "agent_main.py"

    command = f"{python_path} {agent_main_path} >> /var/log/agent.log 2>&1"
    job = cron.new(command=command, comment="AI Agent Cron Job")
    job.minute.every(1)  # Set the job to run every minute

    cron.write()
