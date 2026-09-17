import io
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Advanced OCR with Layout Understanding"
    assert data["short_name"] == "AORL"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ocr_engine"] == "paddleocr"


def test_upload_invalid_extension():
    fake_file = io.BytesIO(b"random content")
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malicious.exe", fake_file, "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]


def test_upload_valid_image():
    # Create simple in-memory PNG with padding
    img = Image.new("RGB", (500, 180), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((60, 70), "INVOICE #9988", fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test_invoice.png", buf, "image/png")},
    )
    assert response.status_code == 201
    doc = response.json()
    assert doc["document_id"] is not None
    assert doc["filename"] == "test_invoice.png"
    assert len(doc["pages"]) == 1
    assert doc["processing"]["status"] == "COMPLETED"
    assert len(doc["pages"][0]["ocr_blocks"]) >= 1

    # Verify retrieval
    doc_id = doc["document_id"]
    get_res = client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["document_id"] == doc_id

    # Verify OCR endpoint
    ocr_res = client.get(f"/api/v1/documents/{doc_id}/ocr")
    assert ocr_res.status_code == 200
    assert len(ocr_res.json()) >= 1

    # Verify Search endpoint with recognized token
    recognized_text = doc["pages"][0]["ocr_blocks"][0]["text"]
    search_token = recognized_text[:4]
    search_res = client.get(f"/api/v1/documents/{doc_id}/search?q={search_token}")
    assert search_res.status_code == 200
    assert search_res.json()["total_matches"] >= 1


    # Verify DocNova Ask endpoint
    ask_res = client.post(
        f"/api/v1/documents/{doc_id}/ask",
        json={"question": "What is the invoice number?"},
    )
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert ask_data["answer"] != ""

    # Verify Compare endpoint (compare doc to itself)
    comp_res = client.post(
        "/api/v1/documents/compare",
        json={"doc_a_id": doc_id, "doc_b_id": doc_id},
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["similarity_score"] == 1.0

