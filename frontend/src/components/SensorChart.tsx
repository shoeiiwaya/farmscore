"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart,
} from "recharts";

interface DataPoint {
  timestamp: string;
  avg: number;
  min: number;
  max: number;
}

interface SensorChartProps {
  data: DataPoint[];
  sensorType: string;
  color?: string;
}

const SENSOR_LABELS: Record<string, { label: string; unit: string; color: string }> = {
  soil_moisture: { label: "土壌水分", unit: "%", color: "#3b82f6" },
  temperature: { label: "気温", unit: "°C", color: "#ef4444" },
  humidity: { label: "湿度", unit: "%", color: "#8b5cf6" },
  light: { label: "照度", unit: "lux", color: "#f59e0b" },
};

export default function SensorChart({ data, sensorType, color }: SensorChartProps) {
  const config = SENSOR_LABELS[sensorType] || { label: sensorType, unit: "", color: "#6b7280" };
  const chartColor = color || config.color;

  const formatTime = (ts: string) => {
    const d = new Date(ts);
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:00`;
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-700 mb-4">
        {config.label}（{config.unit}）
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`grad-${sensorType}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColor} stopOpacity={0.2} />
              <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatTime}
            tick={{ fontSize: 11 }}
            stroke="#9ca3af"
          />
          <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
          <Tooltip
            labelFormatter={formatTime}
            formatter={(value: number) => [`${value} ${config.unit}`, config.label]}
          />
          <Area
            type="monotone"
            dataKey="avg"
            stroke={chartColor}
            fill={`url(#grad-${sensorType})`}
            strokeWidth={2}
          />
          <Line type="monotone" dataKey="min" stroke="#9ca3af" strokeWidth={1} strokeDasharray="4 4" dot={false} />
          <Line type="monotone" dataKey="max" stroke="#9ca3af" strokeWidth={1} strokeDasharray="4 4" dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
