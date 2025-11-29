"""종합 페이지 (대시보드) - AI K-Food 디자인"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go

# Project Root Setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from utils.style import load_css
from utils.i18n import t, get_lang, set_lang
from components.recipe_grid import get_recipe_image
from components.top_navigation import apply_page_style, render_top_navigation, render_footer

st.set_page_config(
    page_title="종합 정보 - AI K-Food",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 공통 스타일 적용
apply_page_style()
load_css()


@st.cache_data(ttl=3600)
def generate_ai_summary(food_name: str, calories: float, protein: float, carbs: float, fat: float, cooking_time: int) -> str:
    """LLM을 사용하여 AI 요약 생성 (500자)"""
    try:
        from app.core.services.llm_service import LLMService
        llm_service = LLMService()

        lang = get_lang()

        if lang == "ko":
            prompt = f"""당신은 영양 전문가입니다. 아래 음식에 대해 한국어로 500자 내외의 상세한 건강 분석을 작성해주세요.

음식: {food_name}
칼로리: {calories:.0f}kcal
단백질: {protein:.0f}g
탄수화물: {carbs:.0f}g
지방: {fat:.0f}g
조리시간: {cooking_time}분

다음 내용을 포함해주세요:
1. 이 음식의 영양학적 특징과 장점
2. 어떤 사람들에게 추천하는지 (운동 전후, 다이어트 중, 성장기 등)
3. 함께 먹으면 좋은 음식이나 영양 밸런스 팁
4. 주의할 점이 있다면 간단히 언급

친근하고 전문적인 톤으로 작성해주세요. 마크다운 형식 없이 순수 텍스트로만 작성하세요."""
        else:
            prompt = f"""You are a nutrition expert. Write a detailed health analysis (about 400 characters) in English for the following food.

Food: {food_name}
Calories: {calories:.0f}kcal
Protein: {protein:.0f}g
Carbohydrates: {carbs:.0f}g
Fat: {fat:.0f}g
Cooking Time: {cooking_time} minutes

Include:
1. Nutritional benefits
2. Who should eat this (post-workout, diet, etc.)
3. Pairing suggestions
4. Any considerations

Write in a friendly, professional tone. Plain text only, no markdown."""

        response = llm_service.generate(prompt, max_tokens=600)
        return response.strip()
    except Exception as e:
        # LLM 실패 시 기본 텍스트 반환
        if get_lang() == "ko":
            return f"""{food_name}은(는) 한국의 대표적인 전통 음식으로, 균형 잡힌 영양소 구성이 특징입니다.

1인분 기준 {calories:.0f}kcal로 적당한 열량을 제공하며, 단백질 {protein:.0f}g, 탄수화물 {carbs:.0f}g, 지방 {fat:.0f}g의 균형 잡힌 영양 구성을 갖추고 있습니다.

특히 단백질 함량이 풍부하여 운동 후 근육 회복에 도움이 되며, 다이어트 중인 분들도 포만감을 느끼며 즐길 수 있습니다. 탄수화물은 적당량 포함되어 있어 에너지 공급원으로 적합합니다.

이 음식은 신선한 채소와 함께 먹으면 비타민과 식이섬유 섭취를 늘릴 수 있어 더욱 건강한 한 끼가 됩니다. 나트륨 섭취가 걱정된다면 국물은 조금 남기는 것을 권장합니다.

조리시간은 약 {cooking_time}분으로 비교적 간단하게 준비할 수 있어 바쁜 일상 속에서도 영양가 있는 식사를 즐길 수 있습니다."""
        else:
            return f"""{food_name} is a representative traditional Korean dish featuring a well-balanced nutritional composition.

At {calories:.0f}kcal per serving, it provides adequate energy with {protein:.0f}g protein, {carbs:.0f}g carbohydrates, and {fat:.0f}g fat.

The high protein content makes it excellent for post-workout muscle recovery. The moderate carbohydrate level provides sustained energy. Pair with fresh vegetables for added vitamins and fiber.

