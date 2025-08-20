from langsmith import traceable
from langgraph.graph.state import CompiledStateGraph

from src.agents.report_graph import create_report_graph
from src.agents.utils.email_service import MailingService
from src.agents.utils.output_utils import (
    convert_markdown_to_pdf,
    get_request_temp_dir,
    move_file_to_storage,
    store_response_with_timestamp,
)
from src.configuration.db_models import SalesReportRequest
from src.configuration.db_service import default_db
from src.configuration.logger import default_logger
from src.configuration.settings import app_settings


async def execute_sales_report_request(request: SalesReportRequest) -> None:
    default_logger.info(f"Starting research task for KPI: {request.name}")
    retry_count = 0  # TODO: Add tests for retry logic
    result: dict | None = None
    while retry_count < app_settings.retry_limit:
        try:
            research_graph: CompiledStateGraph = await create_report_graph()
            result = await research_graph.ainvoke({"request": request})
            default_logger.info(f"Completed research task for KPI: {request.name}")
            break  # Exit loop if successful
        except Exception as e:
            if retry_count >= app_settings.retry_limit:
                default_logger.error(f"Max retries reached for request {request.name}.")
                break
            retry_count += 1
            default_logger.error(
                f"Error processing request {request.name}: {str(e)}. Retry {retry_count}/{app_settings.retry_limit}."
            )

    email_list = [recipient.email for recipient in request.recipients]
    email_names = [recipient.name for recipient in request.recipients]
    email_names_str = ", ".join(email_names)
    mailing = MailingService(env=app_settings)

    if result:
        temp_dir = get_request_temp_dir(request)
        md_file_path = store_response_with_timestamp(
            response=result["report"], folder=temp_dir, file_name=request.name
        )

        # Convert the Markdown report to PDF and move it to storage
        pdf_path = convert_markdown_to_pdf(
            markdown_path=md_file_path, root_dir=temp_dir
        )
        pdf_path = move_file_to_storage(pdf_path)

        # Send email notification with the report
        email_template: str = result["email_template"]
        email_template = email_template.replace("RECIPIENT", email_names_str)
        mailing.send_email(
            recipients=email_list,
            subject="AI Analyst - Sales Report Generated",
            body=email_template,
            attachments=[pdf_path],
        )

        default_logger.info(
            f"AI Analyst agent ran successfully. Report saved at {pdf_path}."
        )
    else:
        mailing.send_email(
            recipients=email_list,
            subject="AI Analyst Agent Run - Failed",
            body="The AI Analyst agent failed to generate your report.",
        )


@traceable
async def main():
    """
    Main function to run the database agent.
    This is a simple example of how to use the database agent.
    """

    requests = default_db.get_all_sales_report_requests()
    if not requests:
        default_logger.info("No sales report requests found.")
        return

    default_logger.info(f"Found {len(requests)} sales report requests.")

    # Runs the tasks sequentially because of API rate limits
    for request in requests:
        default_logger.info(f"Processing request: {request.name}")
        await execute_sales_report_request(request)

    default_logger.info("All sales report requests processed.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
