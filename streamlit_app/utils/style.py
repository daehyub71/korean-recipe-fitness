import streamlit as st

@st.cache_data
def _get_css():
    """CSS 문자열 반환 (캐싱됨)"""
    return """
        <style>
            /* Import Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;900&display=swap');

            /* Global Styles */
            html, body, [class*="css"] {
                font-family: 'Noto Sans KR', sans-serif;
            }

            /* Light Theme Colors */
            :root {
                --primary-red: #dc2626;
                --primary-red-hover: #b91c1c;
                --bg-white: #ffffff;
                --bg-gray-50: #f9fafb;
                --bg-gray-100: #f3f4f6;
                --text-gray-900: #111827;
                --text-gray-700: #374151;
                --text-gray-500: #6b7280;
                --border-gray-200: #e5e7eb;
            }

            /* Streamlit Main Area Override - Light */
            .stApp {
                background-color: var(--bg-gray-50);
            }

            /* Hide default Streamlit header */
            header[data-testid="stHeader"] {
                background-color: var(--bg-white);
                border-bottom: 1px solid var(--border-gray-200);
            }

            /* Sidebar Override - Light */
            [data-testid="stSidebar"] {
                background-color: var(--bg-white);
                border-right: 1px solid var(--border-gray-200);
            }

            [data-testid="stSidebar"] * {
                color: var(--text-gray-700) !important;
            }

            /* Main Header */
            .main-title {
                font-size: 2rem;
                font-weight: 700;
                color: var(--text-gray-900);
                text-align: center;
                margin: 2rem 0 1.5rem 0;
            }

            /* Search Container */
            .search-container {
                max-width: 800px;
                margin: 0 auto 2rem auto;
                display: flex;
                gap: 0.5rem;
            }

            /* Input Fields - Light */
            .stTextInput > div > div > input {
                background-color: var(--bg-white) !important;
                color: var(--text-gray-900) !important;
                border: 1px solid var(--border-gray-200) !important;
                border-radius: 0.5rem !important;
                padding: 0.75rem 1rem !important;
                font-size: 1rem !important;
            }

            .stTextInput > div > div > input::placeholder {
                color: var(--text-gray-500) !important;
            }

            /* Primary Button (Red) */
            .stButton > button[kind="primary"] {
                background-color: var(--primary-red) !important;
                color: white !important;
                font-weight: 600 !important;
                border: none !important;
                border-radius: 0.5rem !important;
                padding: 0.75rem 2rem !important;
                font-size: 1rem !important;
            }

            .stButton > button[kind="primary"]:hover {
                background-color: var(--primary-red-hover) !important;
            }

            /* Search Results Header */
            .search-results-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 1.5rem 0;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--border-gray-200);
            }

            .search-results-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-gray-900);
            }

            /* Recipe Card Grid */
            .recipe-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1.5rem;
                margin-top: 1.5rem;
            }

            /* Recipe Card */
            .recipe-card {
                background-color: var(--bg-white);
                border-radius: 1rem;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .recipe-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }

            .recipe-card-image {
                width: 100%;
                height: 200px;
                object-fit: cover;
            }

            /* 이미지 로딩 시 레이아웃 이동 방지 */
            [data-testid="stImage"] {
                min-height: 150px;
            }

            /* 폰트 로딩 최적화 */
            * {
                font-display: swap;
            }

            .recipe-card-content {
                padding: 1rem;
            }

            .recipe-card-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: var(--text-gray-900);
                margin-bottom: 0.75rem;
            }

            .recipe-card-info {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: var(--text-gray-500);
                font-size: 0.875rem;
                margin-bottom: 0.5rem;
            }

            .recipe-card-info svg {
                width: 16px;
                height: 16px;
            }

            .recipe-card-button {
                width: 100%;
                padding: 0.75rem;
                margin-top: 1rem;
                background-color: transparent;
                color: var(--primary-red);
                border: 1px solid var(--primary-red);
                border-radius: 0.5rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
            }

            .recipe-card-button:hover {
                background-color: var(--primary-red);
                color: white;
            }

            /* Pagination */
            .pagination {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 0.5rem;
                margin: 2rem 0;
            }

            .page-btn {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: none;
                background-color: transparent;
                color: var(--text-gray-700);
                font-weight: 500;
                cursor: pointer;
            }

            .page-btn.active {
                background-color: var(--text-gray-900);
                color: white;
            }

            /* Metrics styling for light theme */
            [data-testid="stMetricValue"] {
                color: var(--text-gray-900) !important;
            }

            [data-testid="stMetricLabel"] {
                color: var(--text-gray-500) !important;
            }

            /* Success/Warning messages */
            .stSuccess, .stWarning, .stInfo {
                border-radius: 0.5rem;
            }

            /* Selectbox styling */
            .stSelectbox > div > div {
                background-color: var(--bg-white) !important;
                border: 1px solid var(--border-gray-200) !important;
            }

            /* Divider */
            hr {
                border-color: var(--border-gray-200);
            }

        </style>
    """

def load_css():
    """
    Loads custom CSS for the application - Light Theme (AI K-Food Design)
    Uses cached CSS to prevent re-parsing on every render.
    """
    st.markdown(_get_css(), unsafe_allow_html=True)

def card_container(key=None):
    """
    Creates a container with card styling.
    """
    return st.container()
