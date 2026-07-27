"""Recherche web : DuckDuckGo + Tavily"""

import os
from ddgs import DDGS
from tavily import TavilyClient

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")


def search_duckduckgo(query: str) -> str:
    try:
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return ""
        return "\n".join([f"- [{r['title']}]: {r['body']}" for r in results])
    except Exception as e:
        print(f"[DDG Error] {e}")
        return ""


def search_tavily(query: str) -> str:
    if not TAVILY_API_KEY:
        return search_duckduckgo(query)
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        res = client.search(query=query, search_depth="basic", max_results=3)
        return "\n".join([f"- [{r['title']}]: {r['content']}" for r in res.get("results", [])])
    except Exception as e:
        print(f"[Tavily Error] {e}")
        return search_duckduckgo(query)
