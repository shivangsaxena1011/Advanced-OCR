"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FileText,
  Layers,
  Sparkles,
  Upload,
  Clock,
  Trash2,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { DocumentResult } from "@/types/document";
import { listDocuments, deleteDocument } from "@/lib/api";

export default function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentResult[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const docs = await listDocuments();
      setDocuments(docs);
    } catch {
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to delete this document?")) {
      await deleteDocument(id);
      fetchDocs();
    }
  };

  // Real calculated metrics
  const totalDocs = documents.length;
  const totalPages = documents.reduce((acc, d) => acc + (d.metadata?.page_count || 1), 0);
  const totalBlocks = documents.reduce(
    (acc, d) =>
      acc + (d.pages?.reduce((pAcc, p) => pAcc + (p.ocr_blocks?.length || 0), 0) || 0),
    0
  );

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto p-6 sm:p-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Document Intelligence Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Overview of processed files, extracted text blocks, and OCR intelligence.
          </p>
        </div>
        <Link
          href="/upload"
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition"
        >
          <Upload className="w-4 h-4" />
          <span>Upload Document</span>
        </Link>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-[#0f1626] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Total Documents
            </span>
            <FileText className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-bold text-white mt-3">{totalDocs}</div>
          <p className="text-[11px] text-slate-500 mt-1">Persisted in local storage</p>
        </div>

        <div className="p-5 rounded-xl bg-[#0f1626] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              Rasterized Pages
            </span>
            <Layers className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-white mt-3">{totalPages}</div>
          <p className="text-[11px] text-slate-500 mt-1">Rendered at high fidelity</p>
        </div>

        <div className="p-5 rounded-xl bg-[#0f1626] border border-slate-800 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
              OCR Text Blocks
            </span>
            <Sparkles className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-white mt-3">{totalBlocks}</div>
          <p className="text-[11px] text-slate-500 mt-1">Detected by PaddleOCR</p>
        </div>
      </div>

      {/* Recent Documents Table */}
      <div className="rounded-xl bg-[#0f1626] border border-slate-800 overflow-hidden shadow-md">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Recent Documents</h2>
          <span className="text-xs text-slate-400">{documents.length} files</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading documents...</div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileText className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm font-medium text-slate-300">No documents uploaded yet</p>
            <p className="text-xs text-slate-500">
              Upload your first PDF or image to begin document analysis.
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700"
            >
              <Upload className="w-3.5 h-3.5 text-blue-400" />
              Upload Now
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">Document</th>
                  <th className="px-6 py-3">Pages</th>
                  <th className="px-6 py-3">Blocks</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Engine</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {documents.map((doc) => {
                  const blocks = doc.pages?.reduce((a, p) => a + p.ocr_blocks.length, 0) || 0;
                  return (
                    <tr
                      key={doc.document_id}
                      className="hover:bg-slate-800/40 transition group"
                    >
                      <td className="px-6 py-3.5 font-medium text-white flex items-center gap-2.5">
                        <FileText className="w-4 h-4 text-blue-400 shrink-0" />
                        <span className="truncate max-w-xs">{doc.filename}</span>
                      </td>
                      <td className="px-6 py-3.5 text-slate-400">
                        {doc.metadata?.page_count || 1}
                      </td>
                      <td className="px-6 py-3.5 font-mono text-slate-400">{blocks}</td>
                      <td className="px-6 py-3.5">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-950/70 text-emerald-400 border border-emerald-800/50">
                          <CheckCircle2 className="w-3 h-3" />
                          {doc.processing?.status || "COMPLETED"}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 text-slate-400 text-[11px]">
                        {doc.metadata?.ocr_engine || "PaddleOCR"}
                      </td>
                      <td className="px-6 py-3.5 text-right space-x-2">
                        <Link
                          href={`/documents/${doc.document_id}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 font-medium text-xs transition"
                        >
                          <ExternalLink className="w-3 h-3" />
                          Open
                        </Link>
                        <button
                          onClick={() => handleDelete(doc.document_id)}
                          className="p-1 rounded hover:bg-red-950/60 text-slate-500 hover:text-red-400 transition"
                          title="Delete document"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
