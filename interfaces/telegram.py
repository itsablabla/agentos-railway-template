"""
Multi-Bot Telegram Interface for AgentOS
-----------------------------------------
Allows any number of Telegram bots to be wired to any agent, team, or workflow.

Configuration via environment variables:
  TELEGRAM_BOTS=bot1_token:agent-id,bot2_token:team:research-team,bot3_token:workflow:daily-brief

Or via the /telegram/bots management API.

Each bot gets its own webhook at:
  POST /telegram/webhook/{bot_token}

Setup:
1. Create a bot via @BotFather → get token
2. Set webhook: POST /telegram/bots  {"token": "...", "target_type": "agent", "target_id": "pal"}
3. The system auto-registers the webhook with Telegram

Supported target_type values: agent, team, workflow
"""
import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory bot registry (persisted to DB via /config endpoint if available)
# ---------------------------------------------------------------------------
_bot_registry: Dict[str, Dict[str, Any]] = {}
# Format: { token: { "target_type": "agent"|"team"|"workflow", "target_id": str, "bot_info": {...} } }

_agentOS_base_url: str = ""  # Set at startup


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class BotRegistration(BaseModel):
    token: str
    target_type: str  # "agent", "team", "workflow"
    target_id: str
    name: Optional[str] = None  # friendly name, auto-fetched if not set


class BotInfo(BaseModel):
    token_preview: str  # first 10 chars only for safety
    target_type: str
    target_id: str
    name: Optional[str]
    webhook_url: Optional[str]
    bot_username: Optional[str]


# ---------------------------------------------------------------------------
# Telegram Bot API helpers
# ---------------------------------------------------------------------------
async def _tg_get(token: str, method: str, **params) -> Dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


async def _tg_post(token: str, method: str, data: Dict) -> Dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(url, json=data)
        r.raise_for_status()
        return r.json()


async def _set_webhook(token: str, webhook_url: str) -> bool:
    try:
        result = await _tg_post(token, "setWebhook", {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True,
        })
        return result.get("ok", False)
    except Exception as e:
        logger.error(f"Failed to set webhook for bot: {e}")
        return False


async def _get_bot_info(token: str) -> Optional[Dict]:
    try:
        result = await _tg_get(token, "getMe")
        if result.get("ok"):
            return result["result"]
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
    return None


