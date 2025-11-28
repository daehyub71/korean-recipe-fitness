"""
Korean Recipe & Fitness Advisor - Streamlit UI
한식 레시피 검색, 영양정보 분석, 운동 추천 서비스
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트 및 streamlit_app 추가
PROJECT_ROOT = Path(__file__).parent.parent
STREAMLIT_APP = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from components.recipe_card import render_recipe_card
from components.nutrition_card import render_nutrition_card
from components.exercise_card import render_exercise_card
from services.api_client import search_recipe

# 페이지 설정
st.set_page_config(
    page_title="Korean Recipe & Fitness Advisor",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .search-box {
        margin: 2rem auto;
        max-width: 600px;
    }
    .result-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """세션 상태 초기화"""
    if "search_result" not in st.session_state:
        st.session_state.search_result = None
    if "search_history" not in st.session_state:
        st.session_state.search_history = []


def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.header("👤 사용자 프로필")

        weight = st.number_input(
            "체중 (kg)",
            min_value=30.0,
            max_value=200.0,
            value=70.0,
            step=0.5
        )

        height = st.number_input(
            "키 (cm)",
            min_value=100.0,
            max_value=250.0,
            value=170.0,
            step=0.5
        )

        age = st.number_input(
            "나이",
            min_value=10,
            max_value=100,
            value=30,
            step=1
        )

        gender = st.selectbox(
            "성별",
            options=["male", "female"],
            format_func=lambda x: "남성" if x == "male" else "여성"
        )

        activity_level = st.selectbox(
            "활동 수준",
            options=["sedentary", "light", "moderate", "active", "very_active"],
            index=2,
            format_func=lambda x: {
                "sedentary": "좌식 (거의 운동 안함)",
                "light": "가벼움 (주 1-3회)",
                "moderate": "보통 (주 3-5회)",
                "active": "활발 (주 6-7회)",
                "very_active": "매우 활발 (하루 2회)"
            }.get(x, x)
        )

        st.divider()

        # BMI 계산
        height_m = height / 100
        bmi = weight / (height_m ** 2)

        st.metric("BMI", f"{bmi:.1f}")

        if bmi < 18.5:
            st.caption("저체중")
        elif bmi < 25:
            st.caption("정상")
        elif bmi < 30:
            st.caption("과체중")
        else:
            st.caption("비만")

        st.divider()

        # 검색 기록
        if st.session_state.search_history:
            st.subheader("🕐 검색 기록")
            for query in st.session_state.search_history[-5:][::-1]:
                if st.button(query, key=f"history_{query}"):
                    st.session_state.current_query = query
                    st.rerun()

        return {
            "weight": weight,
            "height": height,
            "age": age,
            "gender": gender,
            "activity_level": activity_level
        }


def render_main_content(user_profile: dict):
    """메인 콘텐츠 렌더링"""
    # 헤더
    st.markdown('<p class="main-header">🍳 Korean Recipe & Fitness Advisor</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">한식 레시피 검색, 영양정보 분석, 운동 추천 서비스</p>', unsafe_allow_html=True)

    # 검색 영역
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        query = st.text_input(
            "검색어를 입력하세요",
            placeholder="예: 김치찌개 2인분 레시피",
            key="search_input",
            label_visibility="collapsed"
        )

        # 예시 검색어
        st.caption("💡 예시: 김치찌개 2인분 레시피 | 불고기 만드는 법 | 된장국 영양정보")

        search_clicked = st.button("🔍 검색", type="primary", use_container_width=True)

    # 검색 실행
    if search_clicked and query:
        with st.spinner("검색 중..."):
            result = search_recipe(query, user_profile)
            st.session_state.search_result = result

            # 검색 기록 추가
            if query not in st.session_state.search_history:
                st.session_state.search_history.append(query)

    # 결과 표시
    if st.session_state.search_result:
        render_search_result(st.session_state.search_result)


def render_search_result(result: dict):
    """검색 결과 렌더링"""
    if not result.get("success", False):
        st.error(f"검색 실패: {result.get('error', '알 수 없는 오류')}")
        return

    # 분석된 쿼리 정보
    analyzed = result.get("analyzed_query")
    if analyzed:
        st.info(f"🔍 **{analyzed.get('food_name', '')}** {analyzed.get('servings', 1)}인분 검색 결과")

    # 탭으로 결과 표시
    tab1, tab2, tab3, tab4 = st.tabs(["📖 레시피", "📊 영양정보", "🏃 운동 추천", "💬 AI 응답"])

    with tab1:
        recipe = result.get("recipe")
        if recipe:
            render_recipe_card(recipe)
        else:
            st.warning("레시피를 찾을 수 없습니다.")

    with tab2:
        nutrition = result.get("nutrition")
        if nutrition:
            render_nutrition_card(nutrition)
        else:
            st.warning("영양정보를 찾을 수 없습니다.")

    with tab3:
        exercises = result.get("exercises", [])
        if exercises:
            render_exercise_card(exercises)
        else:
            st.warning("운동 추천 정보가 없습니다.")

    with tab4:
        response_text = result.get("response", "")
        if response_text:
            st.markdown(response_text)
        else:
            st.info("AI 응답이 없습니다.")

    # 처리 시간
    processing_time = result.get("processing_time_ms", 0)
    st.caption(f"⏱️ 처리 시간: {processing_time:.0f}ms")


def main():
    """메인 함수"""
    init_session_state()
    user_profile = render_sidebar()
    render_main_content(user_profile)


if __name__ == "__main__":
    main()
