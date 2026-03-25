"""
Global Crop → Japan Adaptation Analyzer
=========================================
Evaluates which international crops could potentially be cultivated in Japan,
considering Japan's diverse climate zones from Okinawa (subtropical) to Hokkaido (subarctic).

Based on:
- Japan's climate zones (6 regions with distinct conditions)
- Global crop requirements (temperature, precipitation, sunshine)
- Existing cultivation attempts and successes in Japan
"""

from typing import Optional
from app.services.global_data import GLOBAL_CROPS_EXTRA
from app.services.crop_recommender import CROP_DATABASE

# ── 日本の気候帯データ ──────────────────────────────────────

JAPAN_CLIMATE_ZONES = {
    "okinawa": {
        "name": "沖縄・奄美",
        "type": "亜熱帯",
        "temp_avg": 23.1,
        "temp_min": 16.0,
        "temp_max": 29.5,
        "precip_mm": 2040,
        "sunshine_h": 1720,
        "frost_free": 365,
        "lat_range": (24.0, 28.0),
        "examples": "那覇、石垣島、奄美大島",
    },
    "kyushu_south": {
        "name": "南九州・四国南部",
        "type": "暖温帯（温暖）",
        "temp_avg": 17.5,
        "temp_min": 6.0,
        "temp_max": 28.5,
        "precip_mm": 2300,
        "sunshine_h": 1900,
        "frost_free": 300,
        "lat_range": (31.0, 33.5),
        "examples": "鹿児島、宮崎、高知",
    },
    "seto_inland": {
        "name": "瀬戸内・関東南部",
        "type": "暖温帯（温暖乾燥）",
        "temp_avg": 16.0,
        "temp_min": 4.0,
        "temp_max": 28.0,
        "precip_mm": 1200,
        "sunshine_h": 2100,
        "frost_free": 270,
        "lat_range": (33.5, 36.0),
        "examples": "岡山、香川、東京、横浜",
    },
    "tohoku_south": {
        "name": "東北南部・北関東",
        "type": "冷温帯（温和）",
        "temp_avg": 13.0,
        "temp_min": 0.5,
        "temp_max": 26.0,
        "precip_mm": 1400,
        "sunshine_h": 1800,
        "frost_free": 220,
        "lat_range": (36.0, 39.0),
        "examples": "仙台、福島、宇都宮",
    },
    "tohoku_north": {
        "name": "東北北部",
        "type": "冷温帯（寒冷）",
        "temp_avg": 10.5,
        "temp_min": -2.0,
        "temp_max": 25.0,
        "precip_mm": 1300,
        "sunshine_h": 1600,
        "frost_free": 190,
        "lat_range": (39.0, 41.5),
        "examples": "青森、秋田、盛岡",
    },
    "hokkaido": {
        "name": "北海道",
        "type": "亜寒帯",
        "temp_avg": 8.5,
        "temp_min": -5.0,
        "temp_max": 23.0,
        "precip_mm": 1100,
        "sunshine_h": 1700,
        "frost_free": 160,
        "lat_range": (41.5, 45.5),
        "examples": "札幌、旭川、帯広",
    },
}


# ── 日本での栽培実績・試験情報 ──────────────────────────────

