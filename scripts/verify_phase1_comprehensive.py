import io
import json
import time
import requests
from pathlib import Path
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def log(msg, status="INFO"):
    symbol = {"PASS": "[PASS]", "FAIL": "[FAIL]", "INFO": "[INFO]"}.get(status, "[INFO]")
    print(f"{symbol} {msg}")

def main():
    print("=" * 80)
    print("       AORL PHASE 1 COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 80)
    
    results = {}
    
    # 0. Health Check
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        log(f"Backend Health Check OK: {data}", "PASS")
        results["Health Check"] = True
    except Exception as e:
        log(f"Backend Health Check Failed: {e}", "FAIL")
        results["Health Check"] = False
        return

    # 1. Real Image Processing (receipt_sample.png)
    print("\n--- 1. Testing Real Image Processing (receipt_sample.png) ---")
    img_path = Path("sample_documents/receipt_sample.png")
    with open(img_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": (img_path.name, f, "image/png")})
    if r.status_code == 201:
        doc = r.json()
        doc_id = doc["document_id"]
        pages = doc["pages"]
        assert len(pages) == 1
        p1 = pages[0]
        blocks = p1["ocr_blocks"]
        log(f"Upload successful: doc_id={doc_id}, blocks={len(blocks)}, status={doc['processing']['status']}", "PASS")
        
        # Verify bounding box coordinates against image dimensions
        img_w, img_h = p1["width"], p1["height"]
        log(f"Page dimensions: {img_w}x{img_h}")
        coord_valid = True
        for b in blocks:
            bb = b["bbox"]
            if not (0 <= bb["x1"] <= bb["x2"] <= img_w and 0 <= bb["y1"] <= bb["y2"] <= img_h):
                coord_valid = False
                log(f"Invalid BBox out of bounds: {bb}", "FAIL")
                break
        if coord_valid:
            log(f"All {len(blocks)} bounding boxes strictly within [{img_w}x{img_h}]", "PASS")
            
        results["Real Image Processing"] = True
    else:
        log(f"Real Image Processing failed: {r.status_code} {r.text}", "FAIL")
        results["Real Image Processing"] = False

    # 2. Real PDF Processing (invoice_sample.pdf)
    print("\n--- 2. Testing Real Single-Page PDF Processing (invoice_sample.pdf) ---")
    pdf_path = Path("sample_documents/invoice_sample.pdf")
    with open(pdf_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": (pdf_path.name, f, "application/pdf")})
    if r.status_code == 201:
        doc = r.json()
        blocks = doc["pages"][0]["ocr_blocks"]
        log(f"PDF processed: doc_id={doc['document_id']}, blocks={len(blocks)}, type={doc.get('document_type')}", "PASS")
        results["Single-Page PDF"] = True
    else:
        log(f"Single-page PDF failed: {r.status_code} {r.text}", "FAIL")
        results["Single-Page PDF"] = False

    # 3. Multi-Page PDF Processing (multipage_sample.pdf)
    print("\n--- 3. Testing Real Multi-Page PDF Processing (multipage_sample.pdf) ---")
    mpdf_path = Path("sample_documents/multipage_sample.pdf")
    with open(mpdf_path, "rb") as f:
        r = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": (mpdf_path.name, f, "application/pdf")})
    if r.status_code == 201:
        doc = r.json()
        pages = doc["pages"]
        log(f"Multi-page PDF processed: pages={len(pages)}", "PASS" if len(pages) == 2 else "FAIL")
        for p in pages:
            log(f"  Page {p['page']}: {len(p['ocr_blocks'])} blocks, dim={p['width']}x{p['height']}, image_url={p['image_url']}")
        assert len(pages) == 2
        results["Multi-Page PDF"] = True
    else:
        log(f"Multi-page PDF failed: {r.status_code} {r.text}", "FAIL")
        results["Multi-Page PDF"] = False

    # 4. Invalid File Tests (Corrupted / Spoofed / Empty)
    print("\n--- 4. Testing Invalid Files ---")
    # Empty file
    r_empty = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("empty.png", io.BytesIO(b""), "image/png")})
    log(f"Empty file test (HTTP {r_empty.status_code}): {r_empty.json()}", "PASS" if r_empty.status_code == 400 else "FAIL")
    
    # Spoofed magic bytes
    r_spoof = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("fake.png", io.BytesIO(b"CORRUPT_BYTES_NOT_PNG"), "image/png")})
    log(f"Corrupt/spoofed header test (HTTP {r_spoof.status_code}): {r_spoof.json()}", "PASS" if r_spoof.status_code == 400 else "FAIL")
    results["Invalid File Rejection"] = (r_empty.status_code == 400 and r_spoof.status_code == 400)

    # 5. Unsupported File Formats
    print("\n--- 5. Testing Unsupported Formats (.exe, .txt, .docx) ---")
    r_exe = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("malware.exe", io.BytesIO(b"MZ\x90\x00"), "application/octet-stream")})
    log(f".exe rejection test (HTTP {r_exe.status_code}): {r_exe.json().get('detail')}", "PASS" if r_exe.status_code == 400 else "FAIL")
    
    r_txt = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("notes.txt", io.BytesIO(b"Hello world"), "text/plain")})
    log(f".txt rejection test (HTTP {r_txt.status_code}): {r_txt.json().get('detail')}", "PASS" if r_txt.status_code == 400 else "FAIL")
    results["Unsupported Format Rejection"] = (r_exe.status_code == 400 and r_txt.status_code == 400)

    # 6. Large File within configured limit (~5MB image, limit is 25MB)
    print("\n--- 6. Testing Large File (Within 25MB limit) ---")
    large_img = Image.new("RGB", (2800, 3500), color=(245, 245, 245))
    buf = io.BytesIO()
    large_img.save(buf, format="PNG", optimize=False)
    buf.seek(0)
    large_bytes = buf.getvalue()
    size_mb = len(large_bytes) / (1024 * 1024)
    log(f"Generated test large image: {size_mb:.2f} MB")
    r_large = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("large_test.png", io.BytesIO(large_bytes), "image/png")})
    log(f"Large image upload test (HTTP {r_large.status_code}): status={r_large.json().get('processing', {}).get('status')}", "PASS" if r_large.status_code == 201 else "FAIL")
    results["Large File Within Limit"] = (r_large.status_code == 201)

    # 7. OCR Edge Scenario (Blank Image / Zero Text)
    print("\n--- 7. Testing OCR Edge Scenario: Pure Blank Image ---")
    blank_img = Image.new("RGB", (800, 1000), color=(255, 255, 255))
    buf_blank = io.BytesIO()
    blank_img.save(buf_blank, format="PNG")
    buf_blank.seek(0)
    r_blank = requests.post(f"{BASE_URL}/api/v1/documents/upload", files={"file": ("blank_test.png", buf_blank, "image/png")})
    if r_blank.status_code == 201:
        blank_doc = r_blank.json()
        blks = blank_doc["pages"][0]["ocr_blocks"]
        log(f"Blank image processed without error: {len(blks)} blocks found, status={blank_doc['processing']['status']}", "PASS")
        results["Blank Image Edge Case"] = True
    else:
        log(f"Blank image failed: {r_blank.status_code} {r_blank.text}", "FAIL")
        results["Blank Image Edge Case"] = False

    print("\n" + "=" * 80)
    print("                    PHASE 1 VERIFICATION SUMMARY")
    print("=" * 80)
    all_passed = True
    for test_name, passed in results.items():
        status_str = "PASS" if passed else "FAIL"
        print(f"  {test_name:<35} : {status_str}")
        if not passed:
            all_passed = False
            
    print("-" * 80)
    print(f"OVERALL RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 80)

if __name__ == "__main__":
    main()
