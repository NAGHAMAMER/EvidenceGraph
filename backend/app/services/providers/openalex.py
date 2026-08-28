from typing import Any

import httpx

from app.core.config import settings
from app.schemas.paper import Paper, PaperAuthor, ProviderName
from app.services.providers.base import PaperProvider, ProviderRequestError


OPENALEX_SELECT_FIELDS = ",".join(
    [
        "id",
        "doi",
        "display_name",
        "publication_year",
        "publication_date",
        "authorships",
        "abstract_inverted_index",
        "primary_location",
        "best_oa_location",
        "open_access",
        "cited_by_count",
        "topics",
    ]
)


class OpenAlexProvider(PaperProvider):
    name: ProviderName = "openalex"

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client = client

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:
        clean_query = query.strip()

        if not clean_query:
            return []

        params: dict[str, str | int] = {
            "search": clean_query,
            "per_page": max(1, min(limit, 100)),
            "select": OPENALEX_SELECT_FIELDS,
        }

        if settings.openalex_api_key.strip():
            params["api_key"] = settings.openalex_api_key.strip()

        try:
            if self._client is not None:
                response = await self._client.get(
                    self._works_url,
                    params=params,
                )
            else:
                async with httpx.AsyncClient(
                    timeout=settings.request_timeout_seconds
                ) as client:
                    response = await client.get(
                        self._works_url,
                        params=params,
                    )

            response.raise_for_status()
            payload = response.json()

        except httpx.HTTPStatusError as error:
            raise ProviderRequestError(
                self.name,
                f"OpenAlex returned HTTP {error.response.status_code}",
            ) from error

        except httpx.RequestError as error:
            raise ProviderRequestError(
                self.name,
                f"Could not connect to OpenAlex: {error}",
            ) from error

        except ValueError as error:
            raise ProviderRequestError(
                self.name,
                "OpenAlex returned invalid JSON.",
            ) from error

        results = payload.get("results", [])

        if not isinstance(results, list):
            raise ProviderRequestError(
                self.name,
                "OpenAlex response does not contain a valid results list.",
            )

        papers: list[Paper] = []

        for work in results:
            if not isinstance(work, dict):
                continue

            paper = self._map_work(work)

            if paper is not None:
                papers.append(paper)

        return papers

    @property
    def _works_url(self) -> str:
        base_url = settings.openalex_base_url.rstrip("/")
        return f"{base_url}/works"

    @staticmethod
    def _map_work(work: dict[str, Any]) -> Paper | None:
        title = str(work.get("display_name") or "").strip()
        openalex_id = str(work.get("id") or "").strip()
        doi = OpenAlexProvider._normalize_doi(work.get("doi"))

        if not title or not (doi or openalex_id):
            return None

        authors: list[PaperAuthor] = []

        for authorship in work.get("authorships") or []:
            author_data = authorship.get("author") or {}
            author_name = str(
                author_data.get("display_name") or ""
            ).strip()

            if not author_name:
                continue

            authors.append(
                PaperAuthor(
                    name=author_name,
                    orcid=author_data.get("orcid"),
                )
            )

        primary_location = work.get("primary_location") or {}
        best_oa_location = work.get("best_oa_location") or {}
        open_access = work.get("open_access") or {}

        source = primary_location.get("source") or {}
        venue = str(source.get("display_name") or "").strip() or None

        topics: list[str] = []

        for topic in work.get("topics") or []:
            topic_name = str(topic.get("display_name") or "").strip()

            if topic_name:
                topics.append(topic_name)

        url = (
            primary_location.get("landing_page_url")
            or open_access.get("oa_url")
            or (f"https://doi.org/{doi}" if doi else None)
            or openalex_id
        )

        pdf_url = (
            best_oa_location.get("pdf_url")
            or primary_location.get("pdf_url")
        )

        return Paper(
            id=doi or openalex_id,
            doi=doi,
            title=title,
            abstract=OpenAlexProvider._reconstruct_abstract(
                work.get("abstract_inverted_index")
            ),
            authors=authors,
            publication_year=work.get("publication_year"),
            publication_date=work.get("publication_date"),
            venue=venue,
            url=url,
            pdf_url=pdf_url,
            citation_count=work.get("cited_by_count") or 0,
            is_open_access=open_access.get("is_oa"),
            topics=topics,
            providers=["openalex"],
        )

    @staticmethod
    def _normalize_doi(value: Any) -> str | None:
        if not value:
            return None

        doi = str(value).strip().lower()

        for prefix in (
            "https://doi.org/",
            "http://doi.org/",
            "doi:",
        ):
            if doi.startswith(prefix):
                doi = doi.removeprefix(prefix)

        return doi or None

    @staticmethod
    def _reconstruct_abstract(
        inverted_index: dict[str, list[int]] | None,
    ) -> str | None:
        if not inverted_index:
            return None

        positioned_words: list[tuple[int, str]] = []

        for word, positions in inverted_index.items():
            for position in positions:
                positioned_words.append((position, word))

        positioned_words.sort(key=lambda item: item[0])

        abstract = " ".join(
            word for _, word in positioned_words
        )

        return abstract or None
