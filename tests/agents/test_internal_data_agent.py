import pytest


from src.agents.internal_data_agent import create_internal_data_agent


@pytest.mark.asyncio
async def test_single_table_task(internal_database):
    """
    Test the InternalDataAgent with a single table task.

    This test checks if the agent can correctly answer a question
    about revenue from a single table in the database.

    This test will be reviewed in the future when we have a final
    implementation of the InternalDataAgent.
    """
    task = "How much revenue did we make every year that's available in the database?"
    expected = [
        {"Calendar Year": 2013, "Total Revenue": 45707188.00},
        {"Calendar Year": 2014, "Total Revenue": 49929487.20},
        {"Calendar Year": 2015, "Total Revenue": 53991490.45},
        {"Calendar Year": 2016, "Total Revenue": 22633175.55},
    ]

    agent = create_internal_data_agent(internal_database)
    response = await agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    for record in expected:
        # Check that each year and revenue is present in the result content
        # as well as the revenue, be it formatted or not.
        year = str(record["Calendar Year"])
        revenue = str(record["Total Revenue"])
        formatted_revenue = f"{record['Total Revenue']:,.2f}"
        assert year in response_content and (
            revenue in response_content or formatted_revenue in response_content
        )
