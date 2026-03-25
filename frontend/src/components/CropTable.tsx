"use client";

import type { CropRecommendation } from "@/lib/api";

interface CropTableProps {
  crops: CropRecommendation[];
}

function getScoreBg(score: number) {
  if (score >= 75) return "bg-green-100 text-green-800";
  if (score >= 55) return "bg-blue-100 text-blue-800";
  if (score >= 40) return "bg-amber-100 text-amber-800";
  return "bg-red-100 text-red-800";
}

export default function CropTable({ crops }: CropTableProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <div className="px-5 py-3 bg-green-50 border-b border-green-100">
        <h3 className="font-semibold text-green-800 flex items-center gap-2">
          <span>🌾</span> おすすめ作物
        </h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-500">
            <th className="px-5 py-2">作物</th>
            <th className="px-5 py-2">適性</th>
            <th className="px-5 py-2">収量見込み</th>
            <th className="px-5 py-2">栽培時期</th>
            <th className="px-5 py-2 hidden lg:table-cell">理由</th>
          </tr>
        </thead>
        <tbody>
          {crops.map((crop, i) => (
            <tr key={i} className="border-b last:border-0 hover:bg-gray-50">
              <td className="px-5 py-3 font-medium">{crop.crop_name}</td>
              <td className="px-5 py-3">
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreBg(crop.suitability_score)}`}>
                  {Math.round(crop.suitability_score)}
                </span>
              </td>
              <td className="px-5 py-3 text-gray-600">{crop.expected_yield_relative}</td>
              <td className="px-5 py-3 text-gray-600">{crop.growing_season}</td>
              <td className="px-5 py-3 text-gray-500 text-xs hidden lg:table-cell">{crop.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
