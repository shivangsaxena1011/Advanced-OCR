"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCw,
  Eye,
  EyeOff,
  Sparkles,
  Move,
} from "lucide-react";
import { OCRBlock, PageResult } from "@/types/document";
import { getFileUrl } from "@/lib/api";

interface DocumentCanvasProps {
  page: PageResult;
  selectedBlockId: string | null;
  onSelectBlock: (block: OCRBlock | null) => void;
  showBoxes?: boolean;
  showConfidence?: boolean;
  matchingBlockIds?: Set<string>;
}

export default function DocumentCanvas({
  page,
  selectedBlockId,
  onSelectBlock,
  showBoxes = true,
  showConfidence = false,
  matchingBlockIds,
}: DocumentCanvasProps) {

  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const [zoom, setZoom] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredBlock, setHoveredBlock] = useState<OCRBlock | null>(null);

  // Auto-fit to container width on page change
  useEffect(() => {
    if (containerRef.current && page.width > 0) {
      const containerWidth = containerRef.current.clientWidth - 48;
      const initialZoom = Math.min(1.2, Math.max(0.4, containerWidth / page.width));
      setZoom(initialZoom);
      setPan({ x: 0, y: 0 });
    }
  }, [page.page, page.width]);

  // Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0 && (e.target as HTMLElement).tagName !== "rect") {
      setIsPanning(true);
      setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({ x: e.clientX - startPan.x, y: e.clientY - startPan.y });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleZoomIn = () => setZoom((z) => Math.min(3.5, z + 0.15));
  const handleZoomOut = () => setZoom((z) => Math.max(0.2, z - 0.15));
  const handleFit = () => {
    if (containerRef.current && page.width > 0) {
      const containerWidth = containerRef.current.clientWidth - 48;
      setZoom(containerWidth / page.width);
      setPan({ x: 0, y: 0 });
    }
  };
  const handleRotate = () => setRotation((r) => (r + 90) % 360);

  // Confidence color map
  const getBoxColor = (conf: number, isSelected: boolean) => {
    if (isSelected) return "rgba(59, 130, 246, 0.4)";
    if (!showConfidence) return "rgba(14, 165, 233, 0.15)";
    if (conf >= 0.9) return "rgba(16, 185, 129, 0.25)"; // green
    if (conf >= 0.75) return "rgba(234, 179, 8, 0.25)"; // yellow
    return "rgba(239, 68, 68, 0.3)"; // red
  };

  const getBorderColor = (conf: number, isSelected: boolean) => {
    if (isSelected) return "#3b82f6";
    if (!showConfidence) return "#0284c7";
    if (conf >= 0.9) return "#10b981";
    if (conf >= 0.75) return "#eab308";
    return "#ef4444";
  };

  const imageUrl = getFileUrl(page.image_url);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0a0e17] overflow-hidden select-none relative">
      {/* Floating Toolbar */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-700/80 shadow-2xl backdrop-blur-md">
        <button
          onClick={handleZoomOut}
          title="Zoom Out (-)"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-xs font-semibold text-slate-300 w-12 text-center">
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={handleZoomIn}
          title="Zoom In (+)"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <div className="w-px h-4 bg-slate-700 mx-1" />
        <button
          onClick={handleFit}
          title="Fit to Width (0)"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <button
          onClick={handleRotate}
          title="Rotate 90°"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <RotateCw className="w-4 h-4" />
        </button>
      </div>

      {/* Main Canvas Scroll Area */}
      <div
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className={`flex-1 overflow-auto flex items-center justify-center p-8 cursor-${
          isPanning ? "grabbing" : "grab"
        }`}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: "center center",
            transition: isPanning ? "none" : "transform 0.15s ease-out",
          }}
          className="relative shadow-2xl rounded border border-slate-800 bg-white"
        >
          {/* Document Render Image */}
          <img
            ref={imageRef}
            src={imageUrl}
            alt={`Page ${page.page}`}
            className="max-w-none block pointer-events-none"
            style={{ width: `${page.width}px`, height: `${page.height}px` }}
          />

          {/* SVG Bounding Boxes Overlay */}
          {showBoxes && (
            <svg
              className="absolute inset-0 w-full h-full pointer-events-auto"
              viewBox={`0 0 ${page.width} ${page.height}`}
            >
              {page.ocr_blocks.map((block) => {
                const isSelected = selectedBlockId === block.id;
                const isHovered = hoveredBlock?.id === block.id;
                const isMatch = matchingBlockIds?.has(block.id) || false;
                const w = Math.max(2, block.bbox.x2 - block.bbox.x1);
                const h = Math.max(2, block.bbox.y2 - block.bbox.y1);

                const fill = isMatch
                  ? "rgba(234, 179, 8, 0.4)"
                  : getBoxColor(block.confidence, isSelected);
                const stroke = isMatch
                  ? "#f59e0b"
                  : getBorderColor(block.confidence, isSelected || isHovered);

                return (
                  <g key={block.id}>
                    <rect
                      x={block.bbox.x1}
                      y={block.bbox.y1}
                      width={w}
                      height={h}
                      fill={fill}
                      stroke={stroke}
                      strokeWidth={isSelected || isMatch ? 2.5 : isHovered ? 2 : 1}
                      className="cursor-pointer transition-all duration-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectBlock(block);
                      }}
                      onMouseEnter={() => setHoveredBlock(block)}
                      onMouseLeave={() => setHoveredBlock(null)}
                    />
                  </g>
                );
              })}

            </svg>
          )}

          {/* Hover Tooltip */}
          {hoveredBlock && (
            <div
              style={{
                left: `${hoveredBlock.bbox.x1}px`,
                top: `${hoveredBlock.bbox.y1 - 28}px`,
              }}
              className="absolute z-30 pointer-events-none px-2 py-1 rounded bg-slate-900/95 border border-slate-700 text-white text-[11px] font-medium shadow-xl whitespace-nowrap"
            >
              <span className="text-blue-300 font-semibold mr-1.5">
                {Math.round(hoveredBlock.confidence * 100)}%
              </span>
              <span>{hoveredBlock.text}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
