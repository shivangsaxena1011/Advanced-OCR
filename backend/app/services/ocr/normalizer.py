from typing import Any
import numpy as np

from app.schemas.document import BBox, OCRBlock


class OCRNormalizer:
    """
    Normalizes diverse OCR engine outputs into our standardized OCRBlock schema.
    Supports:
    - PaddleOCR 3.x / PaddleX format ({'rec_texts': [...], 'rec_boxes': [...], 'rec_scores': [...]})
    - PaddleOCR 2.x classic format ([[[ [x1,y1],[x2,y2],[x3,y3],[x4,y4] ], (text, confidence)], ...])
    - Generic raw dict/tuple formats
    """

    @classmethod
    def normalize_paddle_result(
        cls, raw_result: Any, page_number: int = 1, id_prefix: str = "ocr"
    ) -> list[OCRBlock]:
        blocks: list[OCRBlock] = []
        if not raw_result:
            return blocks

        # Handle list of results (PaddleOCR returns a list, usually one per image/page)
        if isinstance(raw_result, list):
            # PaddleOCR 3.x returns [ {'rec_texts': [...], 'rec_boxes': [...], 'rec_scores': [...], 'rec_polys': [...]} ]
            if len(raw_result) > 0 and isinstance(raw_result[0], dict):
                return cls._normalize_paddlex_dict(
                    raw_result[0], page_number=page_number, id_prefix=id_prefix
                )

            # PaddleOCR 2.x returns [ [ [ [[x,y],...], (text, score) ], ... ] ]
            items = raw_result
            if len(raw_result) == 1 and isinstance(raw_result[0], list):
                items = raw_result[0]

            return cls._normalize_legacy_list(
                items, page_number=page_number, id_prefix=id_prefix
            )

        # Handle direct dict
        if isinstance(raw_result, dict):
            return cls._normalize_paddlex_dict(
                raw_result, page_number=page_number, id_prefix=id_prefix
            )

        return blocks

    @classmethod
    def _normalize_paddlex_dict(
        cls, result_dict: dict[str, Any], page_number: int = 1, id_prefix: str = "ocr"
    ) -> list[OCRBlock]:
        blocks: list[OCRBlock] = []
        rec_texts = result_dict.get("rec_texts") or []
        rec_scores = result_dict.get("rec_scores") or []
        rec_boxes = result_dict.get("rec_boxes")
        rec_polys = result_dict.get("rec_polys")

        n = len(rec_texts)
        for i in range(n):
            text = str(rec_texts[i]).strip()
            if not text:
                continue

            score = float(rec_scores[i]) if i < len(rec_scores) else 1.0

            # Bounding box
            bbox = None
            if rec_boxes is not None and i < len(rec_boxes):
                box = rec_boxes[i]
                if hasattr(box, "tolist"):
                    box = box.tolist()
                if len(box) == 4:
                    bbox = BBox(
                        x1=float(box[0]),
                        y1=float(box[1]),
                        x2=float(box[2]),
                        y2=float(box[3]),
                    )

            # Polygon
            poly_points = None
            if rec_polys is not None and i < len(rec_polys):
                poly = rec_polys[i]
                if hasattr(poly, "tolist"):
                    poly_points = [[float(pt[0]), float(pt[1])] for pt in poly.tolist()]
                elif isinstance(poly, (list, tuple)):
                    poly_points = [[float(pt[0]), float(pt[1])] for pt in poly]

            # If bbox missing, calculate from polygon
            if bbox is None and poly_points:
                xs = [pt[0] for pt in poly_points]
                ys = [pt[1] for pt in poly_points]
                bbox = BBox(x1=min(xs), y1=min(ys), x2=max(xs), y2=max(ys))

            if bbox is None:
                continue

            block_id = f"{id_prefix}_p{page_number}_{len(blocks) + 1:03d}"
            blocks.append(
                OCRBlock(
                    id=block_id,
                    text=text,
                    confidence=round(score, 4),
                    bbox=bbox,
                    polygon=poly_points,
                    page=page_number,
                )
            )

        return blocks

    @classmethod
    def _normalize_legacy_list(
        cls, items: list[Any], page_number: int = 1, id_prefix: str = "ocr"
    ) -> list[OCRBlock]:
        blocks: list[OCRBlock] = []
        if not items or not isinstance(items, list):
            return blocks

        for item in items:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue

            poly, text_score = item[0], item[1]
            if not isinstance(text_score, (list, tuple)) or len(text_score) < 2:
                continue

            text = str(text_score[0]).strip()
            score = float(text_score[1])
            if not text:
                continue

            poly_points = []
            if hasattr(poly, "tolist"):
                poly = poly.tolist()
            if isinstance(poly, (list, tuple)):
                poly_points = [[float(pt[0]), float(pt[1])] for pt in poly]

            if not poly_points:
                continue

            xs = [pt[0] for pt in poly_points]
            ys = [pt[1] for pt in poly_points]
            bbox = BBox(x1=min(xs), y1=min(ys), x2=max(xs), y2=max(ys))

            block_id = f"{id_prefix}_p{page_number}_{len(blocks) + 1:03d}"
            blocks.append(
                OCRBlock(
                    id=block_id,
                    text=text,
                    confidence=round(score, 4),
                    bbox=bbox,
                    polygon=poly_points,
                    page=page_number,
                )
            )

        return blocks
