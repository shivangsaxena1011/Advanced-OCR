# AORL Architecture Specification

## Overview

Advanced OCR with Layout Understanding (AORL) is an intelligent document-processing platform designed to convert raw image or PDF documents into richly structured, spatially grounded digital assets.

## System Architecture

```
                    Browser / Next.js 15
                             │
                  REST API / HTTP Requests
                             ▼
                    FastAPI REST Backend
  ┌─────────────────────────────────────────────────────────────┐
  │  Core Routers: /documents, /upload, /search, /export, /ask  │
  ├─────────────────────────────────────────────────────────────┤
  │  Processing Pipeline                                        │
  │  ├── 1. PyMuPDF Multi-Page Rasterizer                       │
  │  ├── 2. Image Preprocessing (Quality, Denoise, Deskew)      │
  │  ├── 3. BaseOCREngine Adapter -> PaddleOCR Engine           │
  │  ├── 4. OCR Normalizer (Schema v1.0 standard)               │
  │  ├── 5. Layout Understanding (Headings, Paragraphs, Titles) │
  │  ├── 6. Reading Order Graph Resolver (Multi-column flow)    │
  │  ├── 7. Table Grid Structure Extractor                      │
  │  ├── 8. Named Entity Extractor (Regex + NLP)                │
  │  ├── 9. Key-Value Field Extractor                           │
  │  ├── 10. Document Classifier (Heuristic & Structural)       │
  │  └── 11. Multi-Format Exporter (MD, TXT, HTML, CSV, JSON)   │
  ├─────────────────────────────────────────────────────────────┤
  │  DocNova Grounded AI Engine                                 │
  │  ├── Strict Context Retrieval (Fields, Tables, Spans)       │
  │  ├── Spatial Citation Resolver (Page X, Coordinates)        │
  │  └── Hallucination Guard                                    │
  └─────────────────────────────────────────────────────────────┘
                             │
                    Local Storage / SQLite
         (UUID File Store, Page Renders, JSON Manifests)
```

## Modular Boundaries

1. **OCR Engine Isolation**:
   The application communicates with `BaseOCREngine` rather than binding tightly to PaddleOCR. This enables swapping or chaining alternate engines without refactoring application logic.

2. **Frontend-Backend Decoupling**:
   Next.js 15 App Router provides client-side reactivity, interactive canvas zoom/pan overlays, and server-side safety, while FastAPI handles CPU/GPU-intensive inference.
