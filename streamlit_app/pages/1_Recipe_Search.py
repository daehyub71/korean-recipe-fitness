"""레시피 검색 페이지 - AI K-Food 디자인"""

import streamlit as st
import base64
import sys
from pathlib import Path

# Project Root Setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from services.api_client import search_recipe, search_recipes_multiple
from components.recipe_card import render_recipe_card
from components.recipe_grid import render_recipe_grid, render_pagination, get_recipe_image
from components.top_navigation import apply_page_style, render_footer
from utils.style import load_css
from utils.i18n import t, get_lang, set_lang

st.set_page_config(
    page_title="레시피 검색 - AI K-Food",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 공통 스타일 적용
apply_page_style()
load_css()


def get_base64_image(image_path: str) -> str:
    """이미지를 base64로 인코딩"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


def render_hero_navigation():
    """히어로 섹션용 네비게이션 바"""
    lang = get_lang()

    st.markdown("""
        <style>
            .hero-nav {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem 2rem;
                background: rgba(255,255,255,0.95);
                border-radius: 0 0 1rem 1rem;
            }
            .hero-nav-logo {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .hero-nav-logo span:first-child {
                font-size: 1.5rem;
            }
            .hero-nav-logo span:last-child {
                font-weight: 700;
                font-size: 1.25rem;
                color: #ef4444;
            }
            .hero-nav-menu {
                display: flex;
                gap: 2rem;
            }
            .hero-nav-menu a {
                color: #374151;
                text-decoration: none;
                font-weight: 500;
                font-size: 0.95rem;
            }
            .hero-nav-menu a:hover {
                color: #ef4444;
            }
            .hero-nav-right {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            .login-btn {
                background: #ef4444;
                color: white;
                padding: 0.5rem 1.25rem;
                border-radius: 0.5rem;
                text-decoration: none;
                font-weight: 500;
                font-size: 0.9rem;
            }
            .lang-toggle {
                display: flex;
                gap: 0.5rem;
            }
            .lang-toggle span {
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
                font-size: 0.85rem;
                cursor: pointer;
            }
            .lang-toggle span.active {
                background: #f3f4f6;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

    # 네비게이션 바
    nav_col1, nav_col2, nav_col3 = st.columns([2, 4, 2])

    with nav_col1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0;">
                <span style="font-size: 1.5rem;">🍲</span>
                <span style="font-weight: 700; font-size: 1.25rem; color: #ef4444;">AI K-Food</span>
            </div>
        """, unsafe_allow_html=True)

    with nav_col2:
        menu_cols = st.columns(4)
        with menu_cols[0]:
            if st.button("레시피 검색", key="nav_recipe", type="primary", use_container_width=True):
                pass  # 현재 페이지
        with menu_cols[1]:
            if st.button("영양정보", key="nav_nutrition", type="secondary", use_container_width=True):
                st.switch_page("pages/2_Nutrition_Info.py")
        with menu_cols[2]:
            if st.button("운동 추천", key="nav_exercise", type="secondary", use_container_width=True):
                st.switch_page("pages/3_Workout_Recommendation.py")
        with menu_cols[3]:
            if st.button("종합정보", key="nav_dashboard", type="secondary", use_container_width=True):
                st.switch_page("pages/4_Dashboard.py")

    with nav_col3:
        right_cols = st.columns([2, 1, 1])
        with right_cols[0]:
            st.markdown("""
                <div style="background: #ef4444; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-align: center; font-weight: 500; font-size: 0.9rem; margin-top: 0.25rem;">
                    로그인
                </div>
            """, unsafe_allow_html=True)
        with right_cols[1]:
            if st.button("KO", key="lang_ko", type="primary" if lang == "ko" else "secondary", use_container_width=True):
                set_lang("ko")
                st.rerun()
        with right_cols[2]:
            if st.button("EN", key="lang_en", type="primary" if lang == "en" else "secondary", use_container_width=True):
                set_lang("en")
                st.rerun()


def render_hero_section():
    """히어로 섹션 (배경 이미지 + 검색창)"""
    # 배경 이미지 로드
    hero_image_path = STREAMLIT_APP / "assets" / "images" / "hero_background.jpg"
    hero_base64 = get_base64_image(str(hero_image_path))

    st.markdown(f"""
        <style>
            .hero-section {{
                background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)),
                            url('data:image/jpeg;base64,{hero_base64}');
                background-size: cover;
                background-position: center;
                padding: 4rem 2rem;
                border-radius: 1rem;
                margin: 1rem 0 2rem 0;
                text-align: center;
            }}
            .hero-title {{
                color: white !important;
                font-size: 2.5rem !important;
                font-weight: 700 !important;
                margin-bottom: 2rem !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
                letter-spacing: -0.02em !important;
            }}
            .hero-search-container {{
                max-width: 600px;
                margin: 0 auto;
                display: flex;
                gap: 0.5rem;
            }}
            .hero-search-input {{
                flex: 1;
                padding: 1rem 1.5rem;
                border: none;
                border-radius: 0.5rem;
                font-size: 1rem;
                outline: none;
            }}
            .hero-search-btn {{
                padding: 1rem 2rem;
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 0.5rem;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
            }}
            .hero-search-btn:hover {{
                background: #dc2626;
            }}
        </style>
        <div class="hero-section">
            <h1 class="hero-title">{t("main_title")}</h1>
        </div>
    """, unsafe_allow_html=True)


def render_recipe_card_new(recipe: dict, idx: int):
    """새로운 스타일의 레시피 카드"""
    name = recipe.get("name", "음식")
    calories = recipe.get("calories", 0)
    cooking_time = recipe.get("cooking_time", 30)
    difficulty = recipe.get("difficulty", "쉬움")
    image_url = get_recipe_image(name, recipe.get("image_url", ""))

    # 난이도 텍스트
    difficulty_map = {
        "easy": "쉬움", "medium": "보통", "hard": "어려움",
        "쉬움": "쉬움", "보통": "보통", "어려움": "어려움"
    }
    difficulty_text = difficulty_map.get(difficulty, "쉬움")

    st.markdown(f"""
        <div style="background: white; border-radius: 1rem; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08); height: 100%;">
            <img src="{image_url}" style="width: 100%; height: 180px; object-fit: cover;">
            <div style="padding: 1.25rem;">
                <h3 style="font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 1rem; letter-spacing: -0.01em;">{name}</h3>
                <div style="display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1.25rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem;">
                        <span>🔥</span>
                        <span>칼로리: {calories}kcal</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem;">
                        <span>⏱</span>
                        <span>조리 시간: {cooking_time}분</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: #6b7280; font-size: 0.9rem;">
                        <span>📊</span>
                        <span>난이도: {difficulty_text}</span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 레시피 보기 버튼
    if st.button("레시피 보기", key=f"view_recipe_{idx}", type="primary", use_container_width=True):
        st.session_state.selected_recipe = recipe
        st.session_state.show_recipe_detail = True
        # search_result 업데이트
        st.session_state.search_result = {
            "success": True,
            "recipe": recipe,
            "nutrition": recipe.get("nutrition"),
            "exercises": [],
            "analyzed_query": {"food_name": name, "servings": 1}
        }
        st.rerun()


def render_pagination_new(total_items: int, items_per_page: int, current_page: int) -> int:
    """페이지네이션 렌더링"""
    total_pages = (total_items + items_per_page - 1) // items_per_page

    if total_pages <= 1:
        return current_page

    # 페이지 버튼들
    cols = st.columns([2, 1, 1, 1, 1, 1, 2])

    with cols[0]:
        if st.button("◀", key="prev_page", disabled=(current_page <= 1)):
            return current_page - 1

    # 페이지 번호 (최대 3개 표시)
    start_page = max(1, current_page - 1)
    end_page = min(total_pages, start_page + 2)

    page_cols = [cols[1], cols[2], cols[3]]
    for i, page in enumerate(range(start_page, end_page + 1)):
        if i < len(page_cols):
            with page_cols[i]:
                btn_type = "primary" if page == current_page else "secondary"
                if st.button(str(page), key=f"page_{page}", type=btn_type, use_container_width=True):
                    return page

    with cols[6]:
        if st.button("▶", key="next_page", disabled=(current_page >= total_pages)):
            return current_page + 1

    return current_page


def main():
    # 히어로 네비게이션
    render_hero_navigation()

    # 히어로 섹션
    render_hero_section()

    # 검색 바 (히어로 섹션 아래)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        with st.form(key="search_form", clear_on_submit=False):
            search_col1, search_col2 = st.columns([5, 1])
            with search_col1:
                query = st.text_input(
                    "검색",
                    placeholder=t("search_placeholder"),
                    key="search_input",
                    label_visibility="collapsed"
                )
            with search_col2:
                search_clicked = st.form_submit_button(
                    "검색",
                    type="primary",
                    use_container_width=True
                )

    # 스타일 오버라이드 - 검색 버튼 색상
    st.markdown("""
        <style>
            /* 검색 버튼 coral 색상 */
            div[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] {
                background-color: #ef4444 !important;
                border-color: #ef4444 !important;
            }
            div[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]:hover {
                background-color: #dc2626 !important;
                border-color: #dc2626 !important;
            }

            /* 레시피 보기 버튼 coral 색상 */
            button[kind="primary"] {
                background-color: #ef4444 !important;
                border-color: #ef4444 !important;
            }
            button[kind="primary"]:hover {
                background-color: #dc2626 !important;
                border-color: #dc2626 !important;
            }

            /* 페이지 배경 */
            .stApp {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            }
        </style>
    """, unsafe_allow_html=True)

    # 검색 실행
    if search_clicked and query:
        with st.spinner(t("searching")):
            results = search_recipes_multiple(query, limit=9)

            if results.get("success") and results.get("recipes"):
                st.session_state.search_results = results["recipes"]
                st.session_state.search_query = query
                st.session_state.current_page = 1

                first_recipe = results["recipes"][0]
                st.session_state.search_result = {
                    "success": True,
                    "recipe": first_recipe,
                    "nutrition": results.get("nutrition"),
                    "exercises": results.get("exercises", []),
                    "analyzed_query": {"food_name": query, "servings": 1}
                }
            else:
                st.warning(t("no_results"))

    # 검색 결과 표시
    if "search_results" in st.session_state and st.session_state.search_results:
        recipes = st.session_state.search_results
        query = st.session_state.get("search_query", "")

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # 결과 헤더
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.markdown(f"""
                <h3 style="font-size: 1.25rem; font-weight: 600; color: #111827;">
                    '{query}' {t('search_results')}
                </h3>
            """, unsafe_allow_html=True)
        with header_col2:
            sort_options = ["최신순", "칼로리 낮은순", "칼로리 높은순"]
            sort_option = st.selectbox(
                "정렬",
                sort_options,
                label_visibility="collapsed"
            )

        # 정렬 적용
        if sort_option == "칼로리 낮은순":
            recipes = sorted(recipes, key=lambda x: x.get("calories", 0))
        elif sort_option == "칼로리 높은순":
            recipes = sorted(recipes, key=lambda x: x.get("calories", 0), reverse=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # 페이지네이션
        items_per_page = 9
        current_page = st.session_state.get("current_page", 1)
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_recipes = recipes[start_idx:end_idx]

        # 3열 그리드로 레시피 카드 렌더링
        for row_idx in range(0, len(page_recipes), 3):
            cols = st.columns(3, gap="medium")
            for col_idx, col in enumerate(cols):
                recipe_idx = row_idx + col_idx
                if recipe_idx < len(page_recipes):
                    with col:
                        render_recipe_card_new(page_recipes[recipe_idx], start_idx + recipe_idx)

        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

        # 페이지네이션
        if len(recipes) > items_per_page:
            new_page = render_pagination_new(len(recipes), items_per_page, current_page)
            if new_page != current_page:
                st.session_state.current_page = new_page
                st.rerun()

    # 선택된 레시피 상세 보기
    if st.session_state.get("show_recipe_detail") and st.session_state.get("selected_recipe"):
        st.divider()
        st.markdown(f"### 📖 {t('recipe_detail')}")
        render_recipe_card(st.session_state.selected_recipe)

        # 상세 정보 세션에 저장
        current_recipe_name = st.session_state.selected_recipe.get("name", "")
        stored_recipe_name = st.session_state.get("search_result", {}).get("recipe", {}).get("name", "")

        if current_recipe_name != stored_recipe_name:
            st.session_state.search_result = {
                "success": True,
                "recipe": st.session_state.selected_recipe,
                "nutrition": st.session_state.selected_recipe.get("nutrition"),
                "exercises": [],
                "analyzed_query": {
                    "food_name": current_recipe_name,
                    "servings": 1
                }
            }

    # 푸터
    render_footer()


if __name__ == "__main__":
    main()
