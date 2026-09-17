from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
from PIL import Image

from app.schemas.document import ImageQualityMetrics
from app.services.preprocessing.quality import ImageQualityAnalyzer
from app.services.preprocessing.enhancement import ImageEnhancer
from app.services.preprocessing.deskew import Deskewer


@dataclass
class PreprocessingResult:
    original_image: np.ndarray
    processed_image: np.ndarray
    quality_metrics: ImageQualityMetrics
    scale_factor: float
    skew_angle: float
    is_modified: bool


class PreprocessingPipeline:
    """
    Executes automated image quality assessment and non-destructive image enhancement.
    Preserves original image and provides coordinate scale factors.
    """

    @classmethod
    def run(
        cls,
        image: Image.Image | np.ndarray,
        auto_deskew: bool = True,
        auto_enhance_contrast: bool = True,
        auto_denoise: bool = False,
    ) -> PreprocessingResult:
        if isinstance(image, Image.Image):
            original = np.array(image.convert("RGB"))
        else:
            original = image.copy()

        # 1. Analyze initial quality metrics
        quality = ImageQualityAnalyzer.analyze(original)

        working = original.copy()
        is_modified = False
        scale_factor = 1.0

        # 2. Deskew if angle is significant (> 0.5 deg)
        skew_angle = Deskewer.calculate_skew(ImageEnhancer.to_grayscale(working))
        if auto_deskew and abs(skew_angle) > 0.5:
            working = Deskewer.rotate_image(working, skew_angle)
            is_modified = True

        # 3. Optional contrast enhancement if contrast is low
        if auto_enhance_contrast and quality.contrast < 45:
            gray = ImageEnhancer.to_grayscale(working)
            enhanced_gray = ImageEnhancer.enhance_contrast(gray, clip_limit=1.5)
            # Reconstruct RGB
            working = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
            is_modified = True

        return PreprocessingResult(
            original_image=original,
            processed_image=working,
            quality_metrics=quality,
            scale_factor=scale_factor,
            skew_angle=skew_angle,
            is_modified=is_modified,
        )
