import logging

from google.adk.tools import ToolContext

from google.genai import Client
from google.genai.types import HttpOptions, HttpRetryOptions

from ..config import Nl2SqlModelConfig

logger = logging.getLogger(__name__)

nl2sqlModelConfig = Nl2SqlModelConfig.from_env()

http_options = HttpOptions(
    headers={"user-agent": "bigquery-agent/0.1.0"},
    retry_options=HttpRetryOptions(
        attempts=5,
        initial_delay=1.0,
        max_delay=60.0,
        exp_base=2,
    ),
)
llm_client = Client(
    vertexai=True,
    project=nl2sqlModelConfig.google_cloud_project,
    location=nl2sqlModelConfig.google_cloud_location,
    http_options=http_options,
)

MAX_NUM_ROWS = 10000


def bigquery_nl2sql(
    question: str,
    tool_context: ToolContext,
) -> str:
    """Generates a SQL query from a natural language question.

    Args:
        question (str): Natural language question.
        tool_context (ToolContext): The tool context to use for generating the
            SQL query.

    Returns:
        str: An SQL statement to answer this question.
    """
    logger.debug("bigquery_nl2sql - question: %s", question)

    prompt_template = """
        You are a BigQuery SQL expert tasked with generating SQL in the Google SQL
        dialect based on the user's natural language question.
        Your task is to write a Bigquery SQL query that answers the following question
        while using the provided context.

        **Guidelines:**

        - **Table Referencing:** Always use the full table name with the database prefix
        in the SQL statement.  Tables should be referred to using a fully qualified
        name with enclosed in backticks (`) e.g.
        `project_name.dataset_name.table_name`.  Table names are case sensitive.
        - **Joins:** Join as few tables as possible. When joining tables, ensure all
        join columns are the same data type. Analyze the database and the table schema
        provided to understand the relationships between columns and tables.
        - **Aggregations:**  Use all non-aggregated columns from the `SELECT` statement
        in the `GROUP BY` clause.
        - **SQL Syntax:** Return syntactically and semantically correct SQL for BigQuery
        with proper relation mapping (i.e., project_id, owner, table, and column
        relation). Use SQL `AS` statement to assign a new name temporarily to a table
        column or even a table wherever needed. Always enclose subqueries and union
        queries in parentheses.
        - **Column Usage:** Use *ONLY* the column names (column_name) mentioned in the
        Table Schema. Do *NOT* use any other column names. Associate `column_name`
        mentioned in the Table Schema only to the `table_name` specified under Table
        Schema.
        - **FILTERS:** You should write query effectively  to reduce and minimize the
        total rows to be returned. For example, you can use filters (like `WHERE`,
        `HAVING`, etc. (like 'COUNT', 'SUM', etc.) in the SQL query.
        - **LIMIT ROWS:**  The maximum number of rows returned should be less than
        {MAX_NUM_ROWS}.

        **Schema:**

        The database structure is defined by the following table schemas (possibly with
        sample rows):

        ```
        {SCHEMA}
        ```

        **Natural language question:**

        ```
        {QUESTION}
        ```

        **Think Step-by-Step:** Carefully consider the schema, question, guidelines, and
        best practices outlined above to generate the correct BigQuery SQL.
    """

    schema = tool_context.state["database_settings"]["schema"]

    prompt = prompt_template.format(
        MAX_NUM_ROWS=MAX_NUM_ROWS, SCHEMA=schema, QUESTION=question
    )

    # リトライはHttpRetryOptionsで指定している
    # TODO: クライアントの関心ごとを別クラスに分離する
    response = llm_client.models.generate_content(
        model=nl2sqlModelConfig.nl2sql_model,
        contents=prompt,
        config={"temperature": 0.1},
    )

    sql = response.text
    if sql:
        sql = sql.replace("```sql", "").replace("```", "").strip()

    logger.debug("bigquery_nl2sql - sql:\n%s", sql)

    tool_context.state["sql_query"] = sql

    return sql
