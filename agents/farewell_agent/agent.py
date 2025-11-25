from google.adk.agents.llm_agent import Agent
from .tools import say_goodbye

root_agent = Agent(
    model="gemini-2.0-flash",
    name="farewell_agent",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
    "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",  # Crucial for delegation
    tools=[say_goodbye],
)