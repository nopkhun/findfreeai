"use client";

import { useState, useEffect, useCallback } from "react";
import { getBrainLogs, getBrainRecs } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";

const icons: Record<string, string> = { analysis: "📊", new_apis: "🔍", skill_upgrade: "🚀", report: "📋" };
const titles: Record<string, string> = { analysis: "วิเคราะห์ผลทดสอบ", new_apis: "API ฟรีใหม่", skill_upgrade: "อัปเกรด Skill", report: "รายงานสรุป" };

export default function BrainPage() {
  const [logs, setLogs] = useState<Array<{ time: string; msg: string; level: string }>>([]);
  const [recs, setRecs] = useState<Array<{ category: string; content: string; created_at?: string }>>([]);

  const poll = useCallback(async () => {
    const [l, r] = await Promise.all([getBrainLogs(), getBrainRecs()]);
    if (l) setLogs(l as typeof logs);
    if (r && (r as { items?: unknown[] }).items) setRecs((r as { items: typeof recs }).items);
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, 3000);
    return () => clearInterval(id);
  }, [poll]);

  const logColor = (level: string) =>
    level === "ok" ? "text-[var(--clr-green)]" :
    level === "error" ? "text-[var(--clr-red)]" :
    level === "warn" ? "text-[var(--clr-yellow)]" : "text-muted-foreground";

  return (
    <>
      <h2 className="text-xl font-bold mb-4">🧠 AI วิเคราะห์ (Claude CLI)</h2>

      {recs.length > 0 ? (
        <div className="space-y-4 mb-8">
          {[...recs].reverse().map((r, i) => (
            <Card key={i}>
              <CardContent className="p-5">
                <div className="font-semibold mb-2 text-[var(--clr-accent)]">
                  {icons[r.category] || "📌"} {titles[r.category] || r.category}
                </div>
                <pre className="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground font-[inherit]">{r.content}</pre>
                {r.created_at && (
                  <div className="text-xs mt-2 text-muted-foreground">{new Date(r.created_at).toLocaleString("th-TH")}</div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 mb-8 text-muted-foreground">กดปุ่ม &quot;🧠 AI วิเคราะห์&quot; บน Dashboard ก่อน</div>
      )}

      <h3 className="text-lg font-semibold mb-3">📋 Brain Log</h3>
      <Card className="bg-[#0a0e14]">
        <CardContent className="p-4 font-mono text-xs leading-relaxed max-h-96 overflow-y-auto">
          {logs.length > 0 ? (
            logs.slice(-50).map((l, i) => (
              <div key={i} className={logColor(l.level)}>
                <span className="text-muted-foreground">[{l.time}]</span> {l.msg}
              </div>
            ))
          ) : (
            <div className="text-muted-foreground">รอคำสั่ง...</div>
          )}
        </CardContent>
      </Card>
    </>
  );
}
