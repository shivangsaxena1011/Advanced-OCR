"use client";

import React, { useState } from "react";
import { ExtractedField } from "@/types/document";
import { ListFilter, Copy, Check, MapPin } from "lucide-react";

interface FieldListProps {
  fields: ExtractedField[];
  onSelectField?: (field: ExtractedField) => void;
}

export default function FieldList({ fields, onSelectField }: FieldListProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!fields || fields.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 space-y-2">
        <ListFilter className="w-8 h-8 mx-auto text-slate-600 stroke-[1.5]" />
        <p className="text-xs">No key-value fields detected.</p>
      </div>
    );
  }

  const handleCopy = (f: ExtractedField) => {
    navigator.clipboard.writeText(f.value);
    setCopiedId(f.id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-2 p-3">
      {fields.map((fld) => (
        <div
          key={fld.id}
          onClick={() => onSelectField && onSelectField(fld)}
          className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 flex items-center justify-between cursor-pointer transition"
        >
          <div className="space-y-1 pr-2">
            <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">
              {fld.field}
            </span>
            <p className="text-xs font-mono font-medium text-slate-100 break-words">
              {fld.value}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleCopy(fld);
              }}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition"
              title="Copy value"
            >
              {copiedId === fld.id ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
            <span className="text-[10px] text-slate-500 font-mono">p.{fld.page}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
