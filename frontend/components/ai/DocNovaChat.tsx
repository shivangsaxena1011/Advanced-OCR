"use client";

import React, { useState } from "react";
import { Bot, Send, Sparkles, MapPin, AlertCircle, Loader2 } from "lucide-react";
import { BBox } from "@/types/document";
import { askDocNova } from "@/lib/api";

interface CitationSource {
  page: number;
  type: string;
  reference: string;
  bbox?: BBox;
  source_block?: string;
}

interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  sources?: CitationSource[];
}

interface DocNovaChatProps {
  documentId: string;
  onJumpToSource: (page: number, bbox?: BBox, blockId?: string) => void;
}

export default function DocNovaChat({
  documentId,
  onJumpToSource,
}: DocNovaChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg_welcome",
      sender: "ai",
      text: "Hello! I'm DocNova. Ask me anything about this document—like the total due, dates, itemized costs, or parties involved. Every answer is grounded in extracted evidence.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuestion = input.trim();
    setInput("");

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: "user",
      text: userQuestion,
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await askDocNova(documentId, userQuestion);
      const aiMsg: ChatMessage = {
        id: `ai_${Date.now()}`,
        sender: "ai",
        text: data.answer,
        sources: data.sources,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: `ai_err_${Date.now()}`,
        sender: "ai",
        text: "I couldn't process your question at this moment. Please try again.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0d1320] text-xs">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${
              m.sender === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`max-w-[90%] p-3 rounded-xl leading-relaxed ${
                m.sender === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none shadow-md"
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1 opacity-75">
                {m.sender === "ai" ? (
                  <>
                    <Bot className="w-3.5 h-3.5 text-blue-400" />
                    <span className="font-semibold text-[10px] text-blue-300">
                      DocNova Assistant
                    </span>
                  </>
                ) : (
                  <span className="font-semibold text-[10px] text-blue-100">You</span>
                )}
              </div>
              <p className="whitespace-pre-wrap">{m.text}</p>

              {/* Clickable Citations */}
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-800/80 space-y-1.5">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                    Grounded Sources:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {m.sources.map((s, idx) => (
                      <button
                        key={idx}
                        onClick={() =>
                          onJumpToSource(
                            s.page,
                            s.bbox,
                            s.source_block || undefined
                          )
                        }
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-950/80 hover:bg-blue-900/90 text-blue-300 border border-blue-800/60 text-[10px] transition cursor-pointer"
                        title="Click to highlight on document"
                      >
                        <MapPin className="w-2.5 h-2.5" />
                        <span>
                          p.{s.page} • {s.reference.slice(0, 24)}...
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 p-2">
            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            <span className="text-[11px]">DocNova is reasoning over document evidence...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form onSubmit={handleSend} className="p-3 border-t border-slate-800 bg-slate-950/60 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this document..."
          className="flex-1 px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-xs font-sans"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
