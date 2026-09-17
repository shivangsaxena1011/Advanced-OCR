import logging
from typing import Any
import numpy as np
from PIL import Image

from app.schemas.document import OCRBlock
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.normalizer import OCRNormalizer

logger = logging.getLogger("aorl.ocr.paddle")


class PaddleOCREngine(BaseOCREngine):
    """
    PaddleOCR implementation conforming to BaseOCREngine.
    Applies CPU stability blocklist fixes to prevent PIR / oneDNN runtime issues on Windows.
    """

    def __init__(
        self,
        lang: str = "en",
        use_gpu: bool = False,
        det_db_thresh: float = 0.3,
        det_db_box_thresh: float = 0.5,
    ):
        self.lang = lang
        self.use_gpu = use_gpu
        self.det_db_thresh = det_db_thresh
        self.det_db_box_thresh = det_db_box_thresh
        self._engine: Any = None
        self._initialize_engine()

    def _initialize_engine(self) -> None:
        try:
            # On Windows CPU with PaddlePaddle 3.3.1, apply blocklist to prevent
            # NotImplementedError in ConvertPirAttribute2RuntimeAttribute
            if not self.use_gpu:
                try:
                    import paddlex.inference.models.runners.paddle_static.config.blocklists as bl
                    models_to_block = [
                        "PP-OCRv6_medium_det",
                        "PP-OCRv6_medium_rec",
                        "PP-OCRv4_mobile_det",
                        "en_PP-OCRv4_mobile_rec",
                        "PP-LCNet_x1_0_doc_ori",
                        "PP-LCNet_x1_0_textline_ori",
                    ]
                    for m in models_to_block:
                        if m not in bl.MKLDNN_BLOCKLIST:
                            bl.MKLDNN_BLOCKLIST.append(m)
                except Exception as e:
                    logger.warning(f"Could not configure MKLDNN_BLOCKLIST: {e}")

            from paddleocr import PaddleOCR

            # Initialize PaddleOCR engine
            self._engine = PaddleOCR(
                lang=self.lang,
                text_det_thresh=self.det_db_thresh,
                text_det_box_thresh=self.det_db_box_thresh,
            )
            logger.info(f"PaddleOCR initialized successfully (lang={self.lang}, gpu={self.use_gpu})")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR engine: {e}", exc_info=True)
            self._engine = None

    def process_image(
        self, image: np.ndarray | Image.Image, page_number: int = 1
    ) -> list[OCRBlock]:
        if self._engine is None:
            self._initialize_engine()
            if self._engine is None:
                raise RuntimeError("PaddleOCR engine is not available.")

        # Convert PIL Image to numpy array (RGB)
        if isinstance(image, Image.Image):
            img_np = np.array(image.convert("RGB"))
        elif isinstance(image, np.ndarray):
            img_np = image
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")

        try:
            # PaddleOCR predict accepts numpy ndarray
            raw_res = self._engine.predict(img_np)
            return OCRNormalizer.normalize_paddle_result(
                raw_res, page_number=page_number, id_prefix="ocr"
            )
        except Exception as e:
            logger.error(f"OCR prediction failed for page {page_number}: {e}", exc_info=True)
            raise

    def get_engine_name(self) -> str:
        return "PaddleOCR 3.7 (PP-OCRv6)"
