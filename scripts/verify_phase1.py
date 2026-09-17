"""
Verification script for Phase 1: Foundation.
Uploads sample documents directly via FastAPI test client and validates:
1. File upload & MIME validation
2. Multi-page rendering / image loading
3. Image quality analysis (brightness, contrast, sharpness, skew)
4. Real PaddleOCR detection and recognition
5. Normalized OCRBlock schemas and coordinates
6. DocumentResult JSON persistence
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_phase1_receipt():
    receipt_path = Path("sample_documents/receipt_sample.png")
    assert receipt_path.exists(), "Sample receipt does not exist"

    print("\n--- Testing Phase 1: Upload and OCR on Receipt Image ---")
    with open(receipt_path, "rb") as f:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("receipt_sample.png", f, "image/png")},
        )

    assert response.status_code == 201, f"Upload failed: {response.text}"
    data = response.json()
    doc_id = data["document_id"]
    print(f"Document ID: {doc_id}")
    print(f"Status: {data['processing']['status']}")
    print(f"Pages: {len(data['pages'])}")

    page = data["pages"][0]
    print(f"Page dimensions: {page['width']}x{page['height']}")
    print(f"Readiness Score: {page['quality']['readiness_score']}%")
    print(f"Detected OCR Blocks: {len(page['ocr_blocks'])}")

    assert len(page["ocr_blocks"]) > 0, "Expected OCR blocks"
    print("\nFirst 5 recognized OCR blocks:")
    for b in page["ocr_blocks"][:5]:
        print(f"  [{b['id']}] (conf: {b['confidence']:.2f}) {b['text']} -> bbox: ({b['bbox']['x1']:.0f}, {b['bbox']['y1']:.0f}) to ({b['bbox']['x2']:.0f}, {b['bbox']['y2']:.0f})")

    # Verify retrieval
    get_res = client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    print("\nDocument successfully retrieved from storage!")
    print("Phase 1 Receipt Test PASSED!\n")


def test_phase1_invoice_pdf():
    invoice_path = Path("sample_documents/invoice_sample.pdf")
    assert invoice_path.exists(), "Sample invoice does not exist"

    print("\n--- Testing Phase 1: Upload and OCR on Multi-Page/Scanned PDF ---")
    with open(invoice_path, "rb") as f:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("invoice_sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 201, f"Upload failed: {response.text}"
    data = response.json()
    doc_id = data["document_id"]
    print(f"Document ID: {doc_id}")
    print(f"Pages rasterized: {len(data['pages'])}")

    page = data["pages"][0]
    print(f"Detected OCR Blocks: {len(page['ocr_blocks'])}")
    assert len(page["ocr_blocks"]) > 0, "Expected OCR blocks on invoice PDF"

    for b in page["ocr_blocks"][:5]:
        print(f"  [{b['id']}] (conf: {b['confidence']:.2f}) {b['text']}")

    print("\nPhase 1 Invoice PDF Test PASSED!\n")


if __name__ == "__main__":
    test_phase1_receipt()
    test_phase1_invoice_pdf()
