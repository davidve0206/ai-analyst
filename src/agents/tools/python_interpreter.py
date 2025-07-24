import re
import sys
from io import StringIO
from typing import Dict, Optional

from pydantic import BaseModel, Field
from langchain_core.tools import Tool


class CustomPythonREPL(BaseModel):
    """Simulates a standalone Python REPL."""

    globals: Optional[Dict] = Field(default_factory=dict, alias="_globals")
    locals: Optional[Dict] = Field(default_factory=dict, alias="_locals")

    @staticmethod
    def sanitize_input(query: str) -> str:
        """
        Clean and normalize an input string.

        This function removes leading and trailing whitespace or backticks,
        and strips an optional leading 'python' keyword (case-insensitive)
        commonly used in markdown-style code blocks.

        Args:
            query (str): The raw user input to sanitize.

        Returns:
            str: A cleaned version of the input string, ready for execution or parsing.
        """
        query = re.sub(r"^(\s|`)*(?i:python)?\s*", "", query)
        query = re.sub(r"(\s|`)*$", "", query)
        return query

    def run(self, command: str) -> str:
        """Run command and return output including errors, without multiprocessing."""

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        try:
            cleaned_command = self.sanitize_input(command)
            exec(cleaned_command, self.globals, self.locals)
        except Exception as e:
            output = mystdout.getvalue()
            sys.stdout = old_stdout
            return output + f"\n{repr(e)}"
        else:
            output = mystdout.getvalue()
            sys.stdout = old_stdout
            return output


def create_python_repl_tool() -> Tool:
    """
    Create a tool for executing Python code in a REPL environment.

    Returns:
        Tool: A tool that can execute Python commands.
    """

    python_repl = CustomPythonREPL()
    return Tool(
        name="python_repl",
        description=(
            "A Python shell. Use this to execute python commands. "
            "Input should be a valid python command. If you want to see the output of a value, "
            "you should print it out with `print(...)`."
        ),
        func=python_repl.run,
    )
