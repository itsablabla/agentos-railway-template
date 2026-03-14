"""
AgentOS — Garza OS
------------------
Complete Agno agent suite with all available tools, skills, and interfaces.

Agents (16):
  Original:
  - knowledge-agent  : RAG agent with vector search
  - mcp-agent        : MCP-powered agent (Agno docs + custom MCPs)
  - dash             : Self-learning data/SQL agent (F1 dataset)
  - gcode            : Fast code generation
  - os-control       : System admin — manages all of AgentOS + Telegram bots
  - pal              : Personal assistant with agentic memory
  - scout            : Enterprise knowledge navigator
  - seek             : Deep research with Parallel API

  New — Full Tool Coverage:
  - web-agent        : DuckDuckGo, Wikipedia, arXiv, HackerNews, PubMed, YouTube, YFinance + more
  - analyst          : DuckDB, CSV, Pandas, YFinance, Visualization, Python execution
  - coder            : Python, Shell, File, DuckDB + optional GitHub, E2B
  - media-agent      : DALL-E, YouTube, Giphy + optional ElevenLabs, Fal, Replicate
  - productivity     : GitHub, Notion, Todoist, Linear, Jira, Google Calendar/Sheets + more
  - comms            : Telegram, Slack, Gmail, Twilio, Discord, X, Reddit, Zoom, WhatsApp
  - finance          : YFinance (full), OpenBB, Financial Datasets
  - utility          : Weather, Google Maps, Calculator, BrandFetch + more
  - reasoner         : ReasoningTools + research (uses o4-mini)
  - skills-agent     : Agno Skills system with LocalSkills from /skills directory

Teams (4):
  - research-team    : Seek + Scout (deep research)
  - intelligence-team: Web Agent + Analyst + Reasoner (comprehensive intelligence)
  - dev-team         : Coder + Web Agent + Gcode (software development)

Workflows (1):
  - daily-brief      : Scheduled morning briefing

Interfaces:
  - Telegram         : Multi-bot (TELEGRAM_BOTS env var or POST /telegram/bots)
  - Slack            : SLACK_BOT_TOKEN + SLACK_SIGNING_SECRET
  - AG-UI            : AGUI_ENABLED=true
  - A2A              : A2A_ENABLED=true

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
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# ---------------------------------------------------------------------------
# Original agents
# ---------------------------------------------------------------------------
from agents.knowledge_agent import knowledge_agent
from agents.mcp_agent import mcp_agent
from agents.dash import dash
from agents.gcode import gcode
from agents.os_control import os_control
from agents.pal import pal
from agents.scout import scout
from agents.seek import seek

# ---------------------------------------------------------------------------
# New agents — full tool coverage
# ---------------------------------------------------------------------------
from agents.web_agent import web_agent
from agents.analyst import analyst
from agents.coder import coder
from agents.media_agent import media_agent
from agents.productivity import productivity
from agents.comms import comms
from agents.finance import finance
from agents.utility import utility
from agents.reasoner import reasoner
from agents.skills_agent import skills_agent

# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------
from teams.research import research_team
from teams.intelligence import intelligence_team
from teams.dev import dev_team

# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------
from workflows.daily_brief import daily_brief_workflow

# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------
from db import get_postgres_db
from interfaces.telegram import create_telegram_router

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Build Registry — exposes tools, models, and dbs in the Studio Registry UI
# ---------------------------------------------------------------------------
registry = Registry(
    name="Garza OS Registry",
    description="Registry of all tools, models, and databases available in Garza OS AgentOS",
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
        DuckDuckGoTools(),
        YFinanceTools(),
    ],
    dbs=[
        get_postgres_db(),
    ],
)

# ---------------------------------------------------------------------------
# All agents — ordered by category
# ---------------------------------------------------------------------------
_all_agents = [
    # Original core agents
    knowledge_agent,
    mcp_agent,
    dash,
    gcode,
    os_control,
    pal,
    scout,
    seek,
    # New full-coverage agents
    web_agent,
    analyst,
    coder,
    media_agent,
    productivity,
    comms,
    finance,
    utility,
    reasoner,
    skills_agent,
]

# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Garza OS",
    tracing=True,
    scheduler=True,
    db=get_postgres_db(),
    agents=_all_agents,
    teams=[research_team, intelligence_team, dev_team],
    workflows=[daily_brief_workflow],
    registry=registry,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()

# ---------------------------------------------------------------------------
# Telegram multi-bot interface
# Bots are registered via:
#   1. TELEGRAM_BOTS env var: "token1:agent:pal,token2:team:research-team"
#      Simple format: "token1:pal,token2:research-team" (defaults to agent)
#   2. OS Control agent chat: "connect Telegram bot <token> to <agent>"
#   3. POST /telegram/bots API directly
#   4. GET /telegram/bots to list all registered bots
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
