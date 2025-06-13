from src.configuration.crontab import CronFrequency, set_crontab


def setup_crontab(frequency: CronFrequency) -> str:
    """
    Sets up the crontab with the specified frequency.

    Args:
        frequency (CronFrequency): The frequency at which the cron job should run.
    """
    
    if frequency == CronFrequency.DAY.value:
        # Set up daily cron job
        return "Setting up daily cron job..."
    elif frequency == CronFrequency.MONTH.value:
        # Set up monthly cron job
        return "Setting up monthly cron job..."
    else:
        raise ValueError("Unsupported frequency type for cron job setup")
