from typing import Sequence
from app.schemas.document import BBox, OCRBlock


class LayoutGeometry:
    """
    Spatial geometry utilities for document layout analysis:
    - Bounding box unions
    - Horizontal & vertical overlap computation
    - Line clustering
    """

    @staticmethod
    def compute_union_bbox(blocks: Sequence[OCRBlock]) -> BBox:
        if not blocks:
            return BBox(x1=0, y1=0, x2=0, y2=0)

        min_x = min(b.bbox.x1 for b in blocks)
        min_y = min(b.bbox.y1 for b in blocks)
        max_x = max(b.bbox.x2 for b in blocks)
        max_y = max(b.bbox.y2 for b in blocks)

        return BBox(x1=min_x, y1=min_y, x2=max_x, y2=max_y)

    @staticmethod
    def vertical_overlap(b1: BBox, b2: BBox) -> float:
        top = max(b1.y1, b2.y1)
        bottom = min(b1.y2, b2.y2)
        if bottom <= top:
            return 0.0
        overlap = bottom - top
        h1 = b1.y2 - b1.y1
        h2 = b2.y2 - b2.y1
        min_h = max(1.0, min(h1, h2))
        return overlap / min_h

    @staticmethod
    def horizontal_overlap(b1: BBox, b2: BBox) -> float:
        left = max(b1.x1, b2.x1)
        right = min(b1.x2, b2.x2)
        if right <= left:
            return 0.0
        overlap = right - left
        w1 = b1.x2 - b1.x1
        w2 = b2.x2 - b2.x1
        min_w = max(1.0, min(w1, w2))
        return overlap / min_w

    @staticmethod
    def vertical_gap(top_box: BBox, bottom_box: BBox) -> float:
        return bottom_box.y1 - top_box.y2