async def _send_message(token: str, chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
    try:
        # Telegram has a 4096 char limit — split if needed
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await _tg_post(token, "sendMessage", {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": parse_mode,
            })
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        # Try without markdown if parse fails
        try:
            await _tg_post(token, "sendMessage", {"chat_id": chat_id, "text": text})
            return True
        except Exception:
            return False


async def _send_typing(token: str, chat_id: int):
    try:
        await _tg_post(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"})
    except Exception:
        pass


# ---------------------------------------------------------------------------
# AgentOS API helpers — call the local AgentOS REST API
# ---------------------------------------------------------------------------
async def _run_agent(base_url: str, agent_id: str, message: str, session_id: Optional[str] = None) -> str:
    """Run an agent and return the response text."""
    payload: Dict[str, Any] = {"message": message, "stream": False}
    if session_id:
        payload["session_id"] = session_id

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{base_url}/agents/{agent_id}/runs", json=payload)
        r.raise_for_status()
        data = r.json()

    # Extract text from the run response
    return _extract_text(data)


async def _run_team(base_url: str, team_id: str, message: str, session_id: Optional[str] = None) -> str:
    payload: Dict[str, Any] = {"message": message, "stream": False}
    if session_id:
        payload["session_id"] = session_id

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{base_url}/teams/{team_id}/runs", json=payload)
        r.raise_for_status()
        data = r.json()

    return _extract_text(data)


async def _run_workflow(base_url: str, workflow_id: str, message: str) -> str:
    payload: Dict[str, Any] = {"message": message, "stream": False}

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{base_url}/workflows/{workflow_id}/runs", json=payload)
        r.raise_for_status()
        data = r.json()

    return _extract_text(data)


def _extract_text(data: Any) -> str:
    """Extract the assistant text from an AgentOS run response."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        # Try common response shapes
        for key in ("content", "message", "text", "response", "output"):
            if key in data and isinstance(data[key], str):
                return data[key]
        # Try messages array
        messages = data.get("messages", [])
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, str) and content:
                    return content
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            return block.get("text", "")
        # Fallback: return JSON
        return json.dumps(data, indent=2)[:2000]
    return str(data)[:2000]


# ---------------------------------------------------------------------------
# Load bots from environment variable at startup
# ---------------------------------------------------------------------------
def _load_bots_from_env():
    """
    Parse TELEGRAM_BOTS env var:
    Format: token1:agent:agent-id,token2:team:team-id,token3:workflow:workflow-id
    Simple format (defaults to agent): token1:agent-id,token2:agent-id2
    """
    raw = os.getenv("TELEGRAM_BOTS", "")
    if not raw:
        return

    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) == 2:
            # Simple: token:agent-id
            token, target_id = parts
            _bot_registry[token] = {
                "target_type": "agent",
                "target_id": target_id,
                "name": f"Bot→{target_id}",
                "bot_username": None,
            }
        elif len(parts) == 3:
            # Full: token:type:id
            token, target_type, target_id = parts
            _bot_registry[token] = {
                "target_type": target_type,
                "target_id": target_id,
                "name": f"Bot→{target_type}:{target_id}",
                "bot_username": None,
            }

    logger.info(f"Loaded {len(_bot_registry)} Telegram bots from TELEGRAM_BOTS env var")


# ---------------------------------------------------------------------------
# FastAPI Router
# ---------------------------------------------------------------------------
def create_telegram_router(base_url: str) -> APIRouter:
    """
    Create the Telegram router. Call this after AgentOS is initialized.
    base_url: the public URL of this AgentOS instance (e.g. https://agentos-xxx.up.railway.app)
    """
    global _agentOS_base_url
    _agentOS_base_url = base_url.rstrip("/")

    # Load bots from env
    _load_bots_from_env()

    router = APIRouter(prefix="/telegram", tags=["Telegram"])

    # ------------------------------------------------------------------
    # Management endpoints
    # ------------------------------------------------------------------

    @router.get("/bots", summary="List all registered Telegram bots")
    async def list_bots() -> List[BotInfo]:
        result = []
        for token, info in _bot_registry.items():
            result.append(BotInfo(
                token_preview=token[:10] + "...",
                target_type=info["target_type"],
                target_id=info["target_id"],
                name=info.get("name"),
                webhook_url=f"{_agentOS_base_url}/telegram/webhook/{token}",
                bot_username=info.get("bot_username"),
            ))
        return result

    @router.post("/bots", summary="Register a new Telegram bot and set its webhook")
    async def register_bot(reg: BotRegistration) -> Dict:
        token = reg.token.strip()

        # Validate target_type
        if reg.target_type not in ("agent", "team", "workflow"):
            raise HTTPException(400, "target_type must be 'agent', 'team', or 'workflow'")

        # Fetch bot info from Telegram
        bot_info = await _get_bot_info(token)
        if not bot_info:
            raise HTTPException(400, "Invalid Telegram bot token — could not reach Telegram API")

        # Set webhook
        webhook_url = f"{_agentOS_base_url}/telegram/webhook/{token}"
        ok = await _set_webhook(token, webhook_url)
        if not ok:
            raise HTTPException(500, "Failed to set webhook with Telegram")

        # Register in memory
        _bot_registry[token] = {
            "target_type": reg.target_type,
            "target_id": reg.target_id,
            "name": reg.name or bot_info.get("first_name", f"Bot→{reg.target_id}"),
            "bot_username": bot_info.get("username"),
        }

        return {
            "status": "registered",
            "bot_username": bot_info.get("username"),
            "webhook_url": webhook_url,
            "target_type": reg.target_type,
            "target_id": reg.target_id,
        }

    @router.delete("/bots/{token_preview}", summary="Remove a Telegram bot registration")
    async def remove_bot(token_preview: str) -> Dict:
        # Find by token prefix
        found_token = None
        for token in list(_bot_registry.keys()):
            if token.startswith(token_preview.replace("...", "")):
                found_token = token
                break
        if not found_token:
            raise HTTPException(404, "Bot not found")

        # Delete webhook
        try:
            await _tg_post(found_token, "deleteWebhook", {})
        except Exception:
            pass

        del _bot_registry[found_token]
        return {"status": "removed"}

    @router.post("/bots/refresh-webhooks", summary="Re-register all webhooks (use after URL change)")
    async def refresh_webhooks() -> Dict:
        results = {}
        for token, info in _bot_registry.items():
            webhook_url = f"{_agentOS_base_url}/telegram/webhook/{token}"
            ok = await _set_webhook(token, webhook_url)
            results[token[:10] + "..."] = "ok" if ok else "failed"
        return {"results": results}

    # ------------------------------------------------------------------
    # Webhook endpoint — receives messages from Telegram
    # ------------------------------------------------------------------

    @router.post("/webhook/{token}", summary="Telegram webhook (called by Telegram servers)")
    async def telegram_webhook(token: str, request: Request, background_tasks: BackgroundTasks):
        if token not in _bot_registry:
            # Silently accept but ignore — prevents Telegram from retrying
            return {"ok": True}

        try:
            update = await request.json()
        except Exception:
            return {"ok": True}

        # Process in background so we return 200 immediately to Telegram
        background_tasks.add_task(_handle_update, token, update)
        return {"ok": True}

    return router


async def _handle_update(token: str, update: Dict):
    """Process a Telegram update in the background."""
    bot_info = _bot_registry.get(token)
    if not bot_info:
        return

    # Extract message
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()
    user = message.get("from", {})
    username = user.get("username") or user.get("first_name", "User")

    if not chat_id or not text:
        return

    # Ignore bot commands other than /start /help
    if text.startswith("/start"):
        target = f"{bot_info['target_type']} **{bot_info['target_id']}**"
        await _send_message(token, chat_id,
            f"👋 Hi {username}! I'm connected to {target}.\n\nJust send me a message and I'll respond.")
        return

    if text.startswith("/help"):
        await _send_message(token, chat_id,
            f"*Garza OS — Telegram Interface*\n\n"
            f"Connected to: `{bot_info['target_type']}:{bot_info['target_id']}`\n\n"
            f"Just type your message and I'll respond using the connected agent/team/workflow.\n\n"
            f"Commands:\n/start — Welcome message\n/help — This help message\n/clear — Clear session")
        return

    if text.startswith("/clear"):
        # Clear session by using a new session_id (just acknowledge for now)
        await _send_message(token, chat_id, "✅ Session cleared. Starting fresh!")
        return

    # Use chat_id as session_id for conversation continuity
    session_id = f"tg-{chat_id}"

    # Show typing indicator
    await _send_typing(token, chat_id)

    try:
        target_type = bot_info["target_type"]
        target_id = bot_info["target_id"]
        base_url = _agentOS_base_url or "http://localhost:8000"

        if target_type == "agent":
            response = await _run_agent(base_url, target_id, text, session_id)
        elif target_type == "team":
            response = await _run_team(base_url, target_id, text, session_id)
        elif target_type == "workflow":
            response = await _run_workflow(base_url, target_id, text)
        else:
            response = f"Unknown target type: {target_type}"

        await _send_message(token, chat_id, response)

    except httpx.HTTPStatusError as e:
        logger.error(f"AgentOS API error: {e}")
        await _send_message(token, chat_id,
            f"⚠️ Error calling {bot_info['target_id']}: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Telegram handler error: {e}")
        await _send_message(token, chat_id,
            "⚠️ Something went wrong. Please try again.")
