# FarmScore — 農地ポテンシャル診断マップ

**緯度経度を入力するだけで、世界中どこでも農地の適性をスコアリング。**
土壌・気候・水利・日照・標高の5軸で分析し、最適な作物と肥料を提案します。

## Demo

**マップUI:** https://shoeiiwaya.github.io/farmscore/map.html

> APIサーバーを自分のPCで起動すれば、マップからリアルタイムで診断できます（下記参照）

## 使い方（3ステップ）

### 1. クローン

```bash
git clone https://github.com/shoeiiwaya/farmscore.git
cd farmscore
```

### 2. APIサーバー起動

```bash
cd backend
pip install -r requirements-local.txt   # 軽量版（3パッケージだけ）
python3 run_local.py
```

起動すると:
```
  🌱 FarmScore API starting...
  📍 http://localhost:8000
  📖 http://localhost:8000/docs
  🔍 http://localhost:8000/v1/demo/score?lat=35.44&lon=139.64
```

### 3. マップを開く

`map.html` をブラウザで開く（ダブルクリック or `open map.html`）

地図をクリック → 自動で診断が走ります。

## 機能

| 機能 | 内容 |
|------|------|
| 5軸スコアリング | 土壌・気候・水利・日照・標高を0-100点で評価 |
| 作物データベース | 日本137種 + グローバル13種 = **150種** |
| 肥料アドバイス | 27種の肥料・土壌改良材DB + 10作物の施肥基準 |
| 世界対応 | 23カ国/地域の座標に対応（日本以外も診断可能） |
| リアルタイム気象 | 気象庁AMeDAS 1,286地点（日本のみ） |
| 栽培実績 | 農水省e-Stat連携（都道府県別の生産統計） |
| 日本適応分析 | 海外作物（コーヒー、キヌア等）の日本栽培可能性 |

## API エンドポイント

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/v1/demo/score?lat=35.44&lon=139.64` | 農地スコアリング |
| GET | `/v1/demo/score?lat=35.44&lon=139.64&crop=rice` | 作物指定スコア |
| POST | `/v1/demo/score/batch` | バッチ診断（最大50地点） |
| GET | `/v1/demo/crops` | 作物一覧（150種） |
| GET | `/v1/demo/fertilizers` | 肥料DB（27種） |
| GET | `/v1/demo/fertilizer?crop=rice` | 肥料アドバイス |
| GET | `/v1/demo/fertilizer/standards` | 作物別施肥基準 |
| GET | `/v1/demo/adaptation` | グローバル作物→日本適応分析 |
| GET | `/v1/demo/regions` | サンプル地点（日本8 + 海外6） |
| GET | `/docs` | Swagger UI（インタラクティブAPI仕様書） |

## データソース

| データ | ソース | 認証 |
|--------|--------|------|
| 土壌分類 | 農研機構 日本土壌インベントリー | 不要 |
| 気候データ | Open-Meteo Historical Forecast（5km解像度） | 不要 |
| リアルタイム気象 | 気象庁 AMeDAS（1,286地点） | 不要 |
| 標高 | 国土地理院 DEM（日本）/ Copernicus DEM（海外） | 不要 |
| 河川・洪水 | 国土数値情報（国土交通省） | 不要 |
| 作物統計 | 農水省 e-Stat API | appId |
| 世界生産 | FAO FAOSTAT 2022（内蔵スナップショット） | 不要 |

## プロジェクト構成

```
farmscore/
├── map.html                          # マップUI（Leaflet.js）
├── backend/
│   ├── run_local.py                  # APIサーバー（これだけで動く）
│   ├── requirements-local.txt        # 軽量依存（3パッケージ）
│   └── app/services/
│       ├── scoring_engine.py         # 5軸統合スコアリング
│       ├── soil_analyzer.py          # 土壌分析
│       ├── climate_analyzer.py       # 気候分析（Open-Meteo連携）
│       ├── water_analyzer.py         # 水利分析
│       ├── sunlight_analyzer.py      # 日照分析
│       ├── crop_recommender.py       # 作物推薦（137種）
│       ├── fertilizer_advisor.py     # 肥料アドバイザー（27種）
│       ├── japan_adaptation.py       # 海外作物→日本適応分析
│       ├── global_data.py            # グローバル対応（23カ国）
│       ├── jma_amedas.py             # 気象庁AMeDASリアルタイム
│       ├── estat_client.py           # 農水省e-Stat連携
│       └── open_meteo.py             # Open-Meteo気候API
└── .github/workflows/deploy.yml      # GitHub Pages自動デプロイ
```

## 必要な環境

- Python 3.10+
- インターネット接続（外部API呼び出し）

DB不要・Docker不要。`python3 run_local.py` だけで完結します。

## License

MIT
