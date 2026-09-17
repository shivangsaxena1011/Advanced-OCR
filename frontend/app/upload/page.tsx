import React from "react";
import Dropzone from "@/components/upload/Dropzone";

export default function UploadPage() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 sm:p-12 max-w-5xl mx-auto w-full">
      <div className="text-center space-y-2 mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Upload Document for Analysis
        </h1>
        <p className="text-sm text-slate-400 max-w-lg mx-auto">
          Process PDFs, receipts, invoices, or scanned documents through PaddleOCR with layout detection and bounding box extraction.
        </p>
      </div>

      <Dropzone />
    </div>
  );
}
