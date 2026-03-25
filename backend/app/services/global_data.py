"""
Global Agricultural Data Service
==================================
Enables FarmScore to work anywhere in the world.

- Global elevation via Open-Meteo (Copernicus DEM)
- Global soil estimation from latitude/climate/elevation
- FAO crop production data (top producing countries, built-in)
- Country detection from coordinates

Data sources:
- Open-Meteo: Global elevation + climate (free, no auth)
- FAO FAOSTAT: Crop production statistics (built-in snapshot)
- USDA Hardiness Zones: Plant hardiness mapping
"""

import math
from typing import Optional

import httpx

# ── Country detection from coordinates ──────────────────────

# Simplified country bounding boxes (lat_min, lat_max, lon_min, lon_max, name, code)
COUNTRY_BOXES = [
    # More specific countries FIRST (smaller boxes before larger overlapping ones)
    (20.0, 46.0, 122.0, 154.0, "日本", "JPN"),
    (33.0, 43.8, 124.5, 131.0, "韓国", "KOR"),
    (5.5, 20.5, 97.3, 106.0, "タイ", "THA"),
    (8.0, 23.5, 102.1, 109.5, "ベトナム", "VNM"),
    (4.5, 21.0, 116.5, 127.0, "フィリピン", "PHL"),
    (1.0, 7.5, 100.0, 119.5, "マレーシア", "MYS"),
    (-11.0, 6.0, 95.0, 141.5, "インドネシア", "IDN"),
    (9.0, 28.5, 92.0, 101.2, "ミャンマー", "MMR"),
    (14.5, 32.7, -118.5, -86.5, "メキシコ", "MEX"),
    (32.0, 42.0, 25.0, 45.0, "トルコ", "TUR"),
    (-43.6, -34.0, 166.4, 178.5, "ニュージーランド", "NZL"),
    (-44.0, -10.0, 112.0, 154.0, "オーストラリア", "AUS"),
    (8.0, 37.0, 68.0, 97.5, "インド", "IND"),
    (18.0, 53.5, 73.0, 135.0, "中国", "CHN"),
    (24.5, 49.5, -125.0, -66.5, "アメリカ", "USA"),
    (41.0, 83.5, -141.0, -52.5, "カナダ", "CAN"),
    (-33.8, 5.3, -73.9, -34.8, "ブラジル", "BRA"),
    (-56.0, 13.0, -82.0, -34.0, "南米", "SAM"),
    (36.0, 71.2, -10.5, 40.0, "ヨーロッパ", "EUR"),
    (41.0, 81.8, 19.6, 180.0, "ロシア", "RUS"),
    (25.0, 36.0, 44.0, 63.5, "中東", "MID"),
    (-35.0, 37.5, -20.0, 52.0, "アフリカ", "AFR"),
    (-10.7, 20.5, 95.0, 141.0, "東南アジア", "SEA"),
]


def detect_country(lat: float, lon: float) -> dict:
    """Detect country from coordinates."""
    for lat_min, lat_max, lon_min, lon_max, name, code in COUNTRY_BOXES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return {"name": name, "code": code}
    return {"name": "不明", "code": "UNK"}


# ── Global elevation ────────────────────────────────────────

async def get_global_elevation(lat: float, lon: float) -> float:
    """
    Get elevation for any point on Earth.
    Uses GSI for Japan, Open-Meteo (Copernicus DEM) for rest of world.
    """
    # Japan: use GSI for higher accuracy
    if 20.0 <= lat <= 46.0 and 122.0 <= lon <= 154.0:
        try:
            url = f"https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lat={lat}&lon={lon}&outtype=JSON"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                data = resp.json()
                elev = data.get("elevation")
                if elev and elev != "-----":
                    return float(elev)
        except Exception:
            pass

    # Global: use Open-Meteo (returns elevation in forecast response)
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            data = resp.json()
            elev = data.get("elevation")
            if elev is not None:
                return float(elev)
    except Exception:
        pass

    return 50.0  # fallback


