import pytest


from src.agents.database_agent import create_database_agent


@pytest.mark.asyncio
async def test_single_column_task(internal_database):
    """
    Test the DatabaseAgent with a single table task.

    This test checks if the agent can correctly answer a question
    about revenue from a single table in the database.

    This test will be reviewed in the future when we have a final
    implementation of the DatabaseAgent.
    """
    task = "How much revenue did we make every year that's available in the database?"
    expected = [
        {
            "Year": 2013,
            "TotalRevenue": 38373718.70,
        },
        {
            "Year": 2014,
            "TotalRevenue": 48879106.25,
        },
        {
            "Year": 2015,
            "TotalRevenue": 53827320.95,
        },
        {
            "Year": 2016,
            "TotalRevenue": 31181195.30,
        },
    ]

    agent = create_database_agent(internal_database)
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


@pytest.mark.asyncio
async def test_multi_column_task(internal_database):
    """
    Test the DatabaseAgent with a multi-column task.

    This test checks if the agent can correctly follow the instruction of
    including all columns for the calculation.
    """

    task = "What is the profit margin for each year available in the database?"
    expected = [
        {
            "FiscalYear": 2013,
            "TotalRevenue": 38373718.70,
            "TotalProfit": 19143873.90,
            "ProfitMargin": 0.498879,
        },
        {
            "FiscalYear": 2014,
            "TotalRevenue": 48879106.25,
            "TotalProfit": 24283242.45,
            "ProfitMargin": 0.496802,
        },
        {
            "FiscalYear": 2015,
            "TotalRevenue": 53827320.95,
            "TotalProfit": 26815310.85,
            "ProfitMargin": 0.498172,
        },
        {
            "FiscalYear": 2016,
            "TotalRevenue": 31181195.30,
            "TotalProfit": 15486753.70,
            "ProfitMargin": 0.496669,
        },
    ]

    agent = create_database_agent(internal_database)
    response = await agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)
    for record in expected:
        year = str(record["FiscalYear"])
        revenue = str(record["TotalRevenue"])
        profit = str(record["TotalProfit"])
        margin = str(record["ProfitMargin"])
        formatted_revenue = f"{record['TotalRevenue']:,.2f}"
        formatted_profit = f"{record['TotalProfit']:,.2f}"
        formatted_margin = f"{record['ProfitMargin'] * 100:.4f}"
        assert year in response_content
        assert revenue in response_content or formatted_revenue in response_content
        assert profit in response_content or formatted_profit in response_content
        assert margin in response_content or formatted_margin in response_content


