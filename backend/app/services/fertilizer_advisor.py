"""
Fertilizer & Soil Amendment Advisor
=====================================
Recommends optimal fertilizers, soil amendments, and cultivation materials
based on soil conditions, crop requirements, and regional climate.

Data sources:
- 農水省「施肥基準」(MAFF fertilization standards)
- JA全農 施肥設計ガイドライン
- 一般的な作物栄養学に基づく推奨量

Categories:
1. 基肥（元肥）— Base fertilizer
2. 追肥 — Top dressing
3. 土壌改良材 — Soil amendments
4. 有機質肥料 — Organic fertilizers
5. 微量要素 — Micronutrients
6. 農業資材 — Agricultural materials
"""

from typing import Optional

# ── 肥料データベース ──────────────────────────────────────

FERTILIZER_DATABASE = {
    # ── 化学肥料（Chemical Fertilizers） ────────────────
    "urea": {
        "name_ja": "尿素",
        "name_en": "Urea",
        "category": "窒素肥料",
        "npk": {"N": 46, "P": 0, "K": 0},
        "form": "粒状",
        "speed": "速効性",
        "price_range": "¥1,500-2,500/20kg",
        "notes": "窒素含有量最高。水溶性で即効。葉面散布にも使用可",
        "caution": "施用過多で硝酸態窒素の地下水汚染リスク",
    },
    "ammonium_sulfate": {
        "name_ja": "硫安（硫酸アンモニウム）",
        "name_en": "Ammonium Sulfate",
        "category": "窒素肥料",
        "npk": {"N": 21, "P": 0, "K": 0},
        "form": "粒状",
        "speed": "速効性",
        "price_range": "¥1,200-1,800/20kg",
        "notes": "硫黄も供給。酸性土壌を好む茶・ブルーベリーに適合",
        "best_for": ["tea", "blueberry", "azalea"],
    },
    "calcium_ammonium_nitrate": {
        "name_ja": "石灰窒素",
        "name_en": "Calcium Cyanamide",
        "category": "窒素肥料",
        "npk": {"N": 20, "P": 0, "K": 0},
        "form": "粉状",
        "speed": "緩効性",
        "price_range": "¥2,500-3,500/20kg",
        "notes": "殺虫・除草効果あり。土壌消毒にも使用。植付2週間前施用",
        "caution": "直接種子・苗に触れると薬害",
    },
    "superphosphate": {
        "name_ja": "過リン酸石灰",
        "name_en": "Superphosphate",
        "category": "リン酸肥料",
        "npk": {"N": 0, "P": 17, "K": 0},
        "form": "粉状・粒状",
        "speed": "速効性",
        "price_range": "¥1,000-1,500/20kg",
        "notes": "リン酸の基本肥料。根の発達・花芽形成を促進",
    },
    "fused_phosphate": {
        "name_ja": "溶成リン肥（ようりん）",
        "name_en": "Fused Magnesium Phosphate",
        "category": "リン酸肥料",
        "npk": {"N": 0, "P": 20, "K": 0},
        "form": "粒状",
        "speed": "緩効性",
        "price_range": "¥1,500-2,000/20kg",
        "notes": "Mg・Si含有。酸性土壌でもリン酸が効く。水稲に最適",
        "best_for": ["rice"],
    },
    "potassium_chloride": {
        "name_ja": "塩化カリ",
        "name_en": "Potassium Chloride (MOP)",
        "category": "カリ肥料",
        "npk": {"N": 0, "P": 0, "K": 60},
        "form": "粒状",
        "speed": "速効性",
        "price_range": "¥2,000-3,000/20kg",
        "notes": "カリ含有量高。根菜類の肥大促進に",
        "caution": "塩素忌避作物（タバコ、ジャガイモ）には不向き",
    },
    "potassium_sulfate": {
        "name_ja": "硫酸カリ",
        "name_en": "Potassium Sulfate (SOP)",
        "category": "カリ肥料",
        "npk": {"N": 0, "P": 0, "K": 50},
        "form": "粒状",
        "speed": "速効性",
        "price_range": "¥3,000-4,500/20kg",
        "notes": "塩素フリー。果樹・野菜の品質向上に。硫黄も供給",
        "best_for": ["potato", "tomato", "grape", "tobacco"],
    },
    "compound_888": {
        "name_ja": "化成肥料 8-8-8",
        "name_en": "Compound Fertilizer 8-8-8",
        "category": "複合肥料",
        "npk": {"N": 8, "P": 8, "K": 8},
        "form": "粒状",
        "speed": "速効性",
        "price_range": "¥1,800-2,500/20kg",
        "notes": "万能型。家庭菜園から露地栽培まで幅広く使用",
    },
    "compound_141414": {
        "name_ja": "化成肥料 14-14-14",
        "name_en": "Compound Fertilizer 14-14-14",
        "category": "複合肥料",
        "npk": {"N": 14, "P": 14, "K": 14},
        "form": "粒状",
        "speed": "速効性",
        "price_range": "¥2,500-3,500/20kg",
        "notes": "高度化成。効率的な施肥が可能。大規模栽培向け",
    },
    "slow_release_100": {
        "name_ja": "緩効性肥料（LP100）",
        "name_en": "Controlled-Release Fertilizer (100 day)",
        "category": "複合肥料",
        "npk": {"N": 13, "P": 11, "K": 13},
        "form": "被覆粒状",
        "speed": "緩効性（100日）",
        "price_range": "¥4,000-6,000/20kg",
        "notes": "100日間ゆっくり溶出。追肥不要で省力化。水稲一発肥料",
        "best_for": ["rice"],
    },

    # ── 有機質肥料（Organic Fertilizers） ──────────────
    "compost_cattle": {
        "name_ja": "牛糞堆肥",
        "name_en": "Cattle Manure Compost",
        "category": "有機質肥料",
        "npk": {"N": 1.5, "P": 1.8, "K": 2.2},
        "form": "堆肥",
        "speed": "緩効性",
        "price_range": "¥300-800/40L",
        "notes": "土壌改良効果大。保水性・通気性改善。基肥として2-3t/10a",
    },
    "compost_chicken": {
        "name_ja": "鶏糞",
        "name_en": "Chicken Manure",
        "category": "有機質肥料",
        "npk": {"N": 3.0, "P": 5.0, "K": 2.5},
        "form": "発酵・乾燥",
        "speed": "速効性〜緩効性",
        "price_range": "¥400-700/15kg",
        "notes": "リン酸含量高い。即効性あり。元肥・追肥両方OK",
        "caution": "未発酵品はガス害リスク。完熟品を使用",
    },
    "oil_cake": {
        "name_ja": "油かす（菜種粕）",
        "name_en": "Rapeseed Meal",
        "category": "有機質肥料",
        "npk": {"N": 5.3, "P": 2.0, "K": 1.0},
        "form": "粉状・粒状",
        "speed": "緩効性",
        "price_range": "¥1,200-2,000/20kg",
        "notes": "窒素主体の有機肥料。微生物活性化。果樹・野菜に広く使用",
    },
    "fish_meal": {
        "name_ja": "魚粉（魚かす）",
        "name_en": "Fish Meal",
        "category": "有機質肥料",
        "npk": {"N": 7.0, "P": 6.0, "K": 0.5},
        "form": "粉状",
        "speed": "緩効性",
        "price_range": "¥2,000-3,000/20kg",
        "notes": "アミノ酸豊富。旨味成分向上。トマト・果樹の品質向上に",
        "best_for": ["tomato", "strawberry", "mandarin"],
    },
    "bone_meal": {
        "name_ja": "骨粉",
        "name_en": "Bone Meal",
        "category": "有機質肥料",
        "npk": {"N": 4.0, "P": 20.0, "K": 0},
        "form": "粉状",
        "speed": "緩効性",
        "price_range": "¥1,500-2,500/20kg",
        "notes": "リン酸主体。カルシウム供給。果樹の花芽分化促進",
    },
    "seaweed": {
        "name_ja": "海藻肥料",
        "name_en": "Seaweed Fertilizer",
        "category": "有機質肥料",
        "npk": {"N": 1.0, "P": 0.5, "K": 4.0},
        "form": "液体・粉状",
        "speed": "速効性",
        "price_range": "¥2,000-4,000/1L",
        "notes": "微量要素・植物ホルモン豊富。ストレス耐性向上。葉面散布OK",
    },

    # ── 土壌改良材（Soil Amendments） ─────────────────
    "lime": {
        "name_ja": "苦土石灰",
        "name_en": "Dolomite Lime",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粉状・粒状",
        "speed": "緩効性",
        "price_range": "¥300-600/20kg",
        "notes": "pH矯正（酸性→中性）。Mg供給。100-200kg/10a が標準",
        "use_when": "pH < 5.5",
    },
    "calcium_ite": {
        "name_ja": "消石灰",
        "name_en": "Slaked Lime",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粉状",
        "speed": "速効性",
        "price_range": "¥400-700/20kg",
        "notes": "強アルカリ。pH矯正力が強い。土壌消毒にも",
        "caution": "施用直後の播種・植付は避ける（2週間以上空ける）",
        "use_when": "pH < 5.0",
    },
    "gypsum": {
        "name_ja": "石膏（硫酸カルシウム）",
        "name_en": "Gypsum",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粉状",
        "speed": "緩効性",
        "price_range": "¥500-1,000/20kg",
        "notes": "pHを変えずにCa供給。排水改善。落花生・トマトの尻腐れ防止",
        "best_for": ["peanut", "tomato"],
    },
    "perlite": {
        "name_ja": "パーライト",
        "name_en": "Perlite",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粒状（軽量）",
        "speed": "-",
        "price_range": "¥800-1,500/50L",
        "notes": "排水性・通気性改善。軽量。鉢植え・育苗培土に",
        "use_when": "drainage == 'poor'",
    },
    "vermiculite": {
        "name_ja": "バーミキュライト",
        "name_en": "Vermiculite",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粒状（軽量）",
        "speed": "-",
        "price_range": "¥800-1,200/50L",
        "notes": "保水性・保肥性改善。CEC高。種まき培土に最適",
        "use_when": "drainage == 'excessive'",
    },
    "peat_moss": {
        "name_ja": "ピートモス",
        "name_en": "Peat Moss",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "繊維状",
        "speed": "-",
        "price_range": "¥1,000-2,000/50L",
        "notes": "酸性。保水性大幅改善。ブルーベリー・ツツジ類に最適",
        "best_for": ["blueberry"],
        "use_when": "organic == 'very_low' or organic == 'low'",
    },
    "biochar": {
        "name_ja": "バイオ炭（もみ殻くん炭）",
        "name_en": "Biochar / Rice Hull Charcoal",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 3},
        "form": "粒状",
        "speed": "-",
        "price_range": "¥500-1,500/40L",
        "notes": "通気性・排水性改善。微生物住処。炭素固定でCO2削減効果",
    },
    "zeolite": {
        "name_ja": "ゼオライト",
        "name_en": "Zeolite",
        "category": "土壌改良材",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粒状",
        "speed": "-",
        "price_range": "¥1,000-2,000/20kg",
        "notes": "CEC極高。肥料流亡防止。保肥力大幅改善。砂質土壌に",
        "use_when": "drainage == 'excessive'",
    },

    # ── 微量要素（Micronutrients） ────────────────────
    "iron_chelate": {
        "name_ja": "キレート鉄",
        "name_en": "Iron Chelate (Fe-EDTA)",
        "category": "微量要素",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粉状・液体",
        "speed": "速効性",
        "price_range": "¥1,500-3,000/500g",
        "notes": "鉄欠乏症（黄化）対策。アルカリ土壌で発生しやすい",
    },
    "borax": {
        "name_ja": "ホウ酸",
        "name_en": "Borax",
        "category": "微量要素",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粉状",
        "speed": "速効性",
        "price_range": "¥800-1,500/1kg",
        "notes": "ホウ素欠乏対策。花芽形成・果実品質に重要。過剰注意",
        "best_for": ["cabbage", "broccoli", "apple"],
    },
    "manganese_sulfate": {
        "name_ja": "硫酸マンガン",
        "name_en": "Manganese Sulfate",
        "category": "微量要素",
        "npk": {"N": 0, "P": 0, "K": 0},
        "form": "粉状",
        "speed": "速効性",
        "price_range": "¥1,000-2,000/1kg",
        "notes": "マンガン欠乏対策。光合成促進。大豆で発生しやすい",
        "best_for": ["soybean", "wheat"],
    },
}

