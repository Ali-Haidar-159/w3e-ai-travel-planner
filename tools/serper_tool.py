"""
tools/serper_tool.py
Serper Dev API wrapper – the ONLY external search tool allowed.
"""

import os
import logging
import requests
from crewai.tools import tool

logger = logging.getLogger(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")


@tool("SerperSearch")
def serper_search(query: str) -> str:
    """
    Search the web using the Serper Dev API.
    Use this to find travel attractions, real accommodation prices,
    food costs, transport options, visa requirements, and safety info.
    Input: a plain-text search query string.
    Output: top web results as a formatted string.
    """
    logger.debug("[SerperSearch] Query: %s", query)

    if not SERPER_API_KEY:
        logger.warning("[SerperSearch] SERPER_API_KEY not set; returning mock data.")
        return (
            f"[MOCK RESULT] No real search performed (SERPER_API_KEY missing).\n"
            f"Would have searched: '{query}'\n"
            "Please set SERPER_API_KEY in your .env file."
        )

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": 5}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []

        # Answer box (if present)
        if "answerBox" in data:
            box = data["answerBox"]
            snippet = box.get("answer") or box.get("snippet", "")
            if snippet:
                results.append(f"[Answer Box] {snippet}")

        # Organic results
        for item in data.get("organic", [])[:5]:
            title   = item.get("title", "")
            snippet = item.get("snippet", "")
            link    = item.get("link", "")
            results.append(f"- {title}: {snippet}\n  Source: {link}")

        if not results:
            return "No results found for this query."

        logger.debug("[SerperSearch] Returned %s results.", len(results))
        return "\n\n".join(results)

    except requests.exceptions.Timeout:
        logger.error("[SerperSearch] Request timed out.")
        return "Search failed: Request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        logger.error(f"[SerperSearch] HTTP error: {e}")
        return f"Search failed: HTTP error {e.response.status_code}."
    except requests.exceptions.RequestException as e:
        logger.error(f"[SerperSearch] Request error: {e}")
        return f"Search failed: {str(e)}"
    except Exception as e:
        logger.error(f"[SerperSearch] Unexpected error: {e}")
        return f"Search failed unexpectedly: {str(e)}"
