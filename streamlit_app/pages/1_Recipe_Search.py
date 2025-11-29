"""레시피 검색 페이지 - AI K-Food 디자인"""

import streamlit as st
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
from components.top_navigation import apply_page_style, render_top_navigation, render_footer
from utils.style import load_css
from utils.i18n import t, get_lang

st.set_page_config(
    page_title="레시피 검색 - AI K-Food",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 공통 스타일 적용
apply_page_style()
load_css()


def main():
    # 상단 네비게이션
    render_top_navigation(current_page="recipe")

    # 페이지 타이틀
    st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="font-size: 2.25rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; letter-spacing: -0.02em;">
                {t("main_title")}
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # 검색 바 (Form으로 감싸서 Enter 키로 검색 가능)
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

        # 페이지네이션
        items_per_page = 9
        current_page = st.session_state.get("current_page", 1)
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_recipes = recipes[start_idx:end_idx]

        # 그리드 렌더링
        render_recipe_grid(page_recipes)

        # 페이지네이션
        if len(recipes) > items_per_page:
            new_page = render_pagination(len(recipes), items_per_page, current_page)
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
