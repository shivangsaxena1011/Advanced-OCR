import csv
import io
import json
from app.schemas.document import DocumentResult


class DocumentExporter:
    """
    Exports structured documents into TXT, Markdown, HTML, CSV, and JSON
    strictly preserving the logical reading order.
    """

    @classmethod
    def to_text(cls, doc: DocumentResult) -> str:
        lines: list[str] = []
        lines.append(f"=== {doc.filename} ===")
        if doc.document_type:
            lines.append(f"Document Type: {doc.document_type.upper()}")
        lines.append("")

        for page in doc.pages:
            lines.append(f"--- Page {page.page} ---")
            for block in page.ocr_blocks:
                lines.append(block.text)
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def to_markdown(cls, doc: DocumentResult) -> str:
        lines: list[str] = []
        title = doc.filename
        lines.append(f"# {title}\n")

        if doc.document_type:
            lines.append(f"> **Document Type**: {doc.document_type.capitalize()} (Confidence: {int((doc.document_type_confidence or 0.8) * 100)}%)\n")

        # Key fields if available
        if doc.fields:
            lines.append("### Key Fields\n")
            for f in doc.fields:
                lines.append(f"- **{f.field}**: {f.value}")
            lines.append("")

        # Content by page
        for page in doc.pages:
            if len(doc.pages) > 1:
                lines.append(f"## Page {page.page}\n")

            # If layout blocks exist, format headings vs paragraphs
            if page.layout_blocks:
                for lb in page.layout_blocks:
                    if lb.type == "title":
                        lines.append(f"## {lb.text}\n")
                    elif lb.type == "heading":
                        lines.append(f"### {lb.text}\n")
                    elif lb.type == "list":
                        for item in lb.text.split("\n"):
                            lines.append(f"- {item}")
                        lines.append("")
                    else:
                        lines.append(f"{lb.text}\n")
            else:
                for block in page.ocr_blocks:
                    lines.append(block.text)
                lines.append("")

        # Tables in Markdown format
        if doc.tables:
            lines.append("## Extracted Tables\n")
            for t in doc.tables:
                lines.append(f"### Table {t.table_id} (Page {t.page})\n")
                if t.headers:
                    header_line = "| " + " | ".join(t.headers) + " |"
                    separator = "| " + " | ".join(["---"] * len(t.headers)) + " |"
                    lines.append(header_line)
                    lines.append(separator)
                for row in t.rows:
                    # Pad row if shorter than headers
                    padded_row = row + [""] * (len(t.headers) - len(row))
                    lines.append("| " + " | ".join(padded_row) + " |")
                lines.append("")

        return "\n".join(lines)

    @classmethod
    def to_html(cls, doc: DocumentResult) -> str:
        md = cls.to_markdown(doc)
        # Clean HTML wrapper
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{doc.filename} - AORL Export</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1e293b; }}
h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
h2 {{ color: #1e293b; margin-top: 28px; }}
h3 {{ color: #334155; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }}
th {{ background-color: #f1f5f9; font-weight: 600; }}
blockquote {{ border-left: 4px solid #3b82f6; margin: 0; padding-left: 16px; color: #64748b; }}
</style>
</head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{md}</pre>
</body>
</html>"""
        return html

    @classmethod
    def to_csv(cls, doc: DocumentResult) -> str:
        output = io.StringIO()
        writer = csv.writer(output)

        if not doc.tables:
            # If no tables, export OCR blocks with coordinates
            writer.writerow(["Page", "Block ID", "Text", "Confidence", "x1", "y1", "x2", "y2"])
            for page in doc.pages:
                for b in page.ocr_blocks:
                    writer.writerow([
                        page.page,
                        b.id,
                        b.text,
                        b.confidence,
                        b.bbox.x1,
                        b.bbox.y1,
                        b.bbox.x2,
                        b.bbox.y2,
                    ])
        else:
            for t in doc.tables:
                writer.writerow([f"# Table {t.table_id} (Page {t.page})"])
                if t.headers:
                    writer.writerow(t.headers)
                for row in t.rows:
                    writer.writerow(row)
                writer.writerow([])  # blank line between tables

        return output.getvalue()

    @classmethod
    def to_json(cls, doc: DocumentResult) -> str:
        return doc.model_dump_json(indent=2)
