"""
Test file for the code agent with review implementation.
"""

import pytest

from langchain_core.messages import HumanMessage

from src.agents.code_agent_with_review import (
    CodeAgentState,
    PreConfiguredCodeAgent,
    is_invalid_code_tool_message,
)
from src.agents.models import AppChatModels
from src.agents.utils.prompt_utils import extract_graph_response_content


@pytest.fixture(scope="function")
def code_agent_with_review(models_client: AppChatModels) -> PreConfiguredCodeAgent:
    """
    Fixture to get the code agent with review for testing.
    """
    return PreConfiguredCodeAgent(
        preset_state=CodeAgentState(),
        models=models_client,
        name="test_code_agent_with_review",
    )


@pytest.mark.asyncio
async def test_complex_data_analysis_task(
    code_agent_with_review: PreConfiguredCodeAgent,
):
    """
    Test the code agent with review on a complex data analysis task that requires
    multiple steps and is likely to trigger various graph nodes including:
    - Initial code generation
    - Tool result assessment
    - Possible code review
    - Multiple iterations of refinement

    This test uses a realistic financial analysis scenario that requires:
    1. Data generation/simulation
    2. Statistical calculations
    3. Data validation
    4. Multiple computational steps
    """
    query = """I need you to perform a comprehensive financial portfolio analysis.

Here's what I need you to do step by step:

1. Create a simulated stock portfolio with 5 different stocks with the following characteristics:
   - Stock symbols: AAPL, GOOGL, MSFT, AMZN, TSLA
   - Generate 252 days (1 trading year) of daily price data for each stock
   - Use realistic starting prices and add random daily returns (you can use normal distribution)
   - Starting prices: AAPL=150, GOOGL=2500, MSFT=300, AMZN=3000, TSLA=200

2. Calculate the portfolio performance metrics:
   - Daily returns for each stock
   - Portfolio weights (assume equal weighting: 20% each)
   - Portfolio daily returns
   - Cumulative portfolio returns
   - Portfolio volatility (standard deviation of returns)
   - Sharpe ratio (assume risk-free rate of 2%)

3. Perform risk analysis:
   - Calculate Value at Risk (VaR) at 95% confidence level
   - Calculate maximum drawdown
   - Create a correlation matrix between the stocks

4. Validate your results:
   - Check that portfolio weights sum to 1.0
   - Verify that returns calculations are correct by spot-checking a few days
   - Ensure all metrics are reasonable (e.g., annual volatility between 10-40%)

5. Print a comprehensive summary report showing:
   - Final portfolio value vs initial investment
   - Annual return percentage
   - Annual volatility percentage
   - Sharpe ratio
   - Maximum drawdown percentage
   - 95% VaR
   - Top performing and worst performing stocks

Make sure to use proper financial formulas and validate each step. This is a complex multi-step process, so take your time and be thorough."""

    # Run the agent
    response = await code_agent_with_review.ainvoke(
        messages=[HumanMessage(content=query)]
    )

    assert response is not None, "Agent should return a response"

    # Extract the final response content
    response_content = extract_graph_response_content(response)

    # The response should be substantial given the complexity of the task
    assert len(response_content) > 500, (
        f"Expected substantial response, got {len(response_content)} characters"
    )

    # Review that at least one tool call was successfully made
    tool_call_results = [msg for msg in response["messages"] if msg.type == "tool"]
    successful_tool_calls = [
        call for call in tool_call_results if not is_invalid_code_tool_message(call)
    ]
    assert len(tool_call_results) > 0, "Expected at least one tool call in the response"
    assert len(successful_tool_calls) > 0, "Expected at least one successful tool call"
