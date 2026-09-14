import asyncio
import logging
from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from app.agents.follow_up_analyzer import (
    get_follow_up_analyzer,
)
from app.agents.follow_up_answer_generator import (
    get_follow_up_answer_generator,
)
from app.agents.state import FollowUpResearchState
from app.core.config import settings
from app.schemas.paper import (
    SemanticPaperSearchResponse,
)
from app.schemas.research import (
    ResearchSessionDetail,
    WebSearchResponse,
)
from app.services.multilingual_scientific_search import (
    get_multilingual_scientific_search_service,
)
from app.services.research_memory import (
    get_research_memory_service,
)
from app.services.web_search import (
    get_web_search_service,
)


logger = logging.getLogger(__name__)


async def analyze_follow_up_node(
    state: FollowUpResearchState,
) -> dict:
    analysis = await get_follow_up_analyzer().analyze(
        question=state["question"],
        session=state["session"],
    )

    return {"analysis": analysis}


def route_follow_up(
    state: FollowUpResearchState,
) -> str:
    memory_service = get_research_memory_service()

    has_saved_sources = memory_service.has_sources(
        state["session"]
    )

    if state["analysis"].needs_search:
        return "search"

    if not has_saved_sources:
        return "search"

    return "memory"


async def load_memory_node(
    state: FollowUpResearchState,
) -> dict:
    memory_service = get_research_memory_service()
    analysis = state["analysis"]

    scientific_result = (
        memory_service.build_scientific_result(
            session=state["session"],
            query=analysis.english_query,
            limit=state["limit"],
        )
    )

    web_result = memory_service.build_web_result(
        session=state["session"],
        query=analysis.english_query,
        limit=state["limit"],
    )

    return {
        "scientific_result": scientific_result,
        "web_result": web_result,
        "used_existing_context": True,
        "performed_search": False,
    }


async def search_follow_up_node(
    state: FollowUpResearchState,
) -> dict:
    memory_service = get_research_memory_service()
    analysis = state["analysis"]
    session = state["session"]
    limit = state["limit"]

    saved_scientific_result = (
        memory_service.build_scientific_result(
            session=session,
            query=analysis.english_query,
            limit=limit,
        )
    )

    saved_web_result = (
        memory_service.build_web_result(
            session=session,
            query=analysis.english_query,
            limit=limit,
        )
    )

    scientific_call = (
        get_multilingual_scientific_search_service()
        .search(
            original_query=state["question"],
            english_query=analysis.english_query,
            limit=limit,
        )
    )

    web_call = get_web_search_service().search(
        analysis.english_query
    )

    scientific_outcome, web_outcome = (
        await asyncio.gather(
            scientific_call,
            web_call,
            return_exceptions=True,
        )
    )

    errors = list(state.get("errors", []))

    if isinstance(scientific_outcome, TimeoutError):
        raise scientific_outcome

    if isinstance(web_outcome, TimeoutError):
        raise web_outcome

    if isinstance(scientific_outcome, Exception):
        logger.warning(
            "Follow-up scientific search failed: %s",
            scientific_outcome,
        )

        errors.append(
            str(scientific_outcome)
            or "Follow-up scientific search failed."
        )

        new_scientific_result = (
            SemanticPaperSearchResponse(
                query=analysis.english_query,
                total=0,
                returned=0,
                providers=[],
                papers=[],
            )
        )
    else:
        new_scientific_result = scientific_outcome

    if isinstance(web_outcome, Exception):
        logger.warning(
            "Follow-up web search failed: %s",
            web_outcome,
        )

        errors.append(
            str(web_outcome)
            or "Follow-up web search failed."
        )

        new_web_result = WebSearchResponse(
            query=analysis.english_query,
            total=0,
            results=[],
        )
    else:
        new_web_result = web_outcome

    scientific_result = (
        memory_service.merge_scientific_results(
            query=analysis.english_query,
            saved_result=saved_scientific_result,
            new_result=new_scientific_result,
            limit=limit,
        )
    )

    web_result = memory_service.merge_web_results(
        query=analysis.english_query,
        saved_result=saved_web_result,
        new_result=new_web_result,
        limit=limit,
    )

    return {
        "scientific_result": scientific_result,
        "web_result": web_result,
        "used_existing_context": (
            memory_service.has_sources(session)
        ),
        "performed_search": True,
        "errors": errors,
    }


async def generate_follow_up_answer_node(
    state: FollowUpResearchState,
) -> dict:
    analysis = state["analysis"]

    answer = (
        await get_follow_up_answer_generator().generate(
            question=state["question"],
            english_query=analysis.english_query,
            detected_language=(
                analysis.detected_language
            ),
            language_code=analysis.language_code,
            session=state["session"],
            scientific_result=(
                state["scientific_result"]
            ),
            web_result=state["web_result"],
        )
    )

    return {"generated_answer": answer}


def build_follow_up_graph():
    graph_builder = StateGraph(FollowUpResearchState)

    graph_builder.add_node(
        "analyze_follow_up",
        analyze_follow_up_node,
    )
    graph_builder.add_node(
        "load_memory",
        load_memory_node,
    )
    graph_builder.add_node(
        "search_follow_up",
        search_follow_up_node,
    )
    graph_builder.add_node(
        "generate_answer",
        generate_follow_up_answer_node,
    )

    graph_builder.add_edge(
        START,
        "analyze_follow_up",
    )

    graph_builder.add_conditional_edges(
        "analyze_follow_up",
        route_follow_up,
        {
            "memory": "load_memory",
            "search": "search_follow_up",
        },
    )

    graph_builder.add_edge(
        "load_memory",
        "generate_answer",
    )
    graph_builder.add_edge(
        "search_follow_up",
        "generate_answer",
    )
    graph_builder.add_edge(
        "generate_answer",
        END,
    )

    return graph_builder.compile()


@lru_cache
def get_follow_up_graph():
    return build_follow_up_graph()


async def run_follow_up_agent(
    question: str,
    session: ResearchSessionDetail,
    limit: int = 5,
) -> FollowUpResearchState:
    clean_question = question.strip()

    if not clean_question:
        raise ValueError(
            "Follow-up question cannot be empty."
        )

    if limit < 1:
        raise ValueError(
            "Limit must be at least 1."
        )

    if limit > settings.agent_max_papers:
        raise ValueError(
            "Limit exceeds AGENT_MAX_PAPERS."
        )

    result = await get_follow_up_graph().ainvoke(
        {
            "question": clean_question,
            "limit": limit,
            "session": session,
            "errors": [],
        }
    )

    return result
