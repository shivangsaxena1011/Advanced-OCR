"use client";

import React, { useState, useEffect } from "react";
import {
  Copy,
  Check,
  Edit2,
  X,
  MapPin,
  Percent,
  FileText,
  Table as TableIcon,
  Tag,
  ListFilter,
  Bot,
  Layout,
} from "lucide-react";
import {
  DocumentResult,
  EntityResult,
  ExtractedField,
  LayoutBlock,
  OCRBlock,
  TableResult,
} from "@/types/document";
import TableViewer from "@/components/tables/TableViewer";
import EntityList from "@/components/entities/EntityList";
import FieldList from "@/components/fields/FieldList";
import LayoutBlockList from "@/components/layout/LayoutBlockList";
import DocNovaChat from "@/components/ai/DocNovaChat";

interface BlockInspectorProps {
  document: DocumentResult;
  activePageNum: number;
  selectedBlock: OCRBlock | null;
  onClose: () => void;
  onUpdateText?: (blockId: string, newText: string) => void;
  onSelectEntity?: (entity: EntityResult) => void;
  onSelectField?: (field: ExtractedField) => void;
  onSelectTable?: (table: TableResult) => void;
  onSelectLayoutBlock?: (block: LayoutBlock) => void;
  onJumpToSource: (page: number, bbox?: any, blockId?: string) => void;
}

type TabType = "ocr" | "layout" | "entities" | "tables" | "fields" | "ai";