# ── Global soil estimation ──────────────────────────────────

# Simplified global soil classification based on climate zone
GLOBAL_SOIL_TYPES = {
    "tropical_wet": {"name": "Oxisol（熱帯酸化土）", "group": "oxisol", "ph": "4.5-5.5", "drainage": "good", "organic": "medium", "base_score": 55},
    "tropical_dry": {"name": "Alfisol（半乾燥土）", "group": "alfisol", "ph": "6.0-7.5", "drainage": "moderate", "organic": "low", "base_score": 50},
    "subtropical": {"name": "Ultisol（亜熱帯土）", "group": "ultisol", "ph": "4.5-6.0", "drainage": "good", "organic": "medium", "base_score": 60},
    "temperate": {"name": "Mollisol（温帯草原土）", "group": "mollisol", "ph": "6.0-7.5", "drainage": "good", "organic": "high", "base_score": 80},
    "temperate_forest": {"name": "Alfisol（温帯森林土）", "group": "alfisol_forest", "ph": "5.5-7.0", "drainage": "good", "organic": "medium", "base_score": 70},
    "continental": {"name": "Mollisol（大陸性草原土）", "group": "mollisol", "ph": "6.5-8.0", "drainage": "good", "organic": "high", "base_score": 75},
    "mediterranean": {"name": "Alfisol（地中海性土）", "group": "alfisol_med", "ph": "6.5-8.0", "drainage": "good", "organic": "low", "base_score": 65},
    "arid": {"name": "Aridisol（乾燥土）", "group": "aridisol", "ph": "7.5-9.0", "drainage": "excessive", "organic": "very_low", "base_score": 30},
    "boreal": {"name": "Spodosol（寒帯酸性土）", "group": "spodosol", "ph": "4.0-5.5", "drainage": "poor", "organic": "high", "base_score": 40},
    "volcanic": {"name": "Andisol（火山灰土）", "group": "andisol", "ph": "5.5-6.5", "drainage": "good", "organic": "high", "base_score": 75},
    "alluvial": {"name": "Entisol（沖積土）", "group": "entisol", "ph": "5.5-7.5", "drainage": "moderate", "organic": "medium", "base_score": 70},
}


def estimate_global_soil(lat: float, lon: float, elevation: float, temp: float, precip: float) -> dict:
    """
    Estimate soil type from climate and location.
    More accurate than elevation-only for global use.
    """
    # Japan: use the existing detailed system
    if 20.0 <= lat <= 46.0 and 122.0 <= lon <= 154.0:
        return None  # Signal to use Japanese soil analyzer

    # Alluvial plains (low elevation, near coast/river)
    if elevation < 10:
        return GLOBAL_SOIL_TYPES["alluvial"]

    # Volcanic regions (known areas)
    volcanic_regions = [
        (35, 40, 127, 132),   # Korea/Japan
        (-8, 8, 105, 128),    # Indonesia
        (13, 20, -100, -95),  # Mexico
        (-45, -35, 170, 178), # NZ
        (37, 42, 14, 16),     # Italy
        (63, 66, -20, -14),   # Iceland
    ]
    for vlat_min, vlat_max, vlon_min, vlon_max in volcanic_regions:
        if vlat_min <= lat <= vlat_max and vlon_min <= lon <= vlon_max and elevation > 100:
            return GLOBAL_SOIL_TYPES["volcanic"]

    # Climate-based classification
    if temp >= 24 and precip >= 1500:
        return GLOBAL_SOIL_TYPES["tropical_wet"]
    if temp >= 22 and precip < 800:
        return GLOBAL_SOIL_TYPES["tropical_dry"]
    if temp >= 18 and precip >= 1000:
        return GLOBAL_SOIL_TYPES["subtropical"]
    if temp >= 10 and precip >= 600 and precip < 1200:
        if lat > 30 or lat < -30:
            return GLOBAL_SOIL_TYPES["temperate"]
        return GLOBAL_SOIL_TYPES["subtropical"]
    if temp >= 10 and precip >= 1200:
        return GLOBAL_SOIL_TYPES["temperate_forest"]
    if temp >= 5 and precip < 400:
        return GLOBAL_SOIL_TYPES["arid"]
    if temp >= 5 and precip >= 400:
        return GLOBAL_SOIL_TYPES["continental"]
    if temp >= -5:
        return GLOBAL_SOIL_TYPES["boreal"]
    return GLOBAL_SOIL_TYPES["arid"]


