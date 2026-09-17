import re
from typing import Sequence
from app.schemas.document import ExtractedField, OCRBlock


class KeyValueExtractor:
    """
    Extracts semantic key-value fields with directional proximity and inline delimiter matching.
    Supports Invoice Number, Dates, Totals, Due Dates, Payment Terms, Tax, etc.
    """

    KNOWN_LABELS = [
        "invoice number",
        "invoice no",
        "receipt no",
        "receipt number",
        "invoice date",
        "due date",
        "date",
        "payment terms",
        "billed to",
        "bill to",
        "subtotal",
        "tax",
        "total amount",
        "total due",
        "total",
        "cashier",
    ]

    @classmethod
    def extract_fields(cls, blocks: Sequence[OCRBlock]) -> list[ExtractedField]:
        fields: list[ExtractedField] = []
        seen_keys: set[str] = set()

        for b in blocks:
            text = b.text.strip()
            if not text:
                continue

            # 1. Inline colon or hyphen matching: "Invoice Number: INV-2026-9041"
            if ":" in text or " - " in text:
                parts = text.split(":", 1) if ":" in text else text.split(" - ", 1)
                k = parts[0].strip()
                v = parts[1].strip()

                if k.lower() in cls.KNOWN_LABELS or any(lbl in k.lower() for lbl in cls.KNOWN_LABELS):
                    if k.lower() not in seen_keys and len(v) > 0:
                        seen_keys.add(k.lower())
                        fields.append(
                            ExtractedField(
                                id=f"field_{len(fields) + 1:03d}",
                                field=k,
                                value=v,
                                confidence=0.95,
                                page=b.page,
                                bbox=b.bbox,
                                source_block=b.id,
                            )
                        )
                        continue

            # 2. Key-value where key is in one block and value is immediately to the right
            text_lower = text.lower()
            for lbl in cls.KNOWN_LABELS:
                if text_lower == lbl or text_lower.rstrip(":") == lbl:
                    if lbl in seen_keys:
                        continue
                    # Find candidate block to the right (within 250px)
                    candidate = None
                    min_dist = float("inf")
                    for other in blocks:
                        if other.id == b.id or other.page != b.page:
                            continue
                        # Check horizontal alignment
                        v_overlap = max(
                            0.0,
                            min(b.bbox.y2, other.bbox.y2) - max(b.bbox.y1, other.bbox.y1),
                        )
                        if v_overlap > 5 and other.bbox.x1 >= b.bbox.x2 - 10:
                            dist = other.bbox.x1 - b.bbox.x2
                            if 0 <= dist < 300 and dist < min_dist:
                                min_dist = dist
                                candidate = other

                    if candidate:
                        seen_keys.add(lbl)
                        fields.append(
                            ExtractedField(
                                id=f"field_{len(fields) + 1:03d}",
                                field=text.rstrip(":"),
                                value=candidate.text.strip(),
                                confidence=0.92,
                                page=b.page,
                                bbox=candidate.bbox,
                                source_block=candidate.id,
                            )
                        )

        return fields
