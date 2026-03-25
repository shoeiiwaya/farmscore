"use client";

import { useState } from "react";

const ENDPOINTS = [
  {
    method: "GET",
    path: "/v1/demo/score",
    description: "農地適性スコア（デモ・認証不要）",
    params: "lat, lon, crop?",
    auth: false,
    example: `curl "https://api.farmscore.jp/v1/demo/score?lat=35.44&lon=139.64&crop=tomato"`,
  },
  {
    method: "GET",
    path: "/v1/score",
    description: "農地適性スコア（本番・APIキー必須）",
    params: "lat, lon, crop?",
    auth: true,
    example: `curl -H "X-API-Key: fs_YOUR_KEY" "https://api.farmscore.jp/v1/score?lat=35.44&lon=139.64"`,
  },
  {
    method: "POST",
    path: "/v1/score/batch",
    description: "バッチスコアリング（最大50地点）",
    params: "locations[]",
    auth: true,
    example: `curl -X POST -H "X-API-Key: fs_YOUR_KEY" -H "Content-Type: application/json" \\
  -d '{"locations": [{"lat": 35.44, "lon": 139.64}, {"lat": 36.08, "lon": 140.07}]}' \\
  "https://api.farmscore.jp/v1/score/batch"`,
  },
  {
    method: "GET",
    path: "/v1/fields",
    description: "圃場一覧",
    params: "-",
    auth: true,
    example: `curl -H "Authorization: Bearer YOUR_TOKEN" "https://api.farmscore.jp/v1/fields"`,
  },
  {
    method: "POST",
    path: "/v1/fields",
    description: "圃場を登録",
    params: "name, lat, lon, area_sqm?, crop_type?",
    auth: true,
    example: `curl -X POST -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" \\
  -d '{"name": "第1圃場", "lat": 35.44, "lon": 139.64, "crop_type": "tomato"}' \\
  "https://api.farmscore.jp/v1/fields"`,
  },
  {
    method: "GET",
    path: "/v1/fields/{id}/readings",
    description: "センサーデータ取得",
    params: "sensor_type?, hours?",
    auth: true,
    example: `curl -H "Authorization: Bearer YOUR_TOKEN" "https://api.farmscore.jp/v1/fields/{id}/readings?sensor_type=soil_moisture&hours=24"`,
  },
  {
    method: "GET",
    path: "/v1/fields/{id}/alerts",
    description: "アラート一覧",
    params: "-",
    auth: true,
    example: `curl -H "Authorization: Bearer YOUR_TOKEN" "https://api.farmscore.jp/v1/fields/{id}/alerts"`,
  },
  {
    method: "POST",
    path: "/v1/webhook/sensor",
    description: "センサーデータ受信Webhook",
    params: "device_id, value, ...",
    auth: false,
    example: `curl -X POST -H "Content-Type: application/json" \\
  -d '{"device_id": "dragino-001", "soil_moisture": 42.5, "battery": 95}' \\
  "https://api.farmscore.jp/v1/webhook/sensor"`,
  },
  {
    method: "GET",
    path: "/v1/analytics/dashboard",
    description: "ダッシュボード統計",
    params: "-",
    auth: true,
    example: `curl -H "Authorization: Bearer YOUR_TOKEN" "https://api.farmscore.jp/v1/analytics/dashboard"`,
  },
];

export default function ApiDocs() {
  const [selectedEndpoint, setSelectedEndpoint] = useState(ENDPOINTS[0]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">API ドキュメント</h1>
      <p className="text-gray-600 mb-8">
        FarmScore APIを使って農地データをプログラマティックに取得できます。
        <a href="/docs" className="text-green-600 hover:underline ml-1">Swagger UI →</a>
      </p>

      {/* Plans */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
        {[
          { name: "Free", price: "¥0", calls: "100/月", fields: "3" },
          { name: "Starter", price: "¥5,000", calls: "1,000/月", fields: "10" },
          { name: "Pro", price: "¥20,000", calls: "5,000/月", fields: "50" },
          { name: "Enterprise", price: "要見積", calls: "無制限", fields: "無制限" },
        ].map((plan) => (
          <div
            key={plan.name}
            className={`bg-white rounded-xl border p-5 ${plan.name === "Starter" ? "border-green-300 ring-2 ring-green-100" : "border-gray-200"}`}
          >
            <div className="font-bold text-lg">{plan.name}</div>
            <div className="text-2xl font-bold mt-2">{plan.price}<span className="text-sm text-gray-400">/月</span></div>
            <div className="text-sm text-gray-500 mt-3 space-y-1">
              <p>APIコール: {plan.calls}</p>
              <p>圃場数: {plan.fields}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Endpoints */}
      <h2 className="text-lg font-bold text-gray-800 mb-4">エンドポイント一覧</h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="space-y-2">
          {ENDPOINTS.map((ep, i) => (
            <button
              key={i}
              onClick={() => setSelectedEndpoint(ep)}
              className={`w-full text-left px-4 py-3 rounded-lg border transition text-sm ${
                selectedEndpoint === ep
                  ? "bg-green-50 border-green-300"
                  : "bg-white border-gray-200 hover:border-green-200"
              }`}
            >
              <span className={`inline-block w-14 text-xs font-mono font-bold ${
                ep.method === "GET" ? "text-blue-600" : "text-green-600"
              }`}>
                {ep.method}
              </span>
              <span className="font-mono text-xs">{ep.path}</span>
              {!ep.auth && (
                <span className="ml-2 text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded">公開</span>
              )}
            </button>
          ))}
        </div>

        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-2 py-1 rounded text-xs font-bold ${
              selectedEndpoint.method === "GET" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"
            }`}>
              {selectedEndpoint.method}
            </span>
            <code className="text-sm font-mono">{selectedEndpoint.path}</code>
          </div>
          <p className="text-sm text-gray-700 mb-4">{selectedEndpoint.description}</p>
          <div className="text-sm mb-2 text-gray-500">パラメータ: <code>{selectedEndpoint.params}</code></div>
          <div className="text-sm mb-4 text-gray-500">
            認証: {selectedEndpoint.auth ? "必須（APIキー or JWT）" : "不要"}
          </div>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-green-400 text-xs font-mono whitespace-pre-wrap">{selectedEndpoint.example}</pre>
          </div>
        </div>
      </div>

      {/* Quick start */}
      <div className="mt-10 bg-green-50 rounded-xl border border-green-200 p-6">
        <h2 className="font-bold text-green-800 mb-3">クイックスタート</h2>
        <div className="bg-gray-900 rounded-lg p-4 text-sm font-mono">
          <pre className="text-green-400 whitespace-pre-wrap">{`# 1. デモAPIを試す（認証不要）
curl "https://api.farmscore.jp/v1/demo/score?lat=35.44&lon=139.64"

# 2. アカウント作成
curl -X POST -H "Content-Type: application/json" \\
  -d '{"email": "you@example.com", "password": "your_password"}' \\
  "https://api.farmscore.jp/v1/signup"

# 3. APIキー発行（返却されたtokenを使用）
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  -X POST "https://api.farmscore.jp/v1/api-keys?name=my-app"

# 4. 本番APIを利用
curl -H "X-API-Key: fs_YOUR_KEY" \\
  "https://api.farmscore.jp/v1/score?lat=35.44&lon=139.64&crop=tomato"`}</pre>
        </div>
      </div>
    </div>
  );
}
