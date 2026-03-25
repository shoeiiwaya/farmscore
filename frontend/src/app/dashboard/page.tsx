"use client";

import { useState } from "react";
import SensorChart from "@/components/SensorChart";

// Mock data for demo (replaced by API calls when backend is running)
const MOCK_FIELDS = [
  { id: "1", name: "横浜市 戸塚区 第1圃場", crop: "トマト", score: 72, sensors: 3 },
  { id: "2", name: "横浜市 泉区 第2圃場", crop: "イチゴ", score: 68, sensors: 2 },
];

function generateMockData(hours: number, baseValue: number, variance: number) {
  const data = [];
  const now = new Date();
  for (let i = hours; i >= 0; i--) {
    const ts = new Date(now.getTime() - i * 3600000);
    const val = baseValue + (Math.random() - 0.5) * variance;
    data.push({
      timestamp: ts.toISOString(),
      avg: Math.round(val * 10) / 10,
      min: Math.round((val - variance * 0.3) * 10) / 10,
      max: Math.round((val + variance * 0.3) * 10) / 10,
    });
  }
  return data;
}

const MOCK_ALERTS = [
  { id: "a1", type: "drought", severity: "warning", message: "土壌水分が低下しています: 18%（閾値: 20%）。灌水を検討してください。", time: "2時間前" },
  { id: "a2", type: "frost", severity: "info", message: "明朝の最低気温4°C予報。霜注意。", time: "6時間前" },
];

export default function Dashboard() {
  const [selectedField, setSelectedField] = useState(MOCK_FIELDS[0]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">圃場ダッシュボード</h1>

      {/* Stats overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="text-sm text-gray-500">登録圃場</div>
          <div className="text-3xl font-bold text-gray-900 mt-1">{MOCK_FIELDS.length}</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="text-sm text-gray-500">稼働センサー</div>
          <div className="text-3xl font-bold text-green-600 mt-1">5</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="text-sm text-gray-500">未読アラート</div>
          <div className="text-3xl font-bold text-amber-600 mt-1">{MOCK_ALERTS.length}</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="text-sm text-gray-500">平均スコア</div>
          <div className="text-3xl font-bold text-blue-600 mt-1">70</div>
        </div>
      </div>

      {/* Field selector */}
      <div className="flex gap-3 mb-6 overflow-x-auto pb-2">
        {MOCK_FIELDS.map((f) => (
          <button
            key={f.id}
            onClick={() => setSelectedField(f)}
            className={`flex-shrink-0 px-5 py-3 rounded-xl border transition ${
              selectedField.id === f.id
                ? "bg-green-50 border-green-300 text-green-800"
                : "bg-white border-gray-200 text-gray-700 hover:border-green-200"
            }`}
          >
            <div className="font-semibold text-sm">{f.name}</div>
            <div className="text-xs mt-1 opacity-70">
              {f.crop} / スコア {f.score} / センサー {f.sensors}台
            </div>
          </button>
        ))}
        <button className="flex-shrink-0 px-5 py-3 rounded-xl border border-dashed border-gray-300 text-gray-400 hover:text-green-600 hover:border-green-300 transition">
          + 圃場を追加
        </button>
      </div>

      {/* Alerts */}
      {MOCK_ALERTS.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 mb-8">
          <h2 className="font-semibold text-amber-800 mb-3">アラート</h2>
          <div className="space-y-2">
            {MOCK_ALERTS.map((a) => (
              <div
                key={a.id}
                className="flex items-start gap-3 bg-white rounded-lg p-3 border border-amber-100"
              >
                <span className="text-lg">
                  {a.severity === "critical" ? "🔴" : a.severity === "warning" ? "🟡" : "🔵"}
                </span>
                <div className="flex-1">
                  <p className="text-sm text-gray-800">{a.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{a.time}</p>
                </div>
                <button className="text-xs text-gray-400 hover:text-gray-600">既読</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sensor charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <SensorChart
          data={generateMockData(48, 45, 20)}
          sensorType="soil_moisture"
        />
        <SensorChart
          data={generateMockData(48, 22, 8)}
          sensorType="temperature"
        />
        <SensorChart
          data={generateMockData(48, 65, 15)}
          sensorType="humidity"
        />
        <SensorChart
          data={generateMockData(48, 5000, 4000)}
          sensorType="light"
        />
      </div>

      {/* Quick actions */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <h2 className="font-semibold text-gray-700 mb-4">今日のアクション</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
            <div className="text-sm font-medium text-blue-800">💧 灌水推奨</div>
            <p className="text-xs text-blue-600 mt-1">
              土壌水分が低下傾向です。午前中の灌水を推奨します。
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-4 border border-green-100">
            <div className="text-sm font-medium text-green-800">🌡️ 温度正常</div>
            <p className="text-xs text-green-600 mt-1">
              気温は適温範囲内（18-28°C）で推移しています。
            </p>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
            <div className="text-sm font-medium text-amber-800">🌧️ 降雨予報</div>
            <p className="text-xs text-amber-600 mt-1">
              明日午後から雨の予報。露地作物の対策を検討してください。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
