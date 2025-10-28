import logging
from typing import Union

from models import (
    ChatQuery,
    VectorSearchCaseLawResult,
    VectorSearchResult,
    VectorSearchWerkInstructieResult,
)
from rag.search import search, search_case_laws, search_werk_instructies

logger = logging.getLogger(__name__)


async def search_law_article(chat_query: ChatQuery) -> Union[VectorSearchResult, str]:
    """
    Perform a search for relevant law articles based on the chat query
    """
    try:
        logger.info("Searching the vector database for relevant law articles")
        logger.info(f"Chat query: {chat_query.message}")

        search_result = await search(chat_query.message)
        if len(search_result.documents) == 0:
            return "Ik heb geen relevante informatie kunnen vinden om deze vraag te beantwoorden."

        logger.info(f"Found {len(search_result.urls)} relevant law articles")
        return search_result
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return "Er is een fout opgetreden."


async def search_case_law(
    chat_query: ChatQuery,
) -> VectorSearchCaseLawResult | None | str:
    """
    Perform a search for relevant case law judgments based on the chat query
    """
    try:
        logger.info("Searching the vector database for relevant case law judgments")
        logger.info(f"Chat query: {chat_query.message}")

        search_result = await search_case_laws(chat_query.message)
        if len(search_result.documents) == 0:
            return "Ik heb geen relevante informatie kunnen vinden om deze vraag te beantwoorden."

        logger.info(f"Found {len(search_result.urls)} relevant case law judgments.")
        return search_result
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return "Er is een fout opgetreden."


async def search_werk_instructie(
    chat_query: ChatQuery,
) -> VectorSearchWerkInstructieResult | None | str:
    """
    Perform a search for relevant law articles based on the chat query
    """
    try:
        logger.info("Searching the vector database for relevant work instructions")
        logger.info(f"Chat query: {chat_query.message}")

        search_result = await search_werk_instructies(chat_query.message)
        if len(search_result.documents) == 0:
            return "Ik heb geen relevante informatie kunnen vinden om deze vraag te beantwoorden."

        logger.info(f"Found {len(search_result.urls)} relevant work instructions.")
        return search_result
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return "Er is een fout opgetreden."
