"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import ChatPanel from "@/components/chat-panel";

const tabs = [
  { href: "/", icon: "📡", label: "Dashboard" },
  { href: "/keys", icon: "🔑", label: "API Keys" },
  { href: "/tests", icon: "🧪", label: "ผลทดสอบ" },
  { href: "/brain", icon: "🧠", label: "AI วิเคราะห์" },
  { href: "/proxy", icon: "🔌", label: "Proxy Config" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [chatOpen, setChatOpen] = useState(true);
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const saved = localStorage.getItem("theme") as "dark" | "light" | null;
    if (saved) setTheme(saved);
  }, []);

  useEffect(() => {
    document.documentElement.className = theme === "light"
      ? "light h-full"
      : "dark h-full";
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark");

  return (
    <>
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-6 py-3 border-b bg-card">
        <h1 className="text-xl font-bold flex items-center gap-2">
          🔍 <span className="text-[var(--clr-accent)]">SML AI Router</span>
        </h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[var(--clr-green)] animate-pulse" />
            Live
          </span>
          <Button variant="outline" size="sm" onClick={() => setChatOpen(o => !o)} className="text-xs">
            {chatOpen ? "◀ ซ่อน Chat" : "💬 Chat"}
          </Button>
          <Button variant="outline" size="icon" className="h-8 w-8" onClick={toggleTheme}>
            {theme === "dark" ? "🌙" : "☀️"}
          </Button>
        </div>
      </header>

      {/* Nav */}
      <nav className="flex overflow-x-auto border-b bg-card">
        {tabs.map(tab => {
          const active = pathname === tab.href;
          return (
            <Link key={tab.href} href={tab.href}
              className={`px-5 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                active
                  ? "text-[var(--clr-accent)] border-[var(--clr-accent)]"
                  : "text-muted-foreground border-transparent hover:text-foreground"
              }`}>
              {tab.icon} {tab.label}
            </Link>
          );
        })}
      </nav>

      {/* Content + Chat */}
      <div className="flex flex-1 min-h-0">
        <main className="flex-1 overflow-y-auto p-6 min-w-0">
          {children}
        </main>
        {chatOpen && (
          <aside className="w-[420px] border-l bg-card flex flex-col shrink-0 max-lg:hidden">
            <ChatPanel />
          </aside>
        )}
      </div>
    </>
  );
}
