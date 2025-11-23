from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any


def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Checks if 'get_weather_stateful' is called for 'Paris'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name
    print(
        f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---"
    )
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- Guardrail Logic ---
    target_tool_name = "get_weather_stateful"
    blocked_city = "paris"

    if tool_name == target_tool_name:
        city_argument = args.get("city", "")
        if city_argument and city_argument.lower() == blocked_city:
            print(
                f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---"
            )
            tool_context.state["guardrail_tool_block_triggered"] = True
            print("--- Callback: Set state 'guardrail_tool_block_triggered': True ---")

            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail.",
            }
        else:
            print(
                f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---"
            )
    else:
        print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")

    print(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
    return None