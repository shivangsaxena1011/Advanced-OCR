from typing import Any
from pydantic import BaseModel
from app.schemas.document import DocumentResult


class FieldDiff(BaseModel):
    field: str
    status: str  # "MATCH", "CHANGED", "ADDED_IN_B", "REMOVED_IN_B"
    value_a: str | None = None
    value_b: str | None = None


class CompareResponse(BaseModel):
    doc_a_id: str
    doc_a_name: str
    doc_b_id: str
    doc_b_name: str
    similarity_score: float
    fields_diff: list[FieldDiff]
    entities_common: list[str]
    entities_added: list[str]
    entities_removed: list[str]
    tables_summary: dict[str, Any]


class DocumentComparator:
    """
    Compares two documents across text, extracted key-values, tables, and entities.
    """

    @classmethod
    def compare(cls, doc_a: DocumentResult, doc_b: DocumentResult) -> CompareResponse:
        # 1. Compare fields
        fields_a = {f.field.lower(): f.value for f in doc_a.fields}
        fields_b = {f.field.lower(): f.value for f in doc_b.fields}

        all_keys = set(fields_a.keys()) | set(fields_b.keys())
        field_diffs: list[FieldDiff] = []

        matches = 0
        for k in sorted(all_keys):
            v_a = fields_a.get(k)
            v_b = fields_b.get(k)

            if v_a is not None and v_b is not None:
                if v_a.strip().lower() == v_b.strip().lower():
                    status = "MATCH"
                    matches += 1
                else:
                    status = "CHANGED"
            elif v_a is not None:
                status = "REMOVED_IN_B"
            else:
                status = "ADDED_IN_B"

            field_diffs.append(
                FieldDiff(
                    field=k,
                    status=status,
                    value_a=v_a,
                    value_b=v_b,
                )
            )

        # 2. Compare entities
        ents_a = {f"{e.type}:{e.text.lower()}" for e in doc_a.entities}
        ents_b = {f"{e.type}:{e.text.lower()}" for e in doc_b.entities}

        common = sorted(ents_a & ents_b)
        added = sorted(ents_b - ents_a)
        removed = sorted(ents_a - ents_b)

        # 3. Tables summary
        tables_summary = {
            "doc_a_tables_count": len(doc_a.tables),
            "doc_b_tables_count": len(doc_b.tables),
            "match": len(doc_a.tables) == len(doc_b.tables),
        }

        # Calculate overall similarity score (0 to 1)
        total_items = max(1, len(all_keys) + max(len(ents_a), len(ents_b)))
        matched_items = matches + len(common)
        similarity = round(min(1.0, matched_items / total_items), 2)

        return CompareResponse(
            doc_a_id=doc_a.document_id,
            doc_a_name=doc_a.filename,
            doc_b_id=doc_b.document_id,
            doc_b_name=doc_b.filename,
            similarity_score=similarity,
            fields_diff=field_diffs,
            entities_common=common,
            entities_added=added,
            entities_removed=removed,
            tables_summary=tables_summary,
        )
