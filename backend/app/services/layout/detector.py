from typing import Sequence
from app.schemas.document import BBox, LayoutBlock, OCRBlock
from app.services.layout.classifier import LayoutClassifier
from app.services.layout.geometry import LayoutGeometry


class LayoutDetector:
    """
    Groups line-level OCR blocks into semantic layout blocks
    (paragraphs, headings, titles, lists, headers, footers).
    Maintains 100% source traceability to constituent OCR block IDs.
    """

    @classmethod
    def detect_layout(
        cls,
        ocr_blocks: Sequence[OCRBlock],
        page_width: int,
        page_height: int,
        page_number: int = 1,
    ) -> list[LayoutBlock]:
        if not ocr_blocks:
            return []

        # Sort OCR blocks top-to-bottom, left-to-right
        sorted_blocks = sorted(ocr_blocks, key=lambda b: (round(b.bbox.y1 / 15) * 15, b.bbox.x1))

        clusters: list[list[OCRBlock]] = []
        current_cluster: list[OCRBlock] = []

        for block in sorted_blocks:
            if not current_cluster:
                current_cluster.append(block)
                continue

            prev_block = current_cluster[-1]
            prev_bbox = prev_block.bbox
            curr_bbox = block.bbox

            # Vertical distance between consecutive lines
            vertical_distance = curr_bbox.y1 - prev_bbox.y2
            avg_line_height = (prev_bbox.height + curr_bbox.height) / 2.0

            # Line height ratio
            height_ratio = max(prev_bbox.height, curr_bbox.height) / max(1.0, min(prev_bbox.height, curr_bbox.height))

            # Heading/title indicators
            prev_is_heading = prev_block.text.isupper() or prev_block.text.startswith(("1.", "2.", "3.", "4.", "5."))
            curr_is_heading = block.text.isupper() or block.text.startswith(("1.", "2.", "3.", "4.", "5."))

            # Horizontal proximity
            h_overlap = LayoutGeometry.horizontal_overlap(prev_bbox, curr_bbox)

            # Check if block should merge into current cluster
            is_close_vertically = -5 <= vertical_distance <= (avg_line_height * 1.1)
            is_aligned = h_overlap > 0.1 or abs(curr_bbox.x1 - prev_bbox.x1) < (page_width * 0.08)
            is_same_style = height_ratio < 1.35 and not prev_is_heading and not curr_is_heading

            if is_close_vertically and is_aligned and is_same_style:
                current_cluster.append(block)
            else:
                clusters.append(current_cluster)
                current_cluster = [block]


        if current_cluster:
            clusters.append(current_cluster)

        # Convert clusters to LayoutBlock instances
        layout_blocks: list[LayoutBlock] = []
        for idx, cluster in enumerate(clusters, 1):
            union_bbox = LayoutGeometry.compute_union_bbox(cluster)
            ltype, conf = LayoutClassifier.classify_cluster(cluster, page_width, page_height)
            aggregated_text = "\n".join(b.text for b in cluster)
            source_ids = [b.id for b in cluster]

            layout_blocks.append(
                LayoutBlock(
                    id=f"layout_p{page_number}_{idx:03d}",
                    type=ltype,
                    text=aggregated_text,
                    bbox=union_bbox,
                    confidence=round(conf, 2),
                    page=page_number,
                    source_ocr_blocks=source_ids,
                )
            )

        return layout_blocks
