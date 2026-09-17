# Advanced OCR with Layout Understanding (AORL)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15.5-black.svg)](https://nextjs.org/)
[![PaddleOCR](https://img.shields.io/badge/OCR-PaddleOCR%203.7-brightgreen.svg)](https://github.com/PaddlePaddle/PaddleOCR)

**AORL** is an enterprise-grade document intelligence platform that combines **PaddleOCR** text detection and recognition with proprietary application-level layout understanding, multi-column reading order resolution, table extraction, entity recognition, key-value pairing, document classification, full-text spatial search, multi-format exports, and the **DocNova** spatially grounded AI assistant.

---

## Key Capabilities

- **High-Fidelity OCR**: Powered by PaddleOCR 3.7 (PP-OCRv6) with automatic normalization and CPU stability safeguards.
- **Multi-Page PDF Processing**: Scanned and digital multi-page PDF rasterization via PyMuPDF with per-page thumbnails.
- **Image Quality & OCR Readiness**: Deterministic Laplacian variance (sharpness), contrast standard deviation, brightness, and auto-deskew angle estimation.
- **Layout Understanding**: Structural block classification into `title`, `heading`, `paragraph`, `list`, `table`, `header`, and `footer` with full source token traceability.
- **Multi-Column Reading Order**: Topological graph ordering preventing horizontal cross-column drift in academic papers and articles.
- **Table Extraction & Reconstruction**: Tabular grid reconstruction with headers, rows, cells, and one-click export to CSV, JSON, and Markdown.
- **Entity & Key-Value Extraction**: Deterministic regex and NLP recognition for `EMAIL`, `PHONE`, `DATE`, `AMOUNT`, `DOCUMENT_ID`, `ORGANIZATION`, and key-value pairs (`Total`, `Due Date`, `Invoice Number`).
- **Document Classification**: Automatic document categorization into `invoice`, `receipt`, `research_paper`, `form`, `report`, `certificate`, `letter`, and `statement`.
- **Full-Text Spatial Search**: Instant query searching across document scans with interactive yellow highlight overlays and keyboard navigation.
- **Multi-Format Exports**: One-click exports strictly following logical reading order into **TXT**, clean **Markdown** (with table grids), **HTML**, **CSV**, and **JSON**.
- **DocNova AI Assistant**: Evidence-grounded natural language question answering with clickable source citation chips that navigate and highlight exact bounding boxes on the canvas.
- **Side-by-Side Comparison**: Structural and field-level diffing between two documents with similarity score calculation.

---

## System Architecture

```
                    User / Client Browser
                             │
                  Next.js 15+ (App Router)
            ┌───────────────────┬───────────────────┐
            │ Workspace Viewer  │  DocNova Chat UI  │
            │ Pan/Zoom Canvas   │  Inspector Panels │
            │ Bounding Boxes    │  Table / Entities │
            └───────────────────┴───────────────────┘
                             │ REST API / JSON
                             ▼
                    FastAPI REST Backend
 ┌─────────────────────────────────────────────────────────────┐
 │ Routers: /documents, /upload, /search, /export, /ask        │
 ├──────────────────────────────┬──────────────────────────────┤
 │ Processing Pipeline          │ Storage & Persistence        │
 │  - Preprocessing (OpenCV)    │  - UUID Storage              │
 │  - PaddleOCR Adapter         │  - Rendered Page PNGs        │
 │  - Layout Analysis Engine    │  - Thumbnails                │
 │  - Reading Order Sorter      │  - Document JSON Manifests   │
 │  - Table Structure Extractor ├──────────────────────────────┤
 │  - Entity & KV Extractor     │ DocNova AI Engine            │
 │  - Document Classifier       │  - Grounded Retrieval        │
 │  - Multi-Format Exporter     │  - Bounding Box Citations    │
 └──────────────────────────────┴──────────────────────────────┘
```

---

## Technology Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Lucide React icons.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, PaddleOCR 3.7, PaddlePaddle 3.3, OpenCV, PyMuPDF, Pillow, NumPy.
- **Containerization**: Docker, Docker Compose.
- **Package Managers**: `uv` (Python), `npm` (Node.js).

---

## Quickstart

### 1. Prerequisites

- Python 3.12+ (64-bit)
- Node.js v20+ & npm
- Git

### 2. Backend Setup

```bash
# Clone the repository
git clone <repo-url>
cd "OCR Reader"

# Create virtual environment using uv
uv venv backend/.venv --python 3.12

# Install backend dependencies
uv pip install -r backend/requirements.txt --python backend/.venv/Scripts/python.exe

# Start the FastAPI backend server
backend\.venv\Scripts\uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

Backend API documentation is available at `http://localhost:8000/docs`.

### 3. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## Docker Deployment

To launch the complete platform using Docker Compose:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`

---

## Testing & Verification

Run the full automated test suite:

```bash
# Backend pytest suite (14 unit & integration tests)
backend\.venv\Scripts\pytest backend\tests

# End-to-end multi-document pipeline verification
backend\.venv\Scripts\python.exe scripts\verify_full_pipeline.py

# Frontend TypeScript & build check
cd frontend && npm run build
```

---

## Third-Party Components & Licenses

- **PaddleOCR & PaddlePaddle**: Apache 2.0 License. Used as an underlying OCR and text detection engine via our application abstraction layer `BaseOCREngine`.
- **PyMuPDF**: GNU AGPL / Commercial. Used for high-fidelity PDF page rasterization.
- **OpenCV**: Apache 2.0 License. Used for computer vision preprocessing, contrast enhancement, and deskew.
- **FastAPI**: MIT License.
- **Next.js**: MIT License.

---

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
