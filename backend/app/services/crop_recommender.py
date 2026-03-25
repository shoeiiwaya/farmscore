"""
Crop Recommendation Engine
===========================
Recommends optimal crops based on combined soil, climate, water, and sunlight analysis.
"""

from typing import Optional

# Comprehensive crop database for Japan
CROP_DATABASE = {
    "rice": {
        "name_ja": "水稲（コメ）",
        "season": "5月〜10月",
        "temp_range": (15, 30),
        "precip_min": 1000,
        "sunshine_min": 1200,
        "soil_pref": ["gley", "lowland_gray", "alluvial"],
        "category": "穀物",
    },
    "tomato": {
        "name_ja": "トマト",
        "season": "4月〜9月（露地）/ 通年（施設）",
        "temp_range": (15, 30),
        "precip_min": 600,
        "sunshine_min": 1500,
        "soil_pref": ["andosol", "lowland_brown", "forest_brown"],
        "category": "果菜類",
    },
    "strawberry": {
        "name_ja": "イチゴ",
        "season": "12月〜5月（施設）",
        "temp_range": (10, 25),
        "precip_min": 800,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown"],
        "category": "果菜類",
    },
    "cabbage": {
        "name_ja": "キャベツ",
        "season": "通年（品種により）",
        "temp_range": (5, 25),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_gray", "lowland_brown"],
        "category": "葉菜類",
    },
    "sweet_potato": {
        "name_ja": "サツマイモ",
        "season": "5月〜11月",
        "temp_range": (18, 35),
        "precip_min": 800,
        "sunshine_min": 1300,
        "soil_pref": ["sand_dune", "lowland_brown", "red"],
        "category": "根菜類",
    },
    "grape": {
        "name_ja": "ブドウ",
        "season": "7月〜10月",
        "temp_range": (12, 30),
        "precip_min": 500,
        "sunshine_min": 1600,
        "soil_pref": ["forest_brown", "lowland_brown"],
        "category": "果樹",
    },
    "tea": {
        "name_ja": "茶",
        "season": "4月〜10月（収穫）",
        "temp_range": (12, 28),
        "precip_min": 1300,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "red", "forest_brown"],
        "category": "工芸作物",
    },
    "soybean": {
        "name_ja": "大豆",
        "season": "6月〜11月",
        "temp_range": (15, 30),
        "precip_min": 500,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "lowland_gray", "lowland_brown"],
        "category": "豆類",
    },
    "wheat": {
        "name_ja": "小麦",
        "season": "11月〜6月",
        "temp_range": (3, 25),
        "precip_min": 400,
        "sunshine_min": 1200,
        "soil_pref": ["lowland_brown", "lowland_gray", "andosol"],
        "category": "穀物",
    },
    "onion": {
        "name_ja": "タマネギ",
        "season": "9月〜翌6月",
        "temp_range": (5, 25),
        "precip_min": 600,
        "sunshine_min": 1300,
        "soil_pref": ["alluvial", "lowland_brown", "andosol"],
        "category": "根菜類",
    },
    "spinach": {
        "name_ja": "ホウレンソウ",
        "season": "通年（品種により）",
        "temp_range": (5, 20),
        "precip_min": 500,
        "sunshine_min": 1000,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "葉菜類",
    },
    "cucumber": {
        "name_ja": "キュウリ",
        "season": "5月〜9月",
        "temp_range": (18, 30),
        "precip_min": 800,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "果菜類",
    },
    "eggplant": {
        "name_ja": "ナス",
        "season": "5月〜10月",
        "temp_range": (18, 32),
        "precip_min": 800,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "lowland_gray"],
        "category": "果菜類",
    },
    "blueberry": {
        "name_ja": "ブルーベリー",
        "season": "6月〜9月",
        "temp_range": (10, 28),
        "precip_min": 800,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "peat", "forest_brown"],
        "category": "果樹",
    },
    # ── 果樹（追加） ─────────────────────────
    "apple": {
        "name_ja": "リンゴ",
        "season": "9月〜11月",
        "temp_range": (7, 22),
        "precip_min": 800,
        "sunshine_min": 1500,
        "soil_pref": ["forest_brown", "andosol", "lowland_brown"],
        "category": "果樹",
    },
    "peach": {
        "name_ja": "モモ",
        "season": "7月〜9月",
        "temp_range": (12, 28),
        "precip_min": 800,
        "sunshine_min": 1600,
        "soil_pref": ["forest_brown", "lowland_brown", "andosol"],
        "category": "果樹",
    },
    "pear": {
        "name_ja": "ナシ",
        "season": "8月〜10月",
        "temp_range": (10, 28),
        "precip_min": 1000,
        "sunshine_min": 1400,
        "soil_pref": ["lowland_brown", "alluvial", "andosol"],
        "category": "果樹",
    },
    "persimmon": {
        "name_ja": "カキ",
        "season": "10月〜12月",
        "temp_range": (12, 30),
        "precip_min": 1000,
        "sunshine_min": 1300,
        "soil_pref": ["lowland_brown", "forest_brown", "alluvial"],
        "category": "果樹",
    },
    "mandarin": {
        "name_ja": "ミカン（温州）",
        "season": "10月〜1月",
        "temp_range": (15, 30),
        "precip_min": 1200,
        "sunshine_min": 1600,
        "soil_pref": ["red", "forest_brown", "lowland_brown"],
        "category": "果樹",
    },
    "cherry": {
        "name_ja": "サクランボ",
        "season": "6月〜7月",
        "temp_range": (8, 24),
        "precip_min": 800,
        "sunshine_min": 1500,
        "soil_pref": ["forest_brown", "andosol", "lowland_brown"],
        "category": "果樹",
    },
    "plum": {
        "name_ja": "ウメ",
        "season": "6月",
        "temp_range": (10, 28),
        "precip_min": 1000,
        "sunshine_min": 1300,
        "soil_pref": ["forest_brown", "lowland_brown", "andosol"],
        "category": "果樹",
    },
    "kiwi": {
        "name_ja": "キウイフルーツ",
        "season": "10月〜12月",
        "temp_range": (12, 28),
        "precip_min": 1200,
        "sunshine_min": 1400,
        "soil_pref": ["alluvial", "lowland_brown", "andosol"],
        "category": "果樹",
    },
    "fig": {
        "name_ja": "イチジク",
        "season": "8月〜10月",
        "temp_range": (14, 32),
        "precip_min": 800,
        "sunshine_min": 1500,
        "soil_pref": ["alluvial", "lowland_brown", "forest_brown"],
        "category": "果樹",
    },
    "melon": {
        "name_ja": "メロン",
        "season": "6月〜8月",
        "temp_range": (18, 32),
        "precip_min": 500,
        "sunshine_min": 1600,
        "soil_pref": ["sand_dune", "alluvial", "lowland_brown"],
        "category": "果菜類",
    },
    "watermelon": {
        "name_ja": "スイカ",
        "season": "7月〜8月",
        "temp_range": (20, 35),
        "precip_min": 500,
        "sunshine_min": 1500,
        "soil_pref": ["sand_dune", "alluvial", "lowland_brown"],
        "category": "果菜類",
    },
    "mango": {
        "name_ja": "マンゴー",
        "season": "6月〜8月",
        "temp_range": (22, 35),
        "precip_min": 1000,
        "sunshine_min": 1600,
        "soil_pref": ["red", "alluvial", "lowland_brown"],
        "category": "果樹",
    },
    # ── 野菜（追加） ─────────────────────────
    "daikon": {
        "name_ja": "ダイコン",
        "season": "通年（品種により）",
        "temp_range": (5, 25),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "根菜類",
    },
    "carrot": {
        "name_ja": "ニンジン",
        "season": "通年（品種により）",
        "temp_range": (8, 25),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "根菜類",
    },
    "potato": {
        "name_ja": "ジャガイモ",
        "season": "3月〜7月 / 8月〜12月",
        "temp_range": (10, 25),
        "precip_min": 500,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "forest_brown"],
        "category": "根菜類",
    },
    "taro": {
        "name_ja": "サトイモ",
        "season": "4月〜11月",
        "temp_range": (18, 32),
        "precip_min": 1200,
        "sunshine_min": 1200,
        "soil_pref": ["gley", "alluvial", "lowland_gray"],
        "category": "根菜類",
    },
    "burdock": {
        "name_ja": "ゴボウ",
        "season": "3月〜12月",
        "temp_range": (10, 25),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "根菜類",
    },
    "green_pepper": {
        "name_ja": "ピーマン",
        "season": "5月〜10月",
        "temp_range": (18, 32),
        "precip_min": 800,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "果菜類",
    },
    "pumpkin": {
        "name_ja": "カボチャ",
        "season": "5月〜9月",
        "temp_range": (15, 30),
        "precip_min": 600,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "lowland_brown", "forest_brown"],
        "category": "果菜類",
    },
    "zucchini": {
        "name_ja": "ズッキーニ",
        "season": "5月〜8月",
        "temp_range": (15, 28),
        "precip_min": 600,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "果菜類",
    },
    "okra": {
        "name_ja": "オクラ",
        "season": "6月〜9月",
        "temp_range": (20, 35),
        "precip_min": 800,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "果菜類",
    },
    "corn": {
        "name_ja": "トウモロコシ",
        "season": "5月〜9月",
        "temp_range": (15, 30),
        "precip_min": 600,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "穀物",
    },
    "edamame": {
        "name_ja": "枝豆",
        "season": "5月〜9月",
        "temp_range": (15, 30),
        "precip_min": 500,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "lowland_gray", "lowland_brown"],
        "category": "豆類",
    },
    "green_onion": {
        "name_ja": "ネギ",
        "season": "通年",
        "temp_range": (5, 28),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["alluvial", "lowland_brown", "andosol"],
        "category": "葉菜類",
    },
    "chinese_cabbage": {
        "name_ja": "ハクサイ",
        "season": "8月〜翌2月",
        "temp_range": (5, 22),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "葉菜類",
    },
    "broccoli": {
        "name_ja": "ブロッコリー",
        "season": "通年（品種により）",
        "temp_range": (8, 22),
        "precip_min": 600,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "lowland_gray"],
        "category": "葉菜類",
    },
    "asparagus": {
        "name_ja": "アスパラガス",
        "season": "4月〜6月",
        "temp_range": (10, 28),
        "precip_min": 600,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "葉菜類",
    },
    "garlic": {
        "name_ja": "ニンニク",
        "season": "9月〜翌6月",
        "temp_range": (5, 22),
        "precip_min": 500,
        "sunshine_min": 1300,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "根菜類",
    },
    "ginger": {
        "name_ja": "ショウガ",
        "season": "4月〜10月",
        "temp_range": (18, 30),
        "precip_min": 1200,
        "sunshine_min": 1000,
        "soil_pref": ["alluvial", "lowland_brown", "gley"],
        "category": "根菜類",
    },
    "wasabi": {
        "name_ja": "ワサビ",
        "season": "通年（収穫2年目〜）",
        "temp_range": (8, 18),
        "precip_min": 2000,
        "sunshine_min": 800,
        "soil_pref": ["gley", "alluvial", "peat"],
        "category": "根菜類",
    },
    "myoga": {
        "name_ja": "ミョウガ",
        "season": "7月〜10月",
        "temp_range": (15, 28),
        "precip_min": 1200,
        "sunshine_min": 800,
        "soil_pref": ["alluvial", "gley", "lowland_gray"],
        "category": "根菜類",
    },
    "shiso": {
        "name_ja": "シソ（大葉）",
        "season": "6月〜10月",
        "temp_range": (18, 30),
        "precip_min": 800,
        "sunshine_min": 1000,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "葉菜類",
    },
    # ── 花卉・工芸作物 ───────────────────────
    "chrysanthemum": {
        "name_ja": "キク（花卉）",
        "season": "9月〜11月",
        "temp_range": (12, 25),
        "precip_min": 800,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "花卉",
    },
    "carnation": {
        "name_ja": "カーネーション",
        "season": "4月〜6月",
        "temp_range": (10, 22),
        "precip_min": 600,
        "sunshine_min": 1500,
        "soil_pref": ["andosol", "lowland_brown"],
        "category": "花卉",
    },
    "rose": {
        "name_ja": "バラ",
        "season": "5月〜11月",
        "temp_range": (12, 28),
        "precip_min": 800,
        "sunshine_min": 1500,
        "soil_pref": ["andosol", "lowland_brown", "forest_brown"],
        "category": "花卉",
    },
    "sugarcane": {
        "name_ja": "サトウキビ",
        "season": "2月〜翌1月",
        "temp_range": (22, 35),
        "precip_min": 1500,
        "sunshine_min": 1600,
        "soil_pref": ["red", "alluvial", "lowland_brown"],
        "category": "工芸作物",
    },
    "hop": {
        "name_ja": "ホップ",
        "season": "3月〜9月",
        "temp_range": (8, 22),
        "precip_min": 800,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "forest_brown", "lowland_brown"],
        "category": "工芸作物",
    },
    "buckwheat": {
        "name_ja": "ソバ",
        "season": "7月〜10月（夏）/ 8月〜11月（秋）",
        "temp_range": (10, 25),
        "precip_min": 400,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "forest_brown", "lowland_brown"],
        "category": "穀物",
    },
    # ── 牧草・飼料 ───────────────────────────
    "timothy": {
        "name_ja": "チモシー（牧草）",
        "season": "通年",
        "temp_range": (5, 22),
        "precip_min": 800,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "forest_brown", "lowland_brown"],
        "category": "飼料作物",
    },
    "feed_corn": {
        "name_ja": "デントコーン（飼料用）",
        "season": "5月〜10月",
        "temp_range": (15, 30),
        "precip_min": 600,
        "sunshine_min": 1400,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "飼料作物",
    },
    "lettuce": {
        "name_ja": "レタス",
        "season": "通年（高冷地夏秋）",
        "temp_range": (5, 22),
        "precip_min": 500,
        "sunshine_min": 1200,
        "soil_pref": ["andosol", "lowland_brown", "alluvial"],
        "category": "葉菜類",
    },
}


