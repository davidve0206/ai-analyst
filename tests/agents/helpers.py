import os
from src.configuration.settings import BASE_DIR


test_temp_dir = BASE_DIR / "tests" / "temp"
os.makedirs(test_temp_dir, exist_ok=True)

png_file_name = "sales_projection_spain_fixture.png"
csv_file_name = "Spain_sales_history_fixture.csv"


def assert_numeric_value_in_str(
    expected_value: int | float, result: str, error_output: None
) -> None:
    """
    Assert that a numeric value is present in a string.

    Args:
        expected_value (int): The numeric value to check for.
        result (str): The string to search within.

    Raises:
        AssertionError: If the expected value is not found in the string.
    """
    str_value = str(expected_value)
    formatted_value = f"{expected_value:,.2f}"
    error_output = error_output or f"Expected {expected_value} not found in {result}"
    assert str_value in result or formatted_value in result, error_output


california_monthly_sales_in_db = {
    "2022-07": 172959.55,
    "2022-08": 135010.70,
    "2022-09": 232417.60,
    "2022-10": 220462.45,
    "2022-11": 220820.90,
    "2022-12": 199803.00,
    "2023-01": 192188.20,
    "2023-02": 194381.50,
    "2023-03": 219177.95,
    "2023-04": 249891.10,
    "2023-05": 262177.15,
    "2023-06": 169257.70,
    "2023-07": 298161.80,
    "2023-08": 169368.60,
    "2023-09": 200238.90,
    "2023-10": 217520.45,
    "2023-11": 184132.40,
    "2023-12": 244497.65,
    "2024-01": 227591.75,
    "2024-02": 220957.65,
    "2024-03": 211678.75,
    "2024-04": 285375.45,
    "2024-05": 186417.50,
    "2024-06": 269011.10,
    "2024-07": 294432.50,
    "2024-08": 174239.60,
    "2024-09": 210397.65,
    "2024-10": 277312.45,
    "2024-11": 169227.50,
    "2024-12": 248809.15,
    "2025-01": 231620.75,
    "2025-02": 197168.70,
    "2025-03": 232004.15,
    "2025-04": 212986.75,
    "2025-05": 200624.20,
}

operational_values_expected = {
    "VALENCIA": 2167665.7,  # Total sales for Valencia (City breakdown)
    "COMMI-ES1-BTB": 1176778.68,  # Sales by item code
    "17579": 1239757.23,  # Sales by client Id
    "9100": 1234526.39,  # Sales by EU_ITEM_FAMILY
}

sales_analysis_declining_yoy = """### Analysis of Sales History Data for Spain

#### Key Metrics
The following metrics were calculated for the sales data:

- **Total Sales**: Monthly gross amounts summed up.
- **Month-over-Month (MoM) Growth**: Percentage change from the previous month.
- **Year-over-Year (YoY) Growth**: Percentage change from the same month in the previous year.

Here’s a summary of the sales analysis:

| Date       | Total Sales (€) | MoM Growth (%) | YoY Growth (%) |
|------------|------------------|----------------|-----------------|
| 2020-12-31 | 3,236,168        | -              | -               |
| 2021-01-31 | 4,145,849        | 28.11          | -               |
| 2021-02-28 | 3,600,683        | -13.15         | -               |
| ...        | ...              | ...            | ...             |
| 2023-10-31 | 3,040,614        | -30.58         | -24.21          |
| 2023-11-30 | 4,410,770        | 45.06          | -7.12           |

#### Trends and Insights
1. **Recent Trends**: 
   - In the last month (November 2023), total sales were **€4,410,770**, which represents a **45.06% increase** compared to October 2023.
   - Year-over-year growth for November shows a **-7.12%** decline compared to November 2022.

2. **Seasonality**: 
   - The data shows fluctuations in sales, indicating potential seasonality. For instance, sales peak in certain months, followed by declines in others.
   - Notably, there are months (like July and August 2021) with zero sales, indicating possible seasonal closures or reduced activity.

3. **Growth Patterns**:
   - The highest MoM growth recorded was **73.15%** in April 2021, while the largest decline was **-99.99%** in June 2021.
   - The most recent months show a recovery trend after a dip in sales during the summer months of 2023.

4. **Projection**:
   - A linear projection of sales for the next three months has been calculated, suggesting a continuation of the upward trend observed in recent months.

### Visualization
A plot illustrating the evolution of total sales and its projection over the next three months has been created:

- **File Name**: `spain_sales_projection.png`
- **Description**: This graph shows the actual sales figures from December 2020 to November 2023, along with projected sales for December 2023, January 2024, and February 2024. The projection indicates a potential increase in sales, assuming the current trend continues.
"""

