"use client";

import React from "react";
import { EntityResult } from "@/types/document";
import { Tag, MapPin } from "lucide-react";

interface EntityListProps {
  entities: EntityResult[];
  onSelectEntity?: (entity: EntityResult) => void;
}

export default function EntityList({ entities, onSelectEntity }: EntityListProps) {
  if (!entities || entities.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 space-y-2">
        <Tag className="w-8 h-8 mx-auto text-slate-600 stroke-[1.5]" />
        <p className="text-xs">No named entities detected.</p>
      </div>
    );
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "AMOUNT":
      case "CURRENCY":
        return "bg-emerald-950/70 border-emerald-800 text-emerald-300";
      case "DATE":
      case "TIME":
        return "bg-blue-950/70 border-blue-800 text-blue-300";
      case "EMAIL":
      case "URL":
      case "PHONE":
        return "bg-purple-950/70 border-purple-800 text-purple-300";
      case "DOCUMENT_ID":
        return "bg-amber-950/70 border-amber-800 text-amber-300";
      case "ORGANIZATION":
        return "bg-cyan-950/70 border-cyan-800 text-cyan-300";
      default:
        return "bg-slate-800/80 border-slate-700 text-slate-300";
    }
  };

  return (
    <div className="space-y-2 p-3">
      {entities.map((ent) => (
        <div
          key={ent.id}
          onClick={() => onSelectEntity && onSelectEntity(ent)}
          className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 flex items-center justify-between cursor-pointer transition"
        >
          <div className="space-y-1">
            <span
              className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${getTypeColor(
                ent.type
              )}`}
            >
              {ent.type}
            </span>
            <p className="text-xs font-mono text-slate-200">{ent.text}</p>
          </div>

          <div className="flex items-center gap-1 text-[10px] text-slate-500">
            <MapPin className="w-3 h-3 text-slate-600" />
            <span>p.{ent.page}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
