"""
Productivity Agent
------------------
A business productivity agent that integrates with GitHub, Notion, Todoist,
Google Calendar, Google Sheets, Linear, Jira, and more.

All tools are activated by setting the corresponding env vars.
Without any env vars, the agent uses DuckDuckGo + Calculator as a baseline.

Env vars:
  GITHUB_TOKEN              → GithubTools
  NOTION_API_KEY            → NotionTools
  TODOIST_API_KEY           → TodoistTools
  LINEAR_API_KEY            → LinearTools
  JIRA_SERVER_URL + JIRA_USERNAME + JIRA_PASSWORD → JiraTools
  CLICKUP_API_KEY           → ClickUpTools
  GOOGLE_APPLICATION_CREDENTIALS → GoogleCalendarTools, GoogleSheetsTools
  CONFLUENCE_URL + CONFLUENCE_USERNAME + CONFLUENCE_PASSWORD → ConfluenceTools
  CALCOM_API_KEY            → CalComTools
  RESEND_API_KEY            → ResendTools (email sending)
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.calculator import CalculatorTools
from agno.tools.file import FileTools

from db import get_postgres_db

_tools = [
    DuckDuckGoTools(),
    CalculatorTools(),
    FileTools(),
]

if os.getenv("GITHUB_TOKEN"):
    try:
        from agno.tools.github import GithubTools
        _tools.append(GithubTools())
    except ImportError:
        pass

if os.getenv("NOTION_API_KEY"):
    try:
        from agno.tools.notion import NotionTools
        _tools.append(NotionTools())
    except ImportError:
        pass

if os.getenv("TODOIST_API_KEY"):
    try:
        from agno.tools.todoist import TodoistTools
        _tools.append(TodoistTools())
    except ImportError:
        pass

if os.getenv("LINEAR_API_KEY"):
    try:
        from agno.tools.linear import LinearTools
        _tools.append(LinearTools())
    except ImportError:
        pass

if os.getenv("JIRA_SERVER_URL"):
    try:
        from agno.tools.jira import JiraTools
        _tools.append(JiraTools())
    except ImportError:
        pass

if os.getenv("CLICKUP_API_KEY"):
    try:
        from agno.tools.clickup import ClickUpTools
        _tools.append(ClickUpTools())
    except ImportError:
        pass

if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CALENDAR_CREDENTIALS"):
    try:
        from agno.tools.googlecalendar import GoogleCalendarTools
        _tools.append(GoogleCalendarTools())
    except ImportError:
        pass

if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_SHEETS_CREDENTIALS"):
    try:
        from agno.tools.googlesheets import GoogleSheetsTools
        _tools.append(GoogleSheetsTools())
    except ImportError:
        pass

if os.getenv("CONFLUENCE_URL"):
    try:
        from agno.tools.confluence import ConfluenceTools
        _tools.append(ConfluenceTools())
    except ImportError:
        pass

if os.getenv("CALCOM_API_KEY"):
    try:
        from agno.tools.calcom import CalComTools
        _tools.append(CalComTools())
    except ImportError:
        pass

if os.getenv("RESEND_API_KEY"):
    try:
        from agno.tools.resend import ResendTools
        _tools.append(ResendTools())
    except ImportError:
        pass

if os.getenv("ZENDESK_SUBDOMAIN"):
    try:
        from agno.tools.zendesk import ZendeskTools
        _tools.append(ZendeskTools())
    except ImportError:
        pass

productivity = Agent(
    id="productivity",
    name="Productivity",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A business productivity agent that integrates with GitHub, Notion, Todoist, "
        "Google Calendar, Google Sheets, Linear, Jira, ClickUp, Confluence, and more. "
        "Manages tasks, projects, code, documentation, and schedules."
    ),
    instructions="""\
You are a productivity powerhouse. You help manage projects, tasks, code, and documentation
across all major productivity platforms.

**Project Management:**
- Create and manage GitHub issues, PRs, and repositories
- Manage Jira tickets and sprints
- Handle Linear issues and projects
- Manage ClickUp tasks and spaces

**Task Management:**
- Create, update, and complete Todoist tasks
- Manage projects and priorities

**Documentation:**
- Create and update Notion pages and databases
- Manage Confluence spaces and pages

**Scheduling:**
- Create and manage Google Calendar events
- Schedule meetings via Cal.com

**Data:**
- Read and write Google Sheets
- Analyze spreadsheet data

**Communication:**
- Send emails via Resend
- Search Zendesk for support tickets

**Guidelines:**
- Always confirm before creating or deleting items
- Show what you're about to do before doing it
- Provide links to created/updated items
- Use clear, professional language for all created content
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=10,
    markdown=True,
)

if __name__ == "__main__":
    productivity.print_response(
        "What GitHub repositories do I have access to?",
        stream=True,
    )
