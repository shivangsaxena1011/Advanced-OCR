import cv2
import numpy as np


class Deskewer:
    """
    Detects and corrects document skew using Hough Line Transform and minimum area rectangles.
    """

    @classmethod
    def calculate_skew(cls, gray: np.ndarray) -> float:
        # Detect edges
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        # Hough line transform
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10
        )

        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0:
                    continue
                angle = np.degrees(np.arctan2(dy, dx))
                # Only consider near-horizontal document text lines (-45 to +45 deg)
                if -45 < angle < 45:
                    angles.append(angle)

            if angles:
                median_angle = float(np.median(angles))
                return median_angle

        return 0.0

    @classmethod
    def rotate_image(cls, image: np.ndarray, angle: float) -> np.ndarray:
        if abs(angle) < 0.2:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)

        # Compute rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        # Compute new bounding dimensions
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        # Adjust transformation matrix center
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        rotated = cv2.warpAffine(
            image,
            M,
            (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255) if len(image.shape) == 3 else 255,
        )
        return rotated
