"use client";

import React from "react";
import { PageResult } from "@/types/document";
import { getFileUrl } from "@/lib/api";
import { FileText } from "lucide-react";

interface ThumbnailRailProps {
  pages: PageResult[];
  activePage: number;
  onSelectPage: (page: number) => void;
}

export default function ThumbnailRail({
  pages,
  activePage,
  onSelectPage,
}: ThumbnailRailProps) {
  if (pages.length <= 1) return null;

  return (
    <div className="w-48 border-r border-slate-800 bg-[#0c111c] flex flex-col h-full overflow-y-auto p-3 space-y-3 shrink-0">
      <div className="flex items-center justify-between px-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Pages
        </span>
        <span className="text-xs text-slate-500 font-medium">
          {pages.length} total
        </span>
      </div>

      <div className="space-y-3">
        {pages.map((p) => {
          const isActive = p.page === activePage;
          const thumbUrl = getFileUrl(p.thumbnail_url || p.image_url);

          return (
            <button
              key={p.page}
              onClick={() => onSelectPage(p.page)}
              className={`w-full text-left rounded-lg p-2 border transition duration-150 flex flex-col gap-2 ${
                isActive
                  ? "border-blue-500 bg-blue-950/30 ring-1 ring-blue-500/50"
                  : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/80"
              }`}
            >
              <div className="aspect-[3/4] w-full rounded bg-slate-950 overflow-hidden border border-slate-800 flex items-center justify-center relative">
                {thumbUrl ? (
                  <img
                    src={thumbUrl}
                    alt={`Page ${p.page}`}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <FileText className="w-8 h-8 text-slate-600" />
                )}
                <span className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/80 text-[10px] font-mono text-slate-300">
                  p.{p.page}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] px-0.5">
                <span className="font-medium text-slate-300">Page {p.page}</span>
                <span className="text-slate-500">{p.ocr_blocks.length} blocks</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
