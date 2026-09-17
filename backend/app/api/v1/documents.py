from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse

from app.core.config import settings
from app.schemas.document import BlockUpdateRequest, DocumentResult, OCRBlock, ProcessingSummary
from app.services.pipeline import DocumentPipeline
from app.services.storage.file_store import FileStorageService

router = APIRouter(prefix="/documents", tags=["Documents"])

# Singleton pipeline instance initialized at module load
_pipeline_instance: Optional[DocumentPipeline] = None


def get_pipeline() -> DocumentPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DocumentPipeline()
    return _pipeline_instance


@router.post("/upload", response_model=DocumentResult, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing from upload request.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Validate file integrity, extension, size, and magic bytes
    is_valid, mime_type, error_msg = FileStorageService.validate_file(content, file.filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Save to storage
    doc_id, file_path = FileStorageService.save_upload(content, file.filename)

    # Process through pipeline
    try:
        pipeline = get_pipeline()
        doc_result = pipeline.process_document(
            doc_id=doc_id,
            file_path=file_path,
            original_filename=file.filename,
            mime_type=mime_type,
        )
        return doc_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}",
        )


@router.get("", response_model=list[DocumentResult])
async def list_documents():
    return FileStorageService.list_all_documents()


@router.get("/{doc_id}", response_model=DocumentResult)
async def get_document(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc


@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_document(doc_id: str):
    success = FileStorageService.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return {"message": f"Document '{doc_id}' deleted successfully."}


@router.get("/{doc_id}/status", response_model=ProcessingSummary)
async def get_document_status(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc.processing


@router.get("/{doc_id}/ocr", response_model=list[OCRBlock])
async def get_document_ocr(doc_id: str, page: Optional[int] = None):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    all_blocks: list[OCRBlock] = []
    for p in doc.pages:
        if page is None or p.page == page:
            all_blocks.extend(p.ocr_blocks)
    return all_blocks


@router.patch("/{doc_id}/blocks/{block_id}")
async def update_document_block(doc_id: str, block_id: str, payload: BlockUpdateRequest):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    updated = False
    for page in doc.pages:
        for block in page.ocr_blocks:
            if block.id == block_id:
                if payload.text is not None:
                    block.text = payload.text
                if payload.confidence is not None:
                    block.confidence = payload.confidence
                if payload.bbox is not None:
                    block.bbox = payload.bbox
                updated = True
                break

        for lb in page.layout_blocks:
            if lb.id == block_id:
                if payload.text is not None:
                    lb.text = payload.text
                if payload.layout_type is not None:
                    lb.type = payload.layout_type
                if payload.bbox is not None:
                    lb.bbox = payload.bbox
                updated = True
                break
            elif block_id in lb.source_ocr_blocks and payload.text is not None:
                src_texts = [b.text for b in page.ocr_blocks if b.id in lb.source_ocr_blocks]
                if src_texts:
                    lb.text = " ".join(src_texts)

        if updated:
            break

    if not updated:
        raise HTTPException(status_code=404, detail=f"Block '{block_id}' not found in document.")

    FileStorageService.save_document_result(doc)
    return {"status": "success", "message": f"Block '{block_id}' updated successfully.", "document": doc}


@router.get("/{doc_id}/search")
async def search_document(doc_id: str, q: str):


    if not q or not q.strip():
        return {"query": "", "total_matches": 0, "matches": []}

    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    query_clean = q.strip().lower()
    matches = []

    for page in doc.pages:
        for block in page.ocr_blocks:
            if query_clean in block.text.lower():
                matches.append({
                    "page": page.page,
                    "block_id": block.id,
                    "text": block.text,
                    "confidence": block.confidence,
                    "bbox": block.bbox.model_dump(),
                })

    return {
        "query": q.strip(),
        "total_matches": len(matches),
        "matches": matches,
    }


@router.get("/{doc_id}/export/text")
async def export_document_text(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    from app.services.export.exporter import DocumentExporter
    return PlainTextResponse(content=DocumentExporter.to_text(doc), media_type="text/plain")


@router.get("/{doc_id}/export/markdown")
async def export_document_markdown(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    from app.services.export.exporter import DocumentExporter
    return PlainTextResponse(content=DocumentExporter.to_markdown(doc), media_type="text/markdown")


@router.get("/{doc_id}/export/html")
async def export_document_html(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    from app.services.export.exporter import DocumentExporter
    return HTMLResponse(content=DocumentExporter.to_html(doc))


@router.get("/{doc_id}/export/csv")
async def export_document_csv(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    from app.services.export.exporter import DocumentExporter
    return PlainTextResponse(
        content=DocumentExporter.to_csv(doc),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={doc_id}.csv"},
    )


@router.get("/{doc_id}/export/json")
async def export_document_json(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc


@router.get("/{doc_id}/download")
async def download_original_document(doc_id: str):
    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    file_path = FileStorageService.get_upload_path(doc_id)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Original document file not found.")

    return FileResponse(
        path=file_path,
        filename=doc.filename,
        media_type="application/octet-stream",
    )


@router.post("/{doc_id}/ask")

async def ask_docnova(doc_id: str, payload: dict):
    question = payload.get("question")
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    doc = FileStorageService.load_document_result(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    from app.services.llm.retrieval import DocNovaAssistant
    assistant = DocNovaAssistant()
    response = await assistant.answer_question(question, doc)
    return response


@router.post("/compare")
async def compare_documents(payload: dict):
    doc_a_id = payload.get("doc_a_id")
    doc_b_id = payload.get("doc_b_id")

    if not doc_a_id or not doc_b_id:
        raise HTTPException(status_code=400, detail="Both doc_a_id and doc_b_id are required.")

    doc_a = FileStorageService.load_document_result(doc_a_id)
    doc_b = FileStorageService.load_document_result(doc_b_id)

    if not doc_a:
        raise HTTPException(status_code=404, detail=f"Document '{doc_a_id}' not found.")
    if not doc_b:
        raise HTTPException(status_code=404, detail=f"Document '{doc_b_id}' not found.")

    from app.services.compare.service import DocumentComparator
    return DocumentComparator.compare(doc_a, doc_b)


@router.get("/files/processed/{filename}")
async def serve_processed_file(filename: str):



    safe_path = (settings.PROCESSED_PATH / filename).resolve()
    if not str(safe_path).startswith(str(settings.PROCESSED_PATH.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=safe_path, media_type="image/png")


@router.get("/files/thumbnails/{filename}")
async def serve_thumbnail_file(filename: str):
    safe_path = (settings.THUMBNAIL_PATH / filename).resolve()
    if not str(safe_path).startswith(str(settings.THUMBNAIL_PATH.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=safe_path, media_type="image/png")
