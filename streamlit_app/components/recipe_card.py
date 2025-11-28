"""레시피 카드 컴포넌트"""

import streamlit as st
from typing import Dict, List


def render_recipe_card(recipe: Dict):
    """
    레시피 카드 렌더링

    Args:
        recipe: 레시피 정보 딕셔너리
    """
    if not recipe:
        st.warning("레시피 정보가 없습니다.")
        return

    # 레시피 이름 및 카테고리
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"🍳 {recipe.get('name', '레시피')}")
    with col2:
        source = recipe.get("source", "database")
        if source == "llm_fallback":
            st.caption("🤖 AI 생성 레시피")
        else:
            st.caption("📚 DB 레시피")

    # 메타 정보
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        category = recipe.get("category", "")
        if category:
            st.markdown(f"**분류:** {category}")
    with meta_col2:
        cooking_method = recipe.get("cooking_method", "")
        if cooking_method:
            st.markdown(f"**조리법:** {cooking_method}")
    with meta_col3:
        recipe_id = recipe.get("recipe_id", "")
        if recipe_id:
            st.markdown(f"**레시피 ID:** {recipe_id}")

    st.divider()

    # 이미지 (있는 경우)
    image_url = recipe.get("image_url", "")
    if image_url:
        try:
            st.image(image_url, width=400, caption=recipe.get("name", ""))
        except Exception:
            pass

    # 재료
    st.markdown("### 📋 재료")
    ingredients = recipe.get("ingredients", [])
    if ingredients:
        # 2열로 표시
        cols = st.columns(2)
        for i, ingredient in enumerate(ingredients):
            with cols[i % 2]:
                st.markdown(f"• {ingredient}")
    else:
        st.info("재료 정보가 없습니다.")

    st.divider()

    # 조리 순서
    st.markdown("### 👨‍🍳 조리 순서")
    instructions = recipe.get("instructions", [])
    if instructions:
        for i, step in enumerate(instructions, 1):
            # 이미 번호가 있으면 그대로, 없으면 추가
            if not step.strip().startswith(str(i)):
                st.markdown(f"**{i}.** {step}")
            else:
                st.markdown(f"**{step}**" if step[0].isdigit() else step)
    else:
        st.info("조리 순서 정보가 없습니다.")

    # 팁 (있는 경우)
    tips = recipe.get("tips", "")
    if tips:
        st.divider()
        st.markdown("### 💡 조리 팁")
        st.info(tips)


def render_recipe_card_compact(recipe: Dict):
    """
    레시피 카드 컴팩트 버전 (리스트용)

    Args:
        recipe: 레시피 정보 딕셔너리
    """
    with st.container():
        col1, col2 = st.columns([1, 4])

        with col1:
            image_url = recipe.get("image_url", "")
            if image_url:
                try:
                    st.image(image_url, width=100)
                except Exception:
                    st.markdown("🍳")
            else:
                st.markdown("🍳")

        with col2:
            st.markdown(f"**{recipe.get('name', '레시피')}**")
            category = recipe.get("category", "")
            if category:
                st.caption(f"📁 {category}")

            ingredients = recipe.get("ingredients", [])[:3]
            if ingredients:
                st.caption(f"재료: {', '.join(ingredients)}...")

        st.divider()


def render_recipe_list(recipes: List[Dict]):
    """
    레시피 목록 렌더링

    Args:
        recipes: 레시피 목록
    """
    if not recipes:
        st.info("검색 결과가 없습니다.")
        return

    for recipe in recipes:
        render_recipe_card_compact(recipe)
