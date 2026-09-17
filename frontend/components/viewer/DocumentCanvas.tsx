"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCw,
  Eye,
  EyeOff,
  Maximize,
  Minimize,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { OCRBlock, PageResult } from "@/types/document";
import { getFileUrl } from "@/lib/api";

interface DocumentCanvasProps {
  page: PageResult;
  totalPages?: number;
  selectedBlockId: string | null;
  onSelectBlock: (block: OCRBlock | null) => void;
  showBoxes?: boolean;
  onToggleShowBoxes?: () => void;
  showConfidence?: boolean;
  onToggleConfidence?: () => void;
  matchingBlockIds?: Set<string>;
  onPrevPage?: () => void;
  onNextPage?: () => void;
}

export default function DocumentCanvas({
  page,
  totalPages = 1,
  selectedBlockId,
  onSelectBlock,
  showBoxes = true,
  onToggleShowBoxes,
  showConfidence = false,
  matchingBlockIds,
  onPrevPage,
  onNextPage,
}: DocumentCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const [zoom, setZoom] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredBlock, setHoveredBlock] = useState<OCRBlock | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Fullscreen change listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
  }, []);

  const handleToggleFullscreen = () => {
    if (!document.fullscreenElement) {
      wrapperRef.current?.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  };

  // Auto-fit to container on page change or rotation change
  useEffect(() => {
    if (containerRef.current && page.width > 0 && page.height > 0) {
      const isSideways = rotation === 90 || rotation === 270;
      const effectiveW = isSideways ? page.height : page.width;
      const effectiveH = isSideways ? page.width : page.height;

      const containerW = containerRef.current.clientWidth - 48;
      const containerH = containerRef.current.clientHeight - 48;

      const scaleW = containerW / effectiveW;
      const scaleH = containerH / effectiveH;
      const fitZoom = Math.min(1.2, Math.max(0.3, Math.min(scaleW, scaleH)));

      setZoom(fitZoom);
      setPan({ x: 0, y: 0 });
    }
  }, [page.page, page.width, page.height]);

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

  const handleZoomIn = () => setZoom((z) => Math.min(4.0, z + 0.15));
  const handleZoomOut = () => setZoom((z) => Math.max(0.2, z - 0.15));
  const handleFit = () => {
    if (containerRef.current && page.width > 0 && page.height > 0) {
      const isSideways = rotation === 90 || rotation === 270;
      const effectiveW = isSideways ? page.height : page.width;
      const effectiveH = isSideways ? page.width : page.height;

      const containerW = containerRef.current.clientWidth - 48;
      const containerH = containerRef.current.clientHeight - 48;

      const fitZoom = Math.min(containerW / effectiveW, containerH / effectiveH);
      setZoom(Math.max(0.2, Math.min(3.0, fitZoom)));
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
    <div
      ref={wrapperRef}
      className="flex-1 flex flex-col h-full bg-[#0a0e17] overflow-hidden select-none relative"
    >
      {/* Floating Control Toolbar */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-700/80 shadow-2xl backdrop-blur-md">
        {/* Page Navigation Controls */}
        {totalPages > 1 && (
          <div className="flex items-center gap-1 pr-1.5 border-r border-slate-700">
            <button
              onClick={onPrevPage}
              disabled={page.page <= 1}
              title="Previous Page"
              className="p-1.5 rounded-lg hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent text-slate-300 hover:text-white transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono font-medium text-slate-300 px-1 whitespace-nowrap">
              {page.page} / {totalPages}
            </span>
            <button
              onClick={onNextPage}
              disabled={page.page >= totalPages}
              title="Next Page"
              className="p-1.5 rounded-lg hover:bg-slate-800 disabled:opacity-30 disabled:hover:bg-transparent text-slate-300 hover:text-white transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Show/Hide OCR Toggle */}
        <button
          onClick={onToggleShowBoxes}
          title={showBoxes ? "Hide OCR Bounding Boxes" : "Show OCR Bounding Boxes"}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition ${
            showBoxes
              ? "bg-blue-600 text-white shadow-sm shadow-blue-500/30"
              : "text-slate-400 hover:text-white hover:bg-slate-800"
          }`}
        >
          {showBoxes ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
          <span>{showBoxes ? "Hide OCR" : "Show OCR"}</span>
        </button>

        <div className="w-px h-4 bg-slate-700 mx-1" />

        {/* Zoom Controls */}
        <button
          onClick={handleZoomOut}
          title="Zoom Out (-)"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-xs font-semibold text-slate-300 w-12 text-center font-mono">
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

        {/* Fit to Screen */}
        <button
          onClick={handleFit}
          title="Fit to Screen (0)"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <Maximize2 className="w-4 h-4" />
        </button>

        {/* Rotate 90 deg */}
        <button
          onClick={handleRotate}
          title="Rotate 90°"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          <RotateCw className="w-4 h-4" />
        </button>

        {/* Fullscreen Toggle */}
        <button
          onClick={handleToggleFullscreen}
          title={isFullscreen ? "Exit Fullscreen" : "Fullscreen Viewer"}
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 hover:text-white transition"
        >
          {isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
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

          {/* SVG Bounding Boxes Overlay with 1:1 Pixel Coordinate Space */}
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
                    {/* Active Halo for Selected Block */}
                    {isSelected && (
                      <rect
                        x={block.bbox.x1 - 3}
                        y={block.bbox.y1 - 3}
                        width={w + 6}
                        height={h + 6}
                        fill="none"
                        stroke="#60a5fa"
                        strokeWidth={2}
                        strokeDasharray="4 2"
                        className="animate-pulse"
                      />
                    )}
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
                top: `${hoveredBlock.bbox.y1 - 32}px`,
              }}
              className="absolute z-30 pointer-events-none px-2.5 py-1.5 rounded-lg bg-slate-900/95 border border-slate-700 text-white text-[11px] font-medium shadow-2xl backdrop-blur-sm whitespace-nowrap flex items-center gap-2"
            >
              <span className="text-emerald-400 font-mono font-bold">
                {Math.round(hoveredBlock.confidence * 100)}%
              </span>
              <span className="text-slate-200 truncate max-w-[200px]">{hoveredBlock.text}</span>
              <span className="text-[10px] text-slate-500 font-mono">
                [{Math.round(hoveredBlock.bbox.x1)}, {Math.round(hoveredBlock.bbox.y1)}]
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

