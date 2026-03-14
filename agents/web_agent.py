"""
Web Agent
---------
A comprehensive web search and scraping agent with access to every
free search and content-extraction toolkit Agno provides.

Tools (always active — no API key needed):
  - DuckDuckGoTools   : Web search
  - WikipediaTools    : Wikipedia search and article reading
  - ArxivTools        : Academic paper search
  - HackerNewsTools   : HN stories and comments
  - PubmedTools       : Medical/biomedical literature
  - NewspaperTools    : News article extraction
  - Newspaper4kTools  : Enhanced article extraction
  - WebsiteTools      : General website scraping
  - TrafilaturaTools  : Text extraction from any URL
  - YouTubeTools      : YouTube video search and captions
  - YFinanceTools     : Stock/financial data (free)

Activate optional tools by setting env vars:
  TAVILY_API_KEY      → TavilyTools
  EXA_API_KEY         → ExaTools
  SERPER_API_KEY      → SerperApiTools
  JINA_API_KEY        → JinaReaderTools
  FIRECRAWL_API_KEY   → FirecrawlTools
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.arxiv import ArxivTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.pubmed import PubmedTools
from agno.tools.newspaper import NewspaperTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.tools.website import WebsiteTools
from agno.tools.trafilatura import TrafilaturaTools
from agno.tools.youtube import YouTubeTools
from agno.tools.yfinance import YFinanceTools

from db import get_postgres_db

_tools = [
    DuckDuckGoTools(),
    WikipediaTools(),
    ArxivTools(),
    HackerNewsTools(),
    PubmedTools(),
    NewspaperTools(),
    Newspaper4kTools(),
    WebsiteTools(),
    TrafilaturaTools(),
    YouTubeTools(),
    YFinanceTools(),
]

if os.getenv("TAVILY_API_KEY"):
    try:
        from agno.tools.tavily import TavilyTools
        _tools.append(TavilyTools())
    except ImportError:
        pass

if os.getenv("EXA_API_KEY"):
    try:
        from agno.tools.exa import ExaTools
        _tools.append(ExaTools())
    except ImportError:
        pass

if os.getenv("SERPER_API_KEY"):
    try:
        from agno.tools.serper import SerperApiTools
        _tools.append(SerperApiTools())
    except ImportError:
        pass

if os.getenv("JINA_API_KEY"):
    try:
        from agno.tools.jina import JinaReaderTools
        _tools.append(JinaReaderTools())
    except ImportError:
        pass

if os.getenv("FIRECRAWL_API_KEY"):
    try:
        from agno.tools.firecrawl import FirecrawlTools
        _tools.append(FirecrawlTools())
    except ImportError:
        pass

web_agent = Agent(
    id="web-agent",
    name="Web Agent",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A comprehensive web intelligence agent. Searches the web via DuckDuckGo, "
        "reads Wikipedia and arXiv papers, extracts news articles, scrapes websites, "
        "searches YouTube, and retrieves financial data — all without needing API keys."
    ),
    instructions="""\
You are a powerful web research agent. You have access to:

**Search:**
- DuckDuckGo for general web search
- Wikipedia for encyclopedic knowledge
- arXiv for academic papers and research
- HackerNews for tech news and discussions
- PubMed for medical and biomedical literature

**Content Extraction:**
- Website scraping for any URL
- Newspaper/Newspaper4k for news article extraction
- Trafilatura for clean text extraction from any page
- YouTube for video search and transcript retrieval

**Financial Data:**
- Yahoo Finance for stock prices, company info, and financial metrics

**Guidelines:**
- Always cite your sources with URLs
- For research questions, check multiple sources
- For news, use Newspaper tools to get full article text
- For academic topics, check arXiv and PubMed
- For financial data, use YFinance for real-time quotes
- Synthesize information from multiple sources into a clear answer
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
