from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL


def create_python_repl_tool() -> Tool:
    """
    Create a tool for executing Python code in a REPL environment.

    Returns:
        Tool: A tool that can execute Python commands.
    """

    python_repl = PythonREPL()
    return Tool(
        name="python_repl",
        description=(
            "A Python shell. Use this to execute python commands. "
            "Input should be a valid python command. If you want to see the output of a value, "
            "you should print it out with `print(...)`."
        ),
        func=python_repl.run,
    )
