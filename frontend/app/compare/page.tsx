"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  FileDiff,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Sparkles,
} from "lucide-react";
import { DocumentResult } from "@/types/document";
import { listDocuments, compareDocuments } from "@/lib/api";

export default function ComparePage() {
  const [documents, setDocuments] = useState<DocumentResult[]>([]);
  const [docAId, setDocAId] = useState<string>("");
  const [docBId, setDocBId] = useState<string>("");
  const [comparing, setComparing] = useState(false);
  const [compareResult, setCompareResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const docs = await listDocuments();
        setDocuments(docs);
        if (docs.length >= 2) {
          setDocAId(docs[0].document_id);
          setDocBId(docs[1].document_id);
        } else if (docs.length === 1) {
          setDocAId(docs[0].document_id);
          setDocBId(docs[0].document_id);
        }
      } catch {
        // ignore
      }
    }
    load();
  }, []);

  const handleCompare = async () => {
    if (!docAId || !docBId) return;
    setComparing(true);
    setError(null);
    try {
      const data = await compareDocuments(docAId, docBId);
      setCompareResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to compare documents");
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="flex-1 max-w-6xl w-full mx-auto p-6 sm:p-8 space-y-8">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <FileDiff className="w-7 h-7 text-blue-400" />
          Document Comparison
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Compare two documents side-by-side across text structure, extracted key-value fields, tables, and entities.
        </p>
      </div>

      {/* Document Selector */}
      <div className="p-6 rounded-xl bg-[#0f1626] border border-slate-800 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Document A */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Document A (Baseline)
            </label>
            <select
              value={docAId}
              onChange={(e) => setDocAId(e.target.value)}
              className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
            >
              {documents.map((d) => (
                <option key={d.document_id} value={d.document_id}>
                  {d.filename} ({d.document_type || "Document"})
                </option>
              ))}
            </select>
          </div>

          {/* Document B */}
          <div className="space-y-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Document B (Comparison Target)
            </label>
            <select
              value={docBId}
              onChange={(e) => setDocBId(e.target.value)}
              className="w-full p-2.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-blue-500"
            >
              {documents.map((d) => (
                <option key={d.document_id} value={d.document_id}>
                  {d.filename} ({d.document_type || "Document"})
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleCompare}
          disabled={!docAId || !docBId || comparing}
          className="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-xs transition flex items-center justify-center gap-2"
        >
          {comparing ? "Comparing..." : "Run Side-by-Side Comparison"}
        </button>

        {error && (
          <p className="text-xs text-red-400 bg-red-950/40 border border-red-800 p-2.5 rounded">
            {error}
          </p>
        )}
      </div>

      {/* Comparison Results */}
      {compareResult && (
        <div className="space-y-6">
          {/* Summary Metric Card */}
          <div className="p-6 rounded-xl bg-[#0f1626] border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="space-y-1 text-center sm:text-left">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Structural Similarity Score
              </span>
              <div className="text-3xl font-bold text-white">
                {Math.round(compareResult.similarity_score * 100)}%
              </div>
              <p className="text-xs text-slate-500">
                Calculated across matching fields, entities, and table configurations
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
                {compareResult.doc_a_name}
              </span>
              <ArrowRight className="w-4 h-4 text-slate-500" />
              <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300">
                {compareResult.doc_b_name}
              </span>
            </div>
          </div>

          {/* Fields Comparison Table */}
          <div className="rounded-xl bg-[#0f1626] border border-slate-800 overflow-hidden">
            <div className="px-6 py-3.5 border-b border-slate-800">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Key-Value Fields Comparison
              </h3>
            </div>
            {compareResult.fields_diff.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500">
                No matching key-value fields detected.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-900/60 text-slate-400 text-[10px] font-semibold border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-3">Field Key</th>
                      <th className="px-6 py-3">Document A</th>
                      <th className="px-6 py-3">Document B</th>
                      <th className="px-6 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {compareResult.fields_diff.map((f: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="px-6 py-3 font-medium text-slate-200 uppercase">
                          {f.field}
                        </td>
                        <td className="px-6 py-3 font-mono text-slate-400">
                          {f.value_a || "—"}
                        </td>
                        <td className="px-6 py-3 font-mono text-slate-400">
                          {f.value_b || "—"}
                        </td>
                        <td className="px-6 py-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              f.status === "MATCH"
                                ? "bg-emerald-950/70 text-emerald-400 border border-emerald-800"
                                : f.status === "CHANGED"
                                ? "bg-amber-950/70 text-amber-400 border border-amber-800"
                                : "bg-slate-800 text-slate-400"
                            }`}
                          >
                            {f.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Entities Diff */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-[#0f1626] border border-slate-800 space-y-2">
              <span className="text-xs font-semibold text-emerald-400">
                Common Entities ({compareResult.entities_common.length})
              </span>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {compareResult.entities_common.map((e: string, i: number) => (
                  <p key={i} className="text-xs font-mono text-slate-300">
                    • {e}
                  </p>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#0f1626] border border-slate-800 space-y-2">
              <span className="text-xs font-semibold text-blue-400">
                Added in Document B ({compareResult.entities_added.length})
              </span>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {compareResult.entities_added.map((e: string, i: number) => (
                  <p key={i} className="text-xs font-mono text-slate-300">
                    • {e}
                  </p>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#0f1626] border border-slate-800 space-y-2">
              <span className="text-xs font-semibold text-rose-400">
                Removed in Document B ({compareResult.entities_removed.length})
              </span>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {compareResult.entities_removed.map((e: string, i: number) => (
                  <p key={i} className="text-xs font-mono text-slate-300">
                    • {e}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
