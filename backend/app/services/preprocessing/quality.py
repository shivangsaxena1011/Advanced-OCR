import cv2
import numpy as np
from PIL import Image

from app.schemas.document import ImageQualityMetrics


class ImageQualityAnalyzer:
    """
    Computes measurable properties of an input document image and estimates OCR readiness.
    All scores are calculated using deterministic computer vision algorithms.
    """

    @classmethod
    def analyze(cls, image: Image.Image | np.ndarray) -> ImageQualityMetrics:
        if isinstance(image, Image.Image):
            dpi_info = image.info.get("dpi")
            dpi = int(dpi_info[0]) if dpi_info and isinstance(dpi_info, (tuple, list)) else None
            img_np = np.array(image.convert("RGB"))
        else:
            dpi = None
            img_np = image

        h, w = img_np.shape[:2]

        # Convert to grayscale for metrics
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np

        # Brightness (mean pixel intensity 0-255)
        brightness = float(np.mean(gray))

        # Contrast (standard deviation of pixel intensity)
        contrast = float(np.std(gray))

        # Blur estimate (variance of the Laplacian)
        # Higher means sharper, < 100 indicates noticeable blur
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Skew estimate using minimum area bounding box on edges
        skew_angle = cls._estimate_skew_angle(gray)

        # Calculate an application-derived OCR readiness score (0-100)
        score, notes = cls._calculate_readiness_score(
            w, h, dpi, brightness, contrast, laplacian_var, skew_angle
        )

        return ImageQualityMetrics(
            width=w,
            height=h,
            dpi=dpi,
            brightness=round(brightness, 2),
            contrast=round(contrast, 2),
            blur_estimate=round(laplacian_var, 2),
            skew_estimate=round(skew_angle, 2),
            readiness_score=round(score, 1),
            readiness_notes=notes,
        )

    @classmethod
    def _estimate_skew_angle(cls, gray: np.ndarray) -> float:
        try:
            thresh = cv2.threshold(
                gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )[1]
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) < 50:
                return 0.0

            angle = cv2.minAreaRect(coords)[-1]
            # minAreaRect returns angle in [-90, 0)
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle
            else:
                angle = -angle
            return float(angle)
        except Exception:
            return 0.0

    @classmethod
    def _calculate_readiness_score(
        cls,
        w: int,
        h: int,
        dpi: int | None,
        brightness: float,
        contrast: float,
        laplacian_var: float,
        skew_angle: float,
    ) -> tuple[float, list[str]]:
        score = 100.0
        notes: list[str] = []

        # Resolution check
        min_dim = min(w, h)
        if min_dim < 600:
            penalty = 25.0
            score -= penalty
            notes.append("Low resolution image (<600px). Small text may lose legibility.")
        elif min_dim < 1000:
            score -= 10.0
            notes.append("Moderate resolution image.")

        # Brightness check
        if brightness < 60:
            score -= 20.0
            notes.append("Image appears significantly underexposed / dark.")
        elif brightness > 225:
            score -= 15.0
            notes.append("Image appears overexposed / washed out.")

        # Contrast check
        if contrast < 35:
            score -= 20.0
            notes.append("Low contrast between text and background.")

        # Blur check
        if laplacian_var < 50:
            score -= 30.0
            notes.append("High blur detected. Characters may be indistinct.")
        elif laplacian_var < 100:
            score -= 15.0
            notes.append("Mild blur detected.")

        # Skew check
        if abs(skew_angle) > 5.0:
            score -= 15.0
            notes.append(f"Noticeable skew ({abs(skew_angle):.1f}°). Auto-deskew recommended.")

        final_score = max(0.0, min(100.0, score))
        if not notes:
            notes.append("Optimal image clarity, contrast, and orientation for OCR.")

        return final_score, notes