# ── 作物別施肥基準（10aあたり標準施肥量） ──────────────

CROP_FERTILIZATION_STANDARDS = {
    "rice": {
        "name_ja": "水稲",
        "base": {"N": 5, "P": 6, "K": 5, "unit": "kg/10a"},
        "topdress": {"N": 3, "P": 0, "K": 2, "timing": "穂肥（出穂25日前）"},
        "recommended": ["slow_release_100", "fused_phosphate", "compost_cattle"],
        "notes": "一発肥料で省力化可能。ケイ酸質資材で倒伏防止",
    },
    "tomato": {
        "name_ja": "トマト",
        "base": {"N": 15, "P": 20, "K": 15, "unit": "kg/10a"},
        "topdress": {"N": 5, "P": 0, "K": 5, "timing": "2週間ごと"},
        "recommended": ["fish_meal", "gypsum", "potassium_sulfate", "bone_meal"],
        "notes": "尻腐れ防止にCa施用重要。有機質でアミノ酸（旨味）向上",
    },
    "strawberry": {
        "name_ja": "イチゴ",
        "base": {"N": 10, "P": 15, "K": 10, "unit": "kg/10a"},
        "topdress": {"N": 3, "P": 0, "K": 3, "timing": "花房ごと"},
        "recommended": ["fish_meal", "potassium_sulfate", "seaweed"],
        "notes": "窒素過多で果実品質低下。カリ重視で糖度向上",
    },
    "cabbage": {
        "name_ja": "キャベツ",
        "base": {"N": 20, "P": 20, "K": 20, "unit": "kg/10a"},
        "topdress": {"N": 10, "P": 0, "K": 5, "timing": "結球開始期"},
        "recommended": ["compound_141414", "lime", "borax"],
        "notes": "窒素要求量多い。ホウ素欠乏で芯腐れ発生",
    },
    "potato": {
        "name_ja": "ジャガイモ",
        "base": {"N": 10, "P": 15, "K": 12, "unit": "kg/10a"},
        "topdress": {"N": 0, "P": 0, "K": 0, "timing": "基肥のみ"},
        "recommended": ["potassium_sulfate", "compost_cattle", "lime"],
        "notes": "塩化カリ避ける（でんぷん品質低下）。カリで芋の肥大促進",
    },
    "onion": {
        "name_ja": "タマネギ",
        "base": {"N": 12, "P": 15, "K": 12, "unit": "kg/10a"},
        "topdress": {"N": 5, "P": 0, "K": 3, "timing": "2月・3月"},
        "recommended": ["compound_888", "superphosphate", "lime"],
        "notes": "リン酸で根の発達促進。止め肥（収穫1ヶ月前）厳守",
    },
    "grape": {
        "name_ja": "ブドウ",
        "base": {"N": 12, "P": 10, "K": 12, "unit": "kg/10a"},
        "topdress": {"N": 5, "P": 0, "K": 5, "timing": "開花後〜袋掛け前"},
        "recommended": ["potassium_sulfate", "bone_meal", "compost_cattle"],
        "notes": "カリで着色・糖度向上。窒素過多で着色不良・棚もちの悪化",
    },
    "tea": {
        "name_ja": "茶",
        "base": {"N": 30, "P": 10, "K": 10, "unit": "kg/10a"},
        "topdress": {"N": 20, "P": 5, "K": 10, "timing": "春肥・夏肥・秋肥"},
        "recommended": ["ammonium_sulfate", "oil_cake", "compost_cattle"],
        "notes": "窒素施肥量が極めて多い。硫安でpH低下→旨味成分テアニン増加",
    },
    "apple": {
        "name_ja": "リンゴ",
        "base": {"N": 10, "P": 8, "K": 10, "unit": "kg/10a"},
        "topdress": {"N": 5, "P": 0, "K": 5, "timing": "摘果後・収穫後"},
        "recommended": ["potassium_sulfate", "bone_meal", "borax", "compost_cattle"],
        "notes": "ホウ素でコルク化防止。カリで着色・貯蔵性向上",
    },
    "soybean": {
        "name_ja": "大豆",
        "base": {"N": 3, "P": 10, "K": 10, "unit": "kg/10a"},
        "topdress": {"N": 0, "P": 0, "K": 0, "timing": "根粒菌が窒素固定"},
        "recommended": ["superphosphate", "lime", "manganese_sulfate"],
        "notes": "根粒菌が窒素を固定するため窒素施肥は少量。リン酸・カリ重視",
    },
}


