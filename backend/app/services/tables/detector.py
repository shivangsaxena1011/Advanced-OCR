from typing import Sequence
import numpy as np
from app.schemas.document import BBox, OCRBlock, TableCell, TableResult


class TableExtractor:
    """
    Detects and reconstructs tabular data from spatial alignments of OCR blocks.
    Groups aligned text tokens into rows and columns, isolates headers and data cells.
    """

    @classmethod
    def extract_tables_from_page(
        cls,
        ocr_blocks: Sequence[OCRBlock],
        page_number: int = 1,
    ) -> list[TableResult]:
        if len(ocr_blocks) < 4:
            return []

        # 1. Find potential table lines: multiple tokens sharing horizontal alignment (similar Y)
        # Bin blocks by Y coordinate (within 12px tolerance)
        y_tolerance = 14.0
        row_bins: list[list[OCRBlock]] = []

        sorted_by_y = sorted(ocr_blocks, key=lambda b: (b.bbox.y1, b.bbox.x1))

        for block in sorted_by_y:
            placed = False
            for r_bin in row_bins:
                avg_y = sum((b.bbox.y1 + b.bbox.y2) / 2.0 for b in r_bin) / len(r_bin)
                block_center_y = (block.bbox.y1 + block.bbox.y2) / 2.0
                if abs(block_center_y - avg_y) <= y_tolerance:
                    r_bin.append(block)
                    placed = True
                    break
            if not placed:
                row_bins.append([block])

        # A row with >= 3 items (or repeated rows with >= 2 items) indicates tabular columns
        tabular_rows = [sorted(r, key=lambda b: b.bbox.x1) for r in row_bins if len(r) >= 3]

        if len(tabular_rows) < 2:
            # Check for 2-column tabular sequences (e.g. key-value tables like Subtotal / $100)
            pair_rows = [sorted(r, key=lambda b: b.bbox.x1) for r in row_bins if len(r) == 2]
            if len(pair_rows) >= 3:
                tabular_rows = pair_rows
            else:
                return []

        # Cluster contiguous tabular rows into tables
        table_clusters: list[list[list[OCRBlock]]] = []
        current_table: list[list[OCRBlock]] = []

        for row in tabular_rows:
            if not current_table:
                current_table.append(row)
                continue

            prev_row_y = sum(b.bbox.y2 for b in current_table[-1]) / len(current_table[-1])
            curr_row_y = sum(b.bbox.y1 for b in row) / len(row)

            # Contiguous rows gap < 60px
            if 0 <= (curr_row_y - prev_row_y) <= 65:
                current_table.append(row)
            else:
                if len(current_table) >= 2:
                    table_clusters.append(current_table)
                current_table = [row]

        if len(current_table) >= 2:
            table_clusters.append(current_table)

        # Convert each cluster into a TableResult
        tables: list[TableResult] = []
        for t_idx, cluster in enumerate(table_clusters, 1):
            all_blocks_in_table = [b for r in cluster for b in r]
            min_x = min(b.bbox.x1 for b in all_blocks_in_table)
            min_y = min(b.bbox.y1 for b in all_blocks_in_table)
            max_x = max(b.bbox.x2 for b in all_blocks_in_table)
            max_y = max(b.bbox.y2 for b in all_blocks_in_table)

            table_bbox = BBox(x1=min_x, y1=min_y, x2=max_x, y2=max_y)

            # Build grid rows and cells
            headers: list[str] = [b.text for b in cluster[0]]
            data_rows: list[list[str]] = []
            cells: list[TableCell] = []

            # First row as header cells
            for c_idx, b in enumerate(cluster[0]):
                cells.append(
                    TableCell(
                        row_index=0,
                        col_index=c_idx,
                        text=b.text,
                        confidence=b.confidence,
                        bbox=b.bbox,
                    )
                )

            # Remaining rows
            for r_idx, row in enumerate(cluster[1:], 1):
                row_texts = [b.text for b in row]
                data_rows.append(row_texts)
                for c_idx, b in enumerate(row):
                    cells.append(
                        TableCell(
                            row_index=r_idx,
                            col_index=c_idx,
                            text=b.text,
                            confidence=b.confidence,
                            bbox=b.bbox,
                        )
                    )

            tables.append(
                TableResult(
                    table_id=f"table_p{page_number}_{t_idx:02d}",
                    page=page_number,
                    bbox=table_bbox,
                    headers=headers,
                    rows=data_rows,
                    cells=cells,
                    confidence=0.92,
                )
            )

        return tables
