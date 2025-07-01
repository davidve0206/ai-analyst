from src.agents.tools.projections import ProjectionsPlugin


def test_projections_tool_projection():
    """This test is the counterpart to the test in the CoderAgent test suite.

    It tests the ProjectionsPlugin directly, ensuring it can calculate projections."""

    values = [300, 325, 350, 325, 400]
    expected_projection_part = [400, 420, 440]

    plugin = ProjectionsPlugin()
    trend_line = plugin.calculate_trend_and_projection(values, projection_period=3)
    projection = trend_line[-3:]
    int_projection = [int(round(x)) for x in projection]
    assert int_projection == expected_projection_part


def test_projection_tool_trendile():
    values = [
        0.5015,
        0.4977,
        0.4983,
        0.4998,
        0.4973,
        0.4947,
        0.4984,
        0.4965,
        0.5004,
        0.4993,
        0.4966,
        0.4965,
        0.5030,
        0.4923,
        0.4915,
    ]

    expected = [
        0.4996616666666668,
        0.49936523809523825,
        0.49906880952380966,
        0.4987723809523811,
        0.4984759523809525,
        0.49817952380952396,
        0.4978830952380954,
        0.4975866666666668,
        0.4972902380952382,
        0.4969938095238096,
        0.4966973809523811,
        0.4964009523809525,
        0.4961045238095239,
        0.4958080952380953,
        0.4955116666666668,
        0.4952152380952382,
        0.4949188095238096,
        0.49462238095238104,
    ]

    plugin = ProjectionsPlugin()
    projected = plugin.calculate_trend_and_projection(values, projection_period=3)

    assert len(projected) == len(values) + 3
    assert isinstance(projected, list)
    assert all(isinstance(x, float) for x in projected)
    for i in range(len(expected)):
        assert abs(projected[i] - expected[i]) < 1e-6, (
            f"Expected {expected[i]}, got {projected[i]} at index {i}"
        )
