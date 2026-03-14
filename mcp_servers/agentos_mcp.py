"""
AgentOS MCP Server
------------------
Exposes the AgentOS REST API as MCP tools so agents can control
agents, sessions, memory, knowledge, components, schedules, and approvals.

Runs as a streamable HTTP MCP server on port 8001.
Start: python -m mcp_servers.agentos_mcp
"""
import os
import json
import httpx
from typing import Optional, Any
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
AGENTOS_BASE_URL = os.getenv("AGENTOS_BASE_URL", "http://localhost:8000")

mcp = FastMCP(
    name="agentos",
    instructions=(
        "Tools to control and manage the AgentOS instance. "
        "Use these to list/run agents, manage sessions, memory, knowledge, "
        "components, schedules, and approvals."
    ),
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _req(method: str, path: str, **kwargs) -> Any:
    url = f"{AGENTOS_BASE_URL}{path}"
    with httpx.Client(timeout=30) as client:
        resp = getattr(client, method)(url, **kwargs)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return resp.text


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------
@mcp.tool()
def list_agents() -> str:
    """List all available agents in AgentOS."""
    return json.dumps(_req("get", "/agents"), indent=2)


@mcp.tool()
def get_agent(agent_id: str) -> str:
    """Get details of a specific agent by ID."""
    return json.dumps(_req("get", f"/agents/{agent_id}"), indent=2)


@mcp.tool()
def run_agent(agent_id: str, message: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
    """Run an agent with a message. Returns the agent's response.
    
    Args:
        agent_id: The agent ID (e.g. 'knowledge-agent', 'mcp-agent', 'dash', 'gcode', 'pal', 'scout', 'seek')
        message: The message/prompt to send to the agent
        session_id: Optional session ID to continue a conversation
        user_id: Optional user ID for memory/personalization
    """
    body: dict = {"message": message, "stream": False}
    if session_id:
        body["session_id"] = session_id
    if user_id:
        body["user_id"] = user_id
    return json.dumps(_req("post", f"/agents/{agent_id}/runs", json=body), indent=2)


@mcp.tool()
def list_agent_runs(agent_id: str) -> str:
    """List all runs for a specific agent."""
    return json.dumps(_req("get", f"/agents/{agent_id}/runs"), indent=2)


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------
@mcp.tool()
def list_teams() -> str:
    """List all available teams in AgentOS."""
    return json.dumps(_req("get", "/teams"), indent=2)


@mcp.tool()
def run_team(team_id: str, message: str, session_id: Optional[str] = None) -> str:
    """Run a team with a message.
    
    Args:
        team_id: The team ID (e.g. 'research-team')
        message: The message/task to send to the team
        session_id: Optional session ID to continue a conversation
    """
    body: dict = {"message": message, "stream": False}
    if session_id:
        body["session_id"] = session_id
    return json.dumps(_req("post", f"/teams/{team_id}/runs", json=body), indent=2)


# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------
@mcp.tool()
def list_workflows() -> str:
    """List all available workflows in AgentOS."""
    return json.dumps(_req("get", "/workflows"), indent=2)


@mcp.tool()
def run_workflow(workflow_id: str, input_data: Optional[str] = None) -> str:
    """Run a workflow.
    
    Args:
        workflow_id: The workflow ID (e.g. 'daily-brief')
        input_data: Optional JSON string of input data for the workflow
    """
    body = json.loads(input_data) if input_data else {}
    return json.dumps(_req("post", f"/workflows/{workflow_id}/runs", json=body), indent=2)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
@mcp.tool()
def list_sessions(limit: int = 20) -> str:
    """List recent sessions."""
    return json.dumps(_req("get", f"/sessions?limit={limit}"), indent=2)


@mcp.tool()
def get_session(session_id: str) -> str:
    """Get details of a specific session including all runs."""
    return json.dumps(_req("get", f"/sessions/{session_id}"), indent=2)


@mcp.tool()
def delete_session(session_id: str) -> str:
    """Delete a session and all its runs."""
    return json.dumps(_req("delete", f"/sessions/{session_id}"), indent=2)


@mcp.tool()
def rename_session(session_id: str, new_name: str) -> str:
    """Rename a session.
    
    Args:
        session_id: The session ID to rename
        new_name: The new name for the session
    """
    return json.dumps(_req("post", f"/sessions/{session_id}/rename", json={"name": new_name}), indent=2)


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------
@mcp.tool()
def list_memories(user_id: Optional[str] = None) -> str:
    """List all stored memories, optionally filtered by user."""
    path = "/memories"
    if user_id:
        path += f"?user_id={user_id}"
    return json.dumps(_req("get", path), indent=2)


@mcp.tool()
def create_memory(memory: str, user_id: Optional[str] = None, topics: Optional[str] = None) -> str:
    """Create a new memory.
    
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
    return json.dumps(_req("post", "/memories", json=body), indent=2)


@mcp.tool()
def delete_all_memories(user_id: Optional[str] = None) -> str:
    """Delete all memories, optionally for a specific user."""
    body = {}
    if user_id:
        body["user_id"] = user_id
    return json.dumps(_req("delete", "/memories", json=body), indent=2)


@mcp.tool()
def optimize_memories() -> str:
    """Optimize and consolidate stored memories."""
    return json.dumps(_req("post", "/optimize-memories"), indent=2)


# ---------------------------------------------------------------------------
# Knowledge
# ---------------------------------------------------------------------------
@mcp.tool()
def list_knowledge(limit: int = 20) -> str:
    """List all documents in the knowledge base."""
    return json.dumps(_req("get", f"/knowledge/content?limit={limit}"), indent=2)


@mcp.tool()
def add_knowledge(content: str, title: Optional[str] = None, knowledge_id: Optional[str] = None) -> str:
    """Add a document to the knowledge base.
    
    Args:
        content: The text content to add
        title: Optional title for the document
        knowledge_id: Optional knowledge base ID to add to
    """
    body: dict = {"content": content}
    if title:
        body["title"] = title
    if knowledge_id:
        body["knowledge_id"] = knowledge_id
    return json.dumps(_req("post", "/knowledge/content", json=body), indent=2)


@mcp.tool()
def search_knowledge(query: str, limit: int = 5) -> str:
    """Search the knowledge base for relevant documents.
    
    Args:
        query: The search query
        limit: Maximum number of results to return
    """
    return json.dumps(_req("post", "/knowledge/search", json={"query": query, "limit": limit}), indent=2)


@mcp.tool()
def delete_knowledge(content_id: str) -> str:
    """Delete a document from the knowledge base by ID."""
    return json.dumps(_req("delete", f"/knowledge/content/{content_id}"), indent=2)


# ---------------------------------------------------------------------------
# Components (Studio)
# ---------------------------------------------------------------------------
@mcp.tool()
def list_components(component_type: Optional[str] = None) -> str:
    """List all components (agents, teams, workflows) in the Studio registry.
    
    Args:
        component_type: Optional filter - 'agent', 'team', or 'workflow'
    """
    path = "/components"
    if component_type:
        path += f"?component_type={component_type}"
    return json.dumps(_req("get", path), indent=2)


@mcp.tool()
def create_component(name: str, component_type: str, description: Optional[str] = None, config: Optional[str] = None) -> str:
    """Create a new component in the Studio registry.
    
    Args:
        name: The component name
        component_type: 'agent', 'team', or 'workflow'
        description: Optional description
        config: Optional JSON string of component configuration
    """
    body: dict = {
        "name": name,
        "component_type": component_type,
        "stage": "published",
    }
    if description:
        body["description"] = description
    if config:
        body["config"] = json.loads(config)
    return json.dumps(_req("post", "/components", json=body), indent=2)


@mcp.tool()
def delete_component(component_id: str) -> str:
    """Delete a component from the Studio registry."""
    return json.dumps(_req("delete", f"/components/{component_id}"), indent=2)


# ---------------------------------------------------------------------------
# Schedules
# ---------------------------------------------------------------------------
@mcp.tool()
def list_schedules() -> str:
    """List all scheduled tasks."""
    return json.dumps(_req("get", "/schedules"), indent=2)


@mcp.tool()
def trigger_schedule(schedule_id: str) -> str:
    """Manually trigger a schedule to run immediately.
    
    Args:
        schedule_id: The schedule ID to trigger
    """
    return json.dumps(_req("post", f"/schedules/{schedule_id}/trigger"), indent=2)


@mcp.tool()
def enable_schedule(schedule_id: str) -> str:
    """Enable a disabled schedule."""
    return json.dumps(_req("post", f"/schedules/{schedule_id}/enable"), indent=2)


@mcp.tool()
def disable_schedule(schedule_id: str) -> str:
    """Disable an active schedule."""
    return json.dumps(_req("post", f"/schedules/{schedule_id}/disable"), indent=2)


# ---------------------------------------------------------------------------
# Approvals
# ---------------------------------------------------------------------------
@mcp.tool()
def list_approvals() -> str:
    """List all pending approvals."""
    return json.dumps(_req("get", "/approvals"), indent=2)


@mcp.tool()
def resolve_approval(approval_id: str, approved: bool, reason: Optional[str] = None) -> str:
    """Approve or deny a pending approval request.
    
    Args:
        approval_id: The approval ID to resolve
        approved: True to approve, False to deny
        reason: Optional reason for the decision
    """
    body: dict = {"approved": approved}
    if reason:
        body["reason"] = reason
    return json.dumps(_req("post", f"/approvals/{approval_id}/resolve", json=body), indent=2)


# ---------------------------------------------------------------------------
# Metrics & Health
# ---------------------------------------------------------------------------
@mcp.tool()
def get_metrics() -> str:
    """Get usage metrics for all agents, teams, and workflows."""
    return json.dumps(_req("get", "/metrics"), indent=2)


@mcp.tool()
def get_health() -> str:
    """Check the health status of the AgentOS instance."""
    return json.dumps(_req("get", "/health"), indent=2)


@mcp.tool()
def get_registry() -> str:
    """Get the registry of available models, tools, and databases."""
    return json.dumps(_req("get", "/registry"), indent=2)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001, path="/mcp")
