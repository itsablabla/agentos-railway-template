"""
Comms Agent
-----------
A unified communications agent that integrates with Telegram, Slack, Gmail,
Email (SMTP), Twilio, Discord, X/Twitter, Reddit, Zoom, and WhatsApp.

All tools are activated by setting the corresponding env vars.

Env vars:
  TELEGRAM_BOT_TOKEN        → TelegramTools
  SLACK_BOT_TOKEN           → SlackTools (also needs slack_sdk package)
  GMAIL_CREDENTIALS         → GmailTools (needs google-api-python-client)
  SMTP_HOST + SMTP_USER + SMTP_PASSWORD → EmailTools
  TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN → TwilioTools (needs twilio package)
  DISCORD_BOT_TOKEN         → DiscordTools
  X_API_KEY + X_API_SECRET + X_ACCESS_TOKEN + X_ACCESS_SECRET → XTools (needs tweepy)
  REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET → RedditTools (needs praw)
  ZOOM_CLIENT_ID + ZOOM_CLIENT_SECRET     → ZoomTools
  WHATSAPP_ACCESS_TOKEN + WHATSAPP_PHONE_NUMBER_ID → WhatsAppTools
  WEBEX_ACCESS_TOKEN        → WebexTools
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.duckduckgo import DuckDuckGoTools

from db import get_postgres_db

_tools = [DuckDuckGoTools()]

if os.getenv("TELEGRAM_BOT_TOKEN"):
    try:
        from agno.tools.telegram import TelegramTools
        _tools.append(TelegramTools())
    except ImportError:
        pass

if os.getenv("SLACK_BOT_TOKEN"):
    try:
        from agno.tools.slack import SlackTools
        _tools.append(SlackTools())
    except ImportError:
        pass

if os.getenv("GMAIL_CREDENTIALS") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    try:
        from agno.tools.gmail import GmailTools
        _tools.append(GmailTools())
    except ImportError:
        pass

if os.getenv("SMTP_HOST"):
    try:
        from agno.tools.email import EmailTools
        _tools.append(EmailTools(
            sender_email=os.getenv("SMTP_USER", ""),
            sender_name=os.getenv("SMTP_SENDER_NAME", "Garza OS"),
        ))
    except ImportError:
        pass

if os.getenv("TWILIO_ACCOUNT_SID"):
    try:
        from agno.tools.twilio import TwilioTools
        _tools.append(TwilioTools())
    except ImportError:
        pass

if os.getenv("DISCORD_BOT_TOKEN"):
    try:
        from agno.tools.discord import DiscordTools
        _tools.append(DiscordTools())
    except ImportError:
        pass

if os.getenv("X_API_KEY") or os.getenv("TWITTER_API_KEY"):
    try:
        from agno.tools.x import XTools
        _tools.append(XTools())
    except ImportError:
        pass

if os.getenv("REDDIT_CLIENT_ID"):
    try:
        from agno.tools.reddit import RedditTools
        _tools.append(RedditTools())
    except ImportError:
        pass

if os.getenv("ZOOM_CLIENT_ID"):
    try:
        from agno.tools.zoom import ZoomTools
        _tools.append(ZoomTools())
    except ImportError:
        pass

if os.getenv("WHATSAPP_ACCESS_TOKEN"):
    try:
        from agno.tools.whatsapp import WhatsAppTools
        _tools.append(WhatsAppTools())
    except ImportError:
        pass

if os.getenv("WEBEX_ACCESS_TOKEN"):
    try:
        from agno.tools.webex import WebexTools
        _tools.append(WebexTools())
    except ImportError:
        pass

comms = Agent(
    id="comms",
    name="Comms",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A unified communications hub. Sends and reads messages across Telegram, Slack, "
        "Gmail, Email, Twilio SMS, Discord, X/Twitter, Reddit, Zoom, and WhatsApp. "
        "Activate each platform by setting the corresponding env vars."
    ),
    instructions="""\
You are a unified communications hub. You can send and receive messages across all major platforms.

**Messaging Platforms:**
- Telegram: Send messages, read chats, manage bots
- Slack: Post to channels, read messages, manage workspaces
- Discord: Send messages to channels, manage servers
- WhatsApp: Send messages via WhatsApp Business API
- Webex: Send messages to Cisco Webex spaces

**Email:**
- Gmail: Read, send, and manage Gmail
- Email (SMTP): Send emails via any SMTP server

**SMS/Voice:**
- Twilio: Send SMS, make calls, manage phone numbers

**Social Media:**
- X/Twitter: Post tweets, read timeline, search
- Reddit: Post to subreddits, read posts and comments

**Video Conferencing:**
- Zoom: Create meetings, manage participants

**Guidelines:**
- Always confirm before sending messages or posting publicly
- Show the message content before sending
- For email, always confirm recipient and subject
- For social media, note that posts are public
- Respect platform rate limits
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=10,
    markdown=True,
)
