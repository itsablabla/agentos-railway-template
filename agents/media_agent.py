"""
Media Agent
-----------
A creative media agent for image generation, video search, audio synthesis,
and content creation.

Tools (always active):
  - DalleTools     : AI image generation (uses OPENAI_API_KEY)
  - YouTubeTools   : YouTube video search and transcript retrieval
  - WebsiteTools   : Fetch media from URLs
  - DuckDuckGoTools: Search for media and references

Activate optional tools by setting env vars:
  ELEVENLABS_API_KEY  → ElevenLabsTools (text-to-speech)
  FAL_API_KEY         → FalTools (image/video generation)
  REPLICATE_API_KEY   → ReplicateTools (open-source AI models)
  GIPHY_API_KEY       → GiphyTools (GIF search)
  SPOTIFY_CLIENT_ID + SPOTIFY_CLIENT_SECRET → SpotifyTools
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.dalle import DalleTools
from agno.tools.youtube import YouTubeTools
from agno.tools.website import WebsiteTools
from agno.tools.duckduckgo import DuckDuckGoTools

from db import get_postgres_db

_tools = [
    DalleTools(),
    YouTubeTools(),
    WebsiteTools(),
    DuckDuckGoTools(),
]

if os.getenv("GIPHY_API_KEY"):
    try:
        from agno.tools.giphy import GiphyTools
        _tools.append(GiphyTools())
    except ImportError:
        pass

if os.getenv("ELEVENLABS_API_KEY"):
    try:
        from agno.tools.eleven_labs import ElevenLabsTools
        _tools.append(ElevenLabsTools())
    except ImportError:
        pass

if os.getenv("FAL_API_KEY"):
    try:
        from agno.tools.fal import FalTools
        _tools.append(FalTools())
    except ImportError:
        pass

if os.getenv("REPLICATE_API_KEY"):
    try:
        from agno.tools.replicate import ReplicateTools
        _tools.append(ReplicateTools())
    except ImportError:
        pass

if os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"):
    try:
        from agno.tools.spotify import SpotifyTools
        _tools.append(SpotifyTools())
    except ImportError:
        pass

media_agent = Agent(
    id="media-agent",
    name="Media Agent",
    model=OpenAIResponses(id="gpt-4o"),
    db=get_postgres_db(),
    description=(
        "A creative media agent for image generation, video search, audio synthesis, and content creation. "
        "Generates images with DALL-E, searches YouTube for videos, finds GIFs, and can synthesize speech."
    ),
    instructions="""\
You are a creative media agent. You can generate, find, and work with various media types.

**Image Generation (DALL-E):**
- Generate high-quality images from text descriptions
- Create variations of existing images
- Edit images with specific instructions
- Always describe what you're generating before creating it

**Video Search (YouTube):**
- Search for videos on any topic
- Retrieve video transcripts and captions
- Find tutorials, music videos, documentaries

**GIF Search (Giphy — if enabled):**
- Find relevant GIFs for any emotion or topic
- Search by keyword or category

**Audio/Speech (if ElevenLabs enabled):**
- Convert text to natural-sounding speech
- Choose from multiple voice styles

**Guidelines:**
- For image generation, be specific and descriptive in prompts
- Include style, lighting, composition details for better results
- For video search, provide multiple search terms if the first doesn't work
- Always provide URLs/links to found media
""",
    tools=_tools,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)
