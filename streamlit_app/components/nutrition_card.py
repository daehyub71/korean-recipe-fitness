"""영양정보 카드 컴포넌트"""

import streamlit as st
from typing import Dict


def render_nutrition_card(nutrition: Dict):
    """
    영양정보 카드 렌더링

    Args:
        nutrition: 영양정보 딕셔너리
    """
    if not nutrition:
        st.warning("영양정보가 없습니다.")
        return

    # 헤더
    food_name = nutrition.get("food_name", "음식")
    servings = nutrition.get("servings", 1)
    st.subheader(f"📊 {food_name} 영양정보 ({servings}인분)")

    # 제공량
    serving_size = nutrition.get("serving_size", 0)
    if serving_size > 0:
        st.caption(f"1회 제공량: {serving_size:.0f}g")

    st.divider()

    # 주요 영양소 (칼로리, 3대 영양소)
    st.markdown("### 🔥 주요 영양소")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        calories = nutrition.get("calories", 0)
        st.metric("칼로리", f"{calories:.0f} kcal")

    with col2:
        protein = nutrition.get("protein", 0)
        st.metric("단백질", f"{protein:.1f} g")

    with col3:
        fat = nutrition.get("fat", 0)
        st.metric("지방", f"{fat:.1f} g")

    with col4:
        carbs = nutrition.get("carbohydrate", 0)
        st.metric("탄수화물", f"{carbs:.1f} g")

    st.divider()

    # 상세 영양소
    st.markdown("### 📋 상세 영양소")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**당류/섬유소**")
        sugar = nutrition.get("sugar", 0)
        fiber = nutrition.get("fiber", 0)
        st.markdown(f"• 당류: {sugar:.1f}g")
        st.markdown(f"• 식이섬유: {fiber:.1f}g")

    with col2:
        st.markdown("**무기질**")
        sodium = nutrition.get("sodium", 0)
        calcium = nutrition.get("calcium", 0)
        iron = nutrition.get("iron", 0)
        potassium = nutrition.get("potassium", 0)
        st.markdown(f"• 나트륨: {sodium:.0f}mg")
        st.markdown(f"• 칼슘: {calcium:.0f}mg")
        st.markdown(f"• 철분: {iron:.1f}mg")
        st.markdown(f"• 칼륨: {potassium:.0f}mg")

    with col3:
        st.markdown("**비타민/콜레스테롤**")
        vitamin_a = nutrition.get("vitamin_a", 0)
        vitamin_c = nutrition.get("vitamin_c", 0)
        cholesterol = nutrition.get("cholesterol", 0)
        st.markdown(f"• 비타민A: {vitamin_a:.0f}μg")
        st.markdown(f"• 비타민C: {vitamin_c:.1f}mg")
        st.markdown(f"• 콜레스테롤: {cholesterol:.0f}mg")

    # 영양소 비율 차트
    st.divider()
    st.markdown("### 📈 영양소 비율")

    # 칼로리 기여도 계산
    protein_cal = nutrition.get("protein", 0) * 4
    fat_cal = nutrition.get("fat", 0) * 9
    carb_cal = nutrition.get("carbohydrate", 0) * 4
    total_cal = protein_cal + fat_cal + carb_cal

    if total_cal > 0:
        chart_data = {
            "영양소": ["단백질", "지방", "탄수화물"],
            "비율 (%)": [
                round(protein_cal / total_cal * 100, 1),
                round(fat_cal / total_cal * 100, 1),
                round(carb_cal / total_cal * 100, 1)
            ]
        }

        # 간단한 바 차트
        col1, col2, col3 = st.columns(3)
        with col1:
            pct = protein_cal / total_cal * 100
            st.progress(pct / 100, text=f"단백질: {pct:.1f}%")
        with col2:
            pct = fat_cal / total_cal * 100
            st.progress(pct / 100, text=f"지방: {pct:.1f}%")
        with col3:
            pct = carb_cal / total_cal * 100
            st.progress(pct / 100, text=f"탄수화물: {pct:.1f}%")

    # 일일 권장량 대비 (예시)
    st.divider()
    st.markdown("### 📌 일일 권장량 대비")

    # 성인 기준 일일 권장량 (대략적인 값)
    daily_values = {
        "calories": 2000,
        "protein": 50,
        "fat": 65,
        "carbohydrate": 300,
        "sodium": 2000,
        "fiber": 25
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        cal_pct = min(nutrition.get("calories", 0) / daily_values["calories"] * 100, 100)
        st.progress(cal_pct / 100, text=f"칼로리: {cal_pct:.0f}%")

        protein_pct = min(nutrition.get("protein", 0) / daily_values["protein"] * 100, 100)
        st.progress(protein_pct / 100, text=f"단백질: {protein_pct:.0f}%")

    with col2:
        fat_pct = min(nutrition.get("fat", 0) / daily_values["fat"] * 100, 100)
        st.progress(fat_pct / 100, text=f"지방: {fat_pct:.0f}%")

        carb_pct = min(nutrition.get("carbohydrate", 0) / daily_values["carbohydrate"] * 100, 100)
        st.progress(carb_pct / 100, text=f"탄수화물: {carb_pct:.0f}%")

    with col3:
        sodium_pct = min(nutrition.get("sodium", 0) / daily_values["sodium"] * 100, 100)
        st.progress(sodium_pct / 100, text=f"나트륨: {sodium_pct:.0f}%")

        fiber_pct = min(nutrition.get("fiber", 0) / daily_values["fiber"] * 100, 100)
        st.progress(fiber_pct / 100, text=f"식이섬유: {fiber_pct:.0f}%")

    st.caption("※ 일일 권장량은 성인 기준입니다 (칼로리 2000kcal 기준)")


def render_nutrition_card_compact(nutrition: Dict):
    """
    영양정보 카드 컴팩트 버전

    Args:
        nutrition: 영양정보 딕셔너리
    """
    with st.container():
        food_name = nutrition.get("food_name", "음식")
        calories = nutrition.get("calories", 0)
        protein = nutrition.get("protein", 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**{food_name}**")
        with col2:
            st.metric("칼로리", f"{calories:.0f} kcal", label_visibility="collapsed")
        with col3:
            st.metric("단백질", f"{protein:.1f}g", label_visibility="collapsed")
