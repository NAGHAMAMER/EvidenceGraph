from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from app.schemas.follow_up import FollowUpAnalysis
from app.schemas.research import ResearchSessionDetail
from app.services.llm import get_chat_model


SYSTEM_PROMPT = """
You route multilingual follow-up questions in a saved research session.

Your tasks:
1. Detect the language of the new follow-up question.
2. Return its human-readable language name and language code.
3. Rewrite it as a complete standalone English research query.
4. Decide whether the saved research memory contains enough evidence
   to answer the follow-up safely.
5. Set needs_search to false only when the saved sources and previous
   evidence are sufficient to support the answer.
6. Set needs_search to true when the question introduces a new topic,
   asks for missing details, asks for newer information, expands the
   research scope, or cannot be supported by the saved sources.
7. Previous generated answers help interpret the conversation, but
   unsupported model knowledge must not be treated as evidence.
8. Preserve scientific names, technical terms, dates, and numbers.
9. Do not answer the follow-up question.
10. Return only the requested structured data.
""".strip()


class FollowUpAnalyzer:
    def __init__(
        self,
        structured_model: Runnable | None = None,
    ) -> None:
        if structured_model is None:
            structured_model = (
                get_chat_model().with_structured_output(
                    schema=FollowUpAnalysis.model_json_schema(),
                    method="json_schema",
                )
            )

        self._structured_model = structured_model

    @staticmethod
    def build_memory_context(
        session: ResearchSessionDetail,
    ) -> str:
        blocks = [
            (
                "Initial research question: "
                f"{session.initial_question}"
            )
        ]

        seen_papers: set[str] = set()
        seen_web_sources: set[str] = set()

        for turn in session.turns[-5:]:
            blocks.append(
                "\n".join(
                    [
                        (
                            f"Conversation turn "
                            f"{turn.turn_index}:"
                        ),
                        f"Question: {turn.question}",
                        f"Answer: {turn.answer[:2000]}",
                    ]
                )
            )

            for paper in turn.papers:
                paper_key = (
                    paper.doi
                    or paper.id
                ).strip().casefold()

                if paper_key in seen_papers:
                    continue

                seen_papers.add(paper_key)

                abstract = (
                    paper.abstract[:1000]
                    if paper.abstract
                    else "Abstract not available."
                )

                blocks.append(
                    "\n".join(
                        [
                            "Saved scientific paper:",
                            f"Title: {paper.title}",
                            f"DOI: {paper.doi}",
                            f"Abstract: {abstract}",
                        ]
                    )
                )

                if len(seen_papers) >= 10:
                    break

            for source in turn.web_sources:
                source_key = source.url.strip().casefold()

                if source_key in seen_web_sources:
                    continue

                seen_web_sources.add(source_key)

                content = (
                    source.content[:700]
                    if source.content
                    else "Content preview not available."
                )

                blocks.append(
                    "\n".join(
                        [
                            "Saved web source:",
                            f"Title: {source.title}",
                            f"URL: {source.url}",
                            f"Content: {content}",
                        ]
                    )
                )

                if len(seen_web_sources) >= 10:
                    break

        return "\n\n---\n\n".join(blocks)

    async def analyze(
        self,
        question: str,
        session: ResearchSessionDetail,
    ) -> FollowUpAnalysis:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError(
                "Follow-up question cannot be empty."
            )

        memory_context = self.build_memory_context(session)

        user_prompt = "\n".join(
            [
                "Saved research memory:",
                memory_context,
                "",
                "New follow-up question:",
                clean_question,
            ]
        )

        result = await self._structured_model.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
        )

        return FollowUpAnalysis.model_validate(result)


@lru_cache
def get_follow_up_analyzer() -> FollowUpAnalyzer:
    return FollowUpAnalyzer()
