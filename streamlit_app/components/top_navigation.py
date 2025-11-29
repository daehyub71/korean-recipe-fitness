"""공통 상단 네비게이션 컴포넌트"""

import streamlit as st
from utils.i18n import t, get_lang, set_lang


def apply_page_style():
    """페이지 공통 스타일 적용 (사이드바 숨김, 폰트 등)"""
    st.markdown("""
        <style>
            /* 사이드바 숨김 */
            [data-testid="stSidebar"] { display: none; }
            [data-testid="collapsedControl"] { display: none; }

            /* 메인 컨테이너 여백 */
            .block-container {
                padding-top: 2rem !important;
                padding-left: 3rem !important;
                padding-right: 3rem !important;
                max-width: 1400px;
            }

            /* 폰트 설정 */
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif !important;
            }

            /* 제목 스타일 */
            h1 {
                font-size: 2.25rem !important;
                font-weight: 700 !important;
                letter-spacing: -0.02em;
            }

            h3 {
                font-size: 1.5rem !important;
                font-weight: 600 !important;
            }

            h4 {
                font-size: 1.1rem !important;
                font-weight: 600 !important;
            }

            /* 본문 텍스트 */
            p, span, div {
                font-size: 0.95rem;
                line-height: 1.7;
            }

            /* 버튼 스타일 */
            .stButton > button {
                font-family: 'Noto Sans KR', sans-serif !important;
                font-weight: 500 !important;
                border-radius: 0.5rem !important;
                padding: 0.5rem 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)


def render_top_navigation(current_page: str = "home") -> str:
    """
    상단 네비게이션 바 렌더링

    Args:
        current_page: 현재 페이지 ("home", "recipe", "nutrition", "exercise", "dashboard")

    Returns:
        검색어 (있을 경우)
    """
    lang = get_lang()

    # 상단 여백
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Navigation bar using columns
    col1, col2, col3, col4 = st.columns([2, 5, 2, 1])

    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0;">
                <span style="font-size: 1.75rem;">🥬</span>
                <span style="font-weight: 700; font-size: 1.25rem; color: #22c55e; letter-spacing: -0.02em;">AI 한식 푸드</span>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
        with nav_col1:
            btn_type = "primary" if current_page in ["home", "recipe"] else "secondary"
            if st.button(t("nav_recipe"), key="nav_recipe_btn", use_container_width=True, type=btn_type):
                st.switch_page("pages/1_Recipe_Search.py")
        with nav_col2:
            btn_type = "primary" if current_page == "nutrition" else "secondary"
            if st.button(t("nutrition_info"), key="nav_nutrition_btn", use_container_width=True, type=btn_type):
                st.switch_page("pages/2_Nutrition_Info.py")
        with nav_col3:
            btn_type = "primary" if current_page == "exercise" else "secondary"
            if st.button(t("exercise_info"), key="nav_exercise_btn", use_container_width=True, type=btn_type):
                st.switch_page("pages/3_Workout_Recommendation.py")
        with nav_col4:
            btn_type = "primary" if current_page == "dashboard" else "secondary"
            if st.button(t("nav_dashboard"), key="nav_dashboard_btn", use_container_width=True, type=btn_type):
                st.switch_page("pages/4_Dashboard.py")

    with col3:
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            if st.button("KO", key="lang_ko_btn", type="primary" if lang == "ko" else "secondary", use_container_width=True):
                set_lang("ko")
                st.rerun()
        with lang_col2:
            if st.button("EN", key="lang_en_btn", type="primary" if lang == "en" else "secondary", use_container_width=True):
                set_lang("en")
                st.rerun()

    with col4:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.75rem; justify-content: flex-end; padding-top: 0.5rem;">
                <span style="font-size: 1.25rem; cursor: pointer;">🔔</span>
                <span style="font-size: 1.25rem; cursor: pointer;">👤</span>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    return ""


def render_breadcrumb(items: list):
    """
    브레드크럼 렌더링

    Args:
        items: [(라벨, 링크), ...] 형태의 리스트. 링크가 None이면 현재 페이지
    """
    breadcrumb_html = []
    for i, (label, link) in enumerate(items):
        if link:
            breadcrumb_html.append(f'<a href="#" style="color: #6b7280; text-decoration: none;">{label}</a>')
        else:
            breadcrumb_html.append(f'<span style="color: #22c55e; font-weight: 500;">{label}</span>')

        if i < len(items) - 1:
            breadcrumb_html.append('<span style="color: #9ca3af; margin: 0 0.5rem;">/</span>')

    st.markdown(f"""
        <div style="margin-bottom: 1rem; font-size: 0.875rem;">
            {" ".join(breadcrumb_html)}
        </div>
    """, unsafe_allow_html=True)


def render_footer():
    """푸터 렌더링"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; color: #9ca3af; font-size: 0.75rem; padding: 1rem 0; border-top: 1px solid #e5e7eb;">
            {t("footer_copyright")}<br>
            {t("footer_links")}
        </div>
    """, unsafe_allow_html=True)
