from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class BBox(BaseModel):
    x1: float = Field(..., description="Left coordinate in pixels")
    y1: float = Field(..., description="Top coordinate in pixels")
    x2: float = Field(..., description="Right coordinate in pixels")
    y2: float = Field(..., description="Bottom coordinate in pixels")

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def area(self) -> float:
        return self.width * self.height

    def to_list(self) -> list[float]:
        return [self.x1, self.y1, self.x2, self.y2]


class OCRBlock(BaseModel):
    id: str = Field(..., description="Unique ID for OCR block, e.g. ocr_001")
    text: str = Field(..., description="Recognized text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    bbox: BBox = Field(..., description="Bounding box")
    polygon: Optional[list[list[float]]] = Field(None, description="4-point polygon [[x,y],...]")
    page: int = Field(1, ge=1, description="1-indexed page number")


class LayoutBlock(BaseModel):
    id: str = Field(..., description="Unique ID for layout block, e.g. layout_001")
    type: str = Field(
        ...,
        description="Layout type: title, heading, paragraph, list, table, header, footer, etc."
    )
    text: str = Field("", description="Aggregated text within layout block")
    bbox: BBox = Field(..., description="Enclosing bounding box")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Classification confidence")
    page: int = Field(1, ge=1, description="1-indexed page number")
    source_ocr_blocks: list[str] = Field(
        default_factory=list,
        description="IDs of underlying OCR blocks that compose this layout block"
    )


class TableCell(BaseModel):
    row_index: int
    col_index: int
    row_span: int = 1
    col_span: int = 1
    text: str = ""
    confidence: float = 1.0
    bbox: Optional[BBox] = None


class TableResult(BaseModel):
    table_id: str
    page: int
    bbox: BBox
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    cells: list[TableCell] = Field(default_factory=list)
    confidence: float = 1.0


class EntityResult(BaseModel):
    id: str
    type: str = Field(..., description="PERSON, ORGANIZATION, DATE, AMOUNT, EMAIL, PHONE, etc.")
    text: str
    confidence: float = 1.0
    page: int = 1
    bbox: Optional[BBox] = None
    source_block: Optional[str] = None


class ExtractedField(BaseModel):
    id: str
    field: str = Field(..., description="Field label / key e.g. Invoice Number, Total")
    value: str = Field(..., description="Extracted value")
    confidence: float = 1.0
    page: int = 1
    bbox: Optional[BBox] = None
    source_block: Optional[str] = None


class ImageQualityMetrics(BaseModel):
    width: int
    height: int
    dpi: Optional[int] = None
    brightness: float = 0.0
    contrast: float = 0.0
    blur_estimate: float = 0.0
    skew_estimate: float = 0.0
    readiness_score: float = 0.0
    readiness_notes: list[str] = Field(default_factory=list)


class PageResult(BaseModel):
    page: int
    width: int
    height: int
    image_url: str = ""
    thumbnail_url: str = ""
    ocr_blocks: list[OCRBlock] = Field(default_factory=list)
    layout_blocks: list[LayoutBlock] = Field(default_factory=list)
    quality: Optional[ImageQualityMetrics] = None


class DocumentMetadata(BaseModel):
    file_size_bytes: int = 0
    mime_type: str = ""
    page_count: int = 1
    created_at: str = ""
    processing_time_ms: float = 0.0
    ocr_engine: str = "paddleocr"


class ProcessingStageStatus(BaseModel):
    stage: str
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
    message: Optional[str] = None
    duration_ms: Optional[float] = None


class ProcessingSummary(BaseModel):
    status: str = "QUEUED"  # QUEUED, PROCESSING, COMPLETED, FAILED
    current_stage: str = "UPLOAD"
    stages: list[ProcessingStageStatus] = Field(default_factory=list)
    error: Optional[str] = None


class DocumentResult(BaseModel):
    schema_version: str = "1.0"
    document_id: str
    filename: str
    document_type: Optional[str] = None
    document_type_confidence: Optional[float] = None
    pages: list[PageResult] = Field(default_factory=list)
    reading_order: list[str] = Field(
        default_factory=list,
        description="IDs of blocks sorted in logical reading order"
    )
    tables: list[TableResult] = Field(default_factory=list)
    entities: list[EntityResult] = Field(default_factory=list)
    fields: list[ExtractedField] = Field(default_factory=list)
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    processing: ProcessingSummary = Field(default_factory=ProcessingSummary)


class BlockUpdateRequest(BaseModel):
    text: Optional[str] = None
    layout_type: Optional[str] = None
    confidence: Optional[float] = None
    bbox: Optional[BBox] = None

