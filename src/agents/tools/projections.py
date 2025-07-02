import os
from datetime import datetime
from typing import Literal

import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
from semantic_kernel.functions import kernel_function

from src.configuration.settings import TEMP_DIR


class ProjectionsPlugin:
    @kernel_function()
    def calculate_trend_and_projection(
        self, data: list[int], projection_period: int = 3
    ) -> list[float]:
        """
        Calculate a trend line based on the provided data and project
        future values.

        Returns a list of projected values based on a linear trend line
        fitted to the historical data; the length of the trend line will
        be equal to the number of historical data points plus the projection
        period.

        Args:
            data (list[int]): Historical data points to analyze.
            projection_period (int): Number of future points to project.
        Returns:
            list[float]: Trendline including the projected data points.
        """

        points_provided = len(data)
        total_points = points_provided + projection_period

        trendline = Polynomial.fit(range(points_provided), data, 1)

        x_values = list(range(total_points))
        projected_values = trendline(x_values)

        return projected_values.tolist()

    @kernel_function()
    def plot_values_and_store(
        self,
        labels: list[str | int],
        data: list[int],
        plot_tite: str,
        x_axis_name: str = "Time Period",
        y_axis_name: str = "Value",
        plot_type: Literal["line", "bar", "horizontal_bar"] = "line",
        include_trend_line: bool = True,
        projection_period: int = 3,
    ) -> dict[str, str | dict]:
        """
        Generate a plot of the financial values with a trend line
        and projections, if projection_period is greater than 0.

        The plot will include the historical data points,
        a trend line fitted to the historical data, and projected
        values for the specified projection period.

        Args:
            labels (list[int]): Labels for the x-axis, typically representing time periods.
            data (list[int]): Historical financial values to plot.
            plot_tite (str): Title of the plot.
            plot_type (Literal["line", "bar", "horizontal_bar"]): Type of plot to generate.
                - "line": Line plot.
                - "bar": Vertical bar plot.
                - "horizontal_bar": Horizontal bar plot.
            include_trend_line (bool): Whether to include a trend line in the plot.
            projection_period (int): Number of future points to project; 0 if no projection needs to be included.
        Returns:
            dict[str, str]: Dictionary containing the plot image path and the data points.
        """

        if len(labels) != len(data):
            return {"error": "The length of labels and data must be the same."}
        if projection_period < 0:
            return {"error": "Projection period must be a non-negative integer."}

        plt.figure(figsize=(10, 6))

        # Plot historical data
        match plot_type:
            case "line":
                plt.plot(
                    labels,
                    data,
                    marker="o",
                    label="Historical Data",
                    linewidth=2,
                    markersize=6,
                )
            case "bar":
                plt.bar(labels, data, label="Historical Data", alpha=0.7)
            case "horizontal_bar":
                plt.barh(labels, data, label="Historical Data", alpha=0.7)
            case _:
                return {
                    "error": "Invalid plot type. Use 'line', 'bar', or 'horizontal_bar'."
                }

        # Add trend line and projections if requested
        projected_values = None
        extended_labels = None
        projection_labels = None
        projection_data = None

        if include_trend_line or projection_period > 0:
            try:
                # Calculate trend and projections using the existing method
                projected_values = self.calculate_trend_and_projection(
                    data, projection_period
                )

                # Create extended labels for projections
                extended_labels = labels.copy()
                if projection_period > 0:
                    for i in range(1, projection_period + 1):
                        extended_labels.append(f"t+{i}")

                    projection_labels = extended_labels[len(data) :]
                    projection_data = projected_values[
                        len(data) :
                    ]  # Plot trend line for historical data
                if include_trend_line:
                    # Determine the extent of the trend line
                    if projection_period > 0:
                        # Extend trend line to connect with first projection point
                        trend_labels = labels + [extended_labels[len(data)]]
                        trend_values = projected_values[: len(data) + 1]
                    else:
                        # Just show trend for historical data
                        trend_labels = labels
                        trend_values = projected_values[: len(data)]

                    # Plot trend line as a line overlay for all plot types
                    plt.plot(
                        trend_labels,
                        trend_values,
                        "--",
                        color="gray",
                        alpha=0.8,
                        label="Trend Line",
                        linewidth=2,
                    )

                # Plot projections
                if projection_period > 0:
                    if plot_type == "line":
                        plt.plot(
                            projection_labels,
                            projection_data,
                            "o--",
                            color="orange",
                            alpha=0.8,
                            label="Projections",
                            linewidth=2,
                            markersize=6,
                        )
                    elif plot_type == "bar":
                        plt.bar(
                            projection_labels,
                            projection_data,
                            alpha=0.5,
                            color="orange",
                            label="Projections",
                        )
                    elif plot_type == "horizontal_bar":
                        plt.barh(
                            projection_labels,
                            projection_data,
                            alpha=0.5,
                            color="orange",
                            label="Projections",
                        )

            except Exception as e:
                return {
                    "error": f"Error calculating trend line or projections: {str(e)}"
                }

        # Customize the plot
        plt.title(plot_tite, fontsize=14, fontweight="bold")
        plt.xlabel(x_axis_name, fontsize=12)
        plt.ylabel(y_axis_name, fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save the plot to the outputs directory
        try:
            # Create outputs directory if it doesn't exist
            os.makedirs(TEMP_DIR, exist_ok=True)

            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{plot_tite.lower().replace(' ', '_').replace('-', '_')}_{timestamp}.png"
            file_path = os.path.join(TEMP_DIR, filename)

            # Save the plot
            plt.savefig(file_path, dpi=300, bbox_inches="tight")
            plt.close()  # Close the figure to free memory

            # Prepare data summary
            data_summary = {
                "historical_data": list(zip(labels, data)),
                "plot_type": plot_type,
                "include_trend_line": include_trend_line,
                "projection_period": projection_period,
            }

            # Add trend line data if calculated
            if projected_values is not None and include_trend_line:
                trend_line_data = projected_values[: len(data)]
                data_summary["trend_line"] = list(zip(labels, trend_line_data))

            # Add projection data if applicable
            if (
                projection_period > 0
                and projection_labels is not None
                and projection_data is not None
            ):
                data_summary["projections"] = list(
                    zip(projection_labels, projection_data)
                )

            return {
                "plot_path": file_path,
                "data_summary": data_summary,
                "message": f"Plot successfully generated and saved to {file_path}",
            }

        except Exception as e:
            plt.close()  # Ensure figure is closed even if saving fails
            return {"error": f"Error saving plot: {str(e)}"}
