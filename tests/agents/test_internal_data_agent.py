import pytest


from src.agents.internal_data_agent import create_internal_data_agent


@pytest.mark.asyncio
async def test_internal_data_agent_uses_database_agent(internal_database):
    """
    Test the InternalDataAgent with a single table task.

    This test checks if the agent can correctly answer a question
    about revenue from a single table in the database.
    """
    task = "How much revenue did we make every year that's available in the database?"
    expected = [
        {
            "Year": 2022,
            "TotalRevenue": 38373718.70,
        },
        {
            "Year": 2023,
            "TotalRevenue": 48879106.25,
        },
        {
            "Year": 2024,
            "TotalRevenue": 53827320.95,
        },
        {
            "Year": 2025,
            "TotalRevenue": 31181195.30,
        },
    ]

    agent = create_internal_data_agent(internal_database)
    response = await agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)
    for record in expected:
        # Check that each year and revenue is present in the result content
        # as well as the revenue, be it formatted or not.
        year = str(record["Year"])
        revenue = str(record["TotalRevenue"])
        formatted_revenue = f"{record['TotalRevenue']:,.2f}"
        assert year in response_content
        assert revenue in response_content or formatted_revenue in response_content
