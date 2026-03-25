import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FarmScore — 農地ポテンシャル診断",
  description:
    "緯度経度を入力するだけで農地の適性をAIがスコアリング。土壌・気候・水利・日照・標高を分析し、最適な作物を提案します。",
  openGraph: {
    title: "FarmScore — 農地ポテンシャル診断",
    description: "AIが農地の適性を5軸でスコアリング。無料で使えます。",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossOrigin=""
        />
      </head>
      <body className="min-h-screen bg-[var(--fs-bg)] text-gray-900 antialiased">
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 font-bold text-xl text-green-700">
              <span className="text-2xl">🌱</span>
              FarmScore
            </a>
            <div className="flex items-center gap-6 text-sm">
              <a href="/" className="hover:text-green-600 transition">診断</a>
              <a href="/dashboard" className="hover:text-green-600 transition">ダッシュボード</a>
              <a href="/api-docs" className="hover:text-green-600 transition">API</a>
              <a
                href="/docs"
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                無料で始める
              </a>
            </div>
          </div>
        </nav>
        <main>{children}</main>
        <footer className="border-t border-gray-200 mt-20 py-8 text-center text-xs text-gray-500">
          <p>
            FarmScore v1.0 — データソース: 農研機構eSoil, 気象庁, 国土数値情報, 国土地理院DEM
          </p>
          <p className="mt-1">
            本スコアは参考情報です。農業判断の結果について一切の責任を負いません。
          </p>
        </footer>
      </body>
    </html>
  );
}
