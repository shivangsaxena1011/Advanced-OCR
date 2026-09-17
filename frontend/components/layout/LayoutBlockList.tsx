"use client";

import React from "react";
import { LayoutBlock } from "@/types/document";
import { Layout, Heading, AlignLeft, List, Table, MapPin } from "lucide-react";

interface LayoutBlockListProps {
  layoutBlocks: LayoutBlock[];
  onSelectBlock?: (block: LayoutBlock) => void;
}

export default function LayoutBlockList({
  layoutBlocks,
  onSelectBlock,
}: LayoutBlockListProps) {
  if (!layoutBlocks || layoutBlocks.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 space-y-2">
        <Layout className="w-8 h-8 mx-auto text-slate-600 stroke-[1.5]" />
        <p className="text-xs">No layout blocks detected.</p>
      </div>
    );
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "title":
      case "heading":
        return <Heading className="w-3.5 h-3.5 text-blue-400" />;
      case "list":
        return <List className="w-3.5 h-3.5 text-purple-400" />;
      case "table":
        return <Table className="w-3.5 h-3.5 text-emerald-400" />;
      default:
        return <AlignLeft className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-2 p-3">
      {layoutBlocks.map((lb) => (
        <div
          key={lb.id}
          onClick={() => onSelectBlock && onSelectBlock(lb)}
          className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 space-y-1.5 cursor-pointer transition"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              {getTypeIcon(lb.type)}
              <span className="text-[10px] uppercase font-bold text-slate-300">
                {lb.type}
              </span>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">
              {lb.source_ocr_blocks.length} OCR tokens
            </span>
          </div>

          <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
            {lb.text}
          </p>
        </div>
      ))}
    </div>
  );
}
