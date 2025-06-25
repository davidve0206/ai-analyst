import asyncio

from semantic_kernel.agents.runtime import InProcessRuntime

from src.agents.research_team import invoke_research_team_task
from src.agents.tools.db import InternalDatabase
from src.agents.utils import email_service
from src.agents.utils.output_utils import convert_markdown_to_pdf
from src.configuration.kpis import get_kpi_requests
from src.configuration.logger import default_logger
from src.configuration.db import default_config_db_sessionmaker
from src.configuration.recipients import get_recipient_emails
from src.configuration.settings import app_settings


async def main():
    default_logger.info("Starting agent main process...")

    # Get a Runtime instance
    runtime = InProcessRuntime()
    runtime.start()

    # Get the list of KPIs to be processed
    kpi = get_kpi_requests(default_config_db_sessionmaker)
    if not kpi:
        default_logger.error("No KPI requests found. Exiting.")
        return

    # Initialize the internal database
    internal_db = await InternalDatabase.create()

    md_file_path = await invoke_research_team_task(
        kpi=kpi,
        internal_db=internal_db,
        runtime=runtime,
    )

    # Send email notification with the report
    pdf_path = convert_markdown_to_pdf(md_file_path)
    email_list = get_recipient_emails(default_config_db_sessionmaker)
    mailing = email_service.MailingService(env=app_settings)
    mailing.send_email(
        recipients=email_list,
        subject="AI Analyst Agent Started",
        body="The AI Analyst agent has been successfully started and is now running.",
        attachments=[pdf_path],
    )

    default_logger.info(
        f"AI Analyst agent started successfully. Report saved at {pdf_path}."
    )

    """ 
    For future use
    results = {}
    async with asyncio.TaskGroup() as tg:
        for kpi in KPI_LIST:
            tg.create_task(
                invoke_research_team_task(
                    kpi=kpi,
                    internal_db=internal_db,
                    runtime=runtime,
                    results_dict=results,
                )
            )

    await runtime.stop_when_idle() """


if __name__ == "__main__":
    asyncio.run(main())
