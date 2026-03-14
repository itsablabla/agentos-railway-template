"""
AgentOS
-------

The main entry point for AgentOS.

Run:
    python -m app.main
"""

from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.registry import Registry
from agno.models.openai import OpenAIResponses
from agno.tools.mcp import MCPTools

from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
from db import get_postgres_db

# ---------------------------------------------------------------------------
# Build Registry — exposes tools, models, and dbs in the Studio Registry UI
# ---------------------------------------------------------------------------
registry = Registry(
    name="Garza OS Registry",
    description="Registry of tools, models, and databases available in AgentOS",
    models=[
        OpenAIResponses(id="gpt-4o"),
        OpenAIResponses(id="gpt-4o-mini"),
        OpenAIResponses(id="gpt-4.1"),
        OpenAIResponses(id="gpt-4.1-mini"),
        OpenAIResponses(id="o3"),
        OpenAIResponses(id="o4-mini"),
    ],
    tools=[
        MCPTools(url="https://docs.agno.com/mcp"),
    ],
    dbs=[
        get_postgres_db(),
    ],
)

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="AgentOS",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=[knowledge_agent, mcp_agent],
    registry=registry,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
