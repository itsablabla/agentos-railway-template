"""
Skills Agent
------------
An agent that uses Agno's Skills system for domain-specific knowledge packages.
Skills are loaded lazily — the agent discovers them, loads what it needs,
and executes scripts from skill packages.

The /skills directory contains SKILL.md packages that this agent can use.
Add new skills by dropping a directory with a SKILL.md file into /skills.

Built-in skills included:
  - research/      : Deep research methodology
  - coding/        : Software engineering best practices
  - writing/       : Content creation and editing
  - analysis/      : Data analysis frameworks
  - business/      : Business strategy and frameworks
"""
import os
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.skills import Skills, LocalSkills
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.tools.file import FileTools

from db import get_postgres_db

# Skills directory — relative to this file's parent (project root)
_skills_dir = Path(__file__).parent.parent / "skills"
_skills_dir.mkdir(exist_ok=True)

# Build skills loader if directory exists and has content
_skills_loaders = []
if _skills_dir.exists():
    _skills_loaders.append(LocalSkills(str(_skills_dir)))

skills_agent = Agent(
    id="skills-agent",
    name="Skills Agent",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A domain-expert agent powered by Agno's Skills system. "
        "Discovers and loads specialized knowledge packages (skills) on demand, "
        "keeping context efficient by only loading what's needed for each task."
    ),
    instructions="""\
You are a domain-expert agent powered by the Agno Skills system.

**How Skills Work:**
- You have access to a library of skill packages
- Each skill contains specialized instructions, scripts, and references
- Use `get_skill_instructions(skill_name)` to load a skill's full guidance
- Use `get_skill_script(skill_name, script_path)` to get executable scripts
- Use `get_skill_reference(skill_name, ref_path)` to access reference docs

**Available Skill Categories:**
- research: Deep research methodology and frameworks
- coding: Software engineering best practices
- writing: Content creation, editing, and style guides
- analysis: Data analysis frameworks and templates
- business: Business strategy, frameworks, and models

**Workflow:**
1. Identify which skill(s) are relevant to the task
2. Load the skill instructions
3. Follow the skill's methodology
4. Use skill scripts if available
5. Reference skill documentation as needed

**Guidelines:**
- Always load the relevant skill before starting a task
- Follow skill instructions precisely
- Combine multiple skills when tasks span domains
- Use DuckDuckGo to supplement skill knowledge with current information
""",
    tools=[
        DuckDuckGoTools(),
        PythonTools(),
        FileTools(),
    ],
    skills=Skills(loaders=_skills_loaders) if _skills_loaders else None,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    skills_agent.print_response(
        "What skills do you have available?",
        stream=True,
    )
