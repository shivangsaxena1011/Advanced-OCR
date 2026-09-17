import numpy as np
import pytest
from app.services.ocr.normalizer import OCRNormalizer
from app.schemas.document import OCRBlock


def test_normalize_paddlex_dict():
    raw = [
        {
            "rec_texts": ["INVOICE", "TOTAL $100"],
            "rec_scores": [0.995, 0.982],
            "rec_boxes": np.array([
                [10, 20, 100, 50],
                [15, 60, 150, 90],
            ]),
            "rec_polys": [
                np.array([[10, 20], [100, 20], [100, 50], [10, 50]]),
                np.array([[15, 60], [150, 60], [150, 90], [15, 90]]),
            ],
        }
    ]

    blocks = OCRNormalizer.normalize_paddle_result(raw, page_number=1)
    assert len(blocks) == 2
    assert blocks[0].text == "INVOICE"
    assert blocks[0].confidence == 0.995
    assert blocks[0].bbox.x1 == 10.0
    assert blocks[0].bbox.y1 == 20.0
    assert blocks[0].bbox.x2 == 100.0
    assert blocks[0].bbox.y2 == 50.0
    assert blocks[0].page == 1
    assert blocks[0].id == "ocr_p1_001"

    assert blocks[1].text == "TOTAL $100"
    assert blocks[1].confidence == 0.982
    assert blocks[1].id == "ocr_p1_002"


def test_normalize_legacy_list():
    raw = [
        [
            [
                [[10.0, 20.0], [100.0, 20.0], [100.0, 50.0], [10.0, 50.0]],
                ("Legacy Invoice", 0.941),
            ]
        ]
    ]

    blocks = OCRNormalizer.normalize_paddle_result(raw, page_number=2)
    assert len(blocks) == 1
    assert blocks[0].text == "Legacy Invoice"
    assert blocks[0].confidence == 0.941
    assert blocks[0].page == 2
    assert blocks[0].id == "ocr_p2_001"
    assert blocks[0].bbox.x1 == 10.0
    assert blocks[0].bbox.y2 == 50.0


def test_normalize_empty():
    assert OCRNormalizer.normalize_paddle_result(None) == []
    assert OCRNormalizer.normalize_paddle_result([]) == []
    assert OCRNormalizer.normalize_paddle_result([{}]) == []
