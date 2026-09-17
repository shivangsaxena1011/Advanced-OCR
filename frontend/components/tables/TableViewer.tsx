"use client";

import React, { useState } from "react";
import { TableResult } from "@/types/document";
import { Copy, Download, Check, Table as TableIcon } from "lucide-react";

interface TableViewerProps {
  tables: TableResult[];
  onSelectTable?: (table: TableResult) => void;
}

export default function TableViewer({ tables, onSelectTable }: TableViewerProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!tables || tables.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 space-y-2">
        <TableIcon className="w-8 h-8 mx-auto text-slate-600 stroke-[1.5]" />
        <p className="text-xs">No tables detected in this document.</p>
      </div>
    );
  }

  const handleCopy = (t: TableResult) => {
    const csvContent = [
      t.headers.join("\t"),
      ...t.rows.map((r) => r.join("\t")),
    ].join("\n");
    navigator.clipboard.writeText(csvContent);
    setCopiedId(t.table_id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDownloadCsv = (t: TableResult) => {
    const csvRows = [
      t.headers.map((h) => `"${h.replace(/"/g, '""')}"`).join(","),
      ...t.rows.map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(",")),
    ].join("\n");

    const blob = new Blob([csvRows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${t.table_id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadJson = (t: TableResult) => {
    const blob = new Blob([JSON.stringify(t, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${t.table_id}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 p-3">
      {tables.map((t) => (
        <div
          key={t.table_id}
          onClick={() => onSelectTable && onSelectTable(t)}
          className="rounded-xl border border-slate-800 bg-slate-950/70 p-3 space-y-3 cursor-pointer hover:border-slate-700 transition"
        >
          {/* Header Bar */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TableIcon className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-semibold text-slate-200">
                {t.table_id} (Page {t.page})
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopy(t);
                }}
                className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
                title="Copy Table"
              >
                {copiedId === t.table_id ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDownloadCsv(t);
                }}
                className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
                title="Download CSV"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
              </button>
            </div>
          </div>

          {/* Table Grid */}
          <div className="overflow-x-auto rounded border border-slate-800/80">
            <table className="w-full text-left text-[11px] divide-y divide-slate-800">
              <thead className="bg-slate-900/90 text-slate-300 font-semibold">
                <tr>
                  {t.headers.map((h, idx) => (
                    <th key={idx} className="px-2.5 py-1.5 whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 bg-slate-950/40 text-slate-300 font-mono">
                {t.rows.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-800/30">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-2.5 py-1.5 whitespace-nowrap">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
