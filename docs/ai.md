# DocNova AI Document Assistant

## Overview

DocNova is a grounded document assistant that reasons directly over structured OCR output, key-value fields, and extracted tables.

## Grounded Architecture

- **No Raw Document Dumping**: Relevant fields, table rows, and paragraph chunks are queried before synthesis.
- **Clickable Citations**: Every answer references exact pages and bounding box coordinates. Clicking a citation chip in the frontend navigates and highlights that exact region in the canvas viewer.
- **Hallucination Guard**: Returns `"I couldn't find sufficient evidence for that answer in the uploaded document."` if evidence cannot be established from the document.
- **LLM Abstraction**: Works 100% offline out-of-the-box with deterministic semantic extraction, or connects to OpenAI / vLLM when `LLM_API_KEY` is provided.