Cooking time is approximately {cooking_time} minutes, making it convenient for busy lifestyles while maintaining nutritional value."""


def render_donut_chart(calories: float, protein: float, carbs: float, fat: float):
    """영양 정보 도넛 차트"""
    fig = go.Figure(data=[go.Pie(
        values=[protein, carbs, fat],
        labels=['단백질', '탄수화물', '지방'] if get_lang() == "ko" else ['Protein', 'Carbs', 'Fat'],
        hole=0.7,
        marker_colors=['#22c55e', '#86efac', '#dcfce7'],
        textinfo='none',
        hovertemplate='%{label}: %{value}g<extra></extra>'
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=200,
        annotations=[dict(
            text=f'<b style="font-size: 24px; color: #22c55e;">{calories:.0f}</b><br><span style="font-size: 12px; color: #6b7280;">{t("total_calories_label")}</span>',
            x=0.5, y=0.5,
            font_size=14,
            showarrow=False
        )],
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_calorie_balance_bar(intake: float, burned: float):
    """칼로리 밸런스 수평 바 차트"""
    # 가로 스택 바 차트
    fig = go.Figure()

    # 식사 섭취량 (녹색)
    fig.add_trace(go.Bar(
        y=['칼로리'],
        x=[intake],
        name=t("food_intake") if get_lang() == "ko" else "Food Intake",
        orientation='h',
        marker_color='#22c55e',
        text=[f'+{intake:.0f}'],
        textposition='inside',
        textfont={'color': 'white', 'size': 12}
    ))

    # 운동 소모량 (주황색) - 음수 방향
    fig.add_trace(go.Bar(
        y=['칼로리'],
        x=[-burned],
        name=t("exercise_burn") if get_lang() == "ko" else "Exercise Burn",
        orientation='h',
        marker_color='#fb923c',
        text=[f'-{burned:.0f}'],
        textposition='inside',
        textfont={'color': 'white', 'size': 12}
    ))

    fig.update_layout(
        barmode='relative',
        height=80,
        margin=dict(t=5, b=5, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            range=[-600, 700],
            showgrid=False,
            zeroline=True,
            zerolinecolor='#e5e7eb',
            zerolinewidth=1,
            tickvals=[-500, 0, 500, 1000],
            ticktext=['-500', '0', '500', '1,000'],
            tickfont={'size': 10, 'color': '#9ca3af'}
        ),
        yaxis=dict(visible=False)
    )

    return fig


def calculate_exercises(calories: float, weight: float = 70) -> list:
    """칼로리 기반 운동 추천 계산"""
    exercises = [
        {"name": t("jogging"), "met": 7.0, "icon": "🏃", "color": "#22c55e"},
        {"name": t("hiit"), "met": 12.0, "icon": "⚡", "color": "#f59e0b"},
        {"name": t("stretching"), "met": 2.5, "icon": "🧘", "color": "#3b82f6"}
    ]

    result = []
    target_cals = [250, 200, 50]  # 목표 칼로리

    for ex, target in zip(exercises, target_cals):
        duration = target / (ex["met"] * weight / 60)
        result.append({
            "name": ex["name"],
            "duration": round(duration),
            "calories": target,
            "icon": ex["icon"],
            "color": ex["color"]
        })

    return result


def main():
    # 상단 네비게이션
    search_query = render_top_navigation(current_page="dashboard")

    # 검색 실행
    if search_query:
        from services.api_client import search_recipes_multiple
        with st.spinner(t("searching")):
            results = search_recipes_multiple(search_query, limit=1)
            if results.get("success") and results.get("recipes"):
                first_recipe = results["recipes"][0]
                st.session_state.search_result = {
                    "success": True,
                    "recipe": first_recipe,
                    "nutrition": results.get("nutrition") or first_recipe.get("nutrition"),
                    "exercises": results.get("exercises", []),
                    "analyzed_query": {"food_name": search_query, "servings": 1}
                }
                st.session_state.selected_recipe = first_recipe
                st.rerun()

    # 데이터 확인
    result = st.session_state.get("search_result", {})
    recipe = result.get("recipe", {})
    nutrition = result.get("nutrition") or recipe.get("nutrition") or {}

    if not recipe:
        st.info(t("search_first"))
        if st.button(t("go_to_recipe_search"), type="primary"):
            st.switch_page("pages/1_Recipe_Search.py")
        return

    food_name = recipe.get("name", "음식")

    # 영양정보 기본값
    if not nutrition:
        nutrition = {
            "calories": recipe.get("calories", 580),
            "protein": 30,
            "carbohydrate": 75,
            "fat": 18
        }

    calories = nutrition.get("calories", 580)
    protein = nutrition.get("protein", 30)
    carbs = nutrition.get("carbohydrate", 75)
    fat = nutrition.get("fat", 18)
    cooking_time = recipe.get("cooking_time", 35)

    # ===== 페이지 타이틀 =====
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #111827; margin-bottom: 0.75rem; letter-spacing: -0.03em;">
                {food_name}: {t("dashboard_title")}
            </h1>
            <p style="color: #22c55e; font-size: 1.05rem; font-weight: 500;">{t("dashboard_subtitle")}</p>
        </div>
    """, unsafe_allow_html=True)

    # ===== AI 요약 카드 (LLM 생성) =====
    with st.spinner("AI 분석 중..." if get_lang() == "ko" else "AI analyzing..."):
        ai_summary_text = generate_ai_summary(food_name, calories, protein, carbs, fat, cooking_time)

    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 1rem; padding: 1.75rem; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(34,197,94,0.1); border: 1px solid #bbf7d0;">
            <p style="font-weight: 700; color: #166534; margin-bottom: 1rem; font-size: 1.15rem; display: flex; align-items: center; gap: 0.5rem;">
                🤖 {t("ai_summary")}
            </p>
            <p style="color: #374151; margin-bottom: 1.25rem; line-height: 1.9; white-space: pre-line; font-size: 0.95rem;">{ai_summary_text}</p>
            <div style="display: flex; gap: 2rem; padding-top: 1rem; border-top: 1px solid #bbf7d0;">
                <span style="color: #166534; font-weight: 600; font-size: 1rem;">🔥 {calories:.0f} kcal</span>
                <span style="color: #166534; font-weight: 600; font-size: 1rem;">⏱️ {cooking_time}{t("minutes")}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ===== 메인 컨텐츠 (2열) =====
    col_left, col_right = st.columns([1.2, 1], gap="large")

    with col_left:
        # 음식 이미지 + 정보 카드 (통합)
        image_url = get_recipe_image(food_name, recipe.get("image_url", ""))

        # 설명 텍스트
        description = recipe.get("description", "")
        if not description:
            description = "다양한 채소, 양념 고기, 매콤한 고추장 소스를 곁들인 한국의 대표적인 비빔밥입니다. 활기차고 영양가 있는 한 그릇 식사입니다." if get_lang() == "ko" else "A traditional Korean dish with various vegetables, seasoned meat, and spicy gochujang sauce. A vibrant and nutritious one-bowl meal."

        st.markdown(f"""
            <div style="background: white; border-radius: 1rem; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <img src="{image_url}" style="width: 100%; height: 300px; object-fit: cover;">
                <div style="padding: 1.5rem;">
                    <p style="color: #22c55e; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">{t("main_dish")}</p>
                    <h3 style="font-size: 1.75rem; font-weight: 700; color: #111827; margin-bottom: 1rem; letter-spacing: -0.02em;">{food_name}</h3>
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap;">
                        <span style="background: #f3f4f6; padding: 0.35rem 0.85rem; border-radius: 1rem; font-size: 0.85rem; color: #374151;">{t("tag_spicy")}</span>
                        <span style="background: #f3f4f6; padding: 0.35rem 0.85rem; border-radius: 1rem; font-size: 0.85rem; color: #374151;">{t("tag_vegetarian")}</span>
                        <span style="background: #f3f4f6; padding: 0.35rem 0.85rem; border-radius: 1rem; font-size: 0.85rem; color: #374151;">{t("tag_easy")}</span>
                    </div>
                    <p style="color: #374151; line-height: 1.7; margin-bottom: 1rem; font-size: 0.95rem;">{description}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #6b7280; font-size: 0.9rem;">{t("rating")}: 4.5{t("rating_suffix")}</span>
                        <a href="#" onclick="return false;" style="display: inline-block; padding: 0.5rem 1.25rem; border: 2px solid #22c55e; border-radius: 0.5rem; color: #22c55e; text-decoration: none; font-weight: 500; font-size: 0.9rem;">{t("start_cooking")}...</a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 실제 동작하는 버튼 (숨김 처리하고 클릭 이벤트용)
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        if st.button(f"🍳 {t('view_recipe_detail')}", type="secondary", use_container_width=True, key="recipe_detail_btn"):
            st.switch_page("pages/1_Recipe_Search.py")

    with col_right:
        # 영양 정보 카드
        st.markdown(f"""
            <div style="background: white; border-radius: 1rem; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <h4 style="font-weight: 600; color: #111827; margin-bottom: 1rem; font-size: 1.15rem;">{t("nutrition_info")}</h4>
        """, unsafe_allow_html=True)

        # 도넛 차트
        fig = render_donut_chart(calories, protein, carbs, fat)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 영양소 수치
        nut_col1, nut_col2, nut_col3 = st.columns(3)
        with nut_col1:
            st.markdown(f"""
                <div style="text-align: center;">
                    <p style="font-size: 1.25rem; font-weight: 700; color: #111827;">{protein:.0f}g</p>
                    <p style="font-size: 0.75rem; color: #22c55e;">{t("protein")}</p>
                </div>
            """, unsafe_allow_html=True)
        with nut_col2:
            st.markdown(f"""
                <div style="text-align: center;">
                    <p style="font-size: 1.25rem; font-weight: 700; color: #111827;">{carbs:.0f}g</p>
                    <p style="font-size: 0.75rem; color: #22c55e;">{t("carbohydrate")}</p>
                </div>
            """, unsafe_allow_html=True)
        with nut_col3:
            st.markdown(f"""
                <div style="text-align: center;">
                    <p style="font-size: 1.25rem; font-weight: 700; color: #111827;">{fat:.0f}g</p>
                    <p style="font-size: 0.75rem; color: #22c55e;">{t("fat")}</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # 칼로리 밸런스 카드
        st.markdown(f"""
            <div style="background: white; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <h4 style="font-weight: 600; color: #111827; margin-bottom: 1rem; font-size: 1.15rem;">{t("calorie_balance")}</h4>
        """, unsafe_allow_html=True)

        # 칼로리 밸런스 수평 바 차트
        total_burned = 500  # 예상 운동 소모량
        fig_bar = render_calorie_balance_bar(calories, total_burned)
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

        # 범례
        st.markdown(f"""
            <div style="display: flex; justify-content: center; gap: 2rem; margin: 0.75rem 0 1.25rem 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 12px; height: 12px; background: #22c55e; border-radius: 2px;"></span>
                    <span style="font-size: 0.8rem; color: #6b7280;">{t("food_intake")}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="width: 12px; height: 12px; background: #fb923c; border-radius: 2px;"></span>
                    <span style="font-size: 0.8rem; color: #6b7280;">{t("exercise_burn")}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 운동 추천 목록
        exercises = calculate_exercises(calories)

        for ex in exercises:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 0; border-bottom: 1px solid #f3f4f6;">
                    <div style="width: 40px; height: 40px; background: #dcfce7; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <span style="color: #22c55e; font-size: 1.1rem;">{ex['icon']}</span>
                    </div>
                    <div style="flex: 1;">
                        <p style="font-weight: 500; color: #111827; margin: 0; font-size: 0.95rem;">{ex['duration']}{t("minutes")} {ex['name']}</p>
                        <p style="font-size: 0.85rem; color: #22c55e; margin: 0;">-{ex['calories']} kcal</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 푸터
    render_footer()


if __name__ == "__main__":
    main()
