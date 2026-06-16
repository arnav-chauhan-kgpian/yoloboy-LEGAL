"use client";
import { ReactNode } from "react";

export function AppShell({
  sidebar,
  graph,
  panel,
}: {
  sidebar: ReactNode;
  graph: ReactNode;
  panel: ReactNode;
}) {
  return (
    <div className="h-screen w-screen flex overflow-hidden">
      {/* ── Dark sidebar ── */}
      <aside className="w-[300px] flex flex-col bg-shell border-r border-white/[0.06] flex-shrink-0 overflow-hidden">
        {/* Logo */}
        <div className="h-14 flex items-center px-5 border-b border-white/[0.06] flex-shrink-0 gap-3">
          <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center flex-shrink-0">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 11L7 3L12 11" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M4 8.5H10" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
          </div>
          <div>
            <div className="font-semibold text-white text-[14px] tracking-tight leading-none">LexGraph AI</div>
            <div className="text-[10px] text-slate-500 mt-[3px] leading-none">Legal gap intelligence</div>
          </div>
        </div>
        {/* Sidebar content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          {sidebar}
        </div>
      </aside>

      {/* ── Graph canvas ── */}
      <main className="flex-1 min-w-0 bg-surface">
        {graph}
      </main>

      {/* ── Analysis panel ── */}
      <section className="w-[420px] flex-shrink-0 flex flex-col bg-white border-l border-slate-200 min-w-0">
        {panel}
      </section>
    </div>
  );
}
