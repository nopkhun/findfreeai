"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { getModels, fetchJSON, postJSON, type Model, type ChatMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import ReactMarkdown from "react-markdown";

interface Msg {
  role: string;
  content: string;
  provider?: string;
  latency?: number;
  model?: string;
  reason?: string;
  time?: string;
  queryType?: string;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState("auto");
  const [showSettings, setShowSettings] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [promptSaved, setPromptSaved] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  const sessionRef = useRef(
    (typeof window !== "undefined" && localStorage.getItem("chat-session-id")) || "chat-" + Date.now().toString(36)
  );

  useEffect(() => {
    localStorage.setItem("chat-session-id", sessionRef.current);
    Promise.all([getModels(), fetchJSON("/v1/config")]).then(([m, cfg]) => {
      if (m) setModels((m as { data: Model[] }).data || []);
      if (cfg) setSystemPrompt((cfg as { system_prompt?: string }).system_prompt || "");
    });
  }, []);

  const scrollBottom = useCallback(() => {
    setTimeout(() => chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" }), 50);
  }, []);

  const sendDirect = (text: string) => {
    if (!text.trim() || loading) return;
    setInput("");
    doSend(text.trim());
  };

  const send = async () => {
    sendDirect(input);
  };

  const doSend = async (text: string) => {
    if (!text || loading) return;
    const now = new Date().toLocaleTimeString("th-TH", { hour12: false });

    const userMsg: Msg = { role: "user", content: text, time: now };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    scrollBottom();

    try {
      const allMsgs = [...messages, userMsg]
        .filter(m => m.role === "user" || m.role === "assistant")
        .map(m => ({ role: m.role, content: m.content }));

      const r = await fetch("/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Session-ID": sessionRef.current },
        body: JSON.stringify({ model: selectedModel, messages: allMsgs, max_tokens: 2000 }),
      });
      const d = await r.json();
      const p = d._proxy || {};
      const msg = d.choices?.[0]?.message || {};
      const content = msg.content || msg.reasoning || d.error?.message || "ไม่ได้รับคำตอบ";
      setMessages(prev => [...prev, {
        role: "assistant", content, provider: p.provider,
        latency: p.latency_ms, model: p.model, reason: p.reason,
        queryType: p.query_type,
        time: new Date().toLocaleTimeString("th-TH", { hour12: false }),
      }]);

      // สร้าง follow-up suggestions จากบทสนทนา
      generateFollowUps(text, content);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setMessages(prev => [...prev, { role: "assistant", content: `❌ ${msg}`, time: new Date().toLocaleTimeString("th-TH") }]);
    }
    setLoading(false);
    scrollBottom();
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  const clear = () => {
    setMessages([]);
    sessionRef.current = "chat-" + Date.now().toString(36);
    localStorage.setItem("chat-session-id", sessionRef.current);
  };

  const savePrompt = async () => {
    await postJSON("/v1/config", { system_prompt: systemPrompt });
    setPromptSaved(true);
    setTimeout(() => setPromptSaved(false), 2000);
  };

  const allSuggestions = [
    "วันนี้อากาศเป็นยังไง", "เล่าเรื่องตลกให้ฟัง", "เขียน Python hello world",
    "แนะนำอาหารเช้า", "สรุป AI trends 2026", "สูตรผัดกะเพรา",
    "อธิบาย blockchain ง่ายๆ", "เขียน SQL query JOIN", "แต่งกลอน 4 บท",
    "เปรียบเทียบ React vs Vue", "วิธีออกกำลังกายที่บ้าน", "แนะนำหนังน่าดู",
    "อธิบาย API คืออะไร", "สอนทำ Docker เบื้องต้น", "ประวัติศาสตร์สั้นๆ กรุงเทพ",
    "เขียน regex หา email", "วิธีประหยัดเงิน", "แนะนำเพลงฟังสบาย",
    "คำนวณ BMI ให้หน่อย", "เขียน JavaScript sort array",
  ];
  const [quickSuggestions] = useState(() =>
    [...allSuggestions].sort(() => Math.random() - 0.5).slice(0, 10)
  );
  const [followUps, setFollowUps] = useState<string[]>([]);

  const generateFollowUps = (userQ: string, _aiAnswer: string) => {
    // สร้าง follow-up จาก template — ไม่เรียก API (เร็วทันที)
    const templates = [
      `อธิบายเพิ่มเติมเรื่อง "${userQ.slice(0, 20)}"`,
      `ยกตัวอย่างเพิ่มให้หน่อย`,
      `สรุปสั้นๆ ให้หน่อย`,
      `เปรียบเทียบกับอย่างอื่น`,
      `ข้อดีข้อเสียคืออะไร`,
      `มีอะไรที่ควรระวังไหม`,
      `ช่วยเขียนโค้ดตัวอย่างให้หน่อย`,
      `อธิบายแบบง่ายๆ สำหรับมือใหม่`,
    ];
    setFollowUps([...templates].sort(() => Math.random() - 0.5).slice(0, 4));
  };