@pytest.mark.asyncio
async def test_quarterly_task(internal_database):
    """
    Test the DatabaseAgent with a quarterly task.

    This test checks if the agent can correctly answer a question
    about quarterly revenue from the database.
    """
    task = "What was our quarterly profit margin for the available data?"
    expected = [
        {
            "Year": 2013,
            "Quarter": 1,
            "TotalRevenue": 3770410.85,
            "TotalProfit": 1890687.80,
            "ProfitMargin": 0.501454,
        },
        {
            "Year": 2013,
            "Quarter": 2,
            "TotalRevenue": 10706898.35,
            "TotalProfit": 5328659.55,
            "ProfitMargin": 0.497684,
        },
        {
            "Year": 2013,
            "Quarter": 3,
            "TotalRevenue": 12868769.20,
            "TotalProfit": 6413070.45,
            "ProfitMargin": 0.498343,
        },
        {
            "Year": 2013,
            "Quarter": 4,
            "TotalRevenue": 11027640.30,
            "TotalProfit": 5511456.10,
            "ProfitMargin": 0.499785,
        },
        {
            "Year": 2014,
            "Quarter": 1,
            "TotalRevenue": 11401007.30,
            "TotalProfit": 5669875.95,
            "ProfitMargin": 0.497313,
        },
        {
            "Year": 2014,
            "Quarter": 2,
            "TotalRevenue": 11427372.60,
            "TotalProfit": 5653511.05,
            "ProfitMargin": 0.494734,
        },
        {
            "Year": 2014,
            "Quarter": 3,
            "TotalRevenue": 13643584.25,
            "TotalProfit": 6799583.55,
            "ProfitMargin": 0.498372,
        },
        {
            "Year": 2014,
            "Quarter": 4,
            "TotalRevenue": 12407142.10,
            "TotalProfit": 6160271.90,
            "ProfitMargin": 0.496510,
        },
        {
            "Year": 2015,
            "Quarter": 1,
            "TotalRevenue": 12785549.50,
            "TotalProfit": 6397937.95,
            "ProfitMargin": 0.500403,
        },
        {
            "Year": 2015,
            "Quarter": 2,
            "TotalRevenue": 13796715.65,
            "TotalProfit": 6888240.15,
            "ProfitMargin": 0.499266,
        },
        {
            "Year": 2015,
            "Quarter": 3,
            "TotalRevenue": 14152243.00,
            "TotalProfit": 7028442.20,
            "ProfitMargin": 0.496630,
        },
        {
            "Year": 2015,
            "Quarter": 4,
            "TotalRevenue": 13092812.80,
            "TotalProfit": 6500690.55,
            "ProfitMargin": 0.496508,
        },
        {
            "Year": 2016,
            "Quarter": 1,
            "TotalRevenue": 12995725.70,
            "TotalProfit": 6537343.25,
            "ProfitMargin": 0.503037,
        },
        {
            "Year": 2016,
            "Quarter": 2,
            "TotalRevenue": 13214536.95,
            "TotalProfit": 6505961.90,
            "ProfitMargin": 0.492333,
        },
        {
            "Year": 2016,
            "Quarter": 3,
            "TotalRevenue": 4970932.65,
            "TotalProfit": 2443448.55,
            "ProfitMargin": 0.491547,
        },
    ]

    agent = create_database_agent(internal_database)
    response = await agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)
    for record in expected:
        revenue = str(record["TotalRevenue"])
        profit = str(record["TotalProfit"])
        margin = str(record["ProfitMargin"])
        formatted_revenue = f"{record['TotalRevenue']:,.2f}"
        formatted_profit = f"{record['TotalProfit']:,.2f}"
        formatted_margin = f"{record['ProfitMargin'] * 100:.4f}"
        # Note we don't check for the year and quarter in the response
        # because the agent might not return them in the same format.
        assert revenue in response_content or formatted_revenue in response_content
        assert profit in response_content or formatted_profit in response_content
        assert margin in response_content or formatted_margin in response_content


"Please provide the current value of the Quarterly Gross Profit Margin for the latest reporting period."


@pytest.mark.asyncio
async def test_last_quarterly_task(internal_database):
    """
    Test the DatabaseAgent with a "last" quarterly task.

    This test checks if the agent can correctly answer a question
    the "last" quarterly revenue from the database.
    """
    task = "What was our quarterly profit margin for the available data?"
    expected = {
        "Year": 2016,
        "Quarter": 3,
        "TotalRevenue": 4970932.65,
        "TotalProfit": 2443448.55,
        "ProfitMargin": 0.491547,
    }

    agent = create_database_agent(internal_database)
    response = await agent.get_response(messages=task)

    assert response is not None

    response_content = response.content.content
    print(response_content)

    revenue = str(expected["TotalRevenue"])
    profit = str(expected["TotalProfit"])
    margin = str(expected["ProfitMargin"])
    formatted_revenue = f"{expected['TotalRevenue']:,.2f}"
    formatted_profit = f"{expected['TotalProfit']:,.2f}"
    formatted_margin = f"{expected['ProfitMargin'] * 100:.4f}"
    # Note we don't check for the year and quarter in the response
    # because the agent might not return them in the same format.
    assert revenue in response_content or formatted_revenue in response_content
    assert profit in response_content or formatted_profit in response_content
    assert margin in response_content or formatted_margin in response_content
