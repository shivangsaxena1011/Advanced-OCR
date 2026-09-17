from app.schemas.document import BBox, DocumentMetadata, DocumentResult, OCRBlock, PageResult
from app.services.layout.detector import LayoutDetector
from app.services.reading_order.sorter import ReadingOrderResolver
from app.services.tables.detector import TableExtractor
from app.services.entities.extractor import EntityExtractor
from app.services.fields.extractor import KeyValueExtractor
from app.services.classification.service import DocumentClassifier
from app.services.export.exporter import DocumentExporter


def test_layout_detection():
    blocks = [
        OCRBlock(id="ocr_1", text="ANNUAL FINANCIAL REPORT", confidence=0.98, bbox=BBox(x1=100, y1=50, x2=500, y2=80), page=1),
        OCRBlock(id="ocr_2", text="1. Executive Summary", confidence=0.96, bbox=BBox(x1=100, y1=120, x2=300, y2=145), page=1),
        OCRBlock(id="ocr_3", text="During fiscal year 2026, our platform", confidence=0.95, bbox=BBox(x1=100, y1=160, x2=550, y2=180), page=1),
        OCRBlock(id="ocr_4", text="demonstrated 140% growth in document throughput.", confidence=0.95, bbox=BBox(x1=100, y1=185, x2=550, y2=205), page=1),
    ]

    layout_blocks = LayoutDetector.detect_layout(blocks, page_width=800, page_height=1000, page_number=1)
    assert len(layout_blocks) >= 2
    types = [b.type for b in layout_blocks]
    assert "title" in types or "heading" in types


def test_reading_order_two_columns():
    # Title across top
    title = OCRBlock(id="title", text="Two Column Study", confidence=0.99, bbox=BBox(x1=50, y1=40, x2=750, y2=80), page=1)
    # Column 1
    col1_1 = OCRBlock(id="col1_1", text="Col 1 Top", confidence=0.95, bbox=BBox(x1=50, y1=120, x2=350, y2=150), page=1)
    col1_2 = OCRBlock(id="col1_2", text="Col 1 Bottom", confidence=0.95, bbox=BBox(x1=50, y1=200, x2=350, y2=230), page=1)
    # Column 2
    col2_1 = OCRBlock(id="col2_1", text="Col 2 Top", confidence=0.95, bbox=BBox(x1=450, y1=120, x2=750, y2=150), page=1)
    col2_2 = OCRBlock(id="col2_2", text="Col 2 Bottom", confidence=0.95, bbox=BBox(x1=450, y1=200, x2=750, y2=230), page=1)

    all_blocks = [title, col1_1, col2_1, col1_2, col2_2]
    layout_blocks = LayoutDetector.detect_layout(all_blocks, page_width=800, page_height=1000, page_number=1)
    order = ReadingOrderResolver.resolve_reading_order(layout_blocks, page_width=800, page_height=1000)

    assert len(order) >= 3
    # First block should be the title
    assert "p1_001" in order[0]


def test_table_extraction():
    # Grid: Header row + 2 data rows
    table_blocks = [
        # Headers
        OCRBlock(id="h1", text="Item", confidence=0.99, bbox=BBox(x1=50, y1=200, x2=150, y2=220), page=1),
        OCRBlock(id="h2", text="Qty", confidence=0.99, bbox=BBox(x1=250, y1=200, x2=300, y2=220), page=1),
        OCRBlock(id="h3", text="Price", confidence=0.99, bbox=BBox(x1=400, y1=200, x2=450, y2=220), page=1),
        # Row 1
        OCRBlock(id="r1_1", text="Laptop Pro", confidence=0.98, bbox=BBox(x1=50, y1=235, x2=150, y2=255), page=1),
        OCRBlock(id="r1_2", text="2", confidence=0.98, bbox=BBox(x1=250, y1=235, x2=300, y2=255), page=1),
        OCRBlock(id="r1_3", text="$2,400.00", confidence=0.98, bbox=BBox(x1=400, y1=235, x2=480, y2=255), page=1),
        # Row 2
        OCRBlock(id="r2_1", text="Monitor 4K", confidence=0.98, bbox=BBox(x1=50, y1=270, x2=150, y2=290), page=1),
        OCRBlock(id="r2_2", text="1", confidence=0.98, bbox=BBox(x1=250, y1=270, x2=300, y2=290), page=1),
        OCRBlock(id="r2_3", text="$650.00", confidence=0.98, bbox=BBox(x1=400, y1=270, x2=480, y2=290), page=1),
    ]

    tables = TableExtractor.extract_tables_from_page(table_blocks, page_number=1)
    assert len(tables) == 1
    t = tables[0]
    assert len(t.headers) == 3
    assert len(t.rows) == 2
    assert t.rows[0][0] == "Laptop Pro"


def test_entities_and_fields_and_classification():
    blocks = [
        OCRBlock(id="b1", text="ACME Cloud Corporation", confidence=0.99, bbox=BBox(x1=50, y1=50, x2=250, y2=80), page=1),
        OCRBlock(id="b2", text="support@acmecloud.com", confidence=0.99, bbox=BBox(x1=50, y1=90, x2=200, y2=110), page=1),
        OCRBlock(id="b3", text="Invoice Number: INV-99042", confidence=0.98, bbox=BBox(x1=300, y1=50, x2=500, y2=80), page=1),
        OCRBlock(id="b4", text="Invoice Date: September 15, 2026", confidence=0.97, bbox=BBox(x1=300, y1=90, x2=550, y2=110), page=1),
        OCRBlock(id="b5", text="Total Due: $15,800.00", confidence=0.99, bbox=BBox(x1=300, y1=130, x2=450, y2=150), page=1),
    ]

    entities = EntityExtractor.extract_entities(blocks)
    ent_types = [e.type for e in entities]
    assert "EMAIL" in ent_types
    assert "AMOUNT" in ent_types
    assert "DOCUMENT_ID" in ent_types

    fields = KeyValueExtractor.extract_fields(blocks)
    field_names = [f.field.lower() for f in fields]
    assert any("invoice number" in fn for fn in field_names)
    assert any("total" in fn for fn in field_names)

    doc_type, conf = DocumentClassifier.classify_document(blocks)
    assert doc_type == "invoice"
    assert conf >= 0.70


def test_exports():
    doc = DocumentResult(
        document_id="test_export_doc",
        filename="invoice_2026.pdf",
        document_type="invoice",
        document_type_confidence=0.95,
        pages=[
            PageResult(
                page=1,
                width=800,
                height=1000,
                ocr_blocks=[
                    OCRBlock(id="b1", text="ACME INVOICE", confidence=0.99, bbox=BBox(x1=50, y1=50, x2=200, y2=80), page=1),
                    OCRBlock(id="b2", text="Total: $500", confidence=0.98, bbox=BBox(x1=50, y1=100, x2=150, y2=120), page=1),
                ],
                layout_blocks=[],
            )
        ],
        metadata=DocumentMetadata(created_at="2026-09-17T00:00:00Z"),
    )

    txt = DocumentExporter.to_text(doc)
    assert "ACME INVOICE" in txt

    md = DocumentExporter.to_markdown(doc)
    assert "# invoice_2026.pdf" in md

    html = DocumentExporter.to_html(doc)
    assert "<!DOCTYPE html>" in html

    csv_data = DocumentExporter.to_csv(doc)
    assert "ACME INVOICE" in csv_data
