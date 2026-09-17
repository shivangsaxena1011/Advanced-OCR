import re
from typing import Sequence
from app.schemas.document import BBox, OCRBlock


class LayoutClassifier:
    """
    Classifies a cluster of OCR blocks into semantic document types:
    title, heading, paragraph, list, table, header, footer, form_field, key_value.
    """

    @classmethod
    def classify_cluster(
        cls,
        blocks: Sequence[OCRBlock],
        page_width: int,
        page_height: int,
    ) -> tuple[str, float]:
        if not blocks:
            return "paragraph", 0.5

        full_text = " ".join(b.text for b in blocks).strip()
        avg_height = sum(b.bbox.height for b in blocks) / len(blocks)
        union_box = BBox(
            x1=min(b.bbox.x1 for b in blocks),
            y1=min(b.bbox.y1 for b in blocks),
            x2=max(b.bbox.x2 for b in blocks),
            y2=max(b.bbox.y2 for b in blocks),
        )

        # 1. Header / Footer based on relative vertical position
        rel_top = union_box.y1 / page_height
        rel_bottom = union_box.y2 / page_height

        if rel_top < 0.08 and len(full_text) < 100:
            return "header", 0.88

        if rel_bottom > 0.94 and (
            re.search(r"page\s*\d+|\d+\s*of\s*\d+|copyright", full_text, re.IGNORECASE)
            or len(full_text) < 60
        ):
            return "footer", 0.92

        # 2. Title: top 25% of page, large font height, short length
        if rel_top < 0.25 and avg_height >= 18 and len(full_text) < 120:
            return "title", 0.94

        # 3. Heading: short text, uppercase or title case, or numbered (e.g. "1. Introduction")
        is_numbered = bool(re.match(r"^(?:\d+\.|\d+\.\d+|[A-Z]\.)\s+", full_text))
        is_short = len(full_text.split()) <= 10 and len(full_text) < 70
        is_caps = full_text.isupper() and len(full_text) > 3

        if is_numbered or (is_short and (is_caps or avg_height > 15)):
            return "heading", 0.91

        # 4. List item: bullet, dash, or number
        if re.match(r"^(?:[\u2022\u2023\u25E6\u2043\u2219\*\-\+]|\d+[\.\)])\s+", full_text):
            return "list", 0.89

        # 5. Key-Value: e.g. "Date: 2026-09-15" or "Total: $100"
        if re.match(r"^[A-Za-z\s]{2,25}\s*[:=]\s*.+$", full_text):
            return "key_value", 0.87

        # 6. Default: Paragraph
        return "paragraph", 0.85
