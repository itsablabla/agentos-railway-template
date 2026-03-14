"""
AgentOS — Garza OS
------------------
Full Agno demo suite: 7 agents, 1 team, 1 workflow.

Agents:
  - knowledge-agent  : RAG agent for answering questions from a knowledge base
  - mcp-agent        : MCP-powered agent with external tool access
  - dash             : Self-learning data/SQL agent (F1 dataset)
  - gcode            : Lightweight coding agent
  - os-control       : System admin agent — manages all of AgentOS + Telegram bots
  - pal              : Personal agent that learns your preferences
  - scout            : Enterprise knowledge navigator
  - seek             : Deep research agent

Teams:
  - research-team    : Seek + Scout working together on deep research

Workflows:
  - daily-brief      : Scheduled morning briefing workflow

Interfaces:
  - Telegram         : Multi-bot — any agent/team/workflow gets its own bot
                       Configure via TELEGRAM_BOTS env var or OS Control agent chat
  - Slack            : Activate via SLACK_BOT_TOKEN + SLACK_SIGNING_SECRET env vars
  - AG-UI            : Activate via AGUI_ENABLED=true env var
  - A2A              : Activate via A2A_ENABLED=true env var

Run:
    python -m app.main
"""
import logging
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
from interfaces.telegram import create_telegram_router

logger = logging.getLogger(__name__)

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

# ---------------------------------------------------------------------------
# Telegram multi-bot interface
# Bots are registered via:
#   1. TELEGRAM_BOTS env var: "token1:agent:pal,token2:team:research-team"
#   2. OS Control agent chat: "connect Telegram bot <token> to <agent>"
#   3. POST /telegram/bots API directly
# ---------------------------------------------------------------------------
_public_domain = getenv("RAILWAY_PUBLIC_DOMAIN", getenv("PUBLIC_URL", ""))
if _public_domain and not _public_domain.startswith("http"):
    _public_domain = f"https://{_public_domain}"

telegram_router = create_telegram_router(base_url=_public_domain or "http://localhost:8000")
app.include_router(telegram_router)
logger.info(f"Telegram interface mounted at /telegram (public URL: {_public_domain or 'not set'})")

# ---------------------------------------------------------------------------
# Slack interface (activate by setting SLACK_BOT_TOKEN + SLACK_SIGNING_SECRET)
# ---------------------------------------------------------------------------
_slack_token = getenv("SLACK_BOT_TOKEN")
_slack_secret = getenv("SLACK_SIGNING_SECRET")
if _slack_token and _slack_secret:
    try:
        from agno.os.interfaces.slack import Slack
        slack_interface = Slack(token=_slack_token, signing_secret=_slack_secret)
        slack_interface.attach(app, agent_os)
        logger.info("Slack interface activated")
    except ImportError as e:
        logger.warning(f"Slack interface not available: {e}")
    except Exception as e:
        logger.error(f"Failed to attach Slack interface: {e}")

# ---------------------------------------------------------------------------
# AG-UI interface (activate by setting AGUI_ENABLED=true)
# ---------------------------------------------------------------------------
if getenv("AGUI_ENABLED", "").lower() == "true":
    try:
        from agno.os.interfaces.agui import AGUI
        agui_interface = AGUI()
        agui_interface.attach(app, agent_os)
        logger.info("AG-UI interface activated")
    except ImportError as e:
        logger.warning(f"AG-UI interface not available: {e}")
    except Exception as e:
        logger.error(f"Failed to attach AG-UI interface: {e}")

# ---------------------------------------------------------------------------
# A2A interface (activate by setting A2A_ENABLED=true)
# ---------------------------------------------------------------------------
if getenv("A2A_ENABLED", "").lower() == "true":
    try:
        from agno.os.interfaces.a2a import A2A
        a2a_interface = A2A()
        a2a_interface.attach(app, agent_os)
        logger.info("A2A interface activated")
    except ImportError as e:
        logger.warning(f"A2A interface not available: {e}")
    except Exception as e:
        logger.error(f"Failed to attach A2A interface: {e}")

if __name__ == "__main__":
    agent_os.serve(
        app="main:app",
        reload=getenv("RUNTIME_ENV", "prd") == "dev",
    )
