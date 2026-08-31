from functools import lru_cache

from langchain_core.runnables import Runnable
from langchain_tavily import TavilySearch

from app.core.config import settings
from app.schemas.research import (
    WebSearchResponse,
    WebSource,
)


class WebSearchConfigurationError(RuntimeError):
    """Raised when web search is not configured."""


class WebSearchError(RuntimeError):
    """Raised when the external web search fails."""


class WebSearchService:
    def __init__(
        self,
        search_tool: Runnable | None = None,
    ) -> None:
        if search_tool is None:
            if not settings.tavily_api_key.strip():
                raise WebSearchConfigurationError(
                    "TAVILY_API_KEY is not configured."
                )

            search_tool = TavilySearch(
                max_results=settings.web_search_max_results,
                topic="general",
                search_depth="basic",
                include_answer=False,
                include_raw_content=False,
                include_images=False,
            )

        self._search_tool = search_tool

    async def search(
        self,
        query: str,
    ) -> WebSearchResponse:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError(
                "Web search query cannot be empty."
            )

        try:
            raw_response = await self._search_tool.ainvoke(
                {"query": clean_query}
            )
        except Exception as error:
            raise WebSearchError(
                "General web search failed."
            ) from error

        if not isinstance(raw_response, dict):
            raise WebSearchError(
                "Web search returned an invalid response."
            )

        raw_results = raw_response.get("results", [])
        sources: list[WebSource] = []

        for item in raw_results:
            if not isinstance(item, dict):
                continue

            title = str(
                item.get("title") or "Untitled source"
            ).strip()

            url = str(
                item.get("url") or ""
            ).strip()

            content = str(
                item.get("content") or ""
            ).strip()

            score_value = item.get("score")
            score = (
                float(score_value)
                if isinstance(score_value, (int, float))
                else None
            )

            if not url:
                continue

            sources.append(
                WebSource(
                    title=title,
                    url=url,
                    content=content,
                    score=score,
                )
            )

        return WebSearchResponse(
            query=clean_query,
            total=len(sources),
            results=sources,
        )


@lru_cache
def get_web_search_service() -> WebSearchService:
    return WebSearchService()