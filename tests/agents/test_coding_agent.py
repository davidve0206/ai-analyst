import pytest
import pytest_asyncio

from azure.ai.projects.aio import AIProjectClient
from semantic_kernel.agents import AzureAIAgent

from src.agents.coder_agent import create_coder_agent


@pytest_asyncio.fixture(scope="function")
async def coder_agent(azure_ai_client: AIProjectClient):
    """
    Fixture to create an instance of CoderAgent for testing.
    This agent is used to test code generation and execution capabilities.
    """
    agent = await create_coder_agent(azure_ai_client=azure_ai_client)
    yield agent
    await azure_ai_client.agents.delete_agent(agent.id)


@pytest.mark.asyncio
async def test_task_with_basic_interpreter(coder_agent: AzureAIAgent):
    """
    Test the agent with a task that requires basic code generation and execution.
    """
    task = """The company made the following revenue every year: 
    
    2021: 300, 2022: 325, 2023: 350, 2024: 325, 2025: 400.
    
    What is the average yearly revenue?"""
    expected = 340

    response = await coder_agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)
    assert str(expected) in response_content


@pytest.mark.asyncio
async def test_task_with_intermediate_interpreter(coder_agent: AzureAIAgent):
    """
    Test the agent with a task that requires basic code generation and execution.
    """
    task = """The company made the following revenue every year: 
    
    2021: 300, 2022: 325, 2023: 350, 2024: 325, 2025: 400.
    
    What is the average growth rate (CAGR)?"""
    expected = (
        "7.46"  # %, but might include more decimal places so we check for substring
    )

    response = await coder_agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)
    assert expected in response_content


@pytest.mark.asyncio
async def test_task_with_projection_tool(coder_agent: AzureAIAgent):
    """
    Test the agent with a task that requires the projection tool.
    """
    task = """The company made the following revenue every year: 
    
    2021: 300, 2022: 325, 2023: 350, 2024: 325, 2025: 400.
    
    What is the projected revenue for the three years starting in 2026 round to integers?"""
    expected = expected = {2026: 400, 2027: 420, 2028: 440}

    response = await coder_agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)
    for year, revenue in expected.items():
        # Check that each year and revenue is present in the result content
        # as well as the revenue, be it formatted or not.
        year_str = str(year)
        revenue_str = str(revenue)
        assert year_str in response_content
        assert revenue_str in response_content
