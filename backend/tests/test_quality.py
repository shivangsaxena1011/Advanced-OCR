import numpy as np
from PIL import Image, ImageDraw
from app.services.preprocessing.quality import ImageQualityAnalyzer
from app.services.preprocessing.pipeline import PreprocessingPipeline


def test_image_quality_analysis():
    # Create clear synthetic document
    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Document Title", fill=(0, 0, 0))
    draw.line((50, 100, 750, 100), fill=(0, 0, 0), width=2)

    metrics = ImageQualityAnalyzer.analyze(img)
    assert metrics.width == 800
    assert metrics.height == 600
    assert metrics.brightness > 200.0
    assert metrics.readiness_score > 0.0
    assert len(metrics.readiness_notes) > 0


def test_preprocessing_pipeline():
    img = Image.new("RGB", (700, 500), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), "Sample Text Line", fill=(20, 20, 20))

    result = PreprocessingPipeline.run(img)
    assert result.original_image.shape == (500, 700, 3)
    assert result.processed_image.shape == (500, 700, 3)
    assert result.quality_metrics.width == 700
    assert result.scale_factor == 1.0
