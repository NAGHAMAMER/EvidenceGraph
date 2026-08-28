from abc import ABC, abstractmethod

from app.schemas.paper import Paper, ProviderName


class PaperProvider(ABC):
    name: ProviderName

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:
        """Search for papers and return them in the unified Paper format."""
        raise NotImplementedError


class ProviderRequestError(RuntimeError):
    def __init__(
        self,
        provider: ProviderName,
        message: str,
    ) -> None:
        self.provider = provider
        self.message = message

        super().__init__(f"{provider}: {message}")
