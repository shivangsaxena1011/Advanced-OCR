export interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface OCRBlock {
  id: string;
  text: string;
  confidence: number;
  bbox: BBox;
  polygon?: number[][];
  page: number;
}

export interface LayoutBlock {
  id: string;
  type: string;
  text: string;
  bbox: BBox;
  confidence: number;
  page: number;
  source_ocr_blocks: string[];
}

export interface TableCell {
  row_index: number;
  col_index: number;
  row_span?: number;
  col_span?: number;
  text: string;
  confidence: number;
  bbox?: BBox;
}

export interface TableResult {
  table_id: string;
  page: number;
  bbox: BBox;
  headers: string[];
  rows: string[][];
  cells?: TableCell[];
  confidence: number;
}

export interface EntityResult {
  id: string;
  type: string;
  text: string;
  confidence: number;
  page: number;
  bbox?: BBox;
  source_block?: string;
}

export interface ExtractedField {
  id: string;
  field: string;
  value: string;
  confidence: number;
  page: number;
  bbox?: BBox;
  source_block?: string;
}

export interface ImageQualityMetrics {
  width: number;
  height: number;
  dpi?: number;
  brightness: number;
  contrast: number;
  blur_estimate: number;
  skew_estimate: number;
  readiness_score: number;
  readiness_notes: string[];
}

export interface PageResult {
  page: number;
  width: number;
  height: number;
  image_url: string;
  thumbnail_url: string;
  ocr_blocks: OCRBlock[];
  layout_blocks: LayoutBlock[];
  quality?: ImageQualityMetrics;
}

export interface DocumentMetadata {
  file_size_bytes: number;
  mime_type: string;
  page_count: number;
  created_at: string;
  processing_time_ms: number;
  ocr_engine: string;
}

export interface ProcessingStageStatus {
  stage: string;
  status: "PENDING" | "IN_PROGRESS" | "COMPLETED" | "FAILED" | "SKIPPED";
  message?: string;
  duration_ms?: number;
}

export interface ProcessingSummary {
  status: "QUEUED" | "PROCESSING" | "COMPLETED" | "FAILED";
  current_stage: string;
  stages: ProcessingStageStatus[];
  error?: string;
}

export interface DocumentResult {
  schema_version: string;
  document_id: string;
  filename: string;
  document_type?: string;
  document_type_confidence?: number;
  pages: PageResult[];
  reading_order: string[];
  tables: TableResult[];
  entities: EntityResult[];
  fields: ExtractedField[];
  metadata: DocumentMetadata;
  processing: ProcessingSummary;
}
