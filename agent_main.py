import asyncio

from semantic_kernel.agents.runtime import InProcessRuntime

from src.agents.research_team import invoke_research_team_task
from src.agents.tools.db import InternalDatabase
from src.agents.utils import email_service
from src.agents.utils.output_utils import (
    clean_temp_folder,
    convert_markdown_to_pdf,
    move_file_to_storage,
)
from src.configuration.kpis import get_sales_report_request
from src.configuration.logger import default_logger
from src.configuration.db import default_config_db_sessionmaker
from src.configuration.recipients import get_recipient_emails
from src.configuration.settings import TEMP_DIR, app_settings
from src.configuration.auth import get_azure_ai_agent_client


async def main():
    default_logger.info("Starting agent main process...")

    # Get the list of KPIs to be processed
    request = get_sales_report_request(default_config_db_sessionmaker)
    if not request:
        default_logger.error("No Sales requests found. Exiting.")
        return

    # Get a Runtime instance
    runtime = InProcessRuntime()
    runtime.start()

    # Get the Azure AI Agent client
    azure_ai_client = get_azure_ai_agent_client()
    # Initialize the internal database
    internal_db = await InternalDatabase.create()

    md_file_path = await invoke_research_team_task(
        request=request,
        internal_db=internal_db,
        runtime=runtime,
        azure_ai_client=azure_ai_client,
    )

    # Convert the Markdown report to PDF and move it to storage
    pdf_path = convert_markdown_to_pdf(md_file_path)
    pdf_path = move_file_to_storage(pdf_path)

    # Send email notification with the report
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

    await runtime.stop_when_idle()
    await azure_ai_client.close()
    clean_temp_folder()

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
