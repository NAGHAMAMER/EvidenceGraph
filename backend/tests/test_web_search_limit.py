import asyncio

from app.services.web_search import WebSearchService


class FakeSearchTool:
    def __init__(self) -> None:
        self.received_input = None

    async def ainvoke(self, value):
        self.received_input = value

        return {
            "results": [
                {
                    "title": f"Source {index}",
                    "url": f"https://example.org/{index}",
                    "content": "Evidence content.",
                    "score": 0.9,
                }
                for index in range(1, 5)
            ]
        }


def test_web_search_uses_requested_limit() -> None:
    created_limits: list[int] = []
    fake_tool = FakeSearchTool()

    def create_tool(limit: int):
        created_limits.append(limit)
        return fake_tool

    service = WebSearchService(
        search_tool_factory=create_tool,
    )

    result = asyncio.run(
        service.search(
            "exercise and sleep",
            limit=2,
        )
    )

    assert created_limits == [2]
    assert fake_tool.received_input == {
        "query": "exercise and sleep"
    }
    assert result.total == 2
    assert len(result.results) == 2