"use client";

interface ScoreCardProps {
  title: string;
  score: number;
  icon: string;
  children: React.ReactNode;
}

function getScoreColor(score: number) {
  if (score >= 75) return "text-green-600 bg-green-50 border-green-200";
  if (score >= 55) return "text-blue-600 bg-blue-50 border-blue-200";
  if (score >= 40) return "text-amber-600 bg-amber-50 border-amber-200";
  return "text-red-600 bg-red-50 border-red-200";
}

export default function ScoreCard({ title, score, icon, children }: ScoreCardProps) {
  const colorClass = getScoreColor(score);
  return (
    <div className={`rounded-xl border p-5 ${colorClass}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <h3 className="font-semibold text-base">{title}</h3>
        </div>
        <div className="text-2xl font-bold">{Math.round(score)}</div>
      </div>
      <div className="text-sm space-y-1 opacity-90">{children}</div>
    </div>
  );
}
