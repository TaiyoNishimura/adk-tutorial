import os
import json
from typing import AsyncGenerator
import warnings

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
)

from google.adk.runners import Runner
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.events import Event
from google.adk.agents.run_config import RunConfig, StreamingMode

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables before importing agents
load_dotenv("agents/bigquery/.env")
load_dotenv(".env")

from agents.bigquery.agent import root_agent

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

#
# ADK Streaming
#

APP_NAME = "ADK Streaming example"

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

session_service = DatabaseSessionService(db_url=database_url)


runner = Runner(
    app_name=APP_NAME,
    agent=root_agent,
    session_service=session_service,
)


async def get_or_create_session(user_id: str, session_id: str) -> str:
    session = await runner.session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    if session:
        return session.id

    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    return session.id


async def agent_to_client_sse(events: AsyncGenerator[Event, None]):
    async for event in events:
        part: Part = event.content and event.content.parts and event.content.parts[0]
        if not part:
            continue

        if part.text and event.partial:
            message = {"mime_type": "text/plain", "data": part.text}
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {event}")

    # run_asyncの場合はturn_complete: Trueが返却されないので後付け
    final_message = {
        "turn_complete": True,
        "interrupted": False,
    }
    yield f"data: {json.dumps(final_message)}\n\n"
    print(f"[AGENT TO CLIENT]: {final_message}")


#
# FastAPI web app
#

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEST_PAGE_DIR = Path("test_page")
app.mount("/test_page", StaticFiles(directory=TEST_PAGE_DIR), name="test_page")


@app.get("/")
async def root():
    return FileResponse(os.path.join(TEST_PAGE_DIR, "index.html"))


@app.post("/send/{user_id}/{session_id}")
async def send_message_endpoint(user_id: str, session_id: str, request: Request):
    session_id = await get_or_create_session(user_id, session_id)

    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    if mime_type != "text/plain":
        return {"error": f"Mime type not supported: {mime_type}"}

    user_content = Content(role="user", parts=[Part.from_text(text=data)])
    print(f"[CLIENT TO AGENT]: {data}")

    run_config = RunConfig(
        response_modalities=["TEXT"],
        streaming_mode=StreamingMode.SSE,
    )

    async def event_generator():
        try:
            agent_events = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_content,
                run_config=run_config,
            )
            async for data in agent_to_client_sse(agent_events):
                yield data
        except Exception as e:
            print(f"Error in agent stream: {e}")
            error_message = {"error": str(e), "turn_complete": True}
            yield f"data: {json.dumps(error_message)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )
