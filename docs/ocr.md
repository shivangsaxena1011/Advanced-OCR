# OCR Engine & Adapter Architecture

## BaseOCREngine Interface

```python
class BaseOCREngine(ABC):
    @abstractmethod
    def process_image(self, image: np.ndarray | Image.Image, page_number: int = 1) -> list[OCRBlock]:
        raise NotImplementedError

    @abstractmethod
    def get_engine_name(self) -> str:
        raise NotImplementedError
```

## PaddleOCR 3.7 Implementation

The application leverages PaddleOCR 3.7 (PP-OCRv6) for state-of-the-art text line detection and recognition.

### CPU Stability on Windows

On Windows CPU with PaddlePaddle 3.3.1, PIR/oneDNN execution encounters an unresolved attribute conversion issue when running static models. AORL cleanly resolves this by automatically appending OCR detection and recognition models to `paddlex.inference.models.runners.paddle_static.config.blocklists.MKLDNN_BLOCKLIST`. This allows native Paddle inference on CPU with 100% stability and zero crashes.

## Normalization Schema

Raw engine outputs are normalized into standard Pydantic models:

```json
{
  "id": "ocr_p1_001",
  "text": "INVOICE #9041",
  "confidence": 0.992,
  "bbox": {
    "x1": 50.0,
    "y1": 60.0,
    "x2": 250.0,
    "y2": 95.0
  },
  "page": 1
}
```
