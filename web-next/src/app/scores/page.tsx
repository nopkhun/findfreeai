"use client";

import { useState, useEffect, useCallback } from "react";
import { fetchJSON } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ScoreEntry {
  id: string;
  score: number;
  grade: string;
  detail: string;
  breakdown: { success_rate: number; speed: number; reliability: number; volume: number };
  total_ok?: number;
  total_fail?: number;
  ok?: number;
  fail?: number;
  avg_latency_ms: number;
  fail_streak?: number;
  provider?: string;
}

interface ScoresData {
  provider_ranking: ScoreEntry[];
  model_ranking: ScoreEntry[];
  total_requests: number;
  last_updated: string;
}

const gradeColor = (grade: string) => {
  if (grade === "A+" || grade === "A") return "text-[var(--clr-green)] bg-[var(--clr-green)]/15";
  if (grade === "B") return "text-[var(--clr-accent)] bg-[var(--clr-accent)]/15";
  if (grade === "C") return "text-[var(--clr-yellow)] bg-[var(--clr-yellow)]/15";
  return "text-[var(--clr-red)] bg-[var(--clr-red)]/15";
};

const scoreBarColor = (score: number) =>
  score >= 80 ? "bg-[var(--clr-green)]" :
  score >= 60 ? "bg-[var(--clr-accent)]" :
  score >= 40 ? "bg-[var(--clr-yellow)]" :
  "bg-[var(--clr-red)]";

function ScoreCard({ entry, rank }: { entry: ScoreEntry; rank: number }) {
  const total = (entry.total_ok ?? entry.ok ?? 0) + (entry.total_fail ?? entry.fail ?? 0);
  const ok = entry.total_ok ?? entry.ok ?? 0;
  const fail = entry.total_fail ?? entry.fail ?? 0;

  return (
    <Card className={rank === 0 ? "ring-1 ring-[var(--clr-green)]/30 border-[var(--clr-green)]" : ""}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {rank < 3 && (
              <span className={`text-lg ${rank === 0 ? "" : "opacity-60"}`}>
                {rank === 0 ? "🥇" : rank === 1 ? "🥈" : "🥉"}
              </span>
            )}
            <span className="font-semibold">{entry.id}</span>
            {entry.provider && (
              <span className="text-xs text-muted-foreground">({entry.provider})</span>
            )}
          </div>
          <Badge className={`text-sm font-bold px-2.5 py-0.5 ${gradeColor(entry.grade)}`}>
            {entry.grade}
          </Badge>
        </div>

        {/* Score bar */}
        <div className="flex items-center gap-3 mb-3">
          <div className="flex-1 h-2.5 rounded-full bg-secondary overflow-hidden">
            <div className={`h-full rounded-full transition-all ${scoreBarColor(entry.score)}`}
              style={{ width: `${entry.score}%` }} />
          </div>
          <span className={`text-lg font-bold font-mono min-w-[3ch] text-right ${
            entry.score >= 80 ? "text-[var(--clr-green)]" :
            entry.score >= 60 ? "text-[var(--clr-accent)]" :
            entry.score >= 40 ? "text-[var(--clr-yellow)]" : "text-[var(--clr-red)]"
          }`}>{entry.score}</span>
        </div>

        {/* Breakdown */}
        <div className="grid grid-cols-4 gap-2 mb-3">
          {[
            { label: "Success", value: entry.breakdown.success_rate, max: 40, icon: "✅" },
            { label: "Speed", value: entry.breakdown.speed, max: 30, icon: "⚡" },
            { label: "Stable", value: entry.breakdown.reliability, max: 20, icon: "🛡️" },
            { label: "Volume", value: entry.breakdown.volume, max: 10, icon: "📊" },
          ].map(b => (
            <div key={b.label} className="text-center">
              <div className="text-[10px] text-muted-foreground mb-0.5">{b.icon} {b.label}</div>
              <div className="h-1 rounded-full bg-secondary overflow-hidden">
                <div className={`h-full rounded-full ${scoreBarColor((b.value / b.max) * 100)}`}
                  style={{ width: `${(b.value / b.max) * 100}%` }} />
              </div>
              <div className="text-[10px] font-mono text-muted-foreground mt-0.5">{b.value}/{b.max}</div>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>✅ {ok}</span>
          <span>❌ {fail}</span>
          <span>⚡ {entry.avg_latency_ms}ms</span>
          {entry.fail_streak !== undefined && entry.fail_streak > 0 && (
            <span className="text-[var(--clr-red)]">🔥 streak {entry.fail_streak}</span>
          )}
          <span className="ml-auto">{total} calls</span>
        </div>
      </CardContent>
    </Card>
  );
}

export default function ScoresPage() {
  const [data, setData] = useState<ScoresData | null>(null);

  const poll = useCallback(async () => {
    const d = await fetchJSON<ScoresData>("/v1/scores");
    if (d) setData(d);
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, 5000);
    return () => clearInterval(id);
  }, [poll]);

  return (
    <>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">📊 Provider & Model Scores</h2>
            <p className="text-sm text-muted-foreground mt-1">
              คำนวณจาก success rate, speed, reliability, volume | อัปเดตอัตโนมัติ
            </p>
          </div>
          {data && (
            <div className="text-right text-xs text-muted-foreground">
              <div>{data.total_requests} requests ทั้งหมด</div>
              {data.last_updated && <div>อัปเดต: {new Date(data.last_updated).toLocaleTimeString("th-TH")}</div>}
            </div>
          )}
        </div>

        {/* Provider Ranking */}
        <div>
          <h3 className="text-lg font-semibold mb-3">🏆 Provider Ranking</h3>
          {data?.provider_ranking && data.provider_ranking.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.provider_ranking.map((entry, i) => (
                <ScoreCard key={entry.id} entry={entry} rank={i} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                ยังไม่มีข้อมูล — ส่ง chat สักหน่อยเพื่อเริ่มเก็บสถิติ
              </CardContent>
            </Card>
          )}
        </div>

        {/* Model Ranking */}
        <div>
          <h3 className="text-lg font-semibold mb-3">🎯 Model Ranking</h3>
          {data?.model_ranking && data.model_ranking.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {data.model_ranking.map((entry, i) => (
                <ScoreCard key={entry.id} entry={entry} rank={i} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                ยังไม่มีข้อมูล — ส่ง chat สักหน่อยเพื่อเริ่มเก็บสถิติ
              </CardContent>
            </Card>
          )}
        </div>

        {/* Score Legend */}
        <Card>
          <CardContent className="p-4">
            <h4 className="font-semibold mb-2 text-sm">📖 วิธีคำนวณ Score (0-100)</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs text-muted-foreground">
              <div><strong className="text-foreground">✅ Success Rate (40%)</strong><br />สัดส่วนที่ตอบสำเร็จ</div>
              <div><strong className="text-foreground">⚡ Speed (30%)</strong><br />&lt;300ms=30, &lt;1s=20, &lt;3s=10, &gt;10s=0</div>
              <div><strong className="text-foreground">🛡️ Reliability (20%)</strong><br />fail streak ยิ่งน้อยยิ่งดี</div>
              <div><strong className="text-foreground">📊 Volume (10%)</strong><br />ยิ่งใช้เยอะยิ่งมั่นใจ (max 20 calls)</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
