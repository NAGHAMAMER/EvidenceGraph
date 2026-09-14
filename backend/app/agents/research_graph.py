import logging
from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agents.answer_generator import (
    get_answer_generator,
)
from app.agents.question_analyzer import (
    get_question_analyzer,
)
from app.agents.state import ResearchState
from app.core.config import settings
from app.schemas.paper import SemanticPaperSearchResponse
from app.schemas.research import WebSearchResponse
from app.services.multilingual_scientific_search import (
    get_multilingual_scientific_search_service,
)
from app.services.paper_search import PaperSearchError
from app.services.web_search import (
    WebSearchError,
    get_web_search_service,
)


logger = logging.getLogger(__name__)


async def analyze_question_node(
    state: ResearchState,
) -> dict:
    analysis = await get_question_analyzer().analyze(
        state["question"]
    )

    return {
        "detected_language": analysis.detected_language,
        "language_code": analysis.language_code,
        "english_query": analysis.english_query,
    }


async def search_scientific_node(
    state: ResearchState,
) -> dict:
    try:
        result = await (
            get_multilingual_scientific_search_service()
            .search(
                original_query=state["question"],
                english_query=state["english_query"],
                limit=state["limit"],
            )
        )

        return {"scientific_result": result}

    except PaperSearchError as error:
        logger.warning(
            "Scientific search failed: %s",
            error,
        )

        empty_result = SemanticPaperSearchResponse(
            query=state["question"],
            total=0,
            returned=0,
            providers=[],
            papers=[],
        )

        return {
            "scientific_result": empty_result,
            "errors": [
                *state.get("errors", []),
                str(error),
            ],
        }


async def search_web_node(
    state: ResearchState,
) -> dict:
    try:
        result = await get_web_search_service().search(
            state["english_query"],
            limit=state["limit"],
        )

        return {"web_result": result}

    except WebSearchError as error:
        logger.warning(
            "General web search failed: %s",
            error,
        )

        empty_result = WebSearchResponse(
            query=state["english_query"],
            total=0,
            results=[],
        )

        return {
            "web_result": empty_result,
            "errors": [
                *state.get("errors", []),
                str(error),
            ],
        }


async def generate_answer_node(
    state: ResearchState,
) -> dict:
    answer = await get_answer_generator().generate(
        question=state["question"],
        detected_language=state["detected_language"],
        language_code=state["language_code"],
        scientific_result=state["scientific_result"],
        web_result=state["web_result"],
    )

    return {"generated_answer": answer}


def build_research_graph():
    graph_builder = StateGraph(ResearchState)

    graph_builder.add_node(
        "analyze_question",
        analyze_question_node,
    )
    graph_builder.add_node(
        "search_scientific",
        search_scientific_node,
    )
    graph_builder.add_node(
        "search_web",
        search_web_node,
    )
    graph_builder.add_node(
        "generate_answer",
        generate_answer_node,
    )

    graph_builder.add_edge(
        START,
        "analyze_question",
    )
    graph_builder.add_edge(
        "analyze_question",
        "search_scientific",
    )
    graph_builder.add_edge(
        "search_scientific",
        "search_web",
    )
    graph_builder.add_edge(
        "search_web",
        "generate_answer",
    )
    graph_builder.add_edge(
        "generate_answer",
        END,
    )

    return graph_builder.compile()


@lru_cache
def get_research_graph():
    return build_research_graph()


async def run_research_agent(
    question: str,
    limit: int = 5,
) -> ResearchState:
    clean_question = question.strip()

    if not clean_question:
        raise ValueError(
            "Research question cannot be empty."
        )

    if limit < 1:
        raise ValueError(
            "Limit must be at least 1."
        )

    if limit > settings.agent_max_papers:
        raise ValueError(
            "Limit exceeds AGENT_MAX_PAPERS."
        )

    result = await get_research_graph().ainvoke(
        {
            "question": clean_question,
            "limit": limit,
            "errors": [],
        }
    )

    return result
