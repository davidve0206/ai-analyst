from numpy.polynomial import Polynomial

from semantic_kernel.functions import kernel_function


class ProjectionsPlugin:
    @kernel_function()
    def calculate_trend_and_projection(
        self, data=list[int], projection_period: int = 3
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
