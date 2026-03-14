"""
OS Control Agent
----------------
A dedicated agent for managing and controlling the AgentOS instance
through the Agno OS UI. Provides full access to all AgentOS API operations:
agents, teams, workflows, sessions, memory, knowledge, schedules, approvals,
components, metrics, and registry.

All tools are native Python functions — no extra services required.

Test:
    python -m agents.os_control
"""

import json as _json
import os as _os

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIResponses

from db import get_postgres_db

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

# Self-referential: this agent calls the same AgentOS instance it runs in.
# In Railway, the service talks to itself via localhost.
AGENTOS_BASE_URL = _os.getenv("AGENTOS_BASE_URL", "http://localhost:8000")


def _call(method: str, path: str, **kwargs) -> str:
    """Make an HTTP call to the AgentOS REST API."""
    url = f"{AGENTOS_BASE_URL}{path}"
    with httpx.Client(timeout=30) as client:
        resp = getattr(client, method)(url, **kwargs)
        resp.raise_for_status()
        try:
            return _json.dumps(resp.json(), indent=2)
        except Exception:
            return resp.text


# ---------------------------------------------------------------------------
# Agent Tools — Agents
# ---------------------------------------------------------------------------
def list_agents() -> str:
    """List all agents available in AgentOS with their IDs and descriptions."""
    return _call("get", "/agents")


def get_agent(agent_id: str) -> str:
    """Get full details of a specific agent.

    Args:
        agent_id: The agent ID (e.g. 'knowledge-agent', 'mcp-agent', 'dash', 'gcode', 'pal', 'scout', 'seek', 'os-control')
    """
    return _call("get", f"/agents/{agent_id}")


def run_agent(agent_id: str, message: str, session_id: str = "") -> str:
    """Run an agent with a message and return its response.

    Args:
        agent_id: The agent ID to run
        message: The message or task to send to the agent
        session_id: Optional session ID to continue an existing conversation
    """
    body: dict = {"message": message, "stream": False}
    if session_id:
        body["session_id"] = session_id
    return _call("post", f"/agents/{agent_id}/runs", json=body)


def list_agent_runs(agent_id: str) -> str:
    """List all runs for a specific agent.

    Args:
        agent_id: The agent ID
    """
    return _call("get", f"/agents/{agent_id}/runs")


# ---------------------------------------------------------------------------
# Agent Tools — Teams
# ---------------------------------------------------------------------------
def list_teams() -> str:
    """List all teams available in AgentOS."""
    return _call("get", "/teams")


def run_team(team_id: str, message: str, session_id: str = "") -> str:
    """Run a team with a message.

    Args:
        team_id: The team ID (e.g. 'research-team')
        message: The research question or task
        session_id: Optional session ID to continue a conversation
    """
    body: dict = {"message": message, "stream": False}
    if session_id:
        body["session_id"] = session_id
    return _call("post", f"/teams/{team_id}/runs", json=body)


# ---------------------------------------------------------------------------
# Agent Tools — Workflows
# ---------------------------------------------------------------------------
def list_workflows() -> str:
    """List all workflows available in AgentOS."""
    return _call("get", "/workflows")


def run_workflow(workflow_id: str) -> str:
    """Trigger a workflow to run.

    Args:
        workflow_id: The workflow ID (e.g. 'daily-brief')
    """
    return _call("post", f"/workflows/{workflow_id}/runs", json={})


# ---------------------------------------------------------------------------
# Agent Tools — Sessions
# ---------------------------------------------------------------------------
def list_sessions(limit: int = 20) -> str:
    """List recent sessions across all agents and teams.

    Args:
        limit: Maximum number of sessions to return (default 20)
    """
    return _call("get", f"/sessions?limit={limit}")


def get_session(session_id: str) -> str:
    """Get details of a specific session including all runs.

    Args:
        session_id: The session ID
    """
    return _call("get", f"/sessions/{session_id}")


def delete_session(session_id: str) -> str:
    """Delete a session and all its runs.

    Args:
        session_id: The session ID to delete
    """
    return _call("delete", f"/sessions/{session_id}")


def rename_session(session_id: str, new_name: str) -> str:
    """Rename a session.

    Args:
        session_id: The session ID to rename
        new_name: The new name for the session
    """
    return _call("post", f"/sessions/{session_id}/rename", json={"name": new_name})


def delete_all_sessions() -> str:
    """Delete all sessions across all agents. Use with caution."""
    return _call("delete", "/sessions")


# ---------------------------------------------------------------------------
# Agent Tools — Memory
# ---------------------------------------------------------------------------
def list_memories(user_id: str = "") -> str:
    """List all memories stored in AgentOS.

    Args:
        user_id: Optional user ID to filter memories
    """
    path = "/memories"
    if user_id:
        path += f"?user_id={user_id}"
    return _call("get", path)


