import io
from pathlib import Path
from typing import List, Tuple
import fitz  # PyMuPDF
from PIL import Image
import numpy as np


class PDFProcessor:
    """
    Handles multi-page PDF rendering to images and thumbnails using PyMuPDF.
    Treats each page as a high-fidelity image for robust scanned/digital document OCR.
    """

    @staticmethod
    def render_pdf_pages(
        pdf_path: Path | bytes,
        dpi: int = 200,
        thumbnail_max_size: int = 250,
    ) -> list[tuple[int, Image.Image, Image.Image]]:
        """
        Renders each page of a PDF document.
        Returns a list of tuples: (page_number_1_indexed, page_image, thumbnail_image)
        """
        results: list[tuple[int, Image.Image, Image.Image]] = []

        if isinstance(pdf_path, (str, Path)):
            doc = fitz.open(str(pdf_path))
        else:
            doc = fitz.open(stream=pdf_path, filetype="pdf")

        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Generate thumbnail
            thumb = img.copy()
            thumb.thumbnail((thumbnail_max_size, thumbnail_max_size), Image.Resampling.LANCZOS)
            
            page_num = page_idx + 1
            results.append((page_num, img, thumb))

        doc.close()
        return results

    @staticmethod
    def get_page_count(pdf_path: Path | bytes) -> int:
        if isinstance(pdf_path, (str, Path)):
            doc = fitz.open(str(pdf_path))
        else:
            doc = fitz.open(stream=pdf_path, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