# ── FAO Crop Production Data (built-in snapshot) ────────────
# Top producing countries for major crops (2022 FAOSTAT data)
# Format: crop_key -> [(country_code, country_name, production_tonnes, area_ha)]

FAO_CROP_PRODUCTION = {
    "rice": [
        ("CHN", "中国", 208_490_000, 29_500_000),
        ("IND", "インド", 195_430_000, 46_400_000),
        ("IDN", "インドネシア", 54_750_000, 10_600_000),
        ("BGD", "バングラデシュ", 57_540_000, 11_800_000),
        ("VNM", "ベトナム", 42_660_000, 7_100_000),
        ("THA", "タイ", 33_500_000, 8_900_000),
        ("JPN", "日本", 7_560_000, 1_350_000),
        ("USA", "アメリカ", 8_100_000, 970_000),
    ],
    "wheat": [
        ("CHN", "中国", 137_720_000, 23_500_000),
        ("IND", "インド", 110_550_000, 31_300_000),
        ("RUS", "ロシア", 104_200_000, 29_200_000),
        ("USA", "アメリカ", 44_900_000, 14_600_000),
        ("CAN", "カナダ", 34_700_000, 10_600_000),
        ("FRA", "フランス", 35_600_000, 5_000_000),
        ("AUS", "オーストラリア", 36_600_000, 12_700_000),
    ],
    "corn": [
        ("USA", "アメリカ", 348_800_000, 32_400_000),
        ("CHN", "中国", 277_200_000, 43_100_000),
        ("BRA", "ブラジル", 109_400_000, 21_500_000),
        ("ARG", "アルゼンチン", 52_000_000, 9_500_000),
        ("IND", "インド", 35_900_000, 10_100_000),
    ],
    "soybean": [
        ("BRA", "ブラジル", 154_600_000, 43_200_000),
        ("USA", "アメリカ", 116_400_000, 33_800_000),
        ("ARG", "アルゼンチン", 43_900_000, 16_200_000),
        ("CHN", "中国", 20_280_000, 10_300_000),
        ("IND", "インド", 12_980_000, 12_500_000),
    ],
    "potato": [
        ("CHN", "中国", 94_360_000, 4_800_000),
        ("IND", "インド", 56_180_000, 2_200_000),
        ("USA", "アメリカ", 18_600_000, 380_000),
        ("RUS", "ロシア", 19_200_000, 1_100_000),
        ("DEU", "ドイツ", 11_300_000, 260_000),
    ],
    "tomato": [
        ("CHN", "中国", 68_250_000, 1_100_000),
        ("IND", "インド", 20_690_000, 812_000),
        ("TUR", "トルコ", 13_000_000, 183_000),
        ("USA", "アメリカ", 10_400_000, 110_000),
        ("ITA", "イタリア", 6_200_000, 95_000),
    ],
    "grape": [
        ("CHN", "中国", 15_330_000, 720_000),
        ("ITA", "イタリア", 8_200_000, 660_000),
        ("FRA", "フランス", 5_900_000, 790_000),
        ("USA", "アメリカ", 5_600_000, 370_000),
        ("ESP", "スペイン", 5_700_000, 930_000),
    ],
    "apple": [
        ("CHN", "中国", 47_600_000, 2_100_000),
        ("TUR", "トルコ", 4_800_000, 175_000),
        ("USA", "アメリカ", 4_600_000, 120_000),
        ("IND", "インド", 2_300_000, 295_000),
        ("POL", "ポーランド", 4_800_000, 165_000),
    ],
    "tea": [
        ("CHN", "中国", 3_350_000, 2_350_000),
        ("IND", "インド", 1_390_000, 640_000),
        ("KEN", "ケニア", 535_000, 270_000),
        ("LKA", "スリランカ", 256_000, 200_000),
        ("JPN", "日本", 69_800, 40_000),
    ],
    "coffee": [
        ("BRA", "ブラジル", 3_760_000, 2_100_000),
        ("VNM", "ベトナム", 1_920_000, 700_000),
        ("COL", "コロンビア", 744_000, 840_000),
        ("IDN", "インドネシア", 795_000, 1_260_000),
        ("ETH", "エチオピア", 540_000, 900_000),
    ],
    "sugarcane": [
        ("BRA", "ブラジル", 746_800_000, 8_100_000),
        ("IND", "インド", 431_800_000, 5_600_000),
        ("CHN", "中国", 106_600_000, 1_200_000),
        ("THA", "タイ", 92_300_000, 1_800_000),
    ],
    "banana": [
        ("IND", "インド", 34_500_000, 920_000),
        ("CHN", "中国", 11_600_000, 370_000),
        ("IDN", "インドネシア", 8_700_000, 110_000),
        ("BRA", "ブラジル", 6_700_000, 440_000),
        ("ECU", "エクアドル", 6_500_000, 170_000),
    ],
    "mango": [
        ("IND", "インド", 24_060_000, 2_300_000),
        ("CHN", "中国", 3_700_000, 350_000),
        ("IDN", "インドネシア", 3_600_000, 210_000),
        ("THA", "タイ", 3_400_000, 410_000),
        ("MEX", "メキシコ", 2_200_000, 220_000),
    ],
    "olive": [
        ("ESP", "スペイン", 8_100_000, 2_700_000),
        ("ITA", "イタリア", 2_700_000, 1_100_000),
        ("GRC", "ギリシャ", 2_300_000, 870_000),
        ("TUR", "トルコ", 1_800_000, 960_000),
        ("MAR", "モロッコ", 1_500_000, 1_100_000),
    ],
    "avocado": [
        ("MEX", "メキシコ", 2_520_000, 250_000),
        ("COL", "コロンビア", 980_000, 110_000),
        ("PER", "ペルー", 890_000, 55_000),
        ("IDN", "インドネシア", 630_000, 31_000),
        ("DOM", "ドミニカ", 610_000, 19_000),
    ],
}

