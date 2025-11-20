from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from my_agent.tools import get_current_time, get_weather

PROVIDER = "vertex_ai"
MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name="weather_agent_v1",
    model=LiteLlm(model=f"{PROVIDER}/{MODEL}"),
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
    "When the user asks for the weather in a specific city, "
    "use the 'get_weather' tool to find the information. "
    "If the tool returns an error, inform the user politely. "
    "If the tool is successful, present the weather report clearly.",
    tools=[get_current_time, get_weather],
)
