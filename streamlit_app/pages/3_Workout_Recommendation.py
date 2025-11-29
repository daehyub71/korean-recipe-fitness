"""운동 추천 페이지 - AI K-Food 디자인"""

import streamlit as st
import sys
from pathlib import Path

# Project Root Setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from components.exercise_card import render_exercise_card, render_exercise_comparison
from components.recipe_grid import get_recipe_image
from components.top_navigation import apply_page_style, render_top_navigation, render_footer
from utils.style import load_css
from utils.i18n import t, get_lang

st.set_page_config(
    page_title="운동 추천 - AI K-Food",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 공통 스타일 적용
apply_page_style()
load_css()


def calculate_exercises(calories: float, weight: float = 70) -> list:
    """칼로리 기반 운동 추천 계산"""
    exercises = [
        {"name": "걷기", "name_kr": "보통 걷기", "met": 3.5, "intensity": "low",
         "description": "편안한 속도로 걷기", "tips": "하루 30분 이상 걷기를 권장합니다."},
        {"name": "자전거", "name_kr": "여가 자전거", "met": 5.5, "intensity": "medium",
         "description": "적당한 속도로 자전거 타기", "tips": "무릎 관절에 부담이 적은 운동입니다."},
        {"name": "달리기", "name_kr": "조깅", "met": 8.0, "intensity": "high",
         "description": "가볍게 달리기", "tips": "심폐 기능 향상에 효과적입니다."}
    ]

    result = []
    for ex in exercises:
        duration = calories / (ex["met"] * weight / 60)
        result.append({
            "name": ex["name"],
            "name_kr": ex["name_kr"],
            "intensity": ex["intensity"],
            "duration_minutes": round(duration, 0),
            "calories_burned": round(calories, 0),
            "met": ex["met"],
            "description": ex["description"],
            "tips": ex["tips"]
        })

    return result


def main():
    # 상단 네비게이션
    nav_search = render_top_navigation(current_page="exercise")

    # 네비게이션 검색 처리
    if nav_search:
        st.session_state.search_query = nav_search
        st.switch_page("pages/1_Recipe_Search.py")

    # 페이지 타이틀
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                {t("exercise_title")}
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # 데이터 확인
    result = st.session_state.get("search_result", {})
    recipe = result.get("recipe", {})
    nutrition = result.get("nutrition") or {}
    exercises = result.get("exercises", [])

    if not recipe:
        st.info(t("search_first"))
        if st.button(t("go_to_recipe_search"), type="primary"):
            st.switch_page("pages/1_Recipe_Search.py")
        return

    food_name = recipe.get("name", "음식")

    # 칼로리 가져오기 (nutrition > recipe 순서)
    calories = 0
    if nutrition:
        calories = nutrition.get("calories", 0)
    if not calories:
        calories = recipe.get("calories", 300)

    # 운동 추천이 없으면 계산
    if not exercises and calories > 0:
        exercises = calculate_exercises(calories)
        # 세션에 저장
        st.session_state.search_result["exercises"] = exercises

    # ===== 상단: 음식 이미지 및 칼로리 정보 =====
    col1, col2 = st.columns([1, 2])

    with col1:
        image_url = get_recipe_image(food_name, recipe.get("image_url", ""))
        st.image(image_url, use_container_width=True)

    with col2:
        st.markdown(f"## {food_name}")
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FFA726, #FF7043); padding: 1.5rem; border-radius: 1rem; color: white;">
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">섭취 칼로리</p>
                <p style="margin: 0; font-size: 2.5rem; font-weight: 700;">{calories:.0f} kcal</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">
                    이 칼로리를 소모하기 위한 운동을 추천해드립니다.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ===== 운동 추천 카드 =====
    if exercises:
        st.markdown("### 🏃 추천 운동")
        st.caption("아래 운동 중 하나를 선택하여 섭취한 칼로리를 소모하세요.")

        render_exercise_card(exercises)

        st.divider()

        # ===== 운동 비교 테이블 =====
        render_exercise_comparison(exercises)

    else:
        st.warning("운동 추천 정보를 계산할 수 없습니다.")

    st.divider()

    # ===== 운동 팁 =====
    st.markdown("### 💡 건강한 운동 팁")

    tip_col1, tip_col2, tip_col3 = st.columns(3)

    with tip_col1:
        st.markdown("""
            <div style="background: #f0fdf4; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #22c55e;">
                <p style="font-weight: 600; color: #166534; margin-bottom: 0.5rem;">🥤 수분 섭취</p>
                <p style="color: #166534; font-size: 0.875rem; margin: 0;">
                    운동 전후로 충분한 물을 마셔주세요. 하루 2L 이상 권장합니다.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with tip_col2:
        st.markdown("""
            <div style="background: #fef3c7; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #f59e0b;">
                <p style="font-weight: 600; color: #92400e; margin-bottom: 0.5rem;">⏰ 식후 운동</p>
                <p style="color: #92400e; font-size: 0.875rem; margin: 0;">
                    식사 후 최소 1-2시간 후에 운동하는 것이 좋습니다.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with tip_col3:
        st.markdown("""
            <div style="background: #eff6ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6;">
                <p style="font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">🧘 스트레칭</p>
                <p style="color: #1e40af; font-size: 0.875rem; margin: 0;">
                    운동 전후 5-10분 스트레칭으로 부상을 예방하세요.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ===== 하단 버튼 =====
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🍳 레시피 보기", type="secondary", use_container_width=True):
            st.switch_page("pages/1_Recipe_Search.py")

    with col2:
        if st.button("📊 영양정보 보기", type="primary", use_container_width=True):
            st.switch_page("pages/2_Nutrition_Info.py")

    # 푸터
    render_footer()


if __name__ == "__main__":
    main()