JAPAN_CULTIVATION_RECORDS = {
    "coffee": {
        "status": "試験栽培・小規模商業化",
        "locations": ["沖縄（やんばる）", "鹿児島（徳之島）", "小笠原諸島"],
        "brand": "沖縄コーヒー、徳之島コーヒー",
        "challenge": "台風被害、収穫量が少ない、コスト高",
        "potential": "high",
        "note": "沖縄で既に商業栽培開始。温暖化で適地拡大の可能性",
    },
    "cacao": {
        "status": "実験栽培",
        "locations": ["沖縄（北部）"],
        "brand": "OKINAWAカカオ（試験段階）",
        "challenge": "最低温度がギリギリ、収量が極めて少ない",
        "potential": "low",
        "note": "温室栽培なら可能だが露地は困難。沖縄でも冬の低温がネック",
    },
    "cassava": {
        "status": "研究栽培",
        "locations": ["沖縄", "鹿児島"],
        "brand": "",
        "challenge": "食文化に馴染みが薄い、加工施設不足",
        "potential": "medium",
        "note": "タピオカ需要で注目。沖縄・南九州で栽培可能",
    },
    "teff": {
        "status": "未栽培（適応可能性あり）",
        "locations": [],
        "brand": "",
        "challenge": "種子入手困難、栽培ノウハウ不足",
        "potential": "high",
        "note": "温度要件（12-27°C）は日本の多くの地域で合致。グルテンフリー需要で市場性あり",
    },
    "quinoa_global": {
        "status": "試験栽培",
        "locations": ["長野", "北海道", "岩手"],
        "brand": "信州キヌア",
        "challenge": "機械化困難、収量が低い",
        "potential": "high",
        "note": "冷涼地で栽培成功例あり。スーパーフード需要で価格が高く採算性に期待",
    },
    "chickpea": {
        "status": "ほぼ未栽培",
        "locations": [],
        "brand": "",
        "challenge": "多湿気候が不適、病害発生",
        "potential": "medium",
        "note": "温度は合うが日本の梅雨・多湿が課題。施設栽培なら可能性あり",
    },
    "lentil": {
        "status": "試験栽培あり",
        "locations": ["北海道"],
        "brand": "",
        "challenge": "湿度耐性が低い、収量不安定",
        "potential": "medium",
        "note": "北海道の冷涼・乾燥気候なら栽培可能。植物性タンパク質需要で注目",
    },
    "durian": {
        "status": "温室実験のみ",
        "locations": ["沖縄（温室）"],
        "brand": "",
        "challenge": "最低温度24°Cが日本では確保困難",
        "potential": "very_low",
        "note": "露地栽培は日本では不可能。加温温室なら理論上可能だがコスト見合わず",
    },
    "coconut": {
        "status": "観賞用のみ",
        "locations": ["沖縄（景観用）"],
        "brand": "",
        "challenge": "結実まで至らないケースが多い",
        "potential": "very_low",
        "note": "沖縄でも結実は安定しない。商業栽培は不可能",
    },
    "date_palm": {
        "status": "未栽培",
        "locations": [],
        "brand": "",
        "challenge": "年間日照2500h以上が必要、日本の多湿不適",
        "potential": "very_low",
        "note": "日本の湿潤気候とは正反対の環境を好む。栽培不可能",
    },
    "rubber": {
        "status": "研究のみ",
        "locations": [],
        "brand": "",
        "challenge": "通年22°C以上が必要、台風リスク",
        "potential": "very_low",
        "note": "日本の気候では商業栽培不可能",
    },
    "palm_oil": {
        "status": "未栽培",
        "locations": [],
        "brand": "",
        "challenge": "通年24°C以上が必要",
        "potential": "very_low",
        "note": "日本の気候では栽培不可能",
    },
    "sorghum_global": {
        "status": "飼料用栽培あり",
        "locations": ["九州", "関東", "東海"],
        "brand": "",
        "challenge": "食用利用の文化がない",
        "potential": "high",
        "note": "飼料用ソルガムは既に栽培実績あり。グルテンフリー穀物としての食用展開に期待",
    },
}