sales_analysis_declining_trend = """### Analysis of Sales History Data for Spain

#### Key Metrics
The following metrics were calculated for the sales data:

- **Total Sales**: Monthly gross amounts summed up.
- **Month-over-Month (MoM) Growth**: Percentage change from the previous month.
- **Year-over-Year (YoY) Growth**: Percentage change from the same month in the previous year.

Here’s a summary of the sales analysis:

| Date       | Total Sales (€) | MoM Growth (%) | YoY Growth (%) |
|------------|------------------|----------------|-----------------|
| 2020-12-31 | 3,236,168        | -              | -               |
| 2021-01-31 | 4,145,849        | 28.11          | -               |
| 2021-02-28 | 3,600,683        | -13.15         | -               |
| ...        | ...              | ...            | ...             |
| 2023-10-31 | 3,040,614        | -30.58         | 0.0          |
| 2023-11-30 | 4,410,770        | 45.06          | 1.1           |

#### Trends and Insights
1. **Recent Trends**: 
   - In the last month (November 2023), total sales were **€4,410,770**, which represents a **45.06% increase** compared to October 2023.
   - Year-over-year growth for November shows a **1.1%** increase compared to November 2022.

2. **Seasonality**: 
   - The data shows fluctuations in sales, indicating potential seasonality. For instance, sales peak in certain months, followed by declines in others.

3. **Growth Patterns**:
   - The highest MoM growth recorded was **73.15%** in April 2021, while the largest decline was **-9.99%** in June 2021.
   - The most recent months show a declining trend after a dip in sales during the summer months of 2023.

4. **Projection**:
   - A linear projection of sales for the next three months has been calculated, suggesting a continuation of the slight downwards trend observed in recent months.

### Visualization
A plot illustrating the evolution of total sales and its projection over the next three months has been created:

- **File Name**: `spain_sales_projection.png`
- **Description**: This graph shows the actual sales figures from December 2020 to November 2023, along with projected sales for December 2023, January 2024, and February 2024. The projection indicates a potential decrease in sales, assuming the current trend continues.
"""

sales_analysis_no_special_case = """### Analysis of Sales History Data for Spain

#### Key Metrics
The following metrics were calculated for the sales data:

- **Total Sales**: Monthly gross amounts summed up.
- **Month-over-Month (MoM) Growth**: Percentage change from the previous month.
- **Year-over-Year (YoY) Growth**: Percentage change from the same month in the previous year.

Here’s a summary of the sales analysis:

| Date       | Total Sales (€) | MoM Growth (%) | YoY Growth (%) |
|------------|------------------|----------------|-----------------|
| 2020-12-31 | 3,236,168        | -              | -               |
| 2021-01-31 | 4,145,849        | 28.11          | -               |
| 2021-02-28 | 3,600,683        | -13.15         | -               |
| ...        | ...              | ...            | ...             |
| 2023-10-31 | 3,040,614        | -30.58         | 1.21          |
| 2023-11-30 | 4,410,770        | 45.06          | 2.12           |

#### Trends and Insights
1. **Recent Trends**: 
   - In the last month (November 2023), total sales were **€4,410,770**, which represents a **45.06% increase** compared to October 2023.
   - Year-over-year growth for November shows a **2.12%** increase compared to November 2022.

2. **Seasonality**: 
   - The data shows fluctuations in sales, indicating potential seasonality. For instance, sales peak in certain months, followed by declines in others.

3. **Growth Patterns**:
   - The highest MoM growth recorded was **73.15%** in April 2021, while the largest decline was **-9.99%** in June 2021.
   - The most recent months show a recovery trend after a dip in sales during the summer months of 2023.

4. **Projection**:
   - A linear projection of sales for the next three months has been calculated, suggesting a continuation of the upward trend observed in recent months.

### Visualization
A plot illustrating the evolution of total sales and its projection over the next three months has been created:

- **File Name**: `spain_sales_projection.png`
- **Description**: This graph shows the actual sales figures from December 2020 to November 2023, along with projected sales for December 2023, January 2024, and February 2024. The projection indicates a potential increase in sales, assuming the current trend continues.
"""
