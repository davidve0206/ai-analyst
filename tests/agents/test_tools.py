import os

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


def test_plot_values_and_store_basic_functionality():
    """Test basic plotting functionality with trend line and projections."""
    plugin = ProjectionsPlugin()

    labels = ["2020", "2021", "2022", "2023"]
    data = [100, 120, 110, 140]

    result = plugin.plot_values_and_store(
        labels=labels,
        data=data,
        plot_tite="Test Financial Plot",
        plot_type="line",
        include_trend_line=True,
        projection_period=2,
    )

    # Check that plot was created successfully
    assert "error" not in result
    assert "plot_path" in result
    assert "data_summary" in result
    assert "message" in result

    # Verify the data structure in summary
    data_summary = result["data_summary"]
    assert "historical_data" in data_summary
    assert "trend_line" in data_summary  # Should include trend line data
    assert "projections" in data_summary  # Should include projections
    assert data_summary["plot_type"] == "line"
    assert data_summary["include_trend_line"] is True
    assert data_summary["projection_period"] == 2

    # Check historical data is correct
    assert data_summary["historical_data"] == list(zip(labels, data))

    # Check projections have correct labels
    projections = data_summary["projections"]
    assert len(projections) == 2
    assert projections[0][0] == "t+1"
    assert projections[1][0] == "t+2"

    # Clean up - delete the generated plot file
    if os.path.exists(result["plot_path"]):
        os.remove(result["plot_path"])


def test_plot_values_and_store_no_projections():
    """Test plotting without projections but with trend line."""
    plugin = ProjectionsPlugin()

    labels = ["1", "2", "3", "4"]
    data = [50, 60, 70, 80]

    result = plugin.plot_values_and_store(
        labels=labels,
        data=data,
        plot_tite="Test No Projections",
        plot_type="bar",
        include_trend_line=True,
        projection_period=0,
    )

    # Check success
    assert "error" not in result
    assert "plot_path" in result

    # Verify data summary
    data_summary = result["data_summary"]
    assert "historical_data" in data_summary
    assert "trend_line" in data_summary  # Should still have trend line
    assert "projections" not in data_summary  # Should not have projections
    assert data_summary["projection_period"] == 0

    # Clean up - delete the generated plot file
    if os.path.exists(result["plot_path"]):
        os.remove(result["plot_path"])


def test_plot_values_and_store_error_handling():
    """Test error handling for invalid inputs."""
    plugin = ProjectionsPlugin()

    # Test mismatched label and data lengths
    result = plugin.plot_values_and_store(
        labels=[1, 2, 3],
        data=[100, 200],  # Different length
        plot_tite="Test Error",
        plot_type="line",
    )

    assert "error" in result
    assert "length of labels and data must be the same" in result["error"]

    # Test negative projection period
    result = plugin.plot_values_and_store(
        labels=[1, 2, 3],
        data=[100, 200, 300],
        plot_tite="Test Error",
        plot_type="line",
        projection_period=-1,
    )

    assert "error" in result
    assert "non-negative integer" in result["error"]

    # Test invalid plot type
    result = plugin.plot_values_and_store(
        labels=[1, 2, 3],
        data=[100, 200, 300],
        plot_tite="Test Error",
        plot_type="invalid_type",
    )

    assert "error" in result
    assert "Invalid plot type" in result["error"]

    # Note: Error cases don't generate plot files, so no cleanup needed
