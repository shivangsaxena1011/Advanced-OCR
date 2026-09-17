import cv2
import numpy as np


class ImageEnhancer:
    """
    Image enhancement utilities:
    - Grayscale conversion
    - Contrast Enhancement (CLAHE)
    - Denoising (bilateral filter / fastNlMeans)
    - Sharpening
    - Adaptive Thresholding
    - Resizing for optimal OCR recognition
    """

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def enhance_contrast(gray: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        return clahe.apply(gray)

    @staticmethod
    def denoise(gray: np.ndarray) -> np.ndarray:
        # Bilateral filter preserves sharp document edges while removing sensor grain
        return cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    @staticmethod
    def sharpen(image: np.ndarray) -> np.ndarray:
        # Unsharp masking
        gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
        sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        return sharpened

    @staticmethod
    def adaptive_threshold(gray: np.ndarray) -> np.ndarray:
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 11
        )

    @staticmethod
    def resize_if_needed(image: np.ndarray, max_side: int = 3000, min_side: int = 800) -> tuple[np.ndarray, float]:
        h, w = image.shape[:2]
        longest = max(h, w)
        shortest = min(h, w)

        scale = 1.0
        if longest > max_side:
            scale = max_side / longest
        elif shortest < min_side:
            scale = min_side / shortest

        if scale != 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
            resized = cv2.resize(image, (new_w, new_h), interpolation=interp)
            return resized, scale
        return image, 1.0
