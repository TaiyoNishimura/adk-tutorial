from google.adk.agents.llm_agent import Agent

from guardrail import block_paris_tool_guardrail
from my_agent.tools import get_current_time, get_weather_stateful

from greeting_agent.agent import root_agent as greeting_agent
from farewell_agent.agent import root_agent as farewell_agent

root_agent = Agent(
    name="weather_agent_v1",
    model="gemini-2.0-flash",
    description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
    instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
    "You have specialized sub-agents: "
    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
    "If it's a weather request, handle it yourself using 'get_weather'. "
    "For anything else, respond appropriately or state you cannot handle it.",
    tools=[get_current_time, get_weather_stateful],
    before_tool_callback=block_paris_tool_guardrail,
    sub_agents=[greeting_agent, farewell_agent],
    output_key="last_weather_report",
)
