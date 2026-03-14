"""
Reasoner Agent
--------------
A structured reasoning and analysis agent using Agno's ReasoningTools
for step-by-step logical analysis, decision support, and problem solving.

Tools:
  - ReasoningTools    : Structured logical analysis with chain-of-thought
  - DuckDuckGoTools   : Research to support reasoning
  - CalculatorTools   : Quantitative analysis
  - WikipediaTools    : Background knowledge
"""
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.reasoning import ReasoningTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.calculator import CalculatorTools
from agno.tools.wikipedia import WikipediaTools

from db import get_postgres_db

reasoner = Agent(
    id="reasoner",
    name="Reasoner",
    model=OpenAIResponses(id="o4-mini"),
    db=get_postgres_db(),
    description=(
        "A structured reasoning and analysis agent. Uses chain-of-thought reasoning "
        "to break down complex problems, evaluate options, and provide well-reasoned conclusions. "
        "Ideal for decision support, logical analysis, and strategic thinking."
    ),
    instructions="""\
You are a structured reasoning agent. You excel at breaking down complex problems
and providing well-reasoned, evidence-based conclusions.

**Reasoning Approach:**
1. Clarify the problem or question
2. Identify key assumptions and constraints
3. Break down into sub-problems
4. Analyze each component systematically
5. Synthesize findings into a coherent conclusion
6. Identify limitations and uncertainties

**When to use each tool:**
- ReasoningTools: For structured step-by-step analysis
- DuckDuckGo: To gather facts and evidence
- Calculator: For quantitative analysis and calculations
- Wikipedia: For background context and definitions

**Output Format:**
- Start with a clear statement of the problem
- Show your reasoning chain explicitly
- Distinguish between facts, inferences, and opinions
- Provide a clear conclusion with confidence level
- Note key uncertainties and alternative interpretations

**Best for:**
- Complex decision analysis
- Strategic planning and trade-off evaluation
- Logical problem solving
- Argument evaluation and critical thinking
- Risk assessment
""",
    tools=[
        ReasoningTools(add_instructions=True),
        DuckDuckGoTools(),
        CalculatorTools(),
        WikipediaTools(),
    ],
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    reasoner.print_response(
        "Should a startup with $500K runway prioritize product development or sales? Analyze the trade-offs.",
        stream=True,
    )
