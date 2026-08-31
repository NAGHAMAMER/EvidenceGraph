from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from app.schemas.paper import SemanticPaperSearchResponse
from app.schemas.research import (
    GeneratedResearchAnswer,
    WebSearchResponse,
)
from app.services.llm import get_chat_model


SYSTEM_PROMPT = """
You are an evidence-focused multidisciplinary research assistant.

Rules:
1. Answer entirely in the same language as the user's original question.
2. Translate and synthesize evidence from both scientific papers
   and general web sources into the user's language.
3. Keep source identifiers, URLs, DOI values, scientific names,
   and necessary technical terms unchanged.
4. Cite scientific papers using identifiers such as [P1].
5. Cite general web sources using identifiers such as [W1].
6. Prefer scientific papers over general web sources.
7. Do not treat a normal web page as scientific evidence.
8. If sources disagree, describe the disagreement.
9. If evidence is insufficient, say so clearly.
10. Do not invent citations, facts, or source identifiers.
11. Do not leave explanatory sentences in another language.
12. Return only the requested structured output.
""".strip()


class AnswerGenerationError(RuntimeError):
    """Raised when an evidence-based answer cannot be generated."""


class AnswerGenerator:
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
    def build_source_context(
        scientific_result: SemanticPaperSearchResponse,
        web_result: WebSearchResponse,
    ) -> str:
        source_blocks: list[str] = []

        for index, paper in enumerate(
            scientific_result.papers,
            start=1,
        ):
            abstract = (
                paper.abstract[:2500]
                if paper.abstract
                else "Abstract not available."
            )

            source_blocks.append(
                "\n".join(
                    [
                        f"[P{index}] SCIENTIFIC PAPER",
                        f"Title: {paper.title}",
                        f"Year: {paper.publication_year}",
                        f"DOI: {paper.doi}",
                        f"URL: {paper.url}",
                        (
                            "Citation count: "
                            f"{paper.citation_count}"
                        ),
                        f"Abstract: {abstract}",
                    ]
                )
            )

        for index, source in enumerate(
            web_result.results,
            start=1,
        ):
            content = (
                source.content[:1500]
                if source.content
                else "Content preview not available."
            )

            source_blocks.append(
                "\n".join(
                    [
                        f"[W{index}] GENERAL WEB SOURCE",
                        f"Title: {source.title}",
                        f"URL: {source.url}",
                        f"Content: {content}",
                    ]
                )
            )

        if not source_blocks:
            raise AnswerGenerationError(
                "No sources are available for answer generation."
            )

        return "\n\n---\n\n".join(source_blocks)

    async def generate(
        self,
        question: str,
        detected_language: str,
        language_code: str,
        scientific_result: SemanticPaperSearchResponse,
        web_result: WebSearchResponse,
    ) -> GeneratedResearchAnswer:
        source_context = self.build_source_context(
            scientific_result=scientific_result,
            web_result=web_result,
        )

        user_prompt = "\n".join(
            [
                f"Original question: {question}",
                (
                    "Required answer language: "
                    f"{detected_language} ({language_code})"
                ),
                "",
                "Available sources:",
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
            update={"evidence": cleaned_evidence}
        )


@lru_cache
def get_answer_generator() -> AnswerGenerator:
    return AnswerGenerator()
