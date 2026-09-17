from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class CitationSource(BaseModel):
    page: int
    type: str  # "field", "table", "layout", "ocr"
    reference: str
    bbox: dict[str, float] | None = None
    source_block: str | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[CitationSource] = []
    confidence: float = 1.0


class BaseLLMProvider(ABC):
    """
    Abstract interface for DocNova Document AI assistant.
    """

    @abstractmethod
    async def answer_question(
        self,
        question: str,
        document_context: dict[str, Any],
    ) -> AskResponse:
        raise NotImplementedError
