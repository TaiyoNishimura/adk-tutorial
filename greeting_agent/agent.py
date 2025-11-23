from google.adk.agents.llm_agent import Agent
from greeting_agent.tools import say_hello
from guardrail import block_keyword_guardrail

root_agent = Agent(
    model="gemini-2.0-flash",
    name="greeting_agent",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
    "Use the 'say_hello' tool to generate the greeting. "
    "If the user provides their name, make sure to pass it to the tool. "
    "Do not engage in any other conversation or tasks.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",  # Crucial for delegation
    tools=[say_hello],
    before_model_callback=block_keyword_guardrail,
)
