import logging

logger = logging.getLogger(__name__)

def bigquery_nl2sql(question: str) -> str:
    """自然言語の問い合わせからSQLクエリを生成する

    Args:
        question (str): 自然言語の質問

    Returns:
        str: 質問に回答するために生成されたSQL
    """
    logger.debug("bigquery_nl2sql - question: %s", question)
    return "SELECT * FROM example_table LIMIT 10;"