import cv2
import numpy as np


class OrientationCorrector:
    """
    Handles orthogonal rotation (90°, 180°, 270°) and general orientation fixes.
    """

    @staticmethod
    def rotate_90_clockwise(image: np.ndarray) -> np.ndarray:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    @staticmethod
    def rotate_180(image: np.ndarray) -> np.ndarray:
        return cv2.rotate(image, cv2.ROTATE_180)

    @staticmethod
    def rotate_270_clockwise(image: np.ndarray) -> np.ndarray:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    @staticmethod
    def rotate_by_step(image: np.ndarray, degrees: int) -> np.ndarray:
        deg = degrees % 360
        if deg == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif deg == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        elif deg == 270:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return image
