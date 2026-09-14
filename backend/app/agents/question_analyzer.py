from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable

from app.schemas.research import QuestionAnalysis
from app.services.llm import get_chat_model


SYSTEM_PROMPT = """
You prepare multilingual questions for scientific and web research.

Your tasks:
1. Detect the language used in the user's question.
2. Return its language name and language code.
3. Translate the question into English.
4. Optimize the English translation as a precise research query.
5. Preserve scientific names, technical terms, dates, and numbers.
6. Do not answer the question.
7. Do not add facts that are not present in the question.

The question may be written in any language or dialect.
Return only the requested structured data.
""".strip()


class QuestionAnalyzer:
    def __init__(
        self,
        structured_model: Runnable | None = None,
    ) -> None:
        if structured_model is None:
            structured_model = (
                get_chat_model().with_structured_output(
                    schema=QuestionAnalysis.model_json_schema(),
                    method="json_schema",
                )
            )

        self._structured_model = structured_model

    async def analyze(
        self,
        question: str,
    ) -> QuestionAnalysis:
        clean_question = question.strip()

        if not clean_question:
            raise ValueError("Question cannot be empty.")

        result = await self._structured_model.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=clean_question),
            ]
        )

        return QuestionAnalysis.model_validate(result)


@lru_cache
def get_question_analyzer() -> QuestionAnalyzer:
    return QuestionAnalyzer()
