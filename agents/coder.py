"""
Coder Agent
-----------
A full-stack code execution agent with Python, Shell, file management,
and optional GitHub integration.

Tools:
  - PythonTools  : Write and execute Python code
  - ShellTools   : Run shell commands
  - FileTools    : Read and write files
  - DuckDbTools  : SQL for data tasks
  - DuckDuckGoTools: Search for documentation and solutions

Activate optional tools by setting env vars:
  GITHUB_TOKEN   → GithubTools (PR creation, issue management, code search)
  E2B_API_KEY    → E2BTools (sandboxed code execution)
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.python import PythonTools
from agno.tools.shell import ShellTools
from agno.tools.file import FileTools
from agno.tools.duckdb import DuckDbTools
from agno.tools.duckduckgo import DuckDuckGoTools

from db import get_postgres_db

_tools = [
    PythonTools(),
    ShellTools(),
    FileTools(),
    DuckDbTools(),
    DuckDuckGoTools(),
]

if os.getenv("GITHUB_TOKEN"):
    try:
        from agno.tools.github import GithubTools
        _tools.append(GithubTools())
    except ImportError:
        pass

if os.getenv("E2B_API_KEY"):
    try:
        from agno.tools.e2b import E2BTools
        _tools.append(E2BTools())
    except ImportError:
        pass

coder = Agent(
    id="coder",
    name="Coder",
    model=OpenAIResponses(id="gpt-4.1"),
    db=get_postgres_db(),
    description=(
        "A full-stack code execution agent. Writes and runs Python, executes shell commands, "
        "manages files, runs SQL queries, and searches for documentation. "
        "Can create, debug, test, and refactor code autonomously."
    ),
    instructions="""\
You are an expert software engineer with full code execution capabilities.

**Capabilities:**
- Write and execute Python code in real-time
- Run shell commands (bash, git, pip, etc.)
- Read and write files
- Run SQL queries with DuckDB
- Search for documentation, libraries, and solutions

**How to approach coding tasks:**
1. Understand the requirement clearly
2. Plan the approach before writing code
3. Write clean, well-commented code
4. Execute and test the code
5. Debug if needed, iterate until working
6. Explain what the code does

**Best practices:**
- Always handle errors with try/except
- Write type hints for function signatures
- Add docstrings to functions
- Test edge cases
- Show the output after execution

**When searching for solutions:**
- Search for the library/framework documentation first
- Look for official examples
- Adapt solutions to the specific use case
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=10,
    markdown=True,
)

if __name__ == "__main__":
    coder.print_response(
        "Write a Python script that fetches the top 5 HackerNews stories and saves them to a CSV file",
        stream=True,
    )
