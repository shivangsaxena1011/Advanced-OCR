#!/usr/bin/env python
"""
AORL Benchmark Suite
Evaluates throughput (pages/min, blocks/sec), memory footprint, stage latencies,
and confidence distribution across sample document sets.
"""

import os
import sys
import time
import tracemalloc
from pathlib import Path
import numpy as np

# Ensure backend root is on sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.pipeline import DocumentPipeline
from app.services.storage.file_store import FileStorageService


def run_benchmarks(sample_dir: Path):
    print("=" * 70)
    print("  AORL PIPELINE BENCHMARK & PERFORMANCE AUDIT")
    print("=" * 70)

    files = list(sample_dir.glob("*.pdf")) + list(sample_dir.glob("*.png")) + list(sample_dir.glob("*.jpg"))
    if not files:
        print(f"No sample documents found in {sample_dir}")
        return

    print(f"Target dataset: {len(files)} documents in '{sample_dir}'")
    print("Initializing DocumentPipeline (PaddleOCR Engine)...")

    t0_init = time.perf_counter()
    pipeline = DocumentPipeline()
    init_time = time.perf_counter() - t0_init
    print(f"Engine warm-up & initialization completed in {init_time:.2f}s\n")

    tracemalloc.start()

    total_pages = 0
    total_blocks = 0
    all_confidences = []
    doc_metrics = []

    t_start = time.perf_counter()

    for file_path in files:
        print(f"Processing: {file_path.name} ...", end=" ", flush=True)
        content = file_path.read_bytes()
        is_valid, mime_type, _ = FileStorageService.validate_file(content, file_path.name)
        doc_id, saved_path = FileStorageService.save_upload(content, file_path.name)

        t_doc_start = time.perf_counter()
        doc_res = pipeline.process_document(
            doc_id=doc_id,
            file_path=saved_path,
            original_filename=file_path.name,
            mime_type=mime_type,
        )
        t_doc_end = time.perf_counter()
        doc_elapsed = t_doc_end - t_doc_start

        pages_count = len(doc_res.pages)
        blocks_count = sum(len(p.ocr_blocks) for p in doc_res.pages)
        conf_list = [b.confidence for p in doc_res.pages for b in p.ocr_blocks]

        total_pages += pages_count
        total_blocks += blocks_count
        all_confidences.extend(conf_list)

        doc_metrics.append({
            "filename": file_path.name,
            "pages": pages_count,
            "blocks": blocks_count,
            "elapsed_s": doc_elapsed,
            "sec_per_page": doc_elapsed / max(1, pages_count),
            "doc_type": doc_res.document_type,
            "mean_conf": float(np.mean(conf_list)) if conf_list else 0.0,
        })
        print(f"Done ({doc_elapsed:.2f}s, {pages_count}p, {blocks_count} blks, type={doc_res.document_type})")

    t_total = time.perf_counter() - t_start
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Calculations
    pages_per_min = (total_pages / t_total) * 60.0 if t_total > 0 else 0.0
    blocks_per_sec = (total_blocks / t_total) if t_total > 0 else 0.0

    print("\n" + "=" * 70)
    print("  PER-DOCUMENT SUMMARY")
    print("=" * 70)
    header = f"{'Document':<26} | {'Pages':<5} | {'Blocks':<6} | {'Time (s)':<8} | {'Type':<15} | {'Avg Conf':<8}"
    print(header)
    print("-" * len(header))
    for m in doc_metrics:
        print(f"{m['filename']:<26} | {m['pages']:<5} | {m['blocks']:<6} | {m['elapsed_s']:<8.2f} | {m['doc_type']:<15} | {m['mean_conf']*100:<7.1f}%")

    print("\n" + "=" * 70)
    print("  THROUGHPUT & RESOURCE BENCHMARKS")
    print("=" * 70)
    print(f"Total processing time:     {t_total:.2f} seconds")
    print(f"Total pages processed:     {total_pages} pages")
    print(f"Total OCR blocks detected: {total_blocks} blocks")
    print(f"Throughput (Pages/min):    {pages_per_min:.2f} pages/min")
    print(f"Throughput (Blocks/sec):   {blocks_per_sec:.2f} blocks/sec")
    print(f"Peak memory footprint:     {peak_mem / (1024 * 1024):.2f} MB")
    print(f"Current memory overhead:   {current_mem / (1024 * 1024):.2f} MB")

    if all_confidences:
        conf_arr = np.array(all_confidences)
        print("\n" + "=" * 70)
        print("  OCR CONFIDENCE DISTRIBUTION")
        print("=" * 70)
        print(f"Min Confidence:            {np.min(conf_arr)*100:.1f}%")
        print(f"Mean Confidence:           {np.mean(conf_arr)*100:.1f}%")
        print(f"Median Confidence:         {np.median(conf_arr)*100:.1f}%")
        print(f"Max Confidence:            {np.max(conf_arr)*100:.1f}%")
        print("Confidence Buckets:")
        b_90_100 = np.sum(conf_arr >= 0.90)
        b_80_90 = np.sum((conf_arr >= 0.80) & (conf_arr < 0.90))
        b_70_80 = np.sum((conf_arr >= 0.70) & (conf_arr < 0.80))
        b_below_70 = np.sum(conf_arr < 0.70)
        n = len(conf_arr)
        print(f"  >= 90%: {b_90_100:>4} ({b_90_100/n*100:.1f}%)")
        print(f"  80-89%: {b_80_90:>4} ({b_80_90/n*100:.1f}%)")
        print(f"  70-79%: {b_70_80:>4} ({b_70_80/n*100:.1f}%)")
        print(f"   < 70%: {b_below_70:>4} ({b_below_70/n*100:.1f}%)")

    print("=" * 70)
    print("  BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    sample_dir = Path(__file__).resolve().parent.parent / "sample_documents"
    run_benchmarks(sample_dir)
