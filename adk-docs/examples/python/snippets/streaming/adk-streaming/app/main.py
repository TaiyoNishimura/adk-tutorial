# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

from google.adk.runners import InMemoryRunner
from google.adk.events import Event
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from google_search_agent.agent import root_agent

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "ADK Streaming example"

# Create global Runner instance
runner = InMemoryRunner(
    app_name=APP_NAME,
    agent=root_agent,
)


async def get_or_create_session(user_id: str, session_id: str) -> str:
    """Gets or creates a session for the given user and session_id"""
    # Try to get existing session
    session = await runner.session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    if session:
        return session.id

    # Create a new Session with the provided session_id
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    return session.id


async def agent_to_client_sse(events: AsyncGenerator[Event, None]):
    """Agent to client communication via SSE"""
    async for event in events:
        # if event has error_message, print it
        if event.error_message:
            error_message = {
                "error": event.error_message,
                "turn_complete": True
            }
            print(f"[AGENT TO CLIENT]: error: {error_message}")
            continue

        # Read the Content and its first Part
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # If it's text and a parial text, send it
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {message}")

    # After all events are processed, send turn_complete
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

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))




@app.post("/send/{user_id}/{session_id}")
async def send_message_endpoint(user_id: str, session_id: str, request: Request):
    """HTTP endpoint for client to agent communication with streaming response"""

    # Get or create session for this user and session_id
    session_id = await get_or_create_session(user_id, session_id)

    # Parse the message
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    # Validate mime type
    if mime_type != "text/plain":
        return {"error": f"Mime type not supported: {mime_type}"}

    # Create user content
    user_content = Content(role="user", parts=[Part.from_text(text=data)])
    print(f"[CLIENT TO AGENT]: {data}")

    # Set response modality
    run_config = RunConfig(
        response_modalities=["TEXT"],
        streaming_mode=StreamingMode.SSE,
    )

    # Run agent with run_async using session_id and stream the response
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
            error_message = {
                "error": str(e),
                "turn_complete": True
            }
            yield f"data: {json.dumps(error_message)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
