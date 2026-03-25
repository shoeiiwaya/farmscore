"""
Admin API — 管理・情報エンドポイント
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/admin/attribution", tags=["admin"])
def attribution():
    """データソース帰属表示"""
    return {
        "data_sources": [
            {
                "name": "農研機構 日本土壌インベントリー (eSoil)",
                "url": "https://soil-inventory.rad.naro.go.jp/",
                "license": "CC BY 4.0",
                "usage": "土壌タイプ・土壌特性分析",
            },
            {
                "name": "気象庁 メッシュ平年値",
                "url": "https://www.data.jma.go.jp/",
                "license": "政府標準利用規約 2.0",
                "usage": "気温・降水量・日照時間の気候分析",
            },
            {
                "name": "国土交通省 国土数値情報",
                "url": "https://nlftp.mlit.go.jp/ksj/",
                "license": "政府標準利用規約 2.0",
                "usage": "河川・洪水浸水想定区域・土地利用",
            },
            {
                "name": "国土地理院 標高API (DEM)",
                "url": "https://maps.gsi.go.jp/development/",
                "license": "政府標準利用規約 2.0",
                "usage": "標高・傾斜・方位分析",
            },
            {
                "name": "JAXA ALOS 全球数値地表モデル",
                "url": "https://www.eorc.jaxa.jp/ALOS/a/jp/",
                "license": "JAXA利用規約",
                "usage": "高解像度地形分析（将来実装）",
            },
            {
                "name": "農林水産省 農林業センサス",
                "url": "https://www.maff.go.jp/j/tokei/census/",
                "license": "政府標準利用規約 2.0",
                "usage": "農業統計・耕作放棄地データ",
            },
        ],
        "disclaimer": "本サービスは参考情報を提供するものであり、農業判断の結果について一切の責任を負いません。",
    }


@router.get("/admin/plans", tags=["admin"])
def plans():
    """利用プラン一覧"""
    return [
        {
            "name": "Free",
            "price_monthly": 0,
            "api_calls": 100,
            "fields": 3,
            "sensors": 5,
            "features": ["農地適性スコア", "作物推薦", "基本ダッシュボード"],
        },
        {
            "name": "Starter",
            "price_monthly": 5000,
            "api_calls": 1000,
            "fields": 10,
            "sensors": 20,
            "features": ["Free全機能", "リアルタイムアラート", "データエクスポート", "APIアクセス"],
        },
        {
            "name": "Pro",
            "price_monthly": 20000,
            "api_calls": 5000,
            "fields": 50,
            "sensors": 100,
            "features": ["Starter全機能", "集計分析", "カスタムアラート", "優先サポート"],
        },
        {
            "name": "Enterprise",
            "price_monthly": "要見積",
            "api_calls": "無制限",
            "fields": "無制限",
            "sensors": "無制限",
            "features": ["Pro全機能", "SLA保証", "専用サポート", "カスタム開発", "オンプレミス対応"],
        },
    ]
