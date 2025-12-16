from google.adk.agents.llm_agent import LlmAgent as Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.planners import PlanReActPlanner

AGENT_NAME = "calculator_agent"
GEMINI_MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name=AGENT_NAME,
    model=GEMINI_MODEL,
    code_executor=BuiltInCodeExecutor(),
    planner=PlanReActPlanner(),
    instruction="""You are a calculator agent.
    When given a mathematical expression, write and execute Python code to calculate the result.
    Return only the final numerical result as plain text, without markdown or code blocks.
    """,
    description="Executes Python code to perform calculations.",
)
