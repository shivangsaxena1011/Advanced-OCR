# Document Processing Pipeline

The AORL pipeline transforms unstructured document inputs into queryable, structured intelligence in 10 deterministic stages:

```text
Upload & Validation
       ↓
Page Rasterization (PyMuPDF)
       ↓
Quality Analysis & Deskew (OpenCV)
       ↓
OCR Text Detection & Recognition (PaddleOCR 3.7)
       ↓
Bounding Box Normalization
       ↓
Layout Understanding & Block Classification
       ↓
Multi-Column Reading Order Topological Sort
       ↓
Table Detection & Grid Extraction
       ↓
Entities & Key-Value Extraction
       ↓
Document Classification & Structured Storage
```

## Stage Descriptions

1. **Upload & Magic-Byte Validation**:
   Verifies MIME types (`image/png`, `image/jpeg`, `image/webp`, `application/pdf`), sanitizes filenames, and generates UUID document identifiers.

2. **Rasterization**:
   Uses PyMuPDF to convert PDF pages into 200 DPI RGB bitmaps and renders 250px thumbnails.

3. **Preprocessing**:
   Measures sharpness (Laplacian variance), contrast standard deviation, brightness, and skew angle via Hough transform. Applies auto-deskew if skew > 0.5°.

4. **OCR Inference**:
   Invokes `PaddleOCREngine` with CPU stability blocklist to detect text boundaries and transcribe text line tokens.

5. **Layout Understanding**:
   Clusters tokens into semantic blocks (`title`, `heading`, `paragraph`, `list`, `table`, `header`, `footer`).

6. **Reading Order**:
   Identifies column gutters and sequences full-width spanning titles first, followed by left-to-right column progression.

7. **Table Reconstruction**:
   Aligns rows and columns, isolating headers and data cells for export.

8. **Information Extraction**:
   Extracts deterministic entities (EMAIL, PHONE, DATE, AMOUNT, DOC_ID) and pairs key-value fields.

9. **Classification**:
   Determines document category (`invoice`, `receipt`, `research_paper`, `form`, etc.) with confidence.

10. **Storage**:
    Saves document JSON manifest and page images to persistent storage.