def analyze_japan_adaptation() -> dict:
    """
    Analyze which global crops could be adapted for cultivation in Japan.
    Returns feasibility assessment for each crop across Japan's climate zones.
    """
    results = []

    for crop_key, crop_data in GLOBAL_CROPS_EXTRA.items():
        temp_min, temp_max = crop_data["temp_range"]
        precip_min = crop_data["precip_min"]
        sunshine_min = crop_data["sunshine_min"]

        # Check each Japanese climate zone
        zone_results = []
        for zone_key, zone in JAPAN_CLIMATE_ZONES.items():
            temp_ok = zone["temp_min"] >= temp_min - 5 and zone["temp_avg"] >= temp_min
            precip_ok = zone["precip_mm"] >= precip_min
            sun_ok = zone["sunshine_h"] >= sunshine_min

            score = 0
            if temp_ok:
                score += 40
            elif zone["temp_avg"] >= temp_min - 3:
                score += 20  # Marginal
            if precip_ok:
                score += 30
            elif zone["precip_mm"] >= precip_min * 0.7:
                score += 15
            if sun_ok:
                score += 30
            elif zone["sunshine_h"] >= sunshine_min * 0.8:
                score += 15

            if score >= 50:
                zone_results.append({
                    "zone": zone_key,
                    "zone_name": zone["name"],
                    "zone_type": zone["type"],
                    "feasibility_score": score,
                    "temp_match": "適合" if temp_ok else "不適" if zone["temp_avg"] < temp_min - 3 else "やや不適",
                    "precip_match": "適合" if precip_ok else "不足",
                    "sunshine_match": "適合" if sun_ok else "不足",
                    "examples": zone["examples"],
                })

        zone_results.sort(key=lambda x: x["feasibility_score"], reverse=True)

        # Get cultivation records if available
        record = JAPAN_CULTIVATION_RECORDS.get(crop_key, {})

        # Overall adaptation rating
        best_score = zone_results[0]["feasibility_score"] if zone_results else 0
        if record.get("potential") == "very_low":
            adaptation = "不可能"
        elif best_score >= 80:
            adaptation = "有望"
        elif best_score >= 60:
            adaptation = "条件付き可能"
        elif best_score >= 40:
            adaptation = "困難"
        else:
            adaptation = "不可能"

        results.append({
            "crop_key": crop_key,
            "crop_name_ja": crop_data["name_ja"],
            "crop_name_en": crop_data["name_en"],
            "category": crop_data["category"],
            "requirements": {
                "temp_range": f"{temp_min}-{temp_max}°C",
                "precip_min_mm": precip_min,
                "sunshine_min_h": sunshine_min,
            },
            "adaptation_rating": adaptation,
            "potential": record.get("potential", "unknown"),
            "best_zones": zone_results[:3],
            "cultivation_record": {
                "status": record.get("status", "情報なし"),
                "locations": record.get("locations", []),
                "brand": record.get("brand", ""),
                "challenge": record.get("challenge", ""),
                "note": record.get("note", ""),
            } if record else None,
        })

    # Sort: promising ones first
    potential_order = {"high": 0, "medium": 1, "low": 2, "very_low": 3, "unknown": 4}
    results.sort(key=lambda x: potential_order.get(x["potential"], 4))

    # Summary stats
    promising = [r for r in results if r["potential"] in ("high", "medium")]
    impossible = [r for r in results if r["adaptation_rating"] == "不可能"]

    return {
        "total_global_crops": len(GLOBAL_CROPS_EXTRA),
        "total_japan_crops": len(CROP_DATABASE),
        "combined_total": len(CROP_DATABASE) + len(GLOBAL_CROPS_EXTRA),
        "adaptation_summary": {
            "promising": len([r for r in results if r["potential"] == "high"]),
            "conditional": len([r for r in results if r["potential"] == "medium"]),
            "difficult": len([r for r in results if r["potential"] == "low"]),
            "impossible": len([r for r in results if r["potential"] == "very_low"]),
        },
        "key_findings": [
            "コーヒー: 沖縄で既に商業栽培開始。温暖化で九州南部にも拡大可能性",
            "キヌア: 長野・北海道で試験栽培成功。スーパーフード需要で高付加価値",
            "テフ: 日本未栽培だが気候条件は適合。グルテンフリー市場で有望",
            "ソルガム: 飼料用は栽培実績あり。食用グルテンフリー穀物として展開可能",
            "レンズマメ・ヒヨコマメ: 植物性タンパク質需要で注目。北海道で可能性",
            "ドリアン・ココナッツ・ナツメヤシ: 日本の気候では商業栽培不可能",
        ],
        "market_opportunity": {
            "health_foods": ["teff", "quinoa_global", "chickpea", "lentil"],
            "tropical_premium": ["coffee", "cacao"],
            "animal_feed_alternative": ["sorghum_global", "cassava"],
        },
        "crops": results,
    }


def get_crop_adaptation_detail(crop_key: str) -> Optional[dict]:
    """Get detailed adaptation analysis for a specific global crop."""
    full = analyze_japan_adaptation()
    for crop in full["crops"]:
        if crop["crop_key"] == crop_key:
            return crop
    return None
