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
