"""
Utility Agent
-------------
A general-purpose utility agent with weather, maps, location services,
web utilities, and miscellaneous tools.

Tools (always active):
  - DuckDuckGoTools   : Web search
  - CalculatorTools   : Math and calculations
  - WebsiteTools      : URL fetching
  - SleepTools        : Pause/delay execution

Activate optional tools by setting env vars:
  OPENWEATHER_API_KEY   → OpenWeatherTools (weather data)
  GOOGLE_MAPS_API_KEY   → GoogleMapTools (places, directions, geocoding)
  BRANDFETCH_API_KEY    → BrandfetchTools (brand logos and info)
  APIFY_API_KEY         → ApifyTools (web scraping actors)
"""
import os

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.calculator import CalculatorTools
from agno.tools.website import WebsiteTools
from agno.tools.sleep import SleepTools

from db import get_postgres_db

_tools = [
    DuckDuckGoTools(),
    CalculatorTools(),
    WebsiteTools(),
    SleepTools(),
]

if os.getenv("OPENWEATHER_API_KEY"):
    try:
        from agno.tools.openweather import OpenWeatherTools
        _tools.append(OpenWeatherTools())
    except ImportError:
        pass

if os.getenv("GOOGLE_MAPS_API_KEY"):
    try:
        from agno.tools.google.maps import GoogleMapTools
        _tools.append(GoogleMapTools())
    except ImportError:
        try:
            from agno.tools.google_maps import GoogleMapTools
            _tools.append(GoogleMapTools())
        except ImportError:
            pass

if os.getenv("BRANDFETCH_API_KEY"):
    try:
        from agno.tools.brandfetch import BrandfetchTools
        _tools.append(BrandfetchTools())
    except ImportError:
        pass

if os.getenv("APIFY_API_KEY"):
    try:
        from agno.tools.apify import ApifyTools
        _tools.append(ApifyTools())
    except ImportError:
        pass

utility = Agent(
    id="utility",
    name="Utility",
    model=OpenAIResponses(id="gpt-4o-mini"),
    db=get_postgres_db(),
    description=(
        "A general-purpose utility agent. Handles weather lookups, location/maps queries, "
        "calculations, URL fetching, brand lookups, and miscellaneous tasks. "
        "Activate weather and maps by setting OPENWEATHER_API_KEY and GOOGLE_MAPS_API_KEY."
    ),
    instructions="""\
You are a versatile utility agent for everyday tasks.

**Weather (if enabled):**
- Current weather conditions for any city
- Temperature, humidity, wind speed, UV index
- Weather forecasts

**Maps & Location (if enabled):**
- Find places, restaurants, businesses nearby
- Get directions and travel times
- Geocode addresses to coordinates

**Calculations:**
- Math, unit conversions, percentages
- Date/time calculations

**Web Utilities:**
- Fetch and read any URL
- Check if a website is up
- Extract content from web pages

**Brand Info (if enabled):**
- Get company logos, colors, and brand assets

**Guidelines:**
- For weather, always include the units (°C/°F, km/h, etc.)
- For calculations, show the formula
- Be concise — utility tasks should have quick, clear answers
""",
    tools=_tools,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=3,
    markdown=True,
)
