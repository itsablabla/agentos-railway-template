"""
Intelligence Team
-----------------
A multi-agent team combining web research, data analysis, and structured reasoning
for comprehensive intelligence gathering and analysis.

Members:
  - Web Agent    : Searches the web, reads articles, fetches financial data
  - Analyst      : Analyzes data, runs SQL, creates visualizations
  - Reasoner     : Applies structured reasoning to synthesize findings

Use for:
  - Market research and competitive analysis
  - Investment research
  - Strategic planning support
  - Complex multi-domain questions
"""
from agno.team import Team
from agno.models.openai import OpenAIResponses

from agents.web_agent import web_agent
from agents.analyst import analyst
from agents.reasoner import reasoner
from db import get_postgres_db

intelligence_team = Team(
    id="intelligence-team",
    name="Intelligence Team",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A multi-agent intelligence team. The Web Agent gathers information from across the web, "
        "the Analyst processes and visualizes data, and the Reasoner synthesizes everything "
        "into structured, evidence-based conclusions."
    ),
    instructions="""\
You are the coordinator of an intelligence team. Route tasks to the right agents:

- **Web Agent**: Use for web search, article reading, news, academic papers, YouTube, financial data
- **Analyst**: Use for data analysis, SQL queries, charts, financial modeling, calculations
- **Reasoner**: Use for structured analysis, decision support, trade-off evaluation, synthesis

**Workflow for complex research:**
1. Have Web Agent gather raw information
2. Have Analyst process and quantify the data
3. Have Reasoner synthesize into conclusions

**Output format:**
- Executive Summary (3-5 sentences)
- Key Findings (numbered, with sources)
- Analysis & Implications
- Recommendations (if applicable)
- Confidence Level and Limitations
""",
    members=[web_agent, analyst, reasoner],
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    markdown=True,
)
