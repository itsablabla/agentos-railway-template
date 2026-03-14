"""
AgentOS — Garza OS
------------------
Full Agno demo suite: 7 agents, 1 team, 1 workflow.

Agents:
  - knowledge-agent  : RAG agent for answering questions from a knowledge base
  - mcp-agent        : MCP-powered agent with external tool access
  - dash             : Self-learning data/SQL agent (F1 dataset)
  - gcode            : Lightweight coding agent
  - pal              : Personal agent that learns your preferences
  - scout            : Enterprise knowledge navigator
  - seek             : Deep research agent

Teams:
  - research-team    : Seek + Scout working together on deep research

Workflows:
  - daily-brief      : Scheduled morning briefing workflow

Run:
    python -m app.main
"""
from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.registry import Registry
from agno.models.openai import OpenAIResponses
from agno.tools.mcp import MCPTools
from agno.tools.parallel import ParallelTools

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
from agents.dash import dash
from agents.gcode import gcode
from agents.os_control import os_control
from agents.pal import pal
from agents.scout import scout
from agents.seek import seek
from teams.research import research_team
from workflows.daily_brief import daily_brief_workflow
from db import get_postgres_db

# ---------------------------------------------------------------------------
# Build Registry — exposes tools, models, and dbs in the Studio Registry UI
# ---------------------------------------------------------------------------
registry = Registry(
    name="Garza OS Registry",
    description="Registry of all tools, models, and databases available in AgentOS",
    models=[
        OpenAIResponses(id="gpt-4o"),
        OpenAIResponses(id="gpt-4o-mini"),
        OpenAIResponses(id="gpt-4.1"),
        OpenAIResponses(id="gpt-4.1-mini"),
        OpenAIResponses(id="o3"),
        OpenAIResponses(id="o4-mini"),
        OpenAIResponses(id="gpt-5.2"),
        OpenAIResponses(id="gpt-5-mini"),
    ],
    tools=[
        MCPTools(url="https://docs.agno.com/mcp"),
        ParallelTools(),
    ],
    dbs=[
        get_postgres_db(),
    ],
)

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Garza OS",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[knowledge_agent, mcp_agent, dash, gcode, os_control, pal, scout, seek],
    teams=[research_team],
    workflows=[daily_brief_workflow],
    registry=registry,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
