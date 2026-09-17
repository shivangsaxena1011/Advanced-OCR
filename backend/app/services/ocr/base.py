from abc import ABC, abstractmethod
from typing import Any
import numpy as np
from PIL import Image

from app.schemas.document import OCRBlock


class BaseOCREngine(ABC):
    """
    Abstract base class for OCR engines.
    Any OCR provider (PaddleOCR, Tesseract, cloud, mock/fallback) implements this interface.
    """

    @abstractmethod
    def process_image(
        self, image: np.ndarray | Image.Image, page_number: int = 1
    ) -> list[OCRBlock]:
        """
        Process an image and return a list of normalized OCRBlock objects.
        Coordinates are relative to the original unscaled image.
        """
        raise NotImplementedError("Subclasses must implement process_image")

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return human-readable engine name and version."""
        raise NotImplementedError