  return (
    <>
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b bg-secondary/50">
        <span className="font-bold text-sm flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[var(--clr-green)] animate-pulse" />
          Chat
        </span>
        <div className="flex items-center gap-1">
          <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)}
            className="px-1.5 py-0.5 rounded text-xs border bg-background border-border text-foreground max-w-[120px]">
            {models.map(m => <option key={m.id} value={m.id}>{m.id.split("/").pop()}</option>)}
          </select>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setShowSettings(s => !s)}>⚙️</Button>
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-[var(--clr-red)]" onClick={clear}>🗑️</Button>
        </div>
      </div>

      {/* System Prompt */}
      {showSettings && (
        <div className="px-3 py-2 border-b bg-background">
          <label className="text-xs font-semibold mb-1 block text-muted-foreground">System Prompt (บุคลิก AI)</label>
          <Textarea value={systemPrompt} onChange={e => setSystemPrompt(e.target.value)}
            rows={3} className="text-xs resize-none" placeholder="เช่น 'คุณคือน้องกุ้ง ผู้ช่วย AI สุดน่ารัก'" />
          <div className="flex items-center justify-between mt-1.5">
            <Button size="sm" className="h-7 text-xs" onClick={savePrompt}>
              {promptSaved ? "✅ บันทึกแล้ว!" : "💾 บันทึก"}
            </Button>
            <span className="text-[10px] text-muted-foreground">inject เป็น system message ทุกครั้ง</span>
          </div>
        </div>
      )}

      {/* OpenClaw link removed */}

      {/* Messages */}
      <div ref={chatRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <div className="text-5xl mb-3">🦞</div>
              <p className="text-sm font-bold mb-1">SML AI Router Chat</p>
              <p className="text-xs text-muted-foreground">AI ตอบผ่าน SML AI Router ฟรี<br />เลือก model หรือใช้ auto</p>
              <div className="flex flex-wrap gap-1.5 mt-3 justify-center">
                {quickSuggestions.map(q => (
                  <Button key={q} variant="outline" size="sm" className="text-xs rounded-full"
                    onClick={() => sendDirect(q)}>
                    {q}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          msg.role === "user" ? (
            <div key={i} className="flex justify-end">
              <div className="px-3 py-2 rounded-2xl rounded-br-sm text-sm max-w-[85%] bg-primary text-primary-foreground">
                {msg.content}
              </div>
            </div>
          ) : (
            <div key={i} className="flex justify-start">
              <div className="max-w-[92%]">
                <div className="px-3 py-2 rounded-2xl rounded-bl-sm text-sm border bg-background prose prose-sm prose-invert max-w-none [&_pre]:bg-secondary [&_pre]:rounded-lg [&_pre]:p-3 [&_pre]:text-xs [&_code]:bg-secondary [&_code]:rounded [&_code]:px-1 [&_code]:text-xs">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {msg.provider && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full font-bold bg-[var(--clr-green)]/15 text-[var(--clr-green)]">{msg.provider}</span>
                  )}
                  {msg.latency && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono bg-secondary ${
                      msg.latency < 500 ? "text-[var(--clr-green)]" : msg.latency < 1500 ? "text-[var(--clr-yellow)]" : "text-[var(--clr-red)]"
                    }`}>{msg.latency}ms</span>
                  )}
                  {msg.model && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-secondary text-muted-foreground">{msg.model.split("/").pop()}</span>
                  )}
                  {msg.queryType && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[var(--clr-purple)]/15 text-[var(--clr-purple)]">{msg.queryType}</span>
                  )}
                </div>
              </div>
            </div>
          )
        ))}

        {/* Follow-up suggestions */}
        {followUps.length > 0 && !loading && messages.length > 0 && (
          <div className="flex flex-wrap gap-1.5 px-1">
            {followUps.map((q, i) => (
              <Button key={i} variant="outline" size="sm" className="text-xs rounded-full h-auto py-1 px-2.5 text-left"
                onClick={() => { setFollowUps([]); sendDirect(q); }}>
                {q}
              </Button>
            ))}
          </div>
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="px-4 py-3 rounded-2xl rounded-bl-sm border bg-background">
              <div className="flex gap-1.5">
                {[0, 150, 300].map(d => (
                  <span key={d} className="w-2 h-2 rounded-full bg-[var(--clr-accent)] animate-bounce" style={{ animationDelay: `${d}ms` }} />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-3 py-2 border-t">
        <div className="flex gap-2">
          <Input value={input} onChange={e => setInput(e.target.value)} onKeyDown={onKey}
            placeholder="พิมพ์ข้อความ..." disabled={loading} className="rounded-xl" />
          <Button onClick={send} disabled={loading || !input.trim()}
            className="rounded-xl px-4 bg-primary text-primary-foreground">
            {loading ? "⏳" : "📤"}
          </Button>
        </div>
      </div>
    </>
  );
}
