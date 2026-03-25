"use client";

interface ScoreGaugeProps {
  score: number;
  grade: string;
  label: string;
  size?: "sm" | "md" | "lg";
}

const gradeColors: Record<string, string> = {
  S: "#22c55e",
  A: "#3b82f6",
  B: "#f59e0b",
  C: "#f97316",
  D: "#ef4444",
};

export default function ScoreGauge({ score, grade, label, size = "md" }: ScoreGaugeProps) {
  const dims = { sm: 80, md: 120, lg: 160 };
  const d = dims[size];
  const r = d / 2 - 8;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (score / 100) * circumference;
  const color = gradeColors[grade] || "#6b7280";

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={d} height={d} className="-rotate-90">
        <circle
          cx={d / 2}
          cy={d / 2}
          r={r}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={size === "lg" ? 10 : 6}
        />
        <circle
          cx={d / 2}
          cy={d / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={size === "lg" ? 10 : 6}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div
        className="absolute flex flex-col items-center justify-center"
        style={{ width: d, height: d }}
      >
        <span className="font-bold" style={{ fontSize: size === "lg" ? 32 : size === "md" ? 24 : 16, color }}>
          {Math.round(score)}
        </span>
        <span
          className="font-bold"
          style={{ fontSize: size === "lg" ? 20 : 14, color }}
        >
          {grade}
        </span>
      </div>
      <span className="text-xs text-gray-500 mt-1">{label}</span>
    </div>
  );
}
