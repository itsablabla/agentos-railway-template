"""
Dev Team
--------
A multi-agent software development team combining code execution,
web research for documentation, and code generation.

Members:
  - Coder      : Full code execution (Python, Shell, File, GitHub)
  - Web Agent  : Documentation search, Stack Overflow, GitHub search
  - Gcode      : Fast code generation and snippets

Use for:
  - Building complete applications
  - Debugging complex issues
  - Architecture design
  - Code review and refactoring
"""
from agno.team import Team
from agno.models.openai import OpenAIResponses

from agents.coder import coder
from agents.web_agent import web_agent
from agents.gcode import gcode
from db import get_postgres_db

dev_team = Team(
    id="dev-team",
    name="Dev Team",
    model=OpenAIResponses(id="gpt-4.1"),
    db=get_postgres_db(),
    description=(
        "A multi-agent software development team. Coder executes code and manages files, "
        "Web Agent searches documentation and solutions, and Gcode generates code snippets quickly. "
        "Together they can build, debug, and ship complete software."
    ),
    instructions="""\
You are the lead engineer coordinating a development team. Route tasks to the right agents:

- **Coder**: Use for executing code, running tests, file operations, shell commands, GitHub
- **Web Agent**: Use for searching documentation, finding libraries, Stack Overflow, GitHub examples
- **Gcode**: Use for quick code generation, boilerplate, and snippets

**Development Workflow:**
1. Understand requirements fully before writing code
2. Search for existing solutions before building from scratch
3. Write code incrementally — test each component
4. Handle errors explicitly
5. Document what was built

**Output format:**
- Brief explanation of the approach
- Code with inline comments
- Test results / execution output
- How to use / next steps
""",
    members=[coder, web_agent, gcode],
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)
