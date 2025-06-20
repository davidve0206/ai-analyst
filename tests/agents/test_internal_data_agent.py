import pytest
from autogen_agentchat.messages import TextMessage

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
        {"Calendar Year": 2013, "Total Revenue": 52563272.64},
        {"Calendar Year": 2014, "Total Revenue": 57418916.89},
        {"Calendar Year": 2015, "Total Revenue": 62090220.81},
        {"Calendar Year": 2016, "Total Revenue": 25971029.11},
    ]

    agent = await create_internal_data_agent(internal_database)
    result = await agent.run(task=task)

    final_message = next(
        (
            msg
            for msg in reversed(result.messages)
            if isinstance(msg, TextMessage) and msg.source == "InternalDataAgent"
        ),
        None,
    )
    result_content = final_message.content if final_message else None

    assert result_content is not None
    print("Agent response:", result_content)

    for record in expected:
        # Check that each year and revenue is present in the result content
        # as well as the revenue, be it formatted or not.
        year = str(record["Calendar Year"])
        revenue = str(record["Total Revenue"])
        formatted_revenue = f"{record['Total Revenue']:,.2f}"
        assert year in result_content and (
            revenue in result_content or formatted_revenue in result_content
        )
