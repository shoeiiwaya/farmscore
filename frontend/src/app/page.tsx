"use client";

import { useState, useCallback } from "react";
import dynamic from "next/dynamic";
import ScoreCard from "@/components/ScoreCard";
import CropTable from "@/components/CropTable";
import type { ScoreResult } from "@/lib/api";
import { fetchScore } from "@/lib/api";

const MapPicker = dynamic(() => import("@/components/MapPicker"), { ssr: false });

const SAMPLE_REGIONS = [
  { name: "横浜（戸塚区）", lat: 35.3964, lon: 139.5309 },
  { name: "千葉 南房総", lat: 35.0465, lon: 139.857 },
  { name: "茨城 つくば", lat: 36.0835, lon: 140.0764 },
  { name: "長野 松本", lat: 36.2381, lon: 137.972 },
  { name: "新潟 魚沼", lat: 37.0667, lon: 138.95 },
  { name: "北海道 十勝", lat: 42.9236, lon: 143.1966 },
  { name: "静岡 牧之原", lat: 34.7421, lon: 138.221 },
  { name: "宮崎 都城", lat: 31.7275, lon: 131.0621 },
];

const CROPS = [
  { key: "", label: "指定なし" },
  { key: "rice", label: "水稲" },
  { key: "tomato", label: "トマト" },
  { key: "strawberry", label: "イチゴ" },
  { key: "cabbage", label: "キャベツ" },
  { key: "sweet_potato", label: "サツマイモ" },
  { key: "grape", label: "ブドウ" },
  { key: "tea", label: "茶" },
  { key: "soybean", label: "大豆" },
  { key: "wheat", label: "小麦" },
  { key: "onion", label: "タマネギ" },
];

export default function Home() {
  const [lat, setLat] = useState(35.4437);
  const [lon, setLon] = useState(139.638);
  const [crop, setCrop] = useState("");
  const [result, setResult] = useState<ScoreResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleScore = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchScore(lat, lon, crop || undefined);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "スコアリングに失敗しました");
    }
    setLoading(false);
  }, [lat, lon, crop]);

  const handleLocationChange = useCallback((newLat: number, newLon: number) => {
    setLat(newLat);
    setLon(newLon);
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          農地ポテンシャル診断
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          地図をクリックするだけで、土壌・気候・水利・日照・標高の5軸で農地の適性をスコアリング。最適な作物を提案します。
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 mb-6 shadow-sm">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[120px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">緯度</label>
            <input
              type="number"
              step="0.0001"
              value={lat}
              onChange={(e) => setLat(Number(e.target.value))}
              className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>
          <div className="flex-1 min-w-[120px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">経度</label>
            <input
              type="number"
              step="0.0001"
              value={lon}
              onChange={(e) => setLon(Number(e.target.value))}
              className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">対象作物</label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              {CROPS.map((c) => (
                <option key={c.key} value={c.key}>{c.label}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleScore}
            disabled={loading}
            className="px-8 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 transition shadow-sm"
          >
            {loading ? "分析中..." : "診断する"}
          </button>
        </div>

        {/* Sample regions */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 self-center">サンプル:</span>
          {SAMPLE_REGIONS.map((r) => (
            <button
              key={r.name}
              onClick={() => {
                setLat(r.lat);
                setLon(r.lon);
              }}
              className="text-xs px-3 py-1 rounded-full bg-gray-100 hover:bg-green-100 text-gray-700 hover:text-green-700 transition"
            >
              {r.name}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">{error}</div>
      )}

      {/* Map */}
      <div className="mb-8">
        <MapPicker
          lat={lat}
          lon={lon}
          onLocationChange={handleLocationChange}
          score={result?.overall_score}
          grade={result?.grade}
        />
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Overall score */}
          <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm text-center">
            <div className="inline-flex items-center gap-6">
              <div className="relative">
                <div
                  className={`w-24 h-24 rounded-full flex items-center justify-center text-white text-3xl font-bold grade-${result.grade}`}
                >
                  {result.grade}
                </div>
              </div>
              <div className="text-left">
                <div className="text-5xl font-bold text-gray-900">
                  {Math.round(result.overall_score)}
                  <span className="text-lg text-gray-400 ml-1">/100</span>
                </div>
                <div className="text-gray-500 mt-1">
                  総合農地適性スコア — {result.elevation.landform}（標高{result.elevation.elevation_m}m）
                </div>
              </div>
            </div>
          </div>

          {/* Sub-scores grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ScoreCard title="土壌" score={result.soil_score} icon="🪨">
              <p><strong>土壌タイプ:</strong> {result.soil.soil_type}（{result.soil.soil_group}）</p>
              <p><strong>pH:</strong> {result.soil.ph_range}</p>
              <p><strong>排水性:</strong> {result.soil.drainage}</p>
              <p><strong>有機物:</strong> {result.soil.organic_matter}</p>
              <p className="mt-2 text-xs">{result.soil.suitability_notes}</p>
            </ScoreCard>

            <ScoreCard title="気候" score={result.climate_score} icon="🌤️">
              <p><strong>年平均気温:</strong> {result.climate.annual_temp_avg}°C</p>
              <p><strong>年間降水量:</strong> {result.climate.annual_precip_mm}mm</p>
              <p><strong>無霜期間:</strong> {result.climate.frost_free_days}日</p>
              <p><strong>積算温度:</strong> {result.climate.growing_degree_days}GDD</p>
              <p><strong>霜リスク:</strong> {result.climate.frost_risk} / <strong>台風:</strong> {result.climate.typhoon_risk}</p>
            </ScoreCard>

            <ScoreCard title="水利" score={result.water_score} icon="💧">
              <p><strong>最寄河川:</strong> {result.water.river_name}（{result.water.nearest_river_km}km）</p>
              <p><strong>洪水リスク:</strong> {result.water.flood_risk_zone}</p>
              <p><strong>地下水:</strong> {result.water.groundwater_depth_est}</p>
              <p><strong>灌漑:</strong> {result.water.irrigation_accessibility}</p>
            </ScoreCard>

            <ScoreCard title="日照" score={result.sunlight_score} icon="☀️">
              <p><strong>年間日照:</strong> {result.sunlight.annual_sunshine_hours}時間</p>
              <p><strong>日射量:</strong> {result.sunlight.avg_daily_radiation_mj} MJ/m²/日</p>
              <p><strong>方位:</strong> {result.sunlight.aspect}</p>
              <p><strong>傾斜:</strong> {result.sunlight.slope_deg}°</p>
            </ScoreCard>

            <ScoreCard title="標高・地形" score={result.elevation_score} icon="⛰️">
              <p><strong>標高:</strong> {result.elevation.elevation_m}m</p>
              <p><strong>地形:</strong> {result.elevation.landform}</p>
              <p><strong>傾斜:</strong> {result.elevation.slope_deg}°</p>
              <p><strong>方位:</strong> {result.elevation.aspect}</p>
            </ScoreCard>
          </div>

          {/* Crop recommendations */}
          <CropTable crops={result.crop_recommendations} />

          {/* Disclaimer */}
          <p className="text-xs text-gray-400 text-center">{result.disclaimer}</p>
        </div>
      )}

      {/* CTA for non-results state */}
      {!result && !loading && (
        <div className="text-center py-16">
          <div className="text-6xl mb-4">🌱</div>
          <h2 className="text-2xl font-bold text-gray-700 mb-2">地図をクリックして診断開始</h2>
          <p className="text-gray-500">
            地図上の任意の地点をクリック、またはサンプル地点を選択して「診断する」を押してください
          </p>
        </div>
      )}
    </div>
  );
}
