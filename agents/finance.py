"""
Finance Agent
-------------
A financial intelligence agent with real-time market data, portfolio analysis,
and economic research capabilities.

Tools (always active — no API key needed):
  - YFinanceTools     : Real-time stock prices, financials, options
  - DuckDuckGoTools   : Financial news search
  - CalculatorTools   : Financial calculations
  - WikipediaTools    : Company and economic background

Activate optional tools by setting env vars:
  OPENBB_PAT                    → OpenBBTools (enhanced market data)
  FINANCIAL_DATASETS_API_KEY    → FinancialDatasetsTools
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.calculator import CalculatorTools
from agno.tools.wikipedia import WikipediaTools

from db import get_postgres_db

_tools = [
    YFinanceTools(
        enable_stock_price=True,
        enable_analyst_recommendations=True,
        enable_stock_fundamentals=True,
        enable_income_statements=True,
        enable_key_financial_ratios=True,
        enable_company_news=True,
        enable_technical_indicators=True,
        enable_historical_prices=True,
        enable_company_info=True,
    ),
    DuckDuckGoTools(),
    CalculatorTools(),
    WikipediaTools(),
]

if os.getenv("OPENBB_PAT"):
    try:
        from agno.tools.openbb import OpenBBTools
        _tools.append(OpenBBTools())
    except ImportError:
        pass

if os.getenv("FINANCIAL_DATASETS_API_KEY"):
    try:
        from agno.tools.financial_datasets import FinancialDatasetsTools
        _tools.append(FinancialDatasetsTools())
    except ImportError:
        pass

finance = Agent(
    id="finance",
    name="Finance",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A financial intelligence agent with real-time market data, portfolio analysis, "
        "and economic research. Retrieves stock prices, financial statements, analyst recommendations, "
        "technical indicators, and company news from Yahoo Finance."
    ),
    instructions="""\
You are a financial intelligence agent. You provide data-driven financial analysis and market insights.

**Market Data (Yahoo Finance):**
- Real-time stock prices and historical data
- Financial statements (income, balance sheet, cash flow)
- Key financial ratios (P/E, P/B, EV/EBITDA, etc.)
- Analyst recommendations and price targets
- Technical indicators (RSI, MACD, moving averages)
- Options chains and derivatives data
- Company news and press releases

**Analysis Capabilities:**
- Compare multiple stocks side-by-side
- Calculate portfolio returns and risk metrics
- Identify trends from historical data
- Perform DCF and valuation analysis
- Screen stocks by financial criteria

**Research:**
- Search for financial news and market commentary
- Look up company backgrounds and business models
- Find economic data and macro trends

**Guidelines:**
- Always note the data timestamp (markets change rapidly)
- Clearly distinguish between data and analysis/opinion
- Include relevant risk factors in recommendations
- Use standard financial notation (e.g., $1.2B, 15.3x P/E)
- For calculations, show the formula and inputs
- Never provide personalized investment advice — present data and analysis only
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    finance.print_response(
        "Give me a comprehensive analysis of NVDA including current price, P/E ratio, and analyst recommendations",
        stream=True,
    )