export default function BlockInspector({
  document,
  activePageNum,
  selectedBlock,
  onClose,
  onUpdateText,
  onSelectEntity,
  onSelectField,
  onSelectTable,
  onSelectLayoutBlock,
  onJumpToSource,
}: BlockInspectorProps) {
  const [activeTab, setActiveTab] = useState<TabType>("ocr");
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState("");

  // Switch to OCR tab when a block is selected
  useEffect(() => {
    if (selectedBlock) {
      setActiveTab("ocr");
      setEditText(selectedBlock.text);
      setIsEditing(false);
    }
  }, [selectedBlock]);

  const handleCopy = () => {
    if (selectedBlock) {
      navigator.clipboard.writeText(selectedBlock.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSaveEdit = () => {
    if (onUpdateText && selectedBlock && editText.trim()) {
      onUpdateText(selectedBlock.id, editText.trim());
    }
    setIsEditing(false);
  };

  const activePage = document.pages.find((p) => p.page === activePageNum);
  const pageLayoutBlocks = activePage?.layout_blocks || [];
  const pageTables = document.tables.filter((t) => t.page === activePageNum);
  const allTables = document.tables;

  return (
    <div className="w-80 md:w-96 border-l border-slate-800 bg-[#0c121e] flex flex-col h-full z-10 shadow-2xl shrink-0">
      {/* Tab Navigation */}
      <div className="flex items-center border-b border-slate-800 bg-slate-950/80 px-1 overflow-x-auto text-[11px] font-medium scrollbar-none">
        <button
          onClick={() => setActiveTab("ocr")}
          className={`flex items-center gap-1 px-3 py-2.5 border-b-2 transition whitespace-nowrap ${
            activeTab === "ocr"
              ? "border-blue-500 text-blue-400 font-semibold bg-blue-950/20"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>OCR</span>
        </button>

        <button
          onClick={() => setActiveTab("layout")}
          className={`flex items-center gap-1 px-3 py-2.5 border-b-2 transition whitespace-nowrap ${
            activeTab === "layout"
              ? "border-blue-500 text-blue-400 font-semibold bg-blue-950/20"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Layout className="w-3.5 h-3.5" />
          <span>Layout ({pageLayoutBlocks.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("entities")}
          className={`flex items-center gap-1 px-3 py-2.5 border-b-2 transition whitespace-nowrap ${
            activeTab === "entities"
              ? "border-blue-500 text-blue-400 font-semibold bg-blue-950/20"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Tag className="w-3.5 h-3.5" />
          <span>Entities ({document.entities.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("tables")}
          className={`flex items-center gap-1 px-3 py-2.5 border-b-2 transition whitespace-nowrap ${
            activeTab === "tables"
              ? "border-blue-500 text-blue-400 font-semibold bg-blue-950/20"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <TableIcon className="w-3.5 h-3.5" />
          <span>Tables ({allTables.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("fields")}
          className={`flex items-center gap-1 px-3 py-2.5 border-b-2 transition whitespace-nowrap ${
            activeTab === "fields"
              ? "border-blue-500 text-blue-400 font-semibold bg-blue-950/20"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <ListFilter className="w-3.5 h-3.5" />
          <span>Fields ({document.fields.length})</span>
        </button>

        <button
          onClick={() => setActiveTab("ai")}
          className={`flex items-center gap-1 px-3 py-2.5 border-b-2 transition whitespace-nowrap ${
            activeTab === "ai"
              ? "border-purple-500 text-purple-400 font-semibold bg-purple-950/20"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Bot className="w-3.5 h-3.5 text-purple-400" />
          <span>DocNova AI</span>
        </button>
      </div>

      {/* Tab Panels */}
      <div className="flex-1 overflow-y-auto">
        {/* TAB 1: OCR Inspector */}
        {activeTab === "ocr" && (
          <div>
            {selectedBlock ? (
              <div className="p-4 space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold text-blue-400">
                      {selectedBlock.id}
                    </span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      Page {selectedBlock.page}
                    </span>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Recognized Text */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                      Recognized Text
                    </label>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={handleCopy}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
                        title="Copy text"
                      >
                        {copied ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
                        title="Edit text"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {isEditing ? (
                    <div className="space-y-2">
                      <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="w-full h-24 p-2 text-xs bg-slate-950 border border-blue-500 rounded-lg text-white font-mono focus:outline-none"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => setIsEditing(false)}
                          className="px-2.5 py-1 rounded text-xs text-slate-400 hover:bg-slate-800"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleSaveEdit}
                          className="px-2.5 py-1 rounded text-xs bg-blue-600 hover:bg-blue-500 text-white font-medium"
                        >
                          Save
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 font-mono text-xs text-slate-100 break-words select-text">
                      {selectedBlock.text}
                    </div>
                  )}
                </div>

                {/* Confidence */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <Percent className="w-3 h-3 text-slate-400" />
                    Confidence
                  </label>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950/60 border border-slate-800">
                    <span className="text-xs text-slate-300">Model Confidence</span>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/60 text-emerald-400">
                      {Math.round(selectedBlock.confidence * 100)}%
                    </span>
                  </div>
                </div>

                {/* Spatial Coordinates */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    Coordinates (Pixels)
                  </label>
                  <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 font-mono text-[11px] space-y-1 text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Top-Left:</span>
                      <span>
                        {Math.round(selectedBlock.bbox.x1)},{" "}
                        {Math.round(selectedBlock.bbox.y1)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Bottom-Right:</span>
                      <span>
                        {Math.round(selectedBlock.bbox.x2)},{" "}
                        {Math.round(selectedBlock.bbox.y2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500 space-y-2">
                <FileText className="w-8 h-8 mx-auto text-slate-600 stroke-[1.5]" />
                <p className="text-xs font-medium text-slate-400">No Block Selected</p>
                <p className="text-[11px] text-slate-500">
                  Click any OCR bounding box in the viewer to inspect text and coordinates.
                </p>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Layout Blocks */}
        {activeTab === "layout" && (
          <LayoutBlockList
            layoutBlocks={pageLayoutBlocks}
            onSelectBlock={onSelectLayoutBlock}
          />
        )}

        {/* TAB 3: Entities */}
        {activeTab === "entities" && (
          <EntityList
            entities={document.entities}
            onSelectEntity={onSelectEntity}
          />
        )}

        {/* TAB 4: Tables */}
        {activeTab === "tables" && (
          <TableViewer tables={allTables} onSelectTable={onSelectTable} />
        )}

        {/* TAB 5: Fields */}
        {activeTab === "fields" && (
          <FieldList fields={document.fields} onSelectField={onSelectField} />
        )}

        {/* TAB 6: DocNova AI Assistant */}
        {activeTab === "ai" && (
          <DocNovaChat
            documentId={document.document_id}
            onJumpToSource={onJumpToSource}
          />
        )}
      </div>
    </div>
  );
}
