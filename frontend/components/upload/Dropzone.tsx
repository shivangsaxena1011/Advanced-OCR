"use client";

import React, { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileText, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { uploadDocument } from "@/lib/api";

const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/webp", "application/pdf"];
const MAX_SIZE_MB = 50;

export default function Dropzone() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStage, setActiveStage] = useState<string>("Ready");
  const [completedStages, setCompletedStages] = useState<string[]>([]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProcess(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndProcess(e.target.files[0]);
    }
  };

  const validateAndProcess = async (selectedFile: File) => {
    setError(null);

    // Validate size
    if (selectedFile.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File exceeds maximum size of ${MAX_SIZE_MB}MB.`);
      return;
    }

    // Validate type
    const isAllowed =
      ALLOWED_TYPES.includes(selectedFile.type) ||
      selectedFile.name.toLowerCase().endsWith(".pdf") ||
      selectedFile.name.toLowerCase().endsWith(".png") ||
      selectedFile.name.toLowerCase().endsWith(".jpg") ||
      selectedFile.name.toLowerCase().endsWith(".jpeg") ||
      selectedFile.name.toLowerCase().endsWith(".webp");

    if (!isAllowed) {
      setError("Unsupported file format. Please upload PDF, PNG, JPG, or WEBP.");
      return;
    }

    setFile(selectedFile);
    setUploading(true);
    setActiveStage("Uploading document...");
    setCompletedStages([]);

    try {
      setActiveStage("Running OCR & layout pipeline...");
      const result = await uploadDocument(selectedFile);

      // Record completed stages from backend response
      const stages = result.processing?.stages?.map((s) => s.stage) || [
        "UPLOAD",
        "PREPROCESSING",
        "OCR",
        "FINALIZATION",
      ];
      setCompletedStages(stages);
      setActiveStage("Completed! Opening workspace...");

      setTimeout(() => {
        router.push(`/documents/${result.document_id}`);
      }, 500);
    } catch (err: any) {
      setError(err.message || "Failed to process document.");
      setUploading(false);
      setActiveStage("Failed");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? "border-blue-500 bg-blue-500/10 scale-[1.01]"
            : "border-slate-700 bg-slate-900/40 hover:border-slate-500 hover:bg-slate-900/80"
        } ${uploading ? "pointer-events-none cursor-default" : ""}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.webp"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />

        {!uploading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-16 h-16 rounded-2xl bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-400 shadow-inner">
              <UploadCloud className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base sm:text-lg font-semibold text-slate-100">
                Upload a document to analyze
              </h3>
              <p className="text-xs sm:text-sm text-slate-400">
                Drag and drop your file here, or browse from your device
              </p>
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                PDF
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                PNG
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                JPG
              </span>
              <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                WEBP
              </span>
              <span className="text-xs text-slate-500 ml-1">Up to 50MB</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 py-4">
            <Loader2 className="w-10 h-10 text-blue-400 animate-spin" />
            <div className="space-y-1 text-center">
              <p className="text-sm font-semibold text-slate-200">{activeStage}</p>
              <p className="text-xs text-slate-400">{file?.name}</p>
            </div>

            {/* Stages indicator */}
            <div className="w-full max-w-sm mt-3 pt-3 border-t border-slate-800/80 space-y-2 text-left">
              {[
                { key: "UPLOAD", label: "File upload & validation" },
                { key: "PAGE_EXTRACTION", label: "Page rasterization (PyMuPDF)" },
                { key: "PREPROCESSING", label: "Quality analysis & deskew" },
                { key: "OCR", label: "PaddleOCR inference & bounding boxes" },
              ].map((stage) => {
                const isDone = completedStages.includes(stage.key);
                return (
                  <div key={stage.key} className="flex items-center justify-between text-xs">
                    <span className={isDone ? "text-slate-300" : "text-slate-500"}>
                      {stage.label}
                    </span>
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <div className="w-2 h-2 rounded-full bg-slate-700" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-950/40 border border-red-800/50 flex items-center gap-2.5 text-xs text-red-300">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
