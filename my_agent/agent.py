import datetime
from zoneinfo import ZoneInfo
from google.adk.agents.llm_agent import Agent


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}."),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
    return {"status": "success", "report": report}


root_agent = Agent(
    model="gemini-2.0-flash",
    name="get_new_york_time_agent",
    description="An agent that provides the current time in New York City.",
    instruction="You are an agent that provides the current time in New York City. When asked for the current time, use the get_current_time function to retrieve and report the time.",
    tools=[get_current_time],
)
