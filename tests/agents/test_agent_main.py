from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.configuration.db_models import RecipientEmail
from agent_main import execute_sales_report_request, main


@pytest.fixture
def default_request_with_recipients(default_request):
    """Extend the default_request fixture with recipients for testing."""
    default_request.recipients = [
        RecipientEmail(email="test@example.com", name="Test User"),
        RecipientEmail(email="manager@example.com", name="Manager User"),
    ]
    return default_request


class TestExecuteSalesReportRequest:
    """Test suite for execute_sales_report_request function."""

    @pytest.mark.asyncio
    async def test_successful_report_generation(self, default_request_with_recipients):
        """Test successful report generation and email sending."""
        # Mock the entire pipeline
        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "report": "# Test Report\n\nThis is a test report.",
            "email_template": "Dear RECIPIENT,\n\nYour report is ready.\n\nBest regards,\nAI Agent",
        }

        with (
            patch("agent_main.create_report_graph", return_value=mock_graph),
            patch("agent_main.get_request_temp_dir", return_value="/tmp/test"),
            patch(
                "agent_main.store_response_with_timestamp",
                return_value="/tmp/test/report.md",
            ),
            patch(
                "agent_main.convert_markdown_to_pdf",
                return_value="/tmp/test/report.pdf",
            ),
            patch(
                "agent_main.move_file_to_storage", return_value="/storage/report.pdf"
            ),
            patch("agent_main.MailingService") as mock_mailing_class,
            patch("agent_main.default_logger"),
        ):
            mock_mailing = MagicMock()
            mock_mailing_class.return_value = mock_mailing

            await execute_sales_report_request(default_request_with_recipients)

            # Verify the report graph was invoked with correct request
            mock_graph.ainvoke.assert_called_once_with(
                {"request": default_request_with_recipients}
            )

            # Verify email was sent with correct parameters
            mock_mailing.send_email.assert_called_once_with(
                recipients=["test@example.com", "manager@example.com"],
                subject="AI Analyst - Sales Report Generated",
                body="Dear Test User, Manager User,\n\nYour report is ready.\n\nBest regards,\nAI Agent",
                attachments=["/storage/report.pdf"],
            )

    @pytest.mark.asyncio
    async def test_report_generation_failure(self, default_request_with_recipients):
        """Test handling of report generation failure."""
        # Mock graph to raise an exception
        mock_graph = AsyncMock()
        mock_graph.ainvoke.side_effect = Exception("Graph processing failed")

        with (
            patch("agent_main.create_report_graph", return_value=mock_graph),
            patch("agent_main.MailingService") as mock_mailing_class,
            patch("agent_main.default_logger"),
            patch("agent_main.app_settings") as mock_settings,
        ):
            mock_settings.retry_limit = 0  # Set to 0 to trigger max retries immediately
            mock_mailing = MagicMock()
            mock_mailing_class.return_value = mock_mailing

            await execute_sales_report_request(default_request_with_recipients)

            # Verify failure email was sent
            mock_mailing.send_email.assert_called_once_with(
                recipients=["test@example.com", "manager@example.com"],
                subject="AI Analyst Agent Run - Failed",
                body="The AI Analyst agent failed to generate your report.",
            )

    @pytest.mark.asyncio
    async def test_retry_logic_eventual_success(self, default_request_with_recipients):
        """Test retry logic with eventual success."""
        mock_graph = AsyncMock()
        # Fail twice, then succeed
        mock_graph.ainvoke.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            {
                "report": "# Success Report",
                "email_template": "Dear RECIPIENT,\n\nSuccess!\n\nAI Agent",
            },
        ]

        with (
            patch("agent_main.create_report_graph", return_value=mock_graph),
            patch("agent_main.get_request_temp_dir", return_value="/tmp/test"),
            patch(
                "agent_main.store_response_with_timestamp",
                return_value="/tmp/test/report.md",
            ),
            patch(
                "agent_main.convert_markdown_to_pdf",
                return_value="/tmp/test/report.pdf",
            ),
            patch(
                "agent_main.move_file_to_storage", return_value="/storage/report.pdf"
            ),
            patch("agent_main.MailingService") as mock_mailing_class,
            patch("agent_main.default_logger"),
            patch("agent_main.app_settings") as mock_settings,
        ):
            mock_settings.retry_limit = 3
            mock_mailing = MagicMock()
            mock_mailing_class.return_value = mock_mailing

            await execute_sales_report_request(default_request_with_recipients)

            # Verify graph was called 3 times (2 failures + 1 success)
            assert mock_graph.ainvoke.call_count == 3

            # Verify success email was sent
            mock_mailing.send_email.assert_called_once_with(
                recipients=["test@example.com", "manager@example.com"],
                subject="AI Analyst - Sales Report Generated",
                body="Dear Test User, Manager User,\n\nSuccess!\n\nAI Agent",
                attachments=["/storage/report.pdf"],
            )

    @pytest.mark.asyncio
    async def test_single_recipient_email_template(self, default_request):
        """Test email template replacement with single recipient."""
        # Use the default request but with a single recipient
        default_request.recipients = [
            RecipientEmail(email="user@example.com", name="User")
        ]

        mock_graph = AsyncMock()
        mock_graph.ainvoke.return_value = {
            "report": "# Single User Report",
            "email_template": "Hello RECIPIENT,\n\nYour report is ready.\n\nAI Agent",
        }

        with (
            patch("agent_main.create_report_graph", return_value=mock_graph),
            patch("agent_main.get_request_temp_dir", return_value="/tmp/test"),
            patch(
                "agent_main.store_response_with_timestamp",
                return_value="/tmp/test/report.md",
            ),
            patch(
                "agent_main.convert_markdown_to_pdf",
                return_value="/tmp/test/report.pdf",
            ),
            patch(
                "agent_main.move_file_to_storage", return_value="/storage/report.pdf"
            ),
            patch("agent_main.MailingService") as mock_mailing_class,
        ):
            mock_mailing = MagicMock()
            mock_mailing_class.return_value = mock_mailing

            await execute_sales_report_request(default_request)

            # Verify email template was correctly personalized for single recipient
            mock_mailing.send_email.assert_called_once_with(
                recipients=["user@example.com"],
                subject="AI Analyst - Sales Report Generated",
                body="Hello User,\n\nYour report is ready.\n\nAI Agent",
                attachments=["/storage/report.pdf"],
            )


