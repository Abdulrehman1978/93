import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SAMBAL — Multilingual Trauma-Aware Intelligence & Response Layer",
  description:
    "AI-Based Real-Time Stress & Trauma Assessment Module for NHAA (14566) & Integrated Portal. Ministry of Social Justice & Empowerment.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased min-h-screen flex flex-col bg-slate-50 text-slate-900">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:p-4 focus:bg-white focus:text-civic-dark focus:z-50 focus:ring-2 focus:ring-civic-teal"
        >
          Skip to main content
        </a>

        {/* National Header Shell */}
        <header className="bg-civic-dark text-white border-b border-slate-700/50 py-3 px-6 shadow-sm">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded bg-civic-teal flex items-center justify-center font-bold text-lg text-white">
                सं
              </div>
              <div>
                <div className="text-base font-semibold tracking-tight text-white leading-tight">
                  SAMBAL Intelligence & Response Layer
                </div>
                <p className="text-xs text-slate-400">
                  National Helpline Against Atrocities (14566) | MoSJE
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4 text-xs">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-teal-900/60 text-teal-200 border border-teal-700/50">
                <span className="w-1.5 h-1.5 rounded-full bg-teal-400 mr-1.5 animate-pulse"></span>
                System Operational
              </span>
              <span className="text-slate-400 hidden sm:inline">
                Helpline: <strong className="text-white">14566</strong>
              </span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main id="main-content" className="flex-1 max-w-7xl w-full mx-auto p-6">
          {children}
        </main>

        {/* Civic Calm Footer */}
        <footer className="bg-slate-900 text-slate-400 text-xs py-6 px-6 border-t border-slate-800">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <p className="font-medium text-slate-200">
                Ministry of Social Justice & Empowerment, Government of India
              </p>
              <p className="text-slate-300 mt-0.5">
                SIH26093 — Trauma-informed, research-grounded decision support
                module.
              </p>
            </div>
            <div className="flex items-center gap-4 text-slate-400">
              <span>
                National Helpline:{" "}
                <strong className="text-slate-200">14566</strong>
              </span>
              <span>
                Tele-MANAS: <strong className="text-slate-200">14416</strong>
              </span>
              <span>
                Emergency: <strong className="text-slate-200">112</strong>
              </span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
