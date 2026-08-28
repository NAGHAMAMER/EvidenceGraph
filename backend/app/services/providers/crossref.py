from datetime import date
from html import unescape
import re
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.paper import Paper, PaperAuthor, ProviderName
from app.services.providers.base import PaperProvider, ProviderRequestError


class CrossrefProvider(PaperProvider):
    name: ProviderName = "crossref"

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
            "query.bibliographic": clean_query,
            "rows": max(1, min(limit, 100)),
        }

        headers = {
            "User-Agent": f"{settings.app_name}/0.1",
        }

        email = settings.crossref_email.strip()

        if email and email != "your_email@example.com":
            params["mailto"] = email
            headers["User-Agent"] = (
                f"{settings.app_name}/0.1 (mailto:{email})"
            )

        try:
            if self._client is not None:
                response = await self._client.get(
                    self._works_url,
                    params=params,
                    headers=headers,
                )
            else:
                async with httpx.AsyncClient(
                    timeout=settings.request_timeout_seconds
                ) as client:
                    response = await client.get(
                        self._works_url,
                        params=params,
                        headers=headers,
                    )

            response.raise_for_status()
            payload = response.json()

        except httpx.HTTPStatusError as error:
            raise ProviderRequestError(
                self.name,
                f"Crossref returned HTTP {error.response.status_code}",
            ) from error

        except httpx.RequestError as error:
            raise ProviderRequestError(
                self.name,
                f"Could not connect to Crossref: {error}",
            ) from error

        except ValueError as error:
            raise ProviderRequestError(
                self.name,
                "Crossref returned invalid JSON.",
            ) from error

        message = payload.get("message")

        if not isinstance(message, dict):
            raise ProviderRequestError(
                self.name,
                "Crossref response does not contain a valid message.",
            )

        items = message.get("items", [])

        if not isinstance(items, list):
            raise ProviderRequestError(
                self.name,
                "Crossref response does not contain a valid items list.",
            )

        papers: list[Paper] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            paper = self._map_work(item)

            if paper is not None:
                papers.append(paper)

        return papers

    @property
    def _works_url(self) -> str:
        base_url = settings.crossref_base_url.rstrip("/")
        return f"{base_url}/works"

    @staticmethod
    def _map_work(item: dict[str, Any]) -> Paper | None:
        title = CrossrefProvider._first_text(item.get("title"))
        doi = CrossrefProvider._normalize_doi(item.get("DOI"))

        url = item.get("URL")

        if doi and not url:
            url = f"https://doi.org/{doi}"

        if not title or not (doi or url):
            return None

        authors: list[PaperAuthor] = []

        for author_data in item.get("author") or []:
            given_name = str(
                author_data.get("given") or ""
            ).strip()

            family_name = str(
                author_data.get("family") or ""
            ).strip()

            author_name = " ".join(
                part
                for part in [given_name, family_name]
                if part
            )

            if not author_name:
                author_name = str(
                    author_data.get("name") or ""
                ).strip()

            if not author_name:
                continue

            authors.append(
                PaperAuthor(
                    name=author_name,
                    orcid=author_data.get("ORCID"),
                )
            )

        publication_year, publication_date = (
            CrossrefProvider._extract_publication_date(item)
        )

        venue = CrossrefProvider._first_text(
            item.get("container-title")
        )

        topics = [
            str(subject).strip()
            for subject in item.get("subject") or []
            if str(subject).strip()
        ]

        return Paper(
            id=doi or str(url),
            doi=doi,
            title=title,
            abstract=CrossrefProvider._clean_abstract(
                item.get("abstract")
            ),
            authors=authors,
            publication_year=publication_year,
            publication_date=publication_date,
            venue=venue,
            url=url,
            pdf_url=CrossrefProvider._extract_pdf_url(item),
            citation_count=item.get("is-referenced-by-count") or 0,
            is_open_access=None,
            topics=topics,
            providers=["crossref"],
        )

    @staticmethod
    def _first_text(value: Any) -> str | None:
        if isinstance(value, list):
            for item in value:
                text = str(item or "").strip()

                if text:
                    return text

            return None

        text = str(value or "").strip()
        return text or None

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
    def _clean_abstract(value: Any) -> str | None:
        if not value:
            return None

        abstract = str(value)

        abstract = re.sub(
            r"<[^>]+>",
            " ",
            abstract,
        )

        abstract = unescape(abstract)
        abstract = re.sub(r"\s+", " ", abstract).strip()

        return abstract or None

    @staticmethod
    def _extract_publication_date(
        item: dict[str, Any],
    ) -> tuple[int | None, date | None]:
        date_fields = [
            "published-print",
            "published-online",
            "published",
            "issued",
        ]

        for field in date_fields:
            date_data = item.get(field) or {}
            date_parts = date_data.get("date-parts") or []

            if not date_parts or not date_parts[0]:
                continue

            parts = date_parts[0]

            try:
                year = int(parts[0])
            except (TypeError, ValueError, IndexError):
                continue

            if len(parts) < 3:
                return year, None

            try:
                full_date = date(
                    year,
                    int(parts[1]),
                    int(parts[2]),
                )
            except (TypeError, ValueError, IndexError):
                return year, None

            return year, full_date

        return None, None

    @staticmethod
    def _extract_pdf_url(
        item: dict[str, Any],
    ) -> str | None:
        for link in item.get("link") or []:
            url = str(link.get("URL") or "").strip()
            content_type = str(
                link.get("content-type") or ""
            ).lower()

            if url and (
                "pdf" in content_type
                or url.lower().endswith(".pdf")
            ):
                return url

        return None
