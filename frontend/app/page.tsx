import React from "react";
import Link from "next/link";
import {
  Layers,
  FileText,
  Table,
  Cpu,
  Search,
  Bot,
  ArrowRight,
  ShieldCheck,
  Zap,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex-1 flex flex-col items-center">
      {/* Hero Section */}
      <section className="w-full max-w-6xl mx-auto px-6 pt-20 pb-16 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-950/70 border border-blue-800/60 text-blue-400 text-xs font-semibold">
          <Zap className="w-3.5 h-3.5" />
          <span>Production Document Intelligence with PaddleOCR</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.15]">
          Advanced OCR. <br />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
            Understand Every Document.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto font-normal">
          Extract text. Understand layouts. Recover tables. Find entities. Ask questions about your documents with spatial grounding.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4">
          <Link
            href="/upload"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-xl shadow-blue-600/25 transition"
          >
            <span>Upload a Document</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/dashboard"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm border border-slate-700 transition"
          >
            <span>Explore Dashboard</span>
          </Link>
        </div>
      </section>

      {/* Capabilities Grid */}
      <section className="w-full max-w-6xl mx-auto px-6 py-16 border-t border-slate-800/80">
        <div className="text-center space-y-2 mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Comprehensive Document Intelligence
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            A unified pipeline from raw pixels to semantic structured understanding.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-[#0f1523] border border-slate-800/80 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-950/80 border border-blue-800/50 flex items-center justify-center text-blue-400">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">PaddleOCR Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Powered by PaddleOCR text detection and recognition with automatic quality assessment, deskew, and normalized bounding box coordinates.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0f1523] border border-slate-800/80 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-950/80 border border-indigo-800/50 flex items-center justify-center text-indigo-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Layout & Reading Order</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Recovers document structure, headings, paragraphs, and multi-column topological reading order avoiding zigzag confusion.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0f1523] border border-slate-800/80 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-950/80 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
              <Table className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Table Extraction</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detects tabular grids, reconstructs rows and columns, and exports cleanly formatted CSV, JSON, and Markdown tables.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0f1523] border border-slate-800/80 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-950/80 border border-purple-800/50 flex items-center justify-center text-purple-400">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Entities & Key-Values</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Extracts named entities (Person, Organization, Date, Amount) and pairs invoice numbers, dates, and totals with source traceability.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0f1523] border border-slate-800/80 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-950/80 border border-cyan-800/50 flex items-center justify-center text-cyan-400">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Full-Text Spatial Search</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Search query terms instantly across multi-page scans with live bounding box highlight overlays and hit navigation.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0f1523] border border-slate-800/80 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-rose-950/80 border border-rose-800/50 flex items-center justify-center text-rose-400">
              <Bot className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">DocNova AI Assistant</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ask grounded natural language questions with strict citation back to page number and bounding box coordinates.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
