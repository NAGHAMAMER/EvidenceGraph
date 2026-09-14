from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from app.agents.answer_generator import AnswerGenerator
from app.schemas.paper import SemanticPaperSearchResponse
from app.schemas.research import (
    GeneratedResearchAnswer,
    ResearchSessionDetail,
    WebSearchResponse,
)
from app.services.llm import get_chat_model


SYSTEM_PROMPT = """
You are an evidence-focused multilingual research assistant
answering a follow-up question inside an existing conversation.

Rules:
1. Interpret the new question using the saved conversation.
2. Answer entirely in the language of the new follow-up question.
3. Use saved conversation answers only as conversational memory.
4. Support factual claims using the provided scientific and web
   sources, not unsupported model knowledge.
5. Cite scientific papers using current identifiers such as [P1].
6. Cite web sources using current identifiers such as [W1].
7. Use only identifiers listed in the current available sources.
8. Prefer scientific papers over general web sources.
9. If sources disagree, describe the disagreement.
10. If evidence is insufficient, state that clearly.
11. Do not invent facts, citations, or source identifiers.
12. Return only the requested structured output.
""".strip()


class FollowUpAnswerGenerator:
    def __init__(
        self,
        structured_model: Runnable | None = None,
    ) -> None:
        if structured_model is None:
            structured_model = (
                get_chat_model().with_structured_output(
                    schema=(
                        GeneratedResearchAnswer
                        .model_json_schema()
                    ),
                    method="json_schema",
                )
            )

        self._structured_model = structured_model

    @staticmethod
    def build_conversation_context(
        session: ResearchSessionDetail,
    ) -> str:
        blocks = []

        for turn in session.turns[-5:]:
            blocks.append(
                "\n".join(
                    [
                        (
                            f"Turn {turn.turn_index} "
                            f"question: {turn.question}"
                        ),
                        (
                            f"Turn {turn.turn_index} "
                            f"answer: {turn.answer[:2500]}"
                        ),
                    ]
                )
            )

        return "\n\n---\n\n".join(blocks)

    async def generate(
        self,
        question: str,
        english_query: str,
        detected_language: str,
        language_code: str,
        session: ResearchSessionDetail,
        scientific_result: SemanticPaperSearchResponse,
        web_result: WebSearchResponse,
    ) -> GeneratedResearchAnswer:
        conversation_context = (
            self.build_conversation_context(session)
        )

        source_context = AnswerGenerator.build_source_context(
            scientific_result=scientific_result,
            web_result=web_result,
        )

        user_prompt = "\n".join(
            [
                "Saved conversation:",
                conversation_context,
                "",
                "New follow-up question:",
                question,
                "",
                (
                    "Standalone English interpretation: "
                    f"{english_query}"
                ),
                (
                    "Required answer language: "
                    f"{detected_language} ({language_code})"
                ),
                "",
                "Current available sources:",
                source_context,
            ]
        )

        result = await self._structured_model.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
        )

        answer = GeneratedResearchAnswer.model_validate(
            result
        )

        valid_source_ids = {
            *[
                f"P{index}"
                for index in range(
                    1,
                    len(scientific_result.papers) + 1,
                )
            ],
            *[
                f"W{index}"
                for index in range(
                    1,
                    len(web_result.results) + 1,
                )
            ],
        }

        cleaned_evidence = [
            evidence.model_copy(
                update={
                    "source_ids": [
                        source_id
                        for source_id in evidence.source_ids
                        if source_id in valid_source_ids
                    ]
                }
            )
            for evidence in answer.evidence
        ]

        return answer.model_copy(
            update={
                "evidence": cleaned_evidence,
            }
        )


@lru_cache
def get_follow_up_answer_generator(
) -> FollowUpAnswerGenerator:
    return FollowUpAnswerGenerator()
