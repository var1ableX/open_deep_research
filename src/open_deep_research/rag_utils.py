"""Utility functions for RAG (Retrieval Augmented Generation) integration."""

import re
import logging
from typing import Annotated

import aiohttp
from langchain_core.tools import tool


async def create_rag_tool(rag_url: str, collection_id: str, access_token: str):
    """Create a RAG tool for a specific collection.

    Args:
        rag_url: The base URL for the RAG API server
        collection_id: The ID of the collection to query
        access_token: The access token for authentication

    Returns:
        A structured tool that can be used to query the RAG collection
    """
    if rag_url.endswith("/"):
        rag_url = rag_url[:-1]

    collection_endpoint = f"{rag_url}/collections/{collection_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                collection_endpoint, headers={"Authorization": f"Bearer {access_token}"}
            ) as response:
                response.raise_for_status()
                collection_data = await response.json()

        # Get the collection name and sanitize it to match the required regex pattern
        raw_collection_name = collection_data.get("name", f"collection_{collection_id}")

        # Sanitize the name to only include alphanumeric characters, underscores, and hyphens
        # Replace any other characters with underscores
        sanitized_name = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_collection_name)

        # Ensure the name is not empty and doesn't exceed 64 characters
        if not sanitized_name:
            sanitized_name = f"collection_{collection_id}"
        collection_name = sanitized_name[:64]

        raw_description = collection_data.get("metadata", {}).get("description")

        if not raw_description:
            collection_description = "Search your collection of documents for results semantically similar to the input query"
        else:
            collection_description = f"Search your collection of documents for results semantically similar to the input query. Collection description: {raw_description}"

        logging.info(f"========= RAG COLLECTION CONFIGURATION ==========")
        logging.info(f"RAG collection configuration - rag_url: {rag_url}, "
                 f"collection_id: {collection_id}, "
                 f"access_token: {access_token}, "
                 f"collection_name: {collection_name}, "
                 f"collection_description: {collection_description}")
        logging.info(f"========= RAG COLLECTION CONFIGURATION END ==========")
        @tool(name_or_callable=collection_name, description=collection_description)
        async def get_documents(
            query: Annotated[str, "The search query to find relevant documents"],
        ) -> str:
            """Search for documents in the collection based on the query."""
            search_endpoint = f"{rag_url}/collections/{collection_id}/documents/search"
            payload = {"query": query, "limit": 10}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        search_endpoint,
                        json=payload,
                        headers={"Authorization": f"Bearer {access_token}"},
                    ) as search_response:
                        search_response.raise_for_status()
                        documents = await search_response.json()

                formatted_docs = "<all-documents>\n"

                for doc in documents:
                    doc_id = doc.get("id", "unknown")
                    content = doc.get("page_content", "")
                    formatted_docs += (
                        f'  <document id="{doc_id}">\n    {content}\n  </document>\n'
                    )

                formatted_docs += "</all-documents>"
                return formatted_docs
            except Exception as e:
                return f"<all-documents>\n  <error>{str(e)}</error>\n</all-documents>"

        return get_documents

    except Exception as e:
        raise Exception(f"Failed to create RAG tool: {str(e)}")
