"""
Generates synthetic document files for testing AORL pipeline.
Uses PyMuPDF (fitz) and Pillow to generate realistic sample documents:
- receipt_sample.png
- invoice_sample.pdf
- two_column_article.pdf
- table_sample.pdf
"""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("sample_documents")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def create_receipt_png():
    img = Image.new("RGB", (600, 900), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    draw.text((200, 40), "SUPERMART STORE #402", fill=(20, 20, 20))
    draw.text((180, 70), "123 Market Street, Suite 100", fill=(70, 70, 70))
    draw.text((230, 95), "Tel: +1-555-0199", fill=(70, 70, 70))
    draw.line((40, 130, 560, 130), fill=(180, 180, 180), width=2)

    draw.text((50, 150), "DATE: 2026-09-15 14:32", fill=(40, 40, 40))
    draw.text((50, 175), "RECEIPT NO: REC-883921", fill=(40, 40, 40))
    draw.text((50, 200), "CASHIER: Sarah M.", fill=(40, 40, 40))
    draw.line((40, 230, 560, 230), fill=(180, 180, 180), width=1)

    items = [
        ("Organic Whole Milk 1gal", "1", "$4.50"),
        ("Sourdough Bread Loaf", "2", "$7.00"),
        ("Roasted Almonds 250g", "1", "$6.25"),
        ("Fresh Valencia Oranges", "3", "$4.20"),
        ("Dark Chocolate 85%", "2", "$5.98"),
    ]

    y = 260
    draw.text((50, y), "ITEM", fill=(20, 20, 20))
    draw.text((380, y), "QTY", fill=(20, 20, 20))
    draw.text((480, y), "PRICE", fill=(20, 20, 20))
    draw.line((40, y + 25, 560, y + 25), fill=(200, 200, 200), width=1)

    y += 40
    for name, qty, price in items:
        draw.text((50, y), name, fill=(50, 50, 50))
        draw.text((390, y), qty, fill=(50, 50, 50))
        draw.text((480, y), price, fill=(50, 50, 50))
        y += 35

    draw.line((40, y + 10, 560, y + 10), fill=(180, 180, 180), width=1)
    y += 30
    draw.text((300, y), "SUBTOTAL:", fill=(50, 50, 50))
    draw.text((480, y), "$27.93", fill=(50, 50, 50))
    y += 30
    draw.text((300, y), "SALES TAX (8%):", fill=(50, 50, 50))
    draw.text((480, y), "$2.23", fill=(50, 50, 50))
    y += 35
    draw.text((300, y), "TOTAL AMOUNT:", fill=(10, 10, 10))
    draw.text((475, y), "$30.16", fill=(10, 10, 10))

    y += 70
    draw.text((190, y), "Thank you for shopping with us!", fill=(100, 100, 100))
    img.save(OUT_DIR / "receipt_sample.png")
    print("Created receipt_sample.png")


def create_invoice_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4

    # Header
    page.insert_text(fitz.Point(50, 60), "INVOICE", fontsize=24, color=(0.1, 0.2, 0.5))
    page.insert_text(fitz.Point(400, 50), "ACME CLOUD CORP", fontsize=12, color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(400, 68), "billing@acmecloud.com", fontsize=10, color=(0.4, 0.4, 0.4))
    page.insert_text(fitz.Point(400, 84), "+1 (800) 555-0144", fontsize=10, color=(0.4, 0.4, 0.4))

    page.draw_line(fitz.Point(50, 100), fitz.Point(545, 100), color=(0.8, 0.8, 0.8), width=1.5)

    # Details
    page.insert_text(fitz.Point(50, 130), "Billed To:", fontsize=11, color=(0.1, 0.1, 0.1))
    page.insert_text(fitz.Point(50, 148), "Global Logistics Ltd.", fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(50, 164), "450 Industrial Park Blvd, Suite 200", fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(50, 180), "accounts@globallogistics.com", fontsize=10, color=(0.3, 0.3, 0.3))

    page.insert_text(fitz.Point(360, 130), "Invoice Number: INV-2026-9041", fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(360, 148), "Invoice Date: September 10, 2026", fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(360, 164), "Due Date: October 10, 2026", fontsize=10, color=(0.2, 0.2, 0.2))
    page.insert_text(fitz.Point(360, 180), "Payment Terms: Net 30", fontsize=10, color=(0.2, 0.2, 0.2))

    # Table Header
    page.draw_rect(fitz.Rect(50, 220, 545, 245), color=(0.9, 0.9, 0.95), fill=(0.93, 0.95, 0.98))
    page.insert_text(fitz.Point(60, 237), "Description", fontsize=10, color=(0.1, 0.2, 0.4))
    page.insert_text(fitz.Point(300, 237), "Hours/Qty", fontsize=10, color=(0.1, 0.2, 0.4))
    page.insert_text(fitz.Point(390, 237), "Rate", fontsize=10, color=(0.1, 0.2, 0.4))
    page.insert_text(fitz.Point(470, 237), "Total", fontsize=10, color=(0.1, 0.2, 0.4))

    rows = [
        ("Cloud Infrastructure Tier 3", "160 hrs", "$45.00", "$7,200.00"),
        ("Database Storage Cluster 2TB", "1 mo", "$850.00", "$850.00"),
        ("Security Audit & Pentest Report", "1 svc", "$2,500.00", "$2,500.00"),
        ("Dedicated Support SLA (Gold)", "1 mo", "$1,200.00", "$1,200.00"),
    ]

    y = 270
    for desc, qty, rate, tot in rows:
        page.insert_text(fitz.Point(60, y), desc, fontsize=10, color=(0.2, 0.2, 0.2))
        page.insert_text(fitz.Point(310, y), qty, fontsize=10, color=(0.3, 0.3, 0.3))
        page.insert_text(fitz.Point(395, y), rate, fontsize=10, color=(0.3, 0.3, 0.3))
        page.insert_text(fitz.Point(470, y), tot, fontsize=10, color=(0.2, 0.2, 0.2))
        page.draw_line(fitz.Point(50, y + 10), fitz.Point(545, y + 10), color=(0.9, 0.9, 0.9), width=0.5)
        y += 30

    y += 20
    page.insert_text(fitz.Point(370, y), "Subtotal:", fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(465, y), "$11,750.00", fontsize=10, color=(0.2, 0.2, 0.2))

    y += 20
    page.insert_text(fitz.Point(370, y), "Tax (0% Export):", fontsize=10, color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(465, y), "$0.00", fontsize=10, color=(0.2, 0.2, 0.2))

    y += 25
    page.draw_rect(fitz.Rect(350, y - 15, 545, y + 15), color=(0.2, 0.4, 0.8), fill=(0.95, 0.97, 1.0))
    page.insert_text(fitz.Point(370, y + 4), "Total Due:", fontsize=11, color=(0.1, 0.2, 0.5))
    page.insert_text(fitz.Point(460, y + 4), "$11,750.00", fontsize=12, color=(0.1, 0.2, 0.5))

    doc.save(OUT_DIR / "invoice_sample.pdf")
    doc.close()
    print("Created invoice_sample.pdf")


def create_two_column_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    page.insert_text(fitz.Point(50, 60), "Deep Learning Architectures for Document AI", fontsize=18, color=(0.1, 0.1, 0.1))
    page.insert_text(fitz.Point(50, 85), "Dr. Alex Vance, Department of Computer Science", fontsize=11, color=(0.4, 0.4, 0.4))
    page.draw_line(fitz.Point(50, 100), fitz.Point(545, 100), color=(0.8, 0.8, 0.8), width=1)

    # Column 1
    page.insert_text(fitz.Point(50, 125), "1. Introduction", fontsize=12, color=(0.1, 0.2, 0.5))
    col1_text = (
        "Document understanding bridges visual perception and linguistic semantics. "
        "Traditional optical character recognition systems primarily emphasize character "
        "transcription, often discarding vital spatial relationships.\n\n"
        "Modern document intelligence frameworks integrate vision backbones with graph "
        "neural representations and multimodal transformers to preserve hierarchical reading "
        "flows across complex multi-column structures."
    )
    page.insert_textbox(fitz.Rect(50, 135, 280, 400), col1_text, fontsize=9.5, color=(0.2, 0.2, 0.2))

    # Column 2
    page.insert_text(fitz.Point(310, 125), "2. Methodology", fontsize=12, color=(0.1, 0.2, 0.5))
    col2_text = (
        "We propose a two-stage topological ordering algorithm. In the first phase, bounding "
        "polygons are projected along vertical density axes to isolate distinct layout columns. "
        "In the second phase, reading flow graphs enforce strict reading order.\n\n"
        "By preventing horizontal cross-column drift, the extracted text maintains semantic integrity "
        "for downstream large language model retrieval."
    )
    page.insert_textbox(fitz.Rect(310, 135, 545, 400), col2_text, fontsize=9.5, color=(0.2, 0.2, 0.2))

    doc.save(OUT_DIR / "two_column_article.pdf")
    doc.close()
    print("Created two_column_article.pdf")


if __name__ == "__main__":
    create_receipt_png()
    create_invoice_pdf()
    create_two_column_pdf()
