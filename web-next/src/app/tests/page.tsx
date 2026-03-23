"use client";

import { useState, useEffect } from "react";
import { getData } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import AppShell from "@/components/app-shell";

export default function TestsPage() {
  const [data, setData] = useState<Record<string, unknown>>({});

  useEffect(() => {
    getData().then(d => { if (d) setData(d as Record<string, unknown>); });
    const id = setInterval(async () => { const d = await getData(); if (d) setData(d as Record<string, unknown>); }, 5000);
    return () => clearInterval(id);
  }, []);

  const testResults = (data.test_results || []) as Array<{
    name: string;
    scoring?: { grade?: string; score?: number };
    chat_result?: { success?: boolean; status_code?: number; latency_ms?: number; response?: string; error?: string };
  }>;
  const keyTests = (data.key_tests || []) as Array<{
    name: string;
    has_key?: boolean;
    free_tier?: string;
    test_result?: { status?: string; message?: string };
  }>;

  const gradeColor = (score: number) =>
    score >= 70 ? "text-[var(--clr-green)] bg-[var(--clr-green)]/15" :
    score >= 40 ? "text-[var(--clr-yellow)] bg-[var(--clr-yellow)]/15" :
    "text-[var(--clr-red)] bg-[var(--clr-red)]/15";

  return (
    <AppShell>
      <h2 className="text-xl font-bold mb-4">🧪 ผลทดสอบ API</h2>
      {testResults.length > 0 ? (
        <Card>
          <CardContent className="p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-secondary/50">
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground">เกรด</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground">คะแนน</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground">ชื่อ</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground">แชท</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground">ความเร็ว</th>
                  <th className="text-left px-4 py-2 text-xs text-muted-foreground">คำตอบ</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {testResults.map((t, i) => {
                  const s = t.scoring || {};
                  const cr = t.chat_result || {};
                  const score = s.score || 0;
                  return (
                    <tr key={i}>
                      <td className="px-4 py-2"><Badge className={gradeColor(score)}>{s.grade || "F"}</Badge></td>
                      <td className={`px-4 py-2 font-bold ${score >= 70 ? "text-[var(--clr-green)]" : score >= 40 ? "text-[var(--clr-yellow)]" : "text-[var(--clr-red)]"}`}>{score}/100</td>
                      <td className="px-4 py-2 font-semibold">{t.name}</td>
                      <td className="px-4 py-2">{cr.success ? "✅" : cr.status_code === 401 ? "🔑" : "❌"}</td>
                      <td className="px-4 py-2 font-mono text-xs">{cr.latency_ms || "-"}ms</td>
                      <td className="px-4 py-2 text-xs truncate max-w-48 text-muted-foreground">{cr.response || cr.error || "-"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center py-12 text-muted-foreground">กดปุ่ม &quot;เริ่มค้นหา&quot; บนหน้า Dashboard ก่อน</div>
      )}

      {keyTests.length > 0 && (
        <>
          <h2 className="text-xl font-bold mt-8 mb-4">🔑 สถานะ API Key</h2>
          <Card>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-secondary/50">
                    <th className="text-left px-4 py-2 text-xs text-muted-foreground">ชื่อ</th>
                    <th className="text-left px-4 py-2 text-xs text-muted-foreground">มี Key</th>
                    <th className="text-left px-4 py-2 text-xs text-muted-foreground">ทดสอบ</th>
                    <th className="text-left px-4 py-2 text-xs text-muted-foreground">ฟรี</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {keyTests.map((k, i) => {
                    const tr = k.test_result || {};
                    return (
                      <tr key={i}>
                        <td className="px-4 py-2 font-semibold">{k.name}</td>
                        <td className="px-4 py-2">{k.has_key ? "✅" : "❌"}</td>
                        <td className={`px-4 py-2 text-sm ${tr.status === "ok" ? "text-[var(--clr-green)]" : tr.status === "rate_limited" ? "text-[var(--clr-yellow)]" : "text-[var(--clr-red)]"}`}>
                          {tr.status === "ok" ? `✅ ${tr.message || ""}` : tr.status === "rate_limited" ? "⚠️ Rate limited" : tr.message || "-"}
                        </td>
                        <td className="px-4 py-2 text-xs text-muted-foreground">{k.free_tier || "-"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </>
      )}
    </AppShell>
  );
}