def score_crop(
    crop_key: str,
    crop_info: dict,
    soil_group: str,
    temp: float,
    precip: float,
    sunshine: float,
) -> float:
    """Score a crop's suitability for given conditions (0-100)."""
    score = 50.0  # base

    # Soil affinity
    if soil_group in crop_info["soil_pref"]:
        idx = crop_info["soil_pref"].index(soil_group)
        score += 20 - idx * 5  # first pref = +20, second = +15, etc.
    else:
        score -= 10

    # Temperature fit
    t_min, t_max = crop_info["temp_range"]
    if t_min <= temp <= t_max:
        # Closer to midpoint = better
        mid = (t_min + t_max) / 2
        score += max(0, 15 - abs(temp - mid) * 1.5)
    elif temp < t_min:
        score -= (t_min - temp) * 3
    else:
        score -= (temp - t_max) * 3

    # Precipitation
    if precip >= crop_info["precip_min"]:
        score += 10
    else:
        score -= (crop_info["precip_min"] - precip) * 0.01

    # Sunshine
    if sunshine >= crop_info["sunshine_min"]:
        score += 10
    else:
        score -= (crop_info["sunshine_min"] - sunshine) * 0.005

    return max(0, min(100, round(score, 1)))


def get_yield_estimate(score: float) -> str:
    """Relative yield estimate based on suitability score."""
    if score >= 80:
        return "高収量が期待できる"
    if score >= 65:
        return "標準的な収量が期待できる"
    if score >= 50:
        return "条件付きで栽培可能"
    if score >= 35:
        return "収量は限定的"
    return "栽培は困難"