def get_fertilizer_recommendation(
    soil_type: str,
    soil_ph: str,
    drainage: str,
    organic_matter: str,
    crop: Optional[str] = None,
) -> dict:
    """
    Generate fertilizer and soil amendment recommendations.

    Args:
        soil_type: Soil type name
        soil_ph: pH range string (e.g., "5.0-6.5")
        drainage: Drainage quality
        organic_matter: Organic matter level
        crop: Target crop key

    Returns:
        dict with recommended fertilizers, amendments, and application guide
    """
    recommendations = {
        "soil_amendments": [],
        "base_fertilizers": [],
        "organic_options": [],
        "micronutrients": [],
        "crop_specific": None,
        "application_guide": [],
    }

    # Parse pH
    try:
        ph_low = float(soil_ph.split("-")[0])
    except (ValueError, IndexError):
        ph_low = 6.0

    # 1. Soil amendments based on conditions
    if ph_low < 5.5:
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["lime"],
            "reason": f"pH {soil_ph} が酸性寄り。苦土石灰で矯正",
            "dosage": "100-200kg/10a",
        })
    if ph_low < 5.0:
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["calcium_ite"],
            "reason": f"pH {soil_ph} が強酸性。消石灰で早急に矯正",
            "dosage": "50-100kg/10a",
        })

    if drainage == "poor":
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["perlite"],
            "reason": "排水不良。パーライトで通気性改善",
            "dosage": "土壌容量の10-20%",
        })
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["biochar"],
            "reason": "排水不良。バイオ炭で排水性・微生物環境改善",
            "dosage": "200-500kg/10a",
        })

    if drainage == "excessive":
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["vermiculite"],
            "reason": "排水過多。バーミキュライトで保水性改善",
            "dosage": "土壌容量の10-20%",
        })
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["zeolite"],
            "reason": "排水過多。ゼオライトで保肥力大幅改善",
            "dosage": "100-200kg/10a",
        })

    if organic_matter in ("very_low", "low"):
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["compost_cattle"],
            "reason": f"有機物が{organic_matter}。堆肥投入で土壌改良",
            "dosage": "2,000-3,000kg/10a",
        })
        recommendations["soil_amendments"].append({
            **FERTILIZER_DATABASE["peat_moss"],
            "reason": "有機物不足。ピートモスで保水性・有機物補給",
            "dosage": "土壌容量の20-30%",
        })

    # 2. Base fertilizer recommendations
    recommendations["base_fertilizers"].append(FERTILIZER_DATABASE["compound_888"])
    recommendations["base_fertilizers"].append(FERTILIZER_DATABASE["compound_141414"])

    # 3. Organic options (always recommend)
    recommendations["organic_options"].append(FERTILIZER_DATABASE["compost_cattle"])
    recommendations["organic_options"].append(FERTILIZER_DATABASE["oil_cake"])
    recommendations["organic_options"].append(FERTILIZER_DATABASE["fish_meal"])
    recommendations["organic_options"].append(FERTILIZER_DATABASE["seaweed"])

    # 4. Crop-specific recommendations
    if crop and crop in CROP_FERTILIZATION_STANDARDS:
        std = CROP_FERTILIZATION_STANDARDS[crop]
        crop_rec = {
            "crop_name": std["name_ja"],
            "base_npk": std["base"],
            "topdress": std["topdress"],
            "recommended_products": [
                FERTILIZER_DATABASE[fid]
                for fid in std["recommended"]
                if fid in FERTILIZER_DATABASE
            ],
            "notes": std["notes"],
        }
        recommendations["crop_specific"] = crop_rec

    # 5. Application timeline
    recommendations["application_guide"] = _build_timeline(crop)

    return recommendations


def _build_timeline(crop: Optional[str]) -> list:
    """Build a seasonal application timeline."""
    timeline = [
        {"period": "秋（10-11月）", "action": "土壌分析・石灰施用", "detail": "pH矯正は早めに。堆肥投入も秋が理想"},
        {"period": "冬（12-2月）", "action": "土壌改良材施用", "detail": "堆肥・バイオ炭を投入し、凍結融解で土壌に馴染ませる"},
        {"period": "春（3-4月）", "action": "基肥施用", "detail": "植付2-3週間前に元肥を施用"},
    ]

    if crop in CROP_FERTILIZATION_STANDARDS:
        std = CROP_FERTILIZATION_STANDARDS[crop]
        timeline.append({
            "period": "生育期",
            "action": f"追肥: N{std['topdress']['N']}-P{std['topdress']['P']}-K{std['topdress']['K']}",
            "detail": std["topdress"]["timing"],
        })

    timeline.append({
        "period": "収穫後", "action": "お礼肥・土壌診断",
        "detail": "収穫で消費した栄養を補給。次作に向けた土壌分析",
    })

    return timeline
