"""Day 1 Test: 데이터 정제 결과 확인"""

import streamlit as st
import sys
import json
from pathlib import Path
import pandas as pd

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Day 1 - 데이터 정제 확인",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Day 1.5: 데이터 정제 결과 확인")

# 파일 경로
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "recipes_raw.json"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "recipes.json"


# 데이터 로드 함수
@st.cache_data
def load_data(file_path: Path) -> list:
    """데이터 로드 및 캐싱"""
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# 원본 vs 정제 비교
st.header("📈 원본 vs 정제 데이터 비교")

raw_data = load_data(RAW_FILE)
processed_data = load_data(PROCESSED_FILE)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "원본 레시피 수",
        f"{len(raw_data):,}개" if raw_data else "없음",
        delta=None
    )

with col2:
    st.metric(
        "정제 후 레시피 수",
        f"{len(processed_data):,}개" if processed_data else "없음",
        delta=f"-{len(raw_data) - len(processed_data)}개 (중복제거)" if raw_data and processed_data else None
    )

with col3:
    if raw_data:
        rate = len(processed_data) / len(raw_data) * 100 if raw_data else 0
        st.metric("정제율", f"{rate:.1f}%")


# 정제된 데이터가 있는 경우만 표시
if processed_data:
    # 카테고리별 분포
    st.header("🏷️ 카테고리별 레시피 분포")

    categories = {}
    for recipe in processed_data:
        cat = recipe.get("category", "기타")
        categories[cat] = categories.get(cat, 0) + 1

    df_cat = pd.DataFrame(list(categories.items()), columns=["카테고리", "레시피 수"])
    df_cat = df_cat.sort_values("레시피 수", ascending=False)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.bar_chart(df_cat.set_index("카테고리"))
    with col2:
        st.dataframe(df_cat, use_container_width=True)


    # 칼로리 분포
    st.header("🔥 칼로리 분포")

    calories = []
    for recipe in processed_data:
        cal = recipe.get("nutrition", {}).get("calories", 0)
        if cal and 0 < cal < 2000:  # 이상치 제외
            calories.append(cal)

    if calories:
        df_cal = pd.DataFrame({"칼로리 (kcal)": calories})

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("평균 칼로리", f"{df_cal['칼로리 (kcal)'].mean():.0f} kcal")
        col2.metric("최소 칼로리", f"{df_cal['칼로리 (kcal)'].min():.0f} kcal")
        col3.metric("최대 칼로리", f"{df_cal['칼로리 (kcal)'].max():.0f} kcal")
        col4.metric("중앙값", f"{df_cal['칼로리 (kcal)'].median():.0f} kcal")

        st.subheader("칼로리 히스토그램")
        # 히스토그램 (bins 형태로)
        import numpy as np
        hist, bins = np.histogram(calories, bins=20)
        bin_labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(hist))]
        df_hist = pd.DataFrame({"구간": bin_labels, "개수": hist})
        st.bar_chart(df_hist.set_index("구간"))


    # 샘플 레시피 상세
    st.header("🍴 샘플 레시피 상세")

    # 검색 기능
    search_term = st.text_input("레시피 검색", placeholder="김치, 된장, 불고기...")

    if search_term:
        filtered = [r for r in processed_data if search_term.lower() in r.get("name", "").lower()]
    else:
        filtered = processed_data[:10]

    st.write(f"표시: {len(filtered)}개 레시피")

    for recipe in filtered[:5]:
        with st.expander(f"🍳 {recipe.get('name', '이름없음')} ({recipe.get('category', '기타')})", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**기본 정보**")
                st.write(f"- 카테고리: {recipe.get('category', '-')}")
                st.write(f"- 조리법: {recipe.get('cooking_method', '-')}")

                st.write("**영양정보**")
                nutrition = recipe.get("nutrition", {})
                st.write(f"- 칼로리: {nutrition.get('calories', 0)} kcal")
                st.write(f"- 탄수화물: {nutrition.get('carbohydrate', 0)} g")
                st.write(f"- 단백질: {nutrition.get('protein', 0)} g")
                st.write(f"- 지방: {nutrition.get('fat', 0)} g")
                st.write(f"- 나트륨: {nutrition.get('sodium', 0)} mg")

            with col2:
                st.write("**재료**")
                ingredients = recipe.get("ingredients", [])
                for ing in ingredients[:10]:
                    st.write(f"- {ing}")
                if len(ingredients) > 10:
                    st.write(f"... 외 {len(ingredients) - 10}개")

            st.write("**조리법**")
            instructions = recipe.get("instructions", [])
            for i, step in enumerate(instructions[:5], 1):
                st.write(f"{i}. {step}")
            if len(instructions) > 5:
                st.write(f"... 외 {len(instructions) - 5}단계")


    # 데이터 품질 체크
    st.header("✅ 데이터 품질 체크")

    quality_checks = {
        "이름 있음": sum(1 for r in processed_data if r.get("name")),
        "카테고리 있음": sum(1 for r in processed_data if r.get("category")),
        "재료 있음": sum(1 for r in processed_data if r.get("ingredients")),
        "조리법 있음": sum(1 for r in processed_data if r.get("instructions")),
        "칼로리 있음": sum(1 for r in processed_data if r.get("nutrition", {}).get("calories", 0) > 0),
    }

    total = len(processed_data)
    for name, count in quality_checks.items():
        pct = count / total * 100 if total > 0 else 0
        status = "✅" if pct >= 80 else "⚠️" if pct >= 50 else "❌"
        st.write(f"{status} {name}: {count:,}/{total:,} ({pct:.1f}%)")

else:
    st.warning("📝 정제된 데이터가 없습니다.")
    st.info("다음 명령을 실행하세요:")
    st.code("""
# 1. 레시피 데이터 수집
python scripts/collect_recipes.py

# 2. 데이터 정제
python scripts/process_recipes.py
    """, language="bash")


# 체크포인트
st.header("📊 Day 1.5 체크포인트")

checks = [
    ("recipes_raw.json 존재", RAW_FILE.exists()),
    ("recipes.json 존재", PROCESSED_FILE.exists()),
    ("정제된 레시피 500개 이상", len(processed_data) >= 500 if processed_data else False),
]

for name, status in checks:
    icon = "✅" if status else "❌"
    st.write(f"{icon} {name}")

if all(status for _, status in checks):
    st.success("✅ Day 1.5 완료! 데이터 정제가 완료되었습니다.")
else:
    st.warning("⚠️ 일부 항목을 완료해주세요.")
