from datetime import datetime, timezone
import logging
from pathlib import Path
import time
from typing import Optional
from PIL import Image

from app.core.config import settings
from app.schemas.document import (
    DocumentResult,
    DocumentMetadata,
    PageResult,
    ProcessingStageStatus,
    ProcessingSummary,
    TableResult,
    EntityResult,
    ExtractedField,
)
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.paddleocr_engine import PaddleOCREngine
from app.services.pdf.processor import PDFProcessor
from app.services.preprocessing.pipeline import PreprocessingPipeline
from app.services.layout.detector import LayoutDetector
from app.services.reading_order.sorter import ReadingOrderResolver
from app.services.tables.detector import TableExtractor
from app.services.entities.extractor import EntityExtractor
from app.services.fields.extractor import KeyValueExtractor
from app.services.classification.service import DocumentClassifier
from app.services.storage.file_store import FileStorageService

logger = logging.getLogger("aorl.pipeline")


class DocumentPipeline:
    """
    Orchestrates end-to-end document processing:
    PDF/Image -> Rasterization -> Preprocessing -> PaddleOCR -> Layout Analysis
    -> Reading Order -> Tables -> Entities -> Fields -> Document Classification.
    """

    def __init__(self, ocr_engine: Optional[BaseOCREngine] = None):
        if ocr_engine is not None:
            self.ocr_engine = ocr_engine
        else:
            self.ocr_engine = PaddleOCREngine(
                lang=settings.OCR_LANGUAGE,
                use_gpu=settings.OCR_USE_GPU,
            )

    def process_document(
        self,
        doc_id: str,
        file_path: Path,
        original_filename: str,
        mime_type: str,
    ) -> DocumentResult:
        start_time = time.perf_counter()
        now_iso = datetime.now(timezone.utc).isoformat()
        file_size = file_path.stat().st_size

        doc_result = DocumentResult(
            document_id=doc_id,
            filename=original_filename,
            metadata=DocumentMetadata(
                file_size_bytes=file_size,
                mime_type=mime_type,
                created_at=now_iso,
                ocr_engine=self.ocr_engine.get_engine_name(),
            ),
            processing=ProcessingSummary(
                status="PROCESSING",
                current_stage="UPLOAD",
                stages=[
                    ProcessingStageStatus(stage="UPLOAD", status="COMPLETED"),
                ],
            ),
        )

        try:
            # 1. Page Extraction Stage
            stage_start = time.perf_counter()
            doc_result.processing.current_stage = "PAGE_EXTRACTION"
            
            pages_data: list[tuple[int, Image.Image, Image.Image]] = []
            if mime_type == "application/pdf":
                pages_data = PDFProcessor.render_pdf_pages(file_path)
            else:
                with Image.open(file_path) as img:
                    rgb_img = img.convert("RGB")
                    thumb = rgb_img.copy()
                    thumb.thumbnail((250, 250), Image.Resampling.LANCZOS)
                    pages_data = [(1, rgb_img, thumb)]

            doc_result.metadata.page_count = len(pages_data)
            extraction_duration = (time.perf_counter() - stage_start) * 1000
            doc_result.processing.stages.append(
                ProcessingStageStatus(
                    stage="PAGE_EXTRACTION",
                    status="COMPLETED",
                    duration_ms=round(extraction_duration, 2),
                )
            )

            # 2. Page-level processing (Preprocessing, OCR, Layout, Tables)
            processed_pages: list[PageResult] = []
            all_tables: list[TableResult] = []
            all_ocr_blocks = []
            all_reading_order: list[str] = []

            total_prep_ms = 0.0
            total_ocr_ms = 0.0
            total_layout_ms = 0.0
            total_table_ms = 0.0

            for page_num, raw_img, thumb_img in pages_data:
                # Save page image & thumbnail
                page_img_url, _ = FileStorageService.save_page_image(doc_id, page_num, raw_img)
                thumb_url, _ = FileStorageService.save_thumbnail(doc_id, page_num, thumb_img)

                # Preprocessing
                p_start = time.perf_counter()
                prep_result = PreprocessingPipeline.run(
                    raw_img, auto_deskew=True, auto_enhance_contrast=True
                )
                total_prep_ms += (time.perf_counter() - p_start) * 1000

                # OCR Processing
                o_start = time.perf_counter()
                ocr_blocks = self.ocr_engine.process_image(
                    prep_result.processed_image, page_number=page_num
                )
                total_ocr_ms += (time.perf_counter() - o_start) * 1000
                all_ocr_blocks.extend(ocr_blocks)

                # Layout Analysis
                l_start = time.perf_counter()
                layout_blocks = LayoutDetector.detect_layout(
                    ocr_blocks,
                    page_width=raw_img.width,
                    page_height=raw_img.height,
                    page_number=page_num,
                )
                total_layout_ms += (time.perf_counter() - l_start) * 1000

                # Reading Order
                page_reading_order = ReadingOrderResolver.resolve_reading_order(
                    layout_blocks,
                    page_width=raw_img.width,
                    page_height=raw_img.height,
                )
                all_reading_order.extend(page_reading_order)

                # Table Extraction
                t_start = time.perf_counter()
                page_tables = TableExtractor.extract_tables_from_page(
                    ocr_blocks, page_number=page_num
                )
                total_table_ms += (time.perf_counter() - t_start) * 1000
                all_tables.extend(page_tables)

                page_res = PageResult(
                    page=page_num,
                    width=raw_img.width,
                    height=raw_img.height,
                    image_url=page_img_url,
                    thumbnail_url=thumb_url,
                    ocr_blocks=ocr_blocks,
                    layout_blocks=layout_blocks,
                    quality=prep_result.quality_metrics,
                )
                processed_pages.append(page_res)

            doc_result.pages = processed_pages
            doc_result.reading_order = all_reading_order
            doc_result.tables = all_tables

            # 3. Document-level Information Extraction (Entities, Fields, Classification)
            ent_start = time.perf_counter()
            doc_result.entities = EntityExtractor.extract_entities(all_ocr_blocks)
            ent_ms = (time.perf_counter() - ent_start) * 1000

            fld_start = time.perf_counter()
            doc_result.fields = KeyValueExtractor.extract_fields(all_ocr_blocks)
            fld_ms = (time.perf_counter() - fld_start) * 1000

            cls_start = time.perf_counter()
            doc_type, doc_conf = DocumentClassifier.classify_document(all_ocr_blocks)
            doc_result.document_type = doc_type
            doc_result.document_type_confidence = doc_conf
            cls_ms = (time.perf_counter() - cls_start) * 1000

            # Record all pipeline stages
            doc_result.processing.stages.extend([
                ProcessingStageStatus(stage="PREPROCESSING", status="COMPLETED", duration_ms=round(total_prep_ms, 2)),
                ProcessingStageStatus(stage="OCR", status="COMPLETED", duration_ms=round(total_ocr_ms, 2)),
                ProcessingStageStatus(stage="LAYOUT", status="COMPLETED", duration_ms=round(total_layout_ms, 2)),
                ProcessingStageStatus(stage="READING_ORDER", status="COMPLETED", duration_ms=1.0),
                ProcessingStageStatus(stage="TABLES", status="COMPLETED", duration_ms=round(total_table_ms, 2)),
                ProcessingStageStatus(stage="ENTITIES", status="COMPLETED", duration_ms=round(ent_ms, 2)),
                ProcessingStageStatus(stage="FIELDS", status="COMPLETED", duration_ms=round(fld_ms, 2)),
                ProcessingStageStatus(stage="CLASSIFICATION", status="COMPLETED", duration_ms=round(cls_ms, 2)),
            ])

            # Finalize
            total_duration = (time.perf_counter() - start_time) * 1000
            doc_result.metadata.processing_time_ms = round(total_duration, 2)
            doc_result.processing.status = "COMPLETED"
            doc_result.processing.current_stage = "COMPLETED"
            doc_result.processing.stages.append(
                ProcessingStageStatus(stage="FINALIZATION", status="COMPLETED", duration_ms=round(total_duration, 2))
            )

            # Persist document result JSON
            FileStorageService.save_document_result(doc_result)
            return doc_result

        except Exception as e:
            logger.error(f"Pipeline error processing document {doc_id}: {e}", exc_info=True)
            doc_result.processing.status = "FAILED"
            doc_result.processing.error = str(e)
            FileStorageService.save_document_result(doc_result)
            raise