def create_memory(memory: str, user_id: str = "", topics: str = "") -> str:
    """Create a new memory in AgentOS.

    Args:
        memory: The memory content to store
        user_id: Optional user ID to associate the memory with
        topics: Optional comma-separated list of topics
    """
    body: dict = {"memory": memory}
    if user_id:
        body["user_id"] = user_id
    if topics:
        body["topics"] = [t.strip() for t in topics.split(",")]
    return _call("post", "/memories", json=body)


def delete_memory(memory_id: str) -> str:
    """Delete a specific memory by ID.

    Args:
        memory_id: The memory ID to delete
    """
    return _call("delete", f"/memories/{memory_id}")


def delete_all_memories(user_id: str = "") -> str:
    """Delete all memories, optionally for a specific user.

    Args:
        user_id: Optional user ID — if provided, only that user's memories are deleted
    """
    body = {}
    if user_id:
        body["user_id"] = user_id
    return _call("delete", "/memories", json=body)


def optimize_memories() -> str:
    """Optimize and consolidate stored memories to remove duplicates and improve quality."""
    return _call("post", "/optimize-memories")


def get_memory_topics() -> str:
    """Get all memory topics currently stored in AgentOS."""
    return _call("get", "/memory_topics")


# ---------------------------------------------------------------------------
# Agent Tools — Knowledge
# ---------------------------------------------------------------------------
def list_knowledge(limit: int = 20) -> str:
    """List all documents in the AgentOS knowledge base.

    Args:
        limit: Maximum number of documents to return
    """
    return _call("get", f"/knowledge/content?limit={limit}")


def add_knowledge(content: str, title: str = "") -> str:
    """Add a document to the AgentOS knowledge base.

    Args:
        content: The text content to add
        title: Optional title for the document
    """
    body: dict = {"content": content}
    if title:
        body["title"] = title
    return _call("post", "/knowledge/content", json=body)


def search_knowledge(query: str, limit: int = 5) -> str:
    """Search the AgentOS knowledge base for relevant documents.

    Args:
        query: The search query
        limit: Maximum number of results to return
    """
    return _call("post", "/knowledge/search", json={"query": query, "limit": limit})


def delete_knowledge(content_id: str) -> str:
    """Delete a document from the knowledge base.

    Args:
        content_id: The content ID to delete
    """
    return _call("delete", f"/knowledge/content/{content_id}")


def delete_all_knowledge() -> str:
    """Delete all documents from the knowledge base. Use with caution."""
    return _call("delete", "/knowledge/content")


# ---------------------------------------------------------------------------
# Agent Tools — Components (Studio)
# ---------------------------------------------------------------------------
def list_components(component_type: str = "") -> str:
    """List all components registered in the AgentOS Studio.

    Args:
        component_type: Optional filter - 'agent', 'team', or 'workflow'
    """
    path = "/components"
    if component_type:
        path += f"?component_type={component_type}"
    return _call("get", path)


def get_component(component_id: str) -> str:
    """Get details of a specific component.

    Args:
        component_id: The component ID
    """
    return _call("get", f"/components/{component_id}")


def delete_component(component_id: str) -> str:
    """Delete a component from the Studio registry.

    Args:
        component_id: The component ID to delete
    """
    return _call("delete", f"/components/{component_id}")


# ---------------------------------------------------------------------------
# Agent Tools — Schedules
# ---------------------------------------------------------------------------
def list_schedules() -> str:
    """List all scheduled tasks in AgentOS."""
    return _call("get", "/schedules")


def get_schedule(schedule_id: str) -> str:
    """Get details of a specific schedule.

    Args:
        schedule_id: The schedule ID
    """
    return _call("get", f"/schedules/{schedule_id}")


def trigger_schedule(schedule_id: str) -> str:
    """Manually trigger a schedule to run immediately.

    Args:
        schedule_id: The schedule ID to trigger
    """
    return _call("post", f"/schedules/{schedule_id}/trigger")


def enable_schedule(schedule_id: str) -> str:
    """Enable a disabled schedule.

    Args:
        schedule_id: The schedule ID to enable
    """
    return _call("post", f"/schedules/{schedule_id}/enable")


def disable_schedule(schedule_id: str) -> str:
    """Disable an active schedule.

    Args:
        schedule_id: The schedule ID to disable
    """
    return _call("post", f"/schedules/{schedule_id}/disable")


def delete_schedule(schedule_id: str) -> str:
    """Delete a schedule.

    Args:
        schedule_id: The schedule ID to delete
    """
    return _call("delete", f"/schedules/{schedule_id}")


# ---------------------------------------------------------------------------
# Agent Tools — Approvals
# ---------------------------------------------------------------------------
def list_approvals() -> str:
    """List all pending approval requests in AgentOS."""
    return _call("get", "/approvals")


def get_approvals_count() -> str:
    """Get the count of pending approvals."""
    return _call("get", "/approvals/count")


