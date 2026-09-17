import re
from typing import Sequence
from app.schemas.document import EntityResult, OCRBlock


class EntityExtractor:
    """
    Extracts named entities from recognized OCR blocks using deterministic patterns and regex:
    EMAIL, URL, PHONE, DATE, CURRENCY, AMOUNT, DOCUMENT_ID, ORGANIZATION, PERSON.
    """

    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    URL_PATTERN = re.compile(r"https?://(?:www\.)?[a-zA-Z0-9./\-_]+\.[a-zA-Z]{2,}(?:/[^\s]*)?")
    PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    DATE_PATTERN = re.compile(
        r"\b(?:\d{4}[-/.]\d{2}[-/.]\d{2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})\b",
        re.IGNORECASE,
    )
    AMOUNT_PATTERN = re.compile(r"(?:[\$\€\£\₹]|\bUSD|\bEUR|\bINR)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)")
    DOC_ID_PATTERN = re.compile(
        r"\b(?:INV|REC|DOC|ID|PO|ORD)[-_]?[0-9A-Za-z]{4,15}\b", re.IGNORECASE
    )
    ORG_PATTERN = re.compile(
        r"\b[A-Z][A-Za-z0-9\s&]{2,30}\s+(?:Corp|Corporation|Inc|LLC|Ltd|Limited|Group|Co|Technologies|Solutions|Services)\b"
    )

    @classmethod
    def extract_entities(cls, blocks: Sequence[OCRBlock]) -> list[EntityResult]:
        entities: list[EntityResult] = []
        seen_texts: set[str] = set()

        for b in blocks:
            text = b.text.strip()
            if not text:
                continue

            # 1. Emails
            for match in cls.EMAIL_PATTERN.finditer(text):
                val = match.group(0)
                if val.lower() not in seen_texts:
                    seen_texts.add(val.lower())
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="EMAIL",
                            text=val,
                            confidence=0.99,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

            # 2. URLs
            for match in cls.URL_PATTERN.finditer(text):
                val = match.group(0)
                if val.lower() not in seen_texts:
                    seen_texts.add(val.lower())
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="URL",
                            text=val,
                            confidence=0.98,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

            # 3. Phone numbers
            for match in cls.PHONE_PATTERN.finditer(text):
                val = match.group(0)
                if len(val.strip()) >= 10 and val not in seen_texts:
                    seen_texts.add(val)
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="PHONE",
                            text=val.strip(),
                            confidence=0.95,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

            # 4. Dates
            for match in cls.DATE_PATTERN.finditer(text):
                val = match.group(0)
                if val not in seen_texts:
                    seen_texts.add(val)
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="DATE",
                            text=val,
                            confidence=0.96,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

            # 5. Amounts
            for match in cls.AMOUNT_PATTERN.finditer(text):
                val = match.group(0)
                if val not in seen_texts:
                    seen_texts.add(val)
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="AMOUNT",
                            text=val.strip(),
                            confidence=0.97,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

            # 6. Document IDs
            for match in cls.DOC_ID_PATTERN.finditer(text):
                val = match.group(0)
                if val not in seen_texts:
                    seen_texts.add(val)
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="DOCUMENT_ID",
                            text=val,
                            confidence=0.94,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

            # 7. Organizations
            for match in cls.ORG_PATTERN.finditer(text):
                val = match.group(0)
                if val not in seen_texts:
                    seen_texts.add(val)
                    entities.append(
                        EntityResult(
                            id=f"ent_{len(entities) + 1:03d}",
                            type="ORGANIZATION",
                            text=val.strip(),
                            confidence=0.91,
                            page=b.page,
                            bbox=b.bbox,
                            source_block=b.id,
                        )
                    )

        return entities