# Global crop suitability parameters (extends Japanese CROP_DATABASE for non-Japanese crops)
GLOBAL_CROPS_EXTRA = {
    "coffee": {
        "name_ja": "コーヒー",
        "name_en": "Coffee",
        "season": "通年（熱帯高地）",
        "temp_range": (15, 28),
        "precip_min": 1200,
        "sunshine_min": 1400,
        "soil_pref": ["ultisol", "andisol", "oxisol"],
        "category": "工芸作物",
    },
    "cacao": {
        "name_ja": "カカオ",
        "name_en": "Cacao",
        "season": "通年（熱帯）",
        "temp_range": (20, 32),
        "precip_min": 1500,
        "sunshine_min": 1200,
        "soil_pref": ["oxisol", "ultisol", "entisol"],
        "category": "工芸作物",
    },
    "rubber": {
        "name_ja": "ゴム",
        "name_en": "Rubber",
        "season": "通年（熱帯）",
        "temp_range": (22, 35),
        "precip_min": 2000,
        "sunshine_min": 1400,
        "soil_pref": ["oxisol", "ultisol"],
        "category": "工芸作物",
    },
    "palm_oil": {
        "name_ja": "アブラヤシ",
        "name_en": "Oil Palm",
        "season": "通年（熱帯）",
        "temp_range": (24, 35),
        "precip_min": 1800,
        "sunshine_min": 1500,
        "soil_pref": ["oxisol", "ultisol", "entisol"],
        "category": "工芸作物",
    },
    "cassava": {
        "name_ja": "キャッサバ",
        "name_en": "Cassava",
        "season": "通年（熱帯・亜熱帯）",
        "temp_range": (20, 35),
        "precip_min": 1000,
        "sunshine_min": 1200,
        "soil_pref": ["oxisol", "ultisol", "alfisol"],
        "category": "根菜類",
    },
    "teff": {
        "name_ja": "テフ",
        "name_en": "Teff",
        "season": "7月〜11月",
        "temp_range": (12, 27),
        "precip_min": 450,
        "sunshine_min": 1400,
        "soil_pref": ["mollisol", "alfisol_forest"],
        "category": "穀物",
    },
    "quinoa_global": {
        "name_ja": "キヌア（南米）",
        "name_en": "Quinoa",
        "season": "9月〜4月（南半球）",
        "temp_range": (5, 20),
        "precip_min": 300,
        "sunshine_min": 1400,
        "soil_pref": ["mollisol", "aridisol", "alfisol"],
        "category": "穀物",
    },
    "sorghum_global": {
        "name_ja": "ソルガム（グローバル）",
        "name_en": "Sorghum",
        "season": "通年（熱帯）/ 5-10月（温帯）",
        "temp_range": (18, 40),
        "precip_min": 400,
        "sunshine_min": 1400,
        "soil_pref": ["mollisol", "alfisol", "aridisol"],
        "category": "穀物",
    },
    "chickpea": {
        "name_ja": "ヒヨコマメ",
        "name_en": "Chickpea",
        "season": "10月〜4月（冬作）",
        "temp_range": (10, 30),
        "precip_min": 400,
        "sunshine_min": 1400,
        "soil_pref": ["mollisol", "alfisol", "aridisol"],
        "category": "豆類",
    },
    "lentil": {
        "name_ja": "レンズマメ",
        "name_en": "Lentil",
        "season": "10月〜5月",
        "temp_range": (8, 25),
        "precip_min": 300,
        "sunshine_min": 1200,
        "soil_pref": ["mollisol", "alfisol"],
        "category": "豆類",
    },
    "date_palm": {
        "name_ja": "ナツメヤシ",
        "name_en": "Date Palm",
        "season": "通年（乾燥地帯）",
        "temp_range": (20, 45),
        "precip_min": 100,
        "sunshine_min": 2500,
        "soil_pref": ["aridisol", "entisol"],
        "category": "果樹",
    },
    "durian": {
        "name_ja": "ドリアン",
        "name_en": "Durian",
        "season": "5月〜8月",
        "temp_range": (24, 35),
        "precip_min": 1500,
        "sunshine_min": 1200,
        "soil_pref": ["oxisol", "ultisol"],
        "category": "果樹",
    },
    "coconut": {
        "name_ja": "ココナッツ",
        "name_en": "Coconut",
        "season": "通年（熱帯）",
        "temp_range": (22, 35),
        "precip_min": 1200,
        "sunshine_min": 1500,
        "soil_pref": ["entisol", "oxisol", "ultisol"],
        "category": "果樹",
    },
}


def get_fao_context(crop_key: str, country_code: str) -> Optional[dict]:
    """
    Get FAO production context for a crop in a country/region.
    Returns global ranking and production data.
    """
    if crop_key not in FAO_CROP_PRODUCTION:
        return None

    producers = FAO_CROP_PRODUCTION[crop_key]
    total_global = sum(p[2] for p in producers)

    # Find if this country is a major producer
    country_rank = None
    country_data = None
    for i, (code, name, prod, area) in enumerate(producers):
        if code == country_code:
            country_rank = i + 1
            country_data = {"name": name, "production_t": prod, "area_ha": area}
            break

    return {
        "crop": crop_key,
        "global_top_producers": [
            {"rank": i + 1, "country": name, "production_t": prod, "area_ha": area}
            for i, (code, name, prod, area) in enumerate(producers[:5])
        ],
        "country_rank": country_rank,
        "country_data": country_data,
        "source": "FAO FAOSTAT 2022 (built-in snapshot)",
    }
