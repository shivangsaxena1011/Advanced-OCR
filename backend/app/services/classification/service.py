import re
from typing import Sequence
from app.schemas.document import DocumentResult, OCRBlock


class DocumentClassifier:
    """
    Classifies documents based on textual keywords, layout density, and structural cues:
    invoice, receipt, resume, research_paper, report, form, certificate, letter, statement, unknown.
    """

    CATEGORIES = {
        "invoice": [
            "invoice",
            "billed to",
            "bill to",
            "invoice number",
            "due date",
            "payment terms",
            "subtotal",
            "tax invoice",
        ],
        "receipt": [
            "receipt",
            "cashier",
            "store #",
            "register",
            "change due",
            "subtotal",
            "total amount",
            "thank you for shopping",
        ],
        "resume": [
            "curriculum vitae",
            "resume",
            "experience",
            "education",
            "skills",
            "employment",
            "certifications",
            "summary",
        ],
        "research_paper": [
            "abstract",
            "introduction",
            "methodology",
            "references",
            "conclusion",
            "results",
            "dataset",
            "doi:",
        ],
        "certificate": [
            "certificate of",
            "certify that",
            "hereby granted",
            "in recognition of",
            "awarded to",
        ],
        "form": [
            "application form",
            "please print",
            "signature of applicant",
            "date of birth",
            "checkbox",
        ],
        "letter": [
            "dear",
            "sincerely",
            "regards",
            "to whom it may concern",
            "faithfully",
        ],
    }

    @classmethod
    def classify_document(cls, blocks: Sequence[OCRBlock]) -> tuple[str, float]:
        if not blocks:
            return "unknown", 0.0

        full_text = " ".join(b.text.lower() for b in blocks)

        scores: dict[str, int] = {cat: 0 for cat in cls.CATEGORIES}

        for cat, keywords in cls.CATEGORIES.items():
            for kw in keywords:
                if kw in full_text:
                    scores[cat] += 2
                    # Exact word boundary match gets extra weight
                    if re.search(rf"\b{re.escape(kw)}\b", full_text):
                        scores[cat] += 1

        best_cat = "unknown"
        best_score = 0

        for cat, sc in scores.items():
            if sc > best_score:
                best_score = sc
                best_cat = cat

        if best_score == 0:
            return "unknown", 0.30

        # Compute confidence based on match count (scaled between 0.65 and 0.96)
        confidence = min(0.96, 0.60 + (best_score * 0.06))
        return best_cat, round(confidence, 2)