class TestMain:
    """Test suite for main function."""

    @pytest.mark.asyncio
    async def test_main_no_requests(self):
        """Test main function when no requests are found."""
        with (
            patch("agent_main.default_db") as mock_db,
            patch("agent_main.default_logger"),
        ):
            mock_db.get_all_sales_report_requests.return_value = []

            await main()

    @pytest.mark.asyncio
    async def test_main_single_request(self, default_request_with_recipients):
        """Test main function with single request."""
        with (
            patch("agent_main.default_db") as mock_db,
            patch("agent_main.execute_sales_report_request") as mock_execute,
            patch("agent_main.default_logger"),
        ):
            mock_db.get_all_sales_report_requests.return_value = [
                default_request_with_recipients
            ]

            await main()

            # Verify request was processed
            mock_execute.assert_called_once_with(default_request_with_recipients)

    @pytest.mark.asyncio
    async def test_main_multiple_requests(self, default_request_with_recipients):
        """Test main function with multiple requests processes them sequentially."""
        # Create a second request by modifying a copy of the default request
        second_request = default_request_with_recipients.__class__(
            **default_request_with_recipients.model_dump()
        )
        second_request.id = 2
        second_request.grouping = None
        second_request.grouping_value = None

        requests = [default_request_with_recipients, second_request]

        with (
            patch("agent_main.default_db") as mock_db,
            patch("agent_main.execute_sales_report_request") as mock_execute,
            patch("agent_main.default_logger"),
        ):
            mock_db.get_all_sales_report_requests.return_value = requests

            await main()

            # Verify both requests were processed in order
            assert mock_execute.call_count == 2
            mock_execute.assert_any_call(default_request_with_recipients)
            mock_execute.assert_any_call(second_request)
