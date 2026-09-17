import os
import re
from typing import Any
import httpx

from app.core.config import settings
from app.schemas.document import DocumentResult
from app.services.llm.base import AskResponse, BaseLLMProvider, CitationSource


class DocNovaAssistant(BaseLLMProvider):
    """
    DocNova Grounded AI Document Assistant.
    Provides source-grounded answers with bounding box citations and hallucination protection.
    """

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = settings.LLM_BASE_URL or "https://api.openai.com/v1"

    async def answer_question(
        self,
        question: str,
        doc: DocumentResult,
    ) -> AskResponse:
        q_clean = question.strip()
        q_lower = q_clean.lower()

        # 1. Retrieve candidate evidence from structured document
        sources: list[CitationSource] = []
        evidence_snippets: list[str] = []

        # Check fields first (highest precision for invoices/receipts)
        for fld in doc.fields:
            field_name = fld.field.lower()
            if any(term in q_lower for term in field_name.split()) or any(term in field_name for term in q_lower.split()):
                sources.append(
                    CitationSource(
                        page=fld.page,
                        type="field",
                        reference=f"{fld.field}: {fld.value}",
                        bbox=fld.bbox.model_dump() if fld.bbox else None,
                        source_block=fld.source_block,
                    )
                )
                evidence_snippets.append(f"Field [{fld.field}]: {fld.value} (Page {fld.page})")

        # Check tables
        for t in doc.tables:
            # Check if query matches table content
            table_matched = False
            for r_idx, row in enumerate(t.rows, 1):
                row_text = " ".join(row).lower()
                if any(term in row_text for term in q_lower.split() if len(term) > 2):
                    table_matched = True
                    evidence_snippets.append(
                        f"Table Row {r_idx} (Page {t.page}): {', '.join(f'{h}: {v}' for h, v in zip(t.headers, row))}"
                    )
            if table_matched:
                sources.append(
                    CitationSource(
                        page=t.page,
                        type="table",
                        reference=f"Table {t.table_id}",
                        bbox=t.bbox.model_dump(),
                        source_block=t.table_id,
                    )
                )

        # Check OCR blocks / layout paragraphs
        for p in doc.pages:
            for b in p.ocr_blocks:
                b_lower = b.text.lower()
                # If key query tokens are in this block
                query_words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
                if query_words and any(qw in b_lower for qw in query_words):
                    if len(sources) < 6:
                        sources.append(
                            CitationSource(
                                page=p.page,
                                type="ocr",
                                reference=b.text,
                                bbox=b.bbox.model_dump(),
                                source_block=b.id,
                            )
                        )
                        evidence_snippets.append(f"Page {p.page}: {b.text}")

        # 2. If external OpenAI-compatible LLM is configured, query it with strict grounded context
        if self.api_key and self.provider == "openai":
            try:
                answer = await self._query_openai(q_clean, evidence_snippets, doc)
                return AskResponse(
                    question=q_clean,
                    answer=answer,
                    sources=sources[:4],
                    confidence=0.95,
                )
            except Exception:
                pass  # fallback to grounded extractor

        # 3. Grounded Deterministic Responder (Hallucination protected)
        if not sources and not evidence_snippets:
            return AskResponse(
                question=q_clean,
                answer="I couldn't find sufficient evidence for that answer in the uploaded document.",
                sources=[],
                confidence=0.2,
            )

        # Formulate direct answer from gathered evidence
        if any("total" in q_lower for _ in [1]):
            total_fld = next((f for f in doc.fields if "total" in f.field.lower()), None)
            if total_fld:
                return AskResponse(
                    question=q_clean,
                    answer=f"The total specified in the document is {total_fld.value}.",
                    sources=[s for s in sources if "total" in s.reference.lower()][:2],
                    confidence=0.98,
                )

        if any(w in q_lower for w in ["invoice number", "invoice no", "receipt no", "id"]):
            id_fld = next((f for f in doc.fields if "invoice" in f.field.lower() or "receipt" in f.field.lower() or "id" in f.field.lower()), None)
            if id_fld:
                return AskResponse(
                    question=q_clean,
                    answer=f"The document identifier is {id_fld.value} ({id_fld.field}).",
                    sources=[s for s in sources if id_fld.value in s.reference][:1],
                    confidence=0.98,
                )

        if any(w in q_lower for w in ["date", "when", "due"]):
            date_fld = next((f for f in doc.fields if "date" in f.field.lower()), None)
            if date_fld:
                return AskResponse(
                    question=q_clean,
                    answer=f"The relevant date found is {date_fld.value} ({date_fld.field}).",
                    sources=[s for s in sources if date_fld.value in s.reference][:1],
                    confidence=0.97,
                )

        # General answer synthesised from top evidence snippets
        top_snippets = "\n• ".join(evidence_snippets[:3])
        return AskResponse(
            question=q_clean,
            answer=f"Based on the document content:\n• {top_snippets}",
            sources=sources[:3],
            confidence=0.90,
        )

    async def _query_openai(
        self, question: str, evidence: list[str], doc: DocumentResult
    ) -> str:
        prompt = (
            f"You are DocNova, a helpful assistant answering questions about an uploaded document ({doc.filename}).\n"
            f"Ground your answer ONLY in the following extracted evidence. If the evidence is insufficient, state exactly: "
            f"'I couldn't find sufficient evidence for that answer in the uploaded document.'\n\n"
            f"Evidence:\n{chr(10).join(evidence)}\n\n"
            f"Question: {question}\nAnswer:"
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
            )
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
            raise RuntimeError("LLM request failed")
