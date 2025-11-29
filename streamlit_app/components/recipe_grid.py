"""레시피 그리드 카드 컴포넌트 - AI K-Food 디자인"""

import streamlit as st
from typing import List, Dict, Optional
import os


@st.cache_data(ttl=3600)
def get_recipe_image(food_name: str, image_url: str = "") -> str:
    """레시피 이미지 URL 반환 (캐싱됨)"""
    from utils.images import get_food_image_url

    # 1. 이미 생성된 Vertex AI 이미지 확인 (새로 생성하지 않음)
    generated_dir = "streamlit_app/assets/images/generated"
    safe_name = "".join([c if c.isalnum() else "_" for c in food_name]).lower()
    generated_path = os.path.join(generated_dir, f"{safe_name}.png")

    if os.path.exists(generated_path):
        return generated_path

    # 2. 원본 이미지 URL
    if image_url:
        return image_url

    # 3. Fallback - 매핑된 이미지
    return get_food_image_url(food_name)


def render_recipe_card_html(recipe: Dict, index: int) -> str:
    """레시피 카드 HTML 생성"""
    name = recipe.get("name", "레시피")
    calories = recipe.get("calories", 0)
    cooking_time = recipe.get("cooking_time", 30)
    difficulty = recipe.get("difficulty", "보통")
    image_url = recipe.get("image_url", "")

    # 난이도 아이콘
    difficulty_icon = "📊"
    if difficulty == "쉬움":
        difficulty_icon = "🟢"
    elif difficulty == "보통":
        difficulty_icon = "🟡"
    elif difficulty == "어려움":
        difficulty_icon = "🔴"

    return f"""
    <div class="recipe-card">
        <img src="{image_url}" class="recipe-card-image" alt="{name}" onerror="this.src='https://via.placeholder.com/400x200?text={name}'">
        <div class="recipe-card-content">
            <h3 class="recipe-card-title">{name}</h3>
            <div class="recipe-card-info">
                <span>🔥 칼로리: {calories:.0f}kcal</span>
            </div>
            <div class="recipe-card-info">
                <span>⏱️ 조리 시간: {cooking_time}분</span>
            </div>
            <div class="recipe-card-info">
                <span>{difficulty_icon} 난이도: {difficulty}</span>
            </div>
        </div>
    </div>
    """


def render_recipe_grid(recipes: List[Dict], on_select_callback=None):
    """
    레시피 그리드 렌더링 (Streamlit 네이티브)

    Args:
        recipes: 레시피 목록
        on_select_callback: 레시피 선택 시 콜백
    """
    if not recipes:
        st.info("검색 결과가 없습니다. 다른 검색어를 시도해보세요.")
        return

    # 3열 그리드
    cols = st.columns(3)

    for i, recipe in enumerate(recipes):
        with cols[i % 3]:
            render_single_card(recipe, i)


def render_single_card(recipe: Dict, index: int):
    """단일 레시피 카드 렌더링"""
    name = recipe.get("name", "레시피")
    calories = recipe.get("calories", 0)
    cooking_time = recipe.get("cooking_time", 30)
    difficulty = recipe.get("difficulty", "보통")

    # 이미지 (캐싱된 함수 사용)
    image_url = get_recipe_image(name, recipe.get("image_url", ""))

    # 카드 컨테이너
    with st.container():
        # 이미지
        try:
            st.image(image_url, use_container_width=True)
        except Exception:
            st.image("https://via.placeholder.com/400x200?text=Image", use_container_width=True)

        # 제목
        st.markdown(f"**{name}**")

        # 정보
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"🔥 {calories:.0f}kcal")
            st.caption(f"⏱️ {cooking_time}분")
        with col2:
            difficulty_emoji = "🟢" if difficulty == "쉬움" else ("🟡" if difficulty == "보통" else "🔴")
            st.caption(f"{difficulty_emoji} {difficulty}")

        # 버튼
        if st.button("레시피 보기", key=f"recipe_btn_{index}", type="secondary", use_container_width=True):
            st.session_state.selected_recipe = recipe
            st.session_state.show_recipe_detail = True


def render_pagination(total_items: int, items_per_page: int = 9, current_page: int = 1):
    """페이지네이션 렌더링"""
    total_pages = (total_items + items_per_page - 1) // items_per_page

    if total_pages <= 1:
        return current_page

    cols = st.columns([2, 1, 1, 1, 2])

    with cols[0]:
        if st.button("◀", disabled=current_page <= 1):
            return current_page - 1

    for i, col in enumerate(cols[1:4]):
        page_num = current_page - 1 + i
        if 1 <= page_num <= total_pages:
            with col:
                if st.button(str(page_num), type="primary" if page_num == current_page else "secondary"):
                    return page_num

    with cols[4]:
        if st.button("▶", disabled=current_page >= total_pages):
            return current_page + 1

    return current_page
