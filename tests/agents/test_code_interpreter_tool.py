from src.agents.tools.python_interpreter import CustomPythonREPL


def test_output_without_errors_with_two_print_statements():
    """Test that CustomPythonREPL correctly handles code without errors and captures multiple print statements."""
    repl = CustomPythonREPL()

    # Execute code with two print statements
    command = """
print("First output")
x = 10 + 5
print(f"Second output: {x}")
"""

    result = repl.run(command)

    # Verify both print statements are captured
    assert "First output" in result
    assert "Second output: 15" in result
    assert result.count("First output") == 1
    assert result.count("Second output: 15") == 1

    # Verify no error representation in output
    assert "Error" not in result
    assert "Exception" not in result


def test_output_with_errors_and_one_print_statement_before():
    """Test that CustomPythonREPL correctly handles code with errors and captures print statement before error."""
    repl = CustomPythonREPL()

    # Execute code with one print statement followed by an error
    command = """
print("Output before error")
result = 10 / 0  # This will cause a ZeroDivisionError
"""

    result = repl.run(command)

    # Verify print statement before error is captured
    assert "Output before error" in result

    # Verify error is captured and represented properly
    assert "ZeroDivisionError" in result
    assert "division by zero" in result

    # Verify the error representation format
    assert (
        "ZeroDivisionError('division by zero')" in result
        or "ZeroDivisionError:" in result
    )
