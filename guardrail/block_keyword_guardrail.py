from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from typing import Optional


def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    print(
        f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---"
    )

    # --- Guardrail Logic ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        # Optionally, set a flag in state to record the block event
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print("--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'."
                    )
                ],
            ),
            error_message=f"Request blocked due to presence of keyword '{keyword_to_block}'.",
        )
    else:
        print(
            f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---"
        )
        return None