def resolve_approval(approval_id: str, approved: bool, reason: str = "") -> str:
    """Approve or deny a pending approval request.

    Args:
        approval_id: The approval ID to resolve
        approved: True to approve, False to deny
        reason: Optional reason for the decision
    """
    body: dict = {"approved": approved}
    if reason:
        body["reason"] = reason
    return _call("post", f"/approvals/{approval_id}/resolve", json=body)


def delete_approval(approval_id: str) -> str:
    """Delete an approval request.

    Args:
        approval_id: The approval ID to delete
    """
    return _call("delete", f"/approvals/{approval_id}")


# ---------------------------------------------------------------------------
# Agent Tools — Metrics, Health, Registry
# ---------------------------------------------------------------------------
def get_metrics() -> str:
    """Get usage metrics for all agents, teams, and workflows in AgentOS."""
    return _call("get", "/metrics")


def refresh_metrics() -> str:
    """Force a refresh of the AgentOS metrics."""
    return _call("post", "/metrics/refresh")


def get_health() -> str:
    """Check the health and status of the AgentOS instance."""
    return _call("get", "/health")


def get_registry() -> str:
    """Get the registry of available models, tools, and databases."""
    return _call("get", "/registry")


def get_config() -> str:
    """Get the current AgentOS configuration."""
    return _call("get", "/config")


# ---------------------------------------------------------------------------
# Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are the OS Control agent — the system administrator for this AgentOS instance.
You have full access to every API endpoint and can manage all aspects of the system
through natural language commands.

## What You Can Do

**Run agents and teams:**
- "Run the research team on [topic]" → `run_team('research-team', ...)`
- "Ask Seek to research [topic]" → `run_agent('seek', ...)`
- "Ask Gcode to write [code]" → `run_agent('gcode', ...)`
- "Trigger the daily brief" → `run_workflow('daily-brief')`

**Manage sessions:**
- "List my recent sessions" → `list_sessions()`
- "Delete session X" → `delete_session(X)`
- "Clear all sessions" → `delete_all_sessions()`

**Manage memory:**
- "What memories do I have?" → `list_memories()`
- "Remember that [fact]" → `create_memory(...)`
- "Delete all memories" → `delete_all_memories()`
- "Optimize my memories" → `optimize_memories()`

**Manage knowledge:**
- "What's in the knowledge base?" → `list_knowledge()`
- "Add this to the knowledge base: [content]" → `add_knowledge(...)`
- "Search knowledge for [query]" → `search_knowledge(...)`
- "Clear the knowledge base" → `delete_all_knowledge()`

**Manage schedules:**
- "What schedules are running?" → `list_schedules()`
- "Trigger schedule X" → `trigger_schedule(X)`
- "Disable schedule X" → `disable_schedule(X)`

**Manage approvals:**
- "Any pending approvals?" → `list_approvals()`
- "Approve request X" → `resolve_approval(X, approved=True)`
- "Deny request X" → `resolve_approval(X, approved=False)`

**System info:**
- "System health?" → `get_health()`
- "Show metrics" → `get_metrics()`
- "What agents are available?" → `list_agents()`
- "What's in the registry?" → `get_registry()`

## Guidelines

- Always confirm before destructive operations (delete all, clear all)
- Show results in a clean, readable format
- If an operation fails, explain why and suggest alternatives
- Be concise — the user is an operator, not a beginner
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
os_control = Agent(
    id="os-control",
    name="OS Control",
    model=OpenAIResponses(id="gpt-4o"),
    db=agent_db,
    description="System administrator agent with full control over the AgentOS instance — manage agents, sessions, memory, knowledge, schedules, and approvals through natural language.",
    instructions=instructions,
    tools=[
        # Agents
        list_agents,
        get_agent,
        run_agent,
        list_agent_runs,
        # Teams
        list_teams,
        run_team,
        # Workflows
        list_workflows,
        run_workflow,
        # Sessions
        list_sessions,
        get_session,
        delete_session,
        rename_session,
        delete_all_sessions,
        # Memory
        list_memories,
        create_memory,
        delete_memory,
        delete_all_memories,
        optimize_memories,
        get_memory_topics,
        # Knowledge
        list_knowledge,
        add_knowledge,
        search_knowledge,
        delete_knowledge,
        delete_all_knowledge,
        # Components
        list_components,
        get_component,
        delete_component,
        # Schedules
        list_schedules,
        get_schedule,
        trigger_schedule,
        enable_schedule,
        disable_schedule,
        delete_schedule,
        # Approvals
        list_approvals,
        get_approvals_count,
        resolve_approval,
        delete_approval,
        # System
        get_metrics,
        refresh_metrics,
        get_health,
        get_registry,
        get_config,
    ],
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=10,
    markdown=True,
)

if __name__ == "__main__":
    os_control.print_response("List all agents in AgentOS", stream=True)
