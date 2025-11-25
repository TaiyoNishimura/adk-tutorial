import asyncio
import warnings
import logging

from dotenv import load_dotenv

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from agents.my_agent.agent import root_agent

load_dotenv("agents/my_agent/.env")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        print(
            f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}"
        )
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            break

    print(f"<<< Agent Response: {final_response_text}")


async def run_stateful_conversation(
    runner: Runner,
    user_id: str,
    session_id: str,
    session_service: InMemorySessionService,
    app_name: str,
):
    print("\n--- Testing State: Temp Unit Conversion & output_key ---")

    print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
    await call_agent_async(
        query="What's the weather in London?",
        runner=runner,
        user_id=user_id,
        session_id=session_id,
    )

    print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
    try:
        # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
        # NOTE: In production with persistent services (Database, VertexAI), you would
        # typically update state via agent actions or specific service APIs if available,
        # not by direct manipulation of internal storage.
        stored_session = session_service.sessions[app_name][user_id][session_id]
        stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
        print(
            f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---"
        )
    except KeyError:
        print(
            f"--- Error: Could not retrieve session '{session_id}' from internal storage for user '{user_id}' in app '{app_name}' to update state. Check IDs and if session was created. ---"
        )
    except Exception as e:
        print(f"--- Error updating internal session state: {e} ---")

    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
    await call_agent_async(
        query="Tell me the weather in New York.",
        runner=runner,
        user_id=user_id,
        session_id=session_id,
    )

    # 4. Test basic delegation (should still work)
    # This will update 'last_weather_report' again, overwriting the NY weather report
    print("\n--- Turn 3: Sending a greeting ---")
    await call_agent_async(
        query="Hi!",
        runner=runner,
        user_id=user_id,
        session_id=session_id,
    )


async def main():
    session_service = InMemorySessionService()

    APP_NAME = "weather_tutorial_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001"

    initial_state = {"user_preference_temperature_unit": "Celsius"}

    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=initial_state
    )

    print(session.state)

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    await run_stateful_conversation(
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
        session_service=session_service,
        app_name=APP_NAME,
    )

    print("\n--- Inspecting Final Session State ---")
    final_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if final_session:
        print(
            f"Final Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}"
        )
        print(
            f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}"
        )
        print(
            f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}"
        )
    else:
        print("\n❌ Error: Could not retrieve final session state.")


if __name__ == "__main__":
    asyncio.run(main())
