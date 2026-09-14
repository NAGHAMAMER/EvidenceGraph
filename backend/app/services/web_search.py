from collections.abc import Callable
from functools import lru_cache

from langchain_core.runnables import Runnable
from langchain_tavily import TavilySearch

from app.core.config import settings
from app.schemas.research import (
    WebSearchResponse,
    WebSource,
)


SearchToolFactory = Callable[[int], Runnable]


class WebSearchConfigurationError(RuntimeError):
    """Raised when web search is not configured."""


class WebSearchError(RuntimeError):
    """Raised when the external web search fails."""


class WebSearchService:
    def __init__(
        self,
        search_tool: Runnable | None = None,
        search_tool_factory: SearchToolFactory | None = None,
    ) -> None:
        if (
            search_tool is not None
            and search_tool_factory is not None
        ):
            raise ValueError(
                "Provide either search_tool or "
                "search_tool_factory, not both."
            )

        if (
            search_tool is None
            and search_tool_factory is None
        ):
            if not settings.tavily_api_key.strip():
                raise WebSearchConfigurationError(
                    "TAVILY_API_KEY is not configured."
                )

            search_tool_factory = (
                self._build_default_search_tool
            )

        self._search_tool = search_tool
        self._search_tool_factory = search_tool_factory

    @staticmethod
    def _build_default_search_tool(
        limit: int,
    ) -> Runnable:
        return TavilySearch(
            max_results=limit,
            topic="general",
            search_depth="basic",
            include_answer=False,
            include_raw_content=False,
            include_images=False,
        )

    def _get_search_tool(
        self,
        limit: int,
    ) -> Runnable:
        if self._search_tool is not None:
            return self._search_tool

        if self._search_tool_factory is None:
            raise WebSearchConfigurationError(
                "Web search tool factory is not configured."
            )

        return self._search_tool_factory(limit)

    async def search(
        self,
        query: str,
        limit: int | None = None,
    ) -> WebSearchResponse:
        clean_query = query.strip()

        if not clean_query:
            raise ValueError(
                "Web search query cannot be empty."
            )

        result_limit = (
            settings.web_search_max_results
            if limit is None
            else limit
        )

        if isinstance(result_limit, bool) or result_limit < 1:
            raise ValueError(
                "Web search limit must be at least 1."
            )

        if result_limit > settings.agent_max_papers:
            raise ValueError(
                "Web search limit exceeds AGENT_MAX_PAPERS."
            )

        search_tool = self._get_search_tool(result_limit)

        try:
            raw_response = await search_tool.ainvoke(
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

            if len(sources) >= result_limit:
                break

        return WebSearchResponse(
            query=clean_query,
            total=len(sources),
            results=sources,
        )


@lru_cache
def get_web_search_service() -> WebSearchService:
    return WebSearchService()