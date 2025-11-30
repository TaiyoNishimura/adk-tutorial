from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

from google.genai import types

from .tools import bigquery_nl2sql

from .config import BigqueryDataConfig

# BigQuery built-in tools in ADK
# https://google.github.io/adk-docs/tools/built-in-tools/#bigquery
ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL = "execute_sql"
bigquery_tool_filter = [ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL]
bigquery_tool_config = BigQueryToolConfig(
    write_mode=WriteMode.BLOCKED, application_name="bigquery-agent/0.1.0"
)
bigquery_toolset = BigQueryToolset(
    tool_filter=bigquery_tool_filter, bigquery_tool_config=bigquery_tool_config
)


bigquery_data_config = BigqueryDataConfig.from_env()


def set_database_settings_before_agent_call(callback_context: CallbackContext) -> None:
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = {
            "data_project_id": bigquery_data_config.data_project_id,
            "dataset_id": bigquery_data_config.dataset_id,
            "schema": bigquery_data_config.schema,
        }


root_agent = Agent(
    model="gemini-2.0-flash",
    name="bigquery_agent",
    instruction=f"""
        You are an AI assistant serving as a SQL expert for BigQuery.
        Your job is to help users generate SQL answers from natural language
        questions. Always respond in Japanese.

        Use the provided tools to help generate the most accurate results.
        1. Use the bigquery_nl2sql tool to generate initial SQL from the question.
        2. Use the {ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL} tool to validate and execute the SQL.
        3. Generate the final result in JSON format with four keys: "explain",
        "sql", "sql_results", "nl_results".
        * "explain": "write out step-by-step reasoning to explain how you are
            generating the query based on the schema, example, and question.",
        * "sql": "Output your generated SQL!",
        * "sql_results": "raw sql execution query_result from
            {ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL}"
        * "nl_results": "Natural language summary of results, otherwise None if
            generated SQL is invalid"
        4. If there are any syntax errors in the query, go back and address the
        error in the SQL. Re-run the updated SQL query (step 2).

        You should pass one tool call to another tool call as needed!

        NOTE: you should ALWAYS USE THE TOOLS (bigquery_nl2sql AND
        {ADK_BUILTIN_BQ_EXECUTE_SQL_TOOL}) to generate SQL, not make up SQL WITHOUT CALLING
        TOOLS. Keep in mind that you are an orchestration agent, not a SQL expert,
        so use the tools to help you generate SQL, but do not make up SQL.

        NOTE: you must ALWAYS PASS the project_id
        {bigquery_data_config.data_project_id} to the execute_sql tool. DO NOT
        pass any other project id.
    """,
    tools=[bigquery_nl2sql, bigquery_toolset],
    before_agent_callback=set_database_settings_before_agent_call,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
