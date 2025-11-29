"""
AI K-Food - 한국 음식 레시피 & 피트니스 어드바이저
메인 페이지: 레시피 검색 + 종합 결과 (영양정보/운동추천)
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go

# Project Root Setup
PROJECT_ROOT = Path(__file__).parent.parent
STREAMLIT_APP = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from utils.style import load_css
from utils.i18n import t, get_lang
from services.api_client import search_recipe, search_recipes_multiple
from components.recipe_card import render_recipe_card
from components.recipe_grid import render_recipe_grid, get_recipe_image
from components.exercise_card import render_exercise_card, render_exercise_comparison
from components.top_navigation import apply_page_style, render_top_navigation, render_footer

# Page Config
st.set_page_config(
    page_title="AI K-Food",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 공통 스타일 적용
apply_page_style()
load_css()


def init_session_state():
    """Initialize session state variables."""
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "weight": 70.0,
            "height": 170.0,
            "age": 30,
            "gender": "male",
            "activity_level": "moderate"
        }
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    if "language" not in st.session_state:
        st.session_state.language = "ko"


def calculate_exercises(calories: float, weight: float = 70) -> list:
    """칼로리 기반 운동 추천 계산"""
    lang = get_lang()

    exercises_data = {
        "ko": [
            {"name": "걷기", "name_kr": "보통 걷기", "met": 3.5, "intensity": "low",
             "description": "편안한 속도로 걷기", "tips": "하루 30분 이상 걷기를 권장합니다."},
            {"name": "자전거", "name_kr": "여가 자전거", "met": 5.5, "intensity": "medium",
             "description": "적당한 속도로 자전거 타기", "tips": "무릎 관절에 부담이 적은 운동입니다."},
            {"name": "달리기", "name_kr": "조깅", "met": 8.0, "intensity": "high",
             "description": "가볍게 달리기", "tips": "심폐 기능 향상에 효과적입니다."}
        ],
        "en": [
            {"name": "Walking", "name_kr": "Walking", "met": 3.5, "intensity": "low",
             "description": "Walk at a comfortable pace", "tips": "30+ minutes of walking daily is recommended."},
            {"name": "Cycling", "name_kr": "Cycling", "met": 5.5, "intensity": "medium",
             "description": "Cycle at moderate speed", "tips": "Low impact on knee joints."},
            {"name": "Running", "name_kr": "Jogging", "met": 8.0, "intensity": "high",
             "description": "Light jogging", "tips": "Effective for cardiovascular health."}
        ]
    }

    exercises = exercises_data.get(lang, exercises_data["ko"])

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


def render_donut_chart(protein: float, fat: float, carbs: float, calories: float):
    """주요 영양소 도넛 차트"""
    lang = get_lang()

    # 라벨
    labels = {
        "ko": ['탄수화물', '단백질', '지방'],
        "en": ['Carbs', 'Protein', 'Fat']
    }

    protein_cal = protein * 4
    fat_cal = fat * 9
    carb_cal = carbs * 4
    total_cal = protein_cal + fat_cal + carb_cal or 1

    protein_pct = round(protein_cal / total_cal * 100)
    fat_pct = round(fat_cal / total_cal * 100)
    carb_pct = round(carb_cal / total_cal * 100)

    fig = go.Figure(data=[go.Pie(
        values=[carb_pct, protein_pct, fat_pct],
        labels=labels.get(lang, labels["ko"]),
        hole=0.6,
        marker_colors=['#FFA726', '#66BB6A', '#BDBDBD'],
        textinfo='none',
        hovertemplate='%{label}: %{value}%<extra></extra>'
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=180,
        annotations=[dict(
            text=f'<b>{calories:.0f}</b><br>kcal',
            x=0.5, y=0.5,
            font_size=18,
            showarrow=False,
            font_color='#FFA726'
        )],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig, protein_pct, fat_pct, carb_pct


def render_nutrition_section(recipe: dict, nutrition: dict):
    """영양정보 섹션 렌더링"""
    food_name = recipe.get("name", t("nutrition_info"))

    # 영양정보가 없으면 추정값 사용
    if not nutrition:
        nutrition = {
            "calories": recipe.get("calories", 300),
            "protein": 15,
            "fat": 12,
            "carbohydrate": 40,
            "sugar": 5,
            "sodium": 500,
            "saturated_fat": 5
        }

    # 칼로리 및 조리시간
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem;">
                <p style="color: #6b7280; margin-bottom: 0.25rem; font-size: 0.875rem;">{t("total_calories")}</p>
                <p style="color: #FFA726; font-size: 2rem; font-weight: 700; margin: 0;">{nutrition.get("calories", 0):.0f} kcal</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        cooking_time = recipe.get("cooking_time", 30)
        st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem;">
                <p style="color: #6b7280; margin-bottom: 0.25rem; font-size: 0.875rem;">{t("expected_cooking_time")}</p>
                <p style="color: #111827; font-size: 2rem; font-weight: 700; margin: 0;">{cooking_time}{t("time") if get_lang() == "en" else "분"}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 주요 영양소 구성 및 일일 권장량
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('main_nutrients')}")

        protein = nutrition.get("protein", 0)
        fat = nutrition.get("fat", 0)
        carbs = nutrition.get("carbohydrate", 0)
        calories = nutrition.get("calories", 0)

        fig, protein_pct, fat_pct, carb_pct = render_donut_chart(protein, fat, carbs, calories)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 범례
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"🟠 {t('carbohydrate')} ({carb_pct}%) **{carbs:.0f}g**")
        with col_b:
            st.markdown(f"🟢 {t('protein')} ({protein_pct}%) **{protein:.0f}g**")
        with col_c:
            st.markdown(f"⚪ {t('fat')} ({fat_pct}%) **{fat:.0f}g**")

    with col2:
        st.markdown(f"#### {t('daily_value')}")

        # 나트륨
        sodium = nutrition.get("sodium", 0)
        sodium_daily = 2000
        sodium_pct = min(sodium / sodium_daily * 100, 100)
        st.markdown(f"**{t('sodium')}** <span style='color: #FFA726; float: right;'>{sodium:.0f}mg / {sodium_daily}mg ({sodium_pct:.0f}%)</span>", unsafe_allow_html=True)
        st.progress(sodium_pct / 100)

        # 당류
        sugar = nutrition.get("sugar", 0)
        sugar_daily = 50
        sugar_pct = min(sugar / sugar_daily * 100, 100)
        st.markdown(f"**{t('sugar')}** <span style='color: #FFA726; float: right;'>{sugar:.0f}g / {sugar_daily}g ({sugar_pct:.0f}%)</span>", unsafe_allow_html=True)
        st.progress(sugar_pct / 100)

        # 포화지방
        sat_fat = nutrition.get("saturated_fat", fat * 0.35)
        sat_fat_daily = 15
        sat_fat_pct = min(sat_fat / sat_fat_daily * 100, 100)
        st.markdown(f"**{t('saturated_fat')}** <span style='color: #FFA726; float: right;'>{sat_fat:.0f}g / {sat_fat_daily}g ({sat_fat_pct:.0f}%)</span>", unsafe_allow_html=True)
        st.progress(sat_fat_pct / 100)

    st.divider()

    # 상세 영양 성분표
    st.markdown(f"#### {t('detailed_nutrition')}")
    st.caption(t("serving_size"))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{t('calories')}** {nutrition.get('calories', 0):.0f} kcal")
        st.markdown(f"**{t('protein')}** {nutrition.get('protein', 0):.1f} g")
        st.markdown(f"**{t('trans_fat')}** {nutrition.get('trans_fat', 0):.1f} g")

    with col2:
        st.markdown(f"**{t('carbohydrate')}** {nutrition.get('carbohydrate', 0):.0f} g")
        st.markdown(f"**{t('fat')}** {nutrition.get('fat', 0):.0f} g")
        st.markdown(f"**{t('cholesterol')}** {nutrition.get('cholesterol', 0):.0f} mg")

    with col3:
        st.markdown(f"**{t('sugar')}** {nutrition.get('sugar', 0):.1f} g")
        st.markdown(f"**{t('saturated_fat')}** {nutrition.get('saturated_fat', fat * 0.35):.1f} g")
        st.markdown(f"**{t('sodium')}** {nutrition.get('sodium', 0):.0f} mg")


def render_exercise_section(recipe: dict, nutrition: dict, exercises: list):
    """운동 추천 섹션 렌더링"""
    food_name = recipe.get("name", t("exercise_info"))

    # 칼로리 가져오기
    calories = 0
    if nutrition:
        calories = nutrition.get("calories", 0)
    if not calories:
        calories = recipe.get("calories", 300)

    # 운동 추천이 없으면 계산
    if not exercises and calories > 0:
        exercises = calculate_exercises(calories)

    # 칼로리 정보 카드
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFA726, #FF7043); padding: 1.5rem; border-radius: 1rem; color: white; margin-bottom: 1rem;">
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">{t("intake_calories")}</p>
            <p style="margin: 0; font-size: 2.5rem; font-weight: 700;">{calories:.0f} kcal</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">
                {t("exercise_recommendation")}
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 운동 추천 카드
    if exercises:
        st.markdown(f"### 🏃 {t('recommended_exercises')}")
        st.caption(t("exercise_desc"))

        render_exercise_card(exercises)

        st.divider()

        # 운동 비교 테이블
        render_exercise_comparison(exercises)
    else:
        st.warning(t("no_results"))

    st.divider()

    # 운동 팁
    st.markdown(f"### 💡 {t('exercise_tips')}")

    tip_col1, tip_col2, tip_col3 = st.columns(3)

    with tip_col1:
        st.markdown(f"""
            <div style="background: #f0fdf4; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #22c55e;">
                <p style="font-weight: 600; color: #166534; margin-bottom: 0.5rem;">🥤 {t("tip_hydration")}</p>
                <p style="color: #166534; font-size: 0.875rem; margin: 0;">
                    {t("tip_hydration_desc")}
                </p>
            </div>
        """, unsafe_allow_html=True)

    with tip_col2:
        st.markdown(f"""
            <div style="background: #fef3c7; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #f59e0b;">
                <p style="font-weight: 600; color: #92400e; margin-bottom: 0.5rem;">⏰ {t("tip_after_meal")}</p>
                <p style="color: #92400e; font-size: 0.875rem; margin: 0;">
                    {t("tip_after_meal_desc")}
                </p>
            </div>
        """, unsafe_allow_html=True)

    with tip_col3:
        st.markdown(f"""
            <div style="background: #eff6ff; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6;">
                <p style="font-weight: 600; color: #1e40af; margin-bottom: 0.5rem;">🧘 {t("tip_stretching")}</p>
                <p style="color: #1e40af; font-size: 0.875rem; margin: 0;">
                    {t("tip_stretching_desc")}
                </p>
            </div>
        """, unsafe_allow_html=True)


def main():
    init_session_state()

    # 상단 네비게이션
    render_top_navigation(current_page="home")

    # 페이지 타이틀
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                {t("main_title")}
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # 검색 바
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.form(key="search_form", clear_on_submit=False):
            search_col1, search_col2 = st.columns([5, 1])
            with search_col1:
                query = st.text_input(
                    t("search_button"),
                    placeholder=t("search_placeholder"),
                    key="search_input",
                    label_visibility="collapsed"
                )
            with search_col2:
                search_clicked = st.form_submit_button(t("search_button"), type="primary", use_container_width=True)

    # 검색 실행
    if search_clicked and query:
        with st.spinner(t("searching")):
            results = search_recipes_multiple(query, limit=9)

            if results.get("success") and results.get("recipes"):
                st.session_state.search_results = results["recipes"]
                st.session_state.search_query = query
                st.session_state.current_page = 1

                # 첫 번째 결과를 상세 정보용으로 저장
                first_recipe = results["recipes"][0]
                st.session_state.search_result = {
                    "success": True,
                    "recipe": first_recipe,
                    "nutrition": results.get("nutrition") or first_recipe.get("nutrition"),
                    "exercises": results.get("exercises", []),
                    "analyzed_query": {"food_name": query, "servings": 1}
                }
                st.session_state.selected_recipe = first_recipe
                st.session_state.show_detail_tabs = True
            else:
                st.warning(t("no_results"))

    # 검색 결과 그리드
    if "search_results" in st.session_state and st.session_state.search_results:
        recipes = st.session_state.search_results
        query = st.session_state.get("search_query", "")

        # 결과 헤더
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### '{query}' {t('search_results')}")
        with col2:
            sort_options = {
                "ko": ["최신순", "칼로리 낮은순", "칼로리 높은순"],
                "en": ["Latest", "Lowest Calories", "Highest Calories"]
            }
            sort_option = st.selectbox(
                t("sort_by"),
                sort_options.get(get_lang(), sort_options["ko"]),
                label_visibility="collapsed"
            )

        st.divider()

        # 정렬 적용
        if sort_option in ["칼로리 낮은순", "Lowest Calories"]:
            recipes = sorted(recipes, key=lambda x: x.get("calories", 0))
        elif sort_option in ["칼로리 높은순", "Highest Calories"]:
            recipes = sorted(recipes, key=lambda x: x.get("calories", 0), reverse=True)

        # 레시피 그리드 (클릭 시 상세 정보 표시)
        cols = st.columns(3)
        for i, recipe in enumerate(recipes[:6]):
            with cols[i % 3]:
                recipe_name = recipe.get("name", "")
                image_url = get_recipe_image(recipe_name, recipe.get("image_url", ""))
                calories = recipe.get("calories", 0)

                # 카드 스타일
                st.markdown(f"""
                    <div style="background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                        <img src="{image_url}" style="width: 100%; height: 150px; object-fit: cover;">
                        <div style="padding: 0.75rem;">
                            <p style="font-weight: 600; margin: 0 0 0.25rem 0; font-size: 0.9rem;">{recipe_name}</p>
                            <p style="color: #FFA726; margin: 0; font-size: 0.8rem;">{calories:.0f} kcal</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if st.button(t("view_recipe"), key=f"view_{i}", use_container_width=True):
                    st.session_state.selected_recipe = recipe
                    st.session_state.search_result = {
                        "success": True,
                        "recipe": recipe,
                        "nutrition": recipe.get("nutrition"),
                        "exercises": [],
                        "analyzed_query": {"food_name": recipe_name, "servings": 1}
                    }
                    st.session_state.show_detail_tabs = True
                    st.rerun()

        st.divider()

    # 상세 정보 탭 (레시피/영양정보/운동추천)
    if st.session_state.get("show_detail_tabs") and st.session_state.get("selected_recipe"):
        recipe = st.session_state.selected_recipe
        result = st.session_state.get("search_result", {})
        nutrition = result.get("nutrition") or recipe.get("nutrition") or {}
        exercises = result.get("exercises", [])

        food_name = recipe.get("name", "")

        st.markdown(f"## 📖 {food_name}")

        # 탭
        tab_recipe, tab_nutrition, tab_exercise = st.tabs([
            f"🍳 {t('view_recipe')}",
            f"📊 {t('nutrition_info')}",
            f"🏃 {t('exercise_info')}"
        ])

        with tab_recipe:
            render_recipe_card(recipe)

        with tab_nutrition:
            render_nutrition_section(recipe, nutrition)

        with tab_exercise:
            render_exercise_section(recipe, nutrition, exercises)

    # 푸터
    render_footer()


if __name__ == "__main__":
    main()
