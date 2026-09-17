from typing import Sequence
from app.schemas.document import BBox, LayoutBlock, OCRBlock


class ReadingOrderResolver:
    """
    Computes natural reading order for complex documents:
    - Multi-column detection (2-column, 3-column articles)
    - Full-width spanning title / header precedence
    - Top-to-bottom, left-to-right topological order
    """

    @classmethod
    def resolve_reading_order(
        cls,
        layout_blocks: Sequence[LayoutBlock],
        page_width: int,
        page_height: int,
    ) -> list[str]:
        if not layout_blocks:
            return []

        # 1. Detect if page has multi-column content
        columns = cls._detect_columns(layout_blocks, page_width)

        if len(columns) <= 1:
            # Single column flow: standard vertical order
            sorted_blocks = sorted(layout_blocks, key=lambda b: (b.bbox.y1, b.bbox.x1))
            return [b.id for b in sorted_blocks]

        # Multi-column flow:
        # Separate full-width spanning blocks (e.g. header, title) from column blocks
        spanning_blocks: list[LayoutBlock] = []
        column_assigned_blocks: dict[int, list[LayoutBlock]] = {i: [] for i in range(len(columns))}

        midpoint_tolerance = page_width * 0.65

        for b in layout_blocks:
            # If block width is more than 65% of page, it spans across columns
            if b.bbox.width > midpoint_tolerance or b.type in ("title", "header"):
                spanning_blocks.append(b)
            else:
                # Assign to closest column
                assigned_col = 0
                best_dist = float("inf")
                center_x = (b.bbox.x1 + b.bbox.x2) / 2.0

                for col_idx, (col_left, col_right) in enumerate(columns):
                    col_center = (col_left + col_right) / 2.0
                    dist = abs(center_x - col_center)
                    if dist < best_dist:
                        best_dist = dist
                        assigned_col = col_idx

                column_assigned_blocks[assigned_col].append(b)

        # Sort spanning blocks by Y
        spanning_blocks.sort(key=lambda b: b.bbox.y1)

        # Sort blocks within each column by Y
        for col_idx in column_assigned_blocks:
            column_assigned_blocks[col_idx].sort(key=lambda b: b.bbox.y1)

        # Build reading order:
        # Spanning blocks that appear before columns -> Column 0 -> Column 1 -> ... -> Footer spanning blocks
        result_order: list[str] = []

        # Find min Y of column blocks
        col_min_y = min(
            (b.bbox.y1 for col in column_assigned_blocks.values() for b in col),
            default=page_height,
        )
        col_max_y = max(
            (b.bbox.y2 for col in column_assigned_blocks.values() for b in col),
            default=0,
        )

        # Top headers/titles
        for sb in spanning_blocks:
            if sb.bbox.y2 <= col_min_y + 30:
                result_order.append(sb.id)

        # Columns left-to-right
        for col_idx in sorted(column_assigned_blocks.keys()):
            for b in column_assigned_blocks[col_idx]:
                result_order.append(b.id)

        # Bottom footers
        for sb in spanning_blocks:
            if sb.bbox.y1 >= col_max_y - 30 and sb.id not in result_order:
                result_order.append(sb.id)

        # Any remaining
        for sb in spanning_blocks:
            if sb.id not in result_order:
                result_order.append(sb.id)

        return result_order

    @classmethod
    def _detect_columns(
        cls, blocks: Sequence[LayoutBlock], page_width: int
    ) -> list[tuple[float, float]]:
        # Count horizontal midpoint occurrences
        left_count = 0
        right_count = 0
        page_center = page_width / 2.0

        for b in blocks:
            if b.bbox.width < page_width * 0.55:
                center_x = (b.bbox.x1 + b.bbox.x2) / 2.0
                if center_x < page_center:
                    left_count += 1
                else:
                    right_count += 1

        # If both left and right have multiple distinct blocks, we have 2 columns
        if left_count >= 2 and right_count >= 2:
            col1 = (0.0, page_center)
            col2 = (page_center, float(page_width))
            return [col1, col2]

        return [(0.0, float(page_width))]
