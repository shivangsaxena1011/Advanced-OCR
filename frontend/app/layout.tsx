import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { FileText, LayoutDashboard, Upload, FileDiff, BookOpen, Layers } from "lucide-react";
import { API_BASE } from "@/lib/api";

export const metadata: Metadata = {
  title: "AORL — Advanced OCR with Layout Understanding",
  description:
    "Intelligent document-processing platform powered by PaddleOCR, layout analysis, table extraction, and grounded AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-[#090d16] text-slate-100 antialiased selection:bg-blue-600/30 selection:text-blue-200">
        {/* Navigation Bar */}
        <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-[#0c121e]/90 backdrop-blur-md px-4 lg:px-8 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:shadow-blue-500/40 transition">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                    AORL
                  </span>
                  <span className="text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-400 border border-blue-800/50">
                    PaddleOCR 3.7
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-normal leading-none hidden sm:block">
                  Document Intelligence Platform
                </p>
              </div>
            </Link>

            <nav className="flex items-center gap-1 sm:gap-2">
              <Link
                href="/dashboard"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/70 transition"
              >
                <LayoutDashboard className="w-4 h-4 text-slate-400" />
                <span>Dashboard</span>
              </Link>
              <Link
                href="/upload"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/70 transition"
              >
                <Upload className="w-4 h-4 text-blue-400" />
                <span>Upload</span>
              </Link>
              <Link
                href="/compare"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/70 transition"
              >
                <FileDiff className="w-4 h-4 text-slate-400" />
                <span className="hidden sm:inline">Compare</span>
              </Link>
              <a
                href={`${API_BASE}/docs`}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition"
              >
                <BookOpen className="w-4 h-4 text-slate-400" />
                <span className="hidden md:inline">API Docs</span>
              </a>
            </nav>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
