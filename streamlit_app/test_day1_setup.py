"""Day 1 Test: 프로젝트 구조 확인"""

import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="Day 1 - 프로젝트 구조 확인",
    page_icon="📁",
    layout="wide"
)

st.title("📁 Day 1.1: 프로젝트 구조 확인")

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

# 필요한 디렉토리 목록
REQUIRED_DIRS = [
    "app",
    "app/core",
    "app/core/agents",
    "app/core/workflow",
    "app/core/services",
    "app/api",
    "app/schemas",
    "scripts",
    "streamlit_app",
    "streamlit_app/components",
    "data",
    "data/raw",
    "data/processed",
    "data/vector_db",
    "data/database",
    "tests",
]

# 필요한 파일 목록
REQUIRED_FILES = [
    "requirements.txt",
    ".env.example",
    ".env",
    ".gitignore",
    "app/__init__.py",
    "app/config.py",
    "app/core/__init__.py",
    "app/core/agents/__init__.py",
    "app/core/workflow/__init__.py",
    "app/core/services/__init__.py",
]


def check_directory(dir_path: str) -> bool:
    """디렉토리 존재 여부 확인"""
    full_path = PROJECT_ROOT / dir_path
    return full_path.exists() and full_path.is_dir()


def check_file(file_path: str) -> bool:
    """파일 존재 여부 확인"""
    full_path = PROJECT_ROOT / file_path
    return full_path.exists() and full_path.is_file()


# 디렉토리 확인
st.header("📂 디렉토리 구조")

col1, col2 = st.columns(2)

with col1:
    st.subheader("필수 디렉토리")
    dir_results = []
    for dir_path in REQUIRED_DIRS:
        exists = check_directory(dir_path)
        dir_results.append(exists)
        icon = "✅" if exists else "❌"
        st.write(f"{icon} `{dir_path}/`")

    dir_success = sum(dir_results)
    dir_total = len(REQUIRED_DIRS)
    st.metric("디렉토리 완료율", f"{dir_success}/{dir_total}", f"{dir_success/dir_total*100:.0f}%")

with col2:
    st.subheader("필수 파일")
    file_results = []
    for file_path in REQUIRED_FILES:
        exists = check_file(file_path)
        file_results.append(exists)
        icon = "✅" if exists else "❌"
        st.write(f"{icon} `{file_path}`")

    file_success = sum(file_results)
    file_total = len(REQUIRED_FILES)
    st.metric("파일 완료율", f"{file_success}/{file_total}", f"{file_success/file_total*100:.0f}%")


# 트리 구조 시각화
st.header("🌳 프로젝트 트리 구조")

tree_output = """
korean-recipe-fitness/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py (Day 4)
│   ├── core/
│   │   ├── agents/
│   │   │   ├── query_analyzer.py (Day 3)
│   │   │   ├── recipe_fetcher.py (Day 3)
│   │   │   ├── nutrition_calculator.py (Day 3)
│   │   │   ├── exercise_recommender.py (Day 3)
│   │   │   └── response_formatter.py (Day 3)
│   │   ├── workflow/
│   │   │   ├── graph.py (Day 3)
│   │   │   └── state.py (Day 3)
│   │   └── services/
│   │       ├── embedding_service.py (Day 2)
│   │       ├── vector_db_service.py (Day 2)
│   │       ├── nutrition_db_service.py (Day 2)
│   │       ├── calorie_calculator.py (Day 3)
│   │       └── llm_service.py (Day 3)
│   ├── api/
│   │   └── routes.py (Day 4)
│   └── schemas/
│       ├── request.py (Day 4)
│       └── response.py (Day 4)
├── scripts/
│   ├── collect_recipes.py (Day 1)
│   ├── collect_nutrition.py (Day 1)
│   ├── process_recipes.py (Day 1)
│   ├── build_vector_db.py (Day 2)
│   └── build_nutrition_db.py (Day 2)
├── streamlit_app/
│   ├── main.py (Day 4)
│   └── components/
│       ├── recipe_card.py (Day 4)
│       ├── nutrition_card.py (Day 4)
│       └── exercise_card.py (Day 4)
├── data/
│   ├── raw/
│   ├── processed/
│   ├── vector_db/
│   └── database/
├── tests/
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── README.md (Day 5)
└── CLAUDE.md (Day 5)
"""

st.code(tree_output, language="text")


# 전체 결과
st.header("📊 Day 1.1 체크포인트")

total_success = dir_success + file_success
total_items = dir_total + file_total
overall_percent = total_success / total_items * 100

if overall_percent == 100:
    st.success(f"✅ Day 1.1 완료! 모든 구조가 생성되었습니다. ({total_success}/{total_items})")
else:
    st.warning(f"⚠️ 진행 중: {total_success}/{total_items} 완료 ({overall_percent:.0f}%)")
    st.info("누락된 항목을 확인하고 생성해주세요.")
