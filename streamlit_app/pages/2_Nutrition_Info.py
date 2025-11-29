"""영양정보 페이지 - AI K-Food 디자인"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Project Root Setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from utils.style import load_css
from utils.i18n import t, get_lang
from components.recipe_grid import get_recipe_image
from components.top_navigation import apply_page_style, render_top_navigation, render_footer

st.set_page_config(
    page_title="영양정보 - AI K-Food",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 공통 스타일 적용
apply_page_style()
load_css()


def get_comparison_recipes():
    """비교할 레시피 3개 가져오기"""
    # 검색 결과에서 선택된 레시피 근처 3개 가져오기
    search_results = st.session_state.get("search_results", [])
    selected_recipe = st.session_state.get("selected_recipe")

    if not search_results:
        return []

    # 선택된 레시피의 인덱스 찾기
    selected_idx = 0
    if selected_recipe:
        for i, r in enumerate(search_results):
            if r.get("name") == selected_recipe.get("name"):
                selected_idx = i
                break

    # 근처 3개 선택 (선택된 것 포함)
    start_idx = max(0, selected_idx)
    end_idx = min(len(search_results), start_idx + 3)

    if end_idx - start_idx < 3 and len(search_results) >= 3:
        start_idx = max(0, end_idx - 3)

    return search_results[start_idx:end_idx]


def render_donut_chart(protein: float, fat: float, carbs: float, calories: float):
    """주요 영양소 도넛 차트"""
    # 칼로리 기여도 계산
    protein_cal = protein * 4
    fat_cal = fat * 9
    carb_cal = carbs * 4
    total_cal = protein_cal + fat_cal + carb_cal

    if total_cal == 0:
        total_cal = 1  # 0으로 나누기 방지

    protein_pct = round(protein_cal / total_cal * 100)
    fat_pct = round(fat_cal / total_cal * 100)
    carb_pct = round(carb_cal / total_cal * 100)

    fig = go.Figure(data=[go.Pie(
        values=[carb_pct, protein_pct, fat_pct],
        labels=['탄수화물', '단백질', '지방'],
        hole=0.6,
        marker_colors=['#FFA726', '#66BB6A', '#BDBDBD'],
        textinfo='none',
        hovertemplate='%{label}: %{value}%<extra></extra>'
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=200,
        annotations=[dict(
            text=f'<b>{calories:.0f}</b><br>kcal',
            x=0.5, y=0.5,
            font_size=20,
            showarrow=False,
            font_color='#FFA726'
        )],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig, protein_pct, fat_pct, carb_pct


def get_nutrition_value(recipe: dict, key: str, default: float = 0) -> float:
    """레시피에서 영양소 값 가져오기 (nutrition 객체 또는 직접 접근, 없으면 추정)"""
    # 먼저 nutrition 객체에서 찾기
    nutrition = recipe.get("nutrition", {})
    if nutrition and key in nutrition:
        value = nutrition.get(key, default)
        if value and value > 0:
            return value

    # 직접 레시피 객체에서 찾기
    value = recipe.get(key, default)
    if value and value > 0:
        return value

    # 없으면 칼로리 기반으로 추정
    calories = recipe.get("calories", 0)
    if nutrition:
        calories = nutrition.get("calories", calories)

    if calories > 0:
        # 한식 기준 영양소 비율 추정 (단백질 20%, 탄수화물 50%, 지방 30%)
        if key == "protein":
            return round(calories * 0.20 / 4, 1)  # 단백질 1g = 4kcal
        elif key == "carbohydrate":
            return round(calories * 0.50 / 4, 1)  # 탄수화물 1g = 4kcal
        elif key == "fat":
            return round(calories * 0.30 / 9, 1)  # 지방 1g = 9kcal
        elif key == "sodium":
            return round(calories * 2, 0)  # 한식 특성상 칼로리당 2mg 정도
        elif key == "sugar":
            return round(calories * 0.05 / 4, 1)  # 당류 약 5%
        elif key == "saturated_fat":
            return round(calories * 0.10 / 9, 1)  # 포화지방 약 10%

    return default


def render_comparison_chart(recipes: list, nutrient_key: str, nutrient_name: str, color: str):
    """영양소별 비교 바 차트"""
    names = [r.get("name", "")[:6] for r in recipes]
    values = []

    for r in recipes:
        values.append(get_nutrition_value(r, nutrient_key, 0))

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=values,
            marker_color=color,
            text=[f'{v:.0f}' for v in values],
            textposition='outside'
        )
    ])

    fig.update_layout(
        title=dict(text=nutrient_name, font_size=12, x=0.5),
        showlegend=False,
        margin=dict(t=30, b=20, l=20, r=20),
        height=150,
        yaxis=dict(visible=False),
        xaxis=dict(tickfont=dict(size=9)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def main():
    # 상단 네비게이션
    nav_search = render_top_navigation(current_page="nutrition")

    # 네비게이션 검색 처리
    if nav_search:
        st.session_state.search_query = nav_search
        st.switch_page("pages/1_Recipe_Search.py")

    # 페이지 타이틀
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                {t("nutrition_title")}
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # 데이터 확인
    result = st.session_state.get("search_result", {})
    recipe = result.get("recipe", {})
    nutrition = result.get("nutrition") or {}

    if not recipe:
        st.info(t("search_first"))
        if st.button(t("go_to_recipe_search"), type="primary"):
            st.switch_page("pages/1_Recipe_Search.py")
        return

    food_name = recipe.get("name", nutrition.get("food_name", "음식") if nutrition else "음식")

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

    # ===== 상단: 음식 이미지 및 정보 =====
    col1, col2 = st.columns([1, 2])

    with col1:
        image_url = get_recipe_image(food_name, recipe.get("image_url", ""))
        st.image(image_url, use_container_width=True)

    with col2:
        st.markdown(f"## {food_name}")
        st.caption("달콤한 간장 양념에 재운 소고기를 구워 만든 한국의 대표적인 요리입니다.")

        # 즐겨찾기 버튼
        if st.button("⭐ 즐겨찾기", key="favorite_btn"):
            st.toast("즐겨찾기에 추가되었습니다!")

    st.divider()

    # ===== 칼로리 및 조리시간 =====
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem;">
                <p style="color: #6b7280; margin-bottom: 0.25rem; font-size: 0.875rem;">총 칼로리 (1인분)</p>
                <p style="color: #FFA726; font-size: 2rem; font-weight: 700; margin: 0;">{:.0f} kcal</p>
            </div>
        """.format(nutrition.get("calories", 0)), unsafe_allow_html=True)

    with col2:
        cooking_time = recipe.get("cooking_time", 30)
        st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem;">
                <p style="color: #6b7280; margin-bottom: 0.25rem; font-size: 0.875rem;">예상 조리 시간</p>
                <p style="color: #111827; font-size: 2rem; font-weight: 700; margin: 0;">{cooking_time}분</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ===== 주요 영양소 구성 및 일일 권장량 =====
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 주요 영양소 구성")

        protein = nutrition.get("protein", 0)
        fat = nutrition.get("fat", 0)
        carbs = nutrition.get("carbohydrate", 0)
        calories = nutrition.get("calories", 0)

        fig, protein_pct, fat_pct, carb_pct = render_donut_chart(protein, fat, carbs, calories)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 범례
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"🟠 탄수화물 ({carb_pct}%) **{carbs:.0f}g**")
        with col_b:
            st.markdown(f"🟢 단백질 ({protein_pct}%) **{protein:.0f}g**")
        with col_c:
            st.markdown(f"⚪ 지방 ({fat_pct}%) **{fat:.0f}g**")

    with col2:
        st.markdown("#### 일일 권장량 대비")

        # 나트륨
        sodium = nutrition.get("sodium", 0)
        sodium_daily = 2000
        sodium_pct = min(sodium / sodium_daily * 100, 100)
        st.markdown(f"**나트륨** <span style='color: #FFA726; float: right;'>{sodium:.0f}mg / {sodium_daily}mg ({sodium_pct:.0f}%)</span>", unsafe_allow_html=True)
        st.progress(sodium_pct / 100)

        # 당류
        sugar = nutrition.get("sugar", 0)
        sugar_daily = 50
        sugar_pct = min(sugar / sugar_daily * 100, 100)
        st.markdown(f"**당류** <span style='color: #FFA726; float: right;'>{sugar:.0f}g / {sugar_daily}g ({sugar_pct:.0f}%)</span>", unsafe_allow_html=True)
        st.progress(sugar_pct / 100)

        # 포화지방
        sat_fat = nutrition.get("saturated_fat", fat * 0.35)
        sat_fat_daily = 15
        sat_fat_pct = min(sat_fat / sat_fat_daily * 100, 100)
        st.markdown(f"**포화지방** <span style='color: #FFA726; float: right;'>{sat_fat:.0f}g / {sat_fat_daily}g ({sat_fat_pct:.0f}%)</span>", unsafe_allow_html=True)
        st.progress(sat_fat_pct / 100)

    st.divider()

    # ===== 상세 영양 성분표 =====
    st.markdown("#### 상세 영양 성분표")
    st.caption("1회 제공량 (300g) 기준")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**열량** {nutrition.get('calories', 0):.0f} kcal")
        st.markdown(f"**단백질** {nutrition.get('protein', 0):.1f} g")
        st.markdown(f"**트랜스지방** {nutrition.get('trans_fat', 0):.1f} g")

    with col2:
        st.markdown(f"**탄수화물** {nutrition.get('carbohydrate', 0):.0f} g")
        st.markdown(f"**지방** {nutrition.get('fat', 0):.0f} g")
        st.markdown(f"**콜레스테롤** {nutrition.get('cholesterol', 0):.0f} mg")

    with col3:
        st.markdown(f"**당류** {nutrition.get('sugar', 0):.1f} g")
        st.markdown(f"**포화지방** {nutrition.get('saturated_fat', fat * 0.35):.1f} g")
        st.markdown(f"**나트륨** {nutrition.get('sodium', 0):.0f} mg")

    st.divider()

    # ===== 영양 정보 비교하기 =====
    st.markdown("""
        <div style="background: #f9fafb; border-radius: 1rem; padding: 1.5rem; margin-top: 1rem;">
            <h4 style="font-weight: 600; color: #111827; margin-bottom: 0.5rem; text-align: center;">영양 정보 비교하기</h4>
            <p style="color: #6b7280; font-size: 0.875rem; text-align: center; margin-bottom: 1.5rem;">
                다른 음식과 영양 정보를 비교해보세요. 비교하고 싶은 음식을 검색하여 추가할 수 있습니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 비교할 레시피 가져오기
    comparison_recipes = get_comparison_recipes()

    if not comparison_recipes:
        comparison_recipes = [recipe]

    # 음식 카드 영역
    num_recipes = min(len(comparison_recipes), 2)
    card_cols = st.columns(3)

    for i in range(3):
        with card_cols[i]:
            if i < num_recipes:
                r = comparison_recipes[i]
                r_name = r.get("name", "")
                img_url = get_recipe_image(r_name, r.get("image_url", ""))
                st.markdown(f"""
                    <div style="background: white; border-radius: 0.75rem; padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
                        <img src="{img_url}" style="width: 100%; height: 100px; object-fit: cover; border-radius: 0.5rem; margin-bottom: 0.75rem;">
                        <p style="font-weight: 600; color: #111827; margin: 0; font-size: 0.95rem;">{r_name[:10]}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # 음식 추가하기 카드
                st.markdown("""
                    <div style="background: white; border-radius: 0.75rem; padding: 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 2px dashed #d1d5db; min-height: 140px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                        <div style="width: 40px; height: 40px; background: #f3f4f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem; color: #9ca3af;">+</span>
                        </div>
                        <p style="color: #9ca3af; margin: 0; font-size: 0.875rem;">음식 추가하기</p>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # 일일 권장량
    daily_values = {
        "calories": 2000,
        "carbohydrate": 324,
        "protein": 55,
        "fat": 54,
        "sodium": 2000
    }

    # 영양소 비교 테이블 (HTML 테이블로 구현)
    # 헤더 생성
    header_html = "<th style='padding: 0.75rem; text-align: left; font-weight: 600; color: #6b7280; background: #f9fafb;'>영양소</th>"
    for i, r in enumerate(comparison_recipes[:2]):
        r_name = r.get("name", "")[:8]
        header_html += f"<th style='padding: 0.75rem; text-align: center; font-weight: 600; color: #111827; background: #f9fafb;'>{r_name} (1인분)</th>"
    header_html += "<th style='padding: 0.75rem; text-align: center; font-weight: 600; color: #6b7280; background: #f9fafb;'>일일 권장량</th>"

    # 데이터 행 생성
    nutrients = [
        ("칼로리", "calories", "kcal"),
        ("탄수화물", "carbohydrate", "g"),
        ("단백질", "protein", "g"),
        ("지방", "fat", "g"),
        ("나트륨", "sodium", "mg")
    ]

    rows_html = ""
    for label, key, unit in nutrients:
        rows_html += f"<tr><td style='padding: 0.75rem; font-weight: 500; color: #374151; border-bottom: 1px solid #e5e7eb;'>{label}</td>"

        for i, r in enumerate(comparison_recipes[:2]):
            value = get_nutrition_value(r, key, 0)

            # 칼로리는 주황색, 나트륨 1000mg 이상은 빨간색
            if key == "calories":
                color = "#FFA726"
            elif key == "sodium" and value > 1000:
                color = "#dc2626"
            else:
                color = "#111827"

            rows_html += f"<td style='padding: 0.75rem; text-align: center; color: {color}; font-weight: 500; border-bottom: 1px solid #e5e7eb;'>{value:.0f} {unit}</td>"

        # 일일 권장량
        daily = daily_values.get(key, 0)
        rows_html += f"<td style='padding: 0.75rem; text-align: center; color: #6b7280; border-bottom: 1px solid #e5e7eb;'>{daily} {unit}</td>"
        rows_html += "</tr>"

    st.markdown(f"""
        <div style="background: white; border-radius: 0.75rem; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr>{header_html}</tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ===== 영양소별 비교 그래프 =====
    if len(comparison_recipes) >= 1:
        st.markdown("""
            <div style="background: #f9fafb; border-radius: 0.75rem; padding: 1.25rem; margin-bottom: 1.5rem;">
                <h4 style="font-weight: 600; color: #111827; margin-bottom: 1rem; text-align: center;">영양소별 비교 그래프</h4>
        """, unsafe_allow_html=True)

        chart_cols = st.columns(5)
        nutrients = [
            ("calories", "칼로리", "#FFA726"),
            ("carbohydrate", "탄수화물", "#66BB6A"),
            ("protein", "단백질", "#42A5F5"),
            ("fat", "지방", "#AB47BC"),
            ("sodium", "나트륨", "#EF5350")
        ]

        for col, (key, name, color) in zip(chart_cols, nutrients):
            with col:
                fig = render_comparison_chart(comparison_recipes[:2], key, name, color)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ===== 하단 버튼 =====
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        st.markdown("""
            <style>
                .recipe-btn {
                    display: block;
                    width: 100%;
                    padding: 1rem;
                    background: #FFA726;
                    color: white;
                    text-align: center;
                    border-radius: 0.5rem;
                    font-weight: 600;
                    text-decoration: none;
                    font-size: 1rem;
                }
                .recipe-btn:hover {
                    background: #FB8C00;
                }
            </style>
        """, unsafe_allow_html=True)
        if st.button("🍳 레시피 보기", type="secondary", use_container_width=True, key="recipe_btn"):
            st.switch_page("pages/1_Recipe_Search.py")

    with btn_col2:
        if st.button("🏃 이 음식에 맞는 운동 추천받기", type="primary", use_container_width=True, key="exercise_btn"):
            st.switch_page("pages/3_Workout_Recommendation.py")

    # 푸터
    render_footer()


if __name__ == "__main__":
    main()
