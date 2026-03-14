"""
Analyst Agent
-------------
A data analysis and financial intelligence agent with SQL, pandas,
financial data, and visualization capabilities.

Tools (always active — no API key needed):
  - DuckDbTools       : In-memory SQL analytics
  - CsvTools          : CSV file reading and analysis
  - PandasTools       : DataFrame manipulation
  - YFinanceTools     : Real-time stock/financial data (free)
  - CalculatorTools   : Math and calculations
  - VisualizationTools: Chart and graph generation
  - PythonTools       : Python code execution for custom analysis

Activate optional tools by setting env vars:
  OPENBB_PAT          → OpenBBTools (enhanced financial data)
  FINANCIAL_DATASETS_API_KEY → FinancialDatasetsTools
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.duckdb import DuckDbTools
from agno.tools.csv_toolkit import CsvTools
from agno.tools.pandas import PandasTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.calculator import CalculatorTools
from agno.tools.visualization import VisualizationTools
from agno.tools.python import PythonTools

from db import get_postgres_db

_tools = [
    DuckDbTools(),
    CsvTools(),
    PandasTools(),
    YFinanceTools(),
    CalculatorTools(),
    VisualizationTools(),
    PythonTools(),
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

analyst = Agent(
    id="analyst",
    name="Analyst",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A data analysis and financial intelligence agent. Runs SQL with DuckDB, "
        "manipulates DataFrames with Pandas, retrieves real-time stock data from Yahoo Finance, "
        "performs calculations, and generates charts and visualizations."
    ),
    instructions="""\
You are a data analysis and financial intelligence agent. You can:

**Data Analysis:**
- Run SQL queries with DuckDB (in-memory, no setup needed)
- Load and analyze CSV files with Pandas
- Perform complex DataFrame operations
- Execute custom Python code for analysis

**Financial Data:**
- Get real-time stock prices, historical data, and company info via Yahoo Finance
- Retrieve earnings, dividends, options chains, and financial statements
- Compare multiple stocks and calculate returns

**Visualization:**
- Create charts, graphs, and plots
- Generate bar charts, line charts, scatter plots, histograms

**Math & Calculations:**
- Perform complex calculations
- Statistical analysis

**Guidelines:**
- Always show your work — display intermediate steps
- For financial analysis, always note the data date/time
- When creating visualizations, describe what the chart shows
- For SQL queries, show the query before the results
- Round financial figures to 2 decimal places
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
