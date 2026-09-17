"use client";

import React, { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Sliders,
  Layers,
  Sparkles,
  Download,
  Search,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";
import { DocumentResult, OCRBlock } from "@/types/document";
import { getDocument } from "@/lib/api";
import DocumentCanvas from "@/components/viewer/DocumentCanvas";
import BlockInspector from "@/components/inspector/BlockInspector";
import ThumbnailRail from "@/components/viewer/ThumbnailRail";

export default function DocumentWorkspacePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const docId = resolvedParams.id;

  const [document, setDocument] = useState<DocumentResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activePageNum, setActivePageNum] = useState<number>(1);
  const [selectedBlock, setSelectedBlock] = useState<OCRBlock | null>(null);

  // Layer toggles
  const [showBoxes, setShowBoxes] = useState(true);
  const [showConfidence, setShowConfidence] = useState(false);
  const [showQualityModal, setShowQualityModal] = useState(false);

  // Search state
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [activeMatchIndex, setActiveMatchIndex] = useState<number>(-1);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await getDocument(docId);
        setDocument(data);
      } catch (err: any) {
        setError(err.message || "Failed to load document");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [docId]);

  // Search execution
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setSearchResults([]);
      setActiveMatchIndex(-1);
      return;
    }
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/documents/${docId}/search?q=${encodeURIComponent(
          query
        )}`
      );
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.matches || []);
        if (data.matches && data.matches.length > 0) {
          setActiveMatchIndex(0);
          jumpToMatch(data.matches[0]);
        } else {
          setActiveMatchIndex(-1);
        }
      }
    } catch {
      // ignore
    }
  };

  const jumpToMatch = (match: any) => {
    if (!match) return;
    setActivePageNum(match.page);
    if (document) {
      const page = document.pages.find((p) => p.page === match.page);
      const blk = page?.ocr_blocks.find((b) => b.id === match.block_id);
      if (blk) setSelectedBlock(blk);
    }
  };

  const nextMatch = () => {
    if (searchResults.length === 0) return;
    const nextIdx = (activeMatchIndex + 1) % searchResults.length;
    setActiveMatchIndex(nextIdx);
    jumpToMatch(searchResults[nextIdx]);
  };

  const prevMatch = () => {
    if (searchResults.length === 0) return;
    const prevIdx = (activeMatchIndex - 1 + searchResults.length) % searchResults.length;
    setActiveMatchIndex(prevIdx);
    jumpToMatch(searchResults[prevIdx]);
  };

  // Keyboard shortcuts (Ctrl+F, Esc)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
        e.preventDefault();
        setShowSearch(true);
      } else if (e.key === "Escape") {
        if (showSearch) {
          setShowSearch(false);
        } else {
          setSelectedBlock(null);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showSearch]);


  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#090d16]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-slate-300">Loading document workspace...</p>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#090d16] p-6">
        <div className="max-w-md w-full p-6 rounded-xl bg-slate-900 border border-slate-800 text-center space-y-4">
          <AlertTriangle className="w-10 h-10 text-red-400 mx-auto" />
          <h2 className="text-lg font-semibold text-slate-100">Unable to Load Document</h2>
          <p className="text-xs text-slate-400">{error || "Document not found"}</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const activePage =
    document.pages.find((p) => p.page === activePageNum) || document.pages[0];
  const totalBlocks = document.pages.reduce((acc, p) => acc + p.ocr_blocks.length, 0);

  const handleUpdateBlockText = (blockId: string, newText: string) => {
    if (!document) return;
    const updatedPages = document.pages.map((p) => ({
      ...p,
      ocr_blocks: p.ocr_blocks.map((b) =>
        b.id === blockId ? { ...b, text: newText } : b
      ),
    }));
    setDocument({ ...document, pages: updatedPages });
    if (selectedBlock && selectedBlock.id === blockId) {
      setSelectedBlock({ ...selectedBlock, text: newText });
    }
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-61px)] overflow-hidden bg-[#090d16]">
      {/* Workspace Sub-Header */}
      <div className="h-12 border-b border-slate-800 bg-[#0c111c] px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
            title="Back to Documents"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          <div>
            <h2 className="text-xs sm:text-sm font-semibold text-slate-100 truncate max-w-[200px] sm:max-w-xs">
              {document.filename}
            </h2>
            <div className="flex items-center gap-2 text-[11px] text-slate-500">
              <span>{document.pages.length} pages</span>
              <span>•</span>
              <span>{totalBlocks} OCR blocks</span>
              <span>•</span>
              <span className="text-blue-400">{document.metadata.ocr_engine}</span>
            </div>
          </div>
        </div>

        {/* View Controls & Toggles */}
        <div className="flex items-center gap-2">
          {/* Search Toggle */}
          <button
            onClick={() => setShowSearch(!showSearch)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition ${
              showSearch
                ? "bg-blue-950/60 border-blue-600 text-blue-300"
                : "bg-slate-800/60 border-slate-700/70 text-slate-400 hover:text-slate-200"
            }`}
            title="Search Document (Ctrl+F)"
          >
            <Search className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Search</span>
          </button>

          {/* Quality badge button */}
          {activePage?.quality && (
            <button
              onClick={() => setShowQualityModal(true)}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition"
              title="Image Quality & OCR Readiness"
            >
              <Info className="w-3.5 h-3.5 text-cyan-400" />
              <span>Readiness: {activePage.quality.readiness_score}%</span>
            </button>
          )}

          {/* Toggle Confidence */}
          <button
            onClick={() => setShowConfidence(!showConfidence)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition ${
              showConfidence
                ? "bg-amber-950/40 border-amber-700/80 text-amber-300"
                : "bg-slate-800/60 border-slate-700/70 text-slate-400 hover:text-slate-200"
            }`}
            title="Toggle Confidence Heatmap"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Confidence</span>
          </button>

          {/* Toggle Boxes */}
          <button
            onClick={() => setShowBoxes(!showBoxes)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border transition ${
              showBoxes
                ? "bg-blue-950/40 border-blue-700/80 text-blue-300"
                : "bg-slate-800/60 border-slate-700/70 text-slate-400 hover:text-slate-200"
            }`}
            title="Toggle Bounding Boxes"
          >
            <Layers className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Boxes</span>
          </button>

          {/* Export Dropdown */}
          <div className="relative group">
            <button
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
              title="Export Document"
            >
              <Download className="w-3.5 h-3.5 text-blue-400" />
              <span>Export</span>
            </button>
            <div className="absolute right-0 mt-1 w-44 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl p-1.5 hidden group-hover:block z-50">
              <a
                href={`http://localhost:8000/api/v1/documents/${docId}/export/markdown`}
                target="_blank"
                download
                className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <span>Markdown</span>
                <span className="text-[10px] text-slate-500 font-mono">.md</span>
              </a>
              <a
                href={`http://localhost:8000/api/v1/documents/${docId}/export/json`}
                target="_blank"
                download
                className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <span>Structured JSON</span>
                <span className="text-[10px] text-slate-500 font-mono">.json</span>
              </a>
              <a
                href={`http://localhost:8000/api/v1/documents/${docId}/export/csv`}
                target="_blank"
                download
                className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <span>Tables CSV</span>
                <span className="text-[10px] text-slate-500 font-mono">.csv</span>
              </a>
              <a
                href={`http://localhost:8000/api/v1/documents/${docId}/export/text`}
                target="_blank"
                download
                className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <span>Plain Text</span>
                <span className="text-[10px] text-slate-500 font-mono">.txt</span>
              </a>
              <a
                href={`http://localhost:8000/api/v1/documents/${docId}/export/html`}
                target="_blank"
                download
                className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <span>HTML Page</span>
                <span className="text-[10px] text-slate-500 font-mono">.html</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Search Bar */}
      {showSearch && (
        <div className="bg-[#0e1626] border-b border-slate-800 px-4 py-2 flex items-center justify-between text-xs">
          <div className="flex items-center gap-3 flex-1 max-w-xl">
            <div className="relative flex-1">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                autoFocus
                placeholder="Search recognized document text... (e.g. Total, Invoice)"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-xs font-mono"
              />
            </div>
            {searchResults.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400 whitespace-nowrap">
                  {activeMatchIndex + 1} of {searchResults.length}
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={prevMatch}
                    className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
                  >
                    ▲
                  </button>
                  <button
                    onClick={nextMatch}
                    className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
                  >
                    ▼
                  </button>
                </div>
              </div>
            )}
            {searchQuery && searchResults.length === 0 && (
              <span className="text-[11px] text-slate-500 whitespace-nowrap">
                No matches found
              </span>
            )}
          </div>
          <button
            onClick={() => setShowSearch(false)}
            className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded hover:bg-slate-800"
          >
            Esc to close
          </button>
        </div>
      )}

      {/* Main Workspace 3-Pane Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Page Thumbnails */}
        <ThumbnailRail
          pages={document.pages}
          activePage={activePageNum}
          onSelectPage={(p) => {
            setActivePageNum(p);
            setSelectedBlock(null);
          }}
        />

        {/* Center Pane: Interactive Canvas Viewer */}
        {activePage && (
          <DocumentCanvas
            key={activePage.page}
            page={activePage}
            selectedBlockId={selectedBlock?.id || null}
            onSelectBlock={(block) => setSelectedBlock(block)}
            showBoxes={showBoxes}
            showConfidence={showConfidence}
            matchingBlockIds={
              new Set(
                searchResults
                  .filter((m) => m.page === activePage.page)
                  .map((m) => m.block_id)
              )
            }
          />
        )}

        {/* Right Pane: Multi-Tab Inspector */}
        <BlockInspector
          document={document}
          activePageNum={activePageNum}
          selectedBlock={selectedBlock}
          onClose={() => setSelectedBlock(null)}
          onUpdateText={handleUpdateBlockText}
          onSelectEntity={(e) => {
            setActivePageNum(e.page);
            if (e.bbox) {
              setSelectedBlock({
                id: e.id,
                text: e.text,
                confidence: e.confidence,
                bbox: e.bbox,
                page: e.page,
              });
            }
          }}
          onSelectField={(f) => {
            setActivePageNum(f.page);
            if (f.bbox) {
              setSelectedBlock({
                id: f.id,
                text: `${f.field}: ${f.value}`,
                confidence: f.confidence,
                bbox: f.bbox,
                page: f.page,
              });
            }
          }}
          onSelectTable={(t) => {
            setActivePageNum(t.page);
            setSelectedBlock({
              id: t.table_id,
              text: `Table ${t.table_id}`,
              confidence: t.confidence,
              bbox: t.bbox,
              page: t.page,
            });
          }}
          onSelectLayoutBlock={(lb) => {
            setActivePageNum(lb.page);
            setSelectedBlock({
              id: lb.id,
              text: lb.text,
              confidence: lb.confidence,
              bbox: lb.bbox,
              page: lb.page,
            });
          }}
          onJumpToSource={(page, bbox, blockId) => {
            setActivePageNum(page);
            if (bbox) {
              setSelectedBlock({
                id: blockId || `src_${Date.now()}`,
                text: "Grounded Source",
                confidence: 1.0,
                bbox: bbox,
                page: page,
              });
            }
          }}
        />
      </div>


      {/* Image Quality Analysis Modal */}
      {showQualityModal && activePage?.quality && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="max-w-md w-full rounded-xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Info className="w-4 h-4 text-cyan-400" />
                Image Quality & OCR Readiness
              </h3>
              <button
                onClick={() => setShowQualityModal(false)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800"
              >
                Close
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-400">Dimensions:</span>
                <span className="font-mono text-slate-200">
                  {activePage.quality.width} × {activePage.quality.height} px
                </span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-400">Brightness:</span>
                <span className="font-mono text-slate-200">{activePage.quality.brightness} / 255</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-400">Contrast StdDev:</span>
                <span className="font-mono text-slate-200">{activePage.quality.contrast}</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-400">Sharpness / Blur (Laplacian):</span>
                <span className="font-mono text-slate-200">{activePage.quality.blur_estimate}</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-400">Estimated Skew Angle:</span>
                <span className="font-mono text-slate-200">{activePage.quality.skew_estimate}°</span>
              </div>

              <div className="pt-2 border-t border-slate-800">
                <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Assessment Notes
                </p>
                <ul className="space-y-1">
                  {activePage.quality.readiness_notes.map((note, idx) => (
                    <li key={idx} className="text-slate-300 flex items-start gap-1.5">
                      <span className="text-blue-400">•</span>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <p className="text-[10px] text-slate-500 italic mt-2">
                * OCR Readiness is an application-derived heuristic score based on contrast, blur, skew, and pixel density.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