def recommend_crops(
    soil_group: str,
    temp: float,
    precip: float,
    sunshine: float,
    target_crop: Optional[str] = None,
    top_n: int = 5,
) -> list[dict]:
    """Recommend top crops for given conditions."""
    scored = []

    for key, info in CROP_DATABASE.items():
        s = score_crop(key, info, soil_group, temp, precip, sunshine)
        scored.append({
            "crop_name": f"{info['name_ja']}（{key}）",
            "suitability_score": s,
            "reason": _build_reason(key, info, soil_group, temp, precip),
            "expected_yield_relative": get_yield_estimate(s),
            "growing_season": info["season"],
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["suitability_score"], reverse=True)

    # If target crop specified, make sure it's included
    if target_crop:
        target_in_list = any(target_crop in c["crop_name"] for c in scored[:top_n])
        if not target_in_list:
            for c in scored:
                if target_crop in c["crop_name"]:
                    scored = [c] + [x for x in scored if x != c]
                    break

    return scored[:top_n]


def _build_reason(
    crop_key: str,
    crop_info: dict,
    soil_group: str,
    temp: float,
    precip: float,
) -> str:
    """Build human-readable reason for recommendation."""
    reasons = []

    if soil_group in crop_info["soil_pref"]:
        reasons.append(f"土壌タイプ（{soil_group}）が適している")
    else:
        reasons.append(f"土壌タイプ（{soil_group}）はやや不適")

    t_min, t_max = crop_info["temp_range"]
    if t_min <= temp <= t_max:
        reasons.append(f"気温{temp}°Cは適温範囲内")
    elif temp < t_min:
        reasons.append(f"気温{temp}°Cは下限{t_min}°Cを下回る")
    else:
        reasons.append(f"気温{temp}°Cは上限{t_max}°Cを上回る")

    if precip >= crop_info["precip_min"]:
        reasons.append("降水量は十分")
    else:
        reasons.append(f"降水量が不足（{precip}mm < 必要{crop_info['precip_min']}mm）")

    return "。".join(reasons)
