"""Day 1 Test: 환경변수 및 API 연결 테스트"""

import streamlit as st
import os
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Day 1 - 환경변수 테스트",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Day 1.3: 환경변수 및 API 연결 테스트")


def mask_key(key: str, show_chars: int = 4) -> str:
    """API 키 마스킹"""
    if not key or len(key) <= show_chars * 2:
        return "***"
    return f"{key[:show_chars]}...{key[-show_chars:]}"


# 환경변수 로드
st.header("📋 환경변수 로드")

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    st.success("✅ .env 파일 로드 성공")
except Exception as e:
    st.error(f"❌ .env 파일 로드 실패: {e}")


# API 키 확인
st.header("🔑 API 키 확인")

col1, col2, col3 = st.columns(3)

# OpenAI API Key
openai_key = os.getenv("OPENAI_API_KEY", "")
with col1:
    st.subheader("OpenAI")
    if openai_key and not openai_key.startswith("sk-proj-your"):
        st.success(f"✅ 설정됨\n`{mask_key(openai_key)}`")
    else:
        st.warning("⚠️ 기본값 또는 미설정")
        st.code("OPENAI_API_KEY=sk-proj-...")

# Recipe API Key
recipe_key = os.getenv("RECIPE_API_KEY", "")
with col2:
    st.subheader("레시피 API")
    if recipe_key:
        st.success(f"✅ 설정됨\n`{mask_key(recipe_key)}`")
    else:
        st.error("❌ 미설정")

# Nutrition API Key
nutrition_key = os.getenv("NUTRITION_API_KEY", "")
with col3:
    st.subheader("영양정보 API")
    if nutrition_key:
        st.success(f"✅ 설정됨\n`{mask_key(nutrition_key, 8)}`")
    else:
        st.error("❌ 미설정")


# Config 클래스 테스트
st.header("⚙️ Config 클래스 테스트")

try:
    from app.config import get_settings
    settings = get_settings()

    st.success("✅ Config 클래스 로드 성공")

    config_data = {
        "app_env": settings.app_env,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "similarity_threshold": settings.similarity_threshold,
        "top_k_results": settings.top_k_results,
        "default_weight_kg": settings.default_weight_kg,
        "default_height_cm": settings.default_height_cm,
        "default_age": settings.default_age,
        "default_gender": settings.default_gender,
    }

    col1, col2 = st.columns(2)
    with col1:
        st.json(config_data)

    with col2:
        st.metric("환경", settings.app_env)
        st.metric("디버그 모드", "ON" if settings.debug else "OFF")
        st.metric("유사도 임계값", settings.similarity_threshold)

except Exception as e:
    st.error(f"❌ Config 클래스 로드 실패: {e}")
    st.code(str(e))


# OpenAI API 연결 테스트
st.header("🤖 OpenAI API 연결 테스트")

if st.button("OpenAI API 테스트 실행"):
    if openai_key and not openai_key.startswith("sk-proj-your"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)

            with st.spinner("API 호출 중..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Say 'Hello, Korean Recipe & Fitness!' in Korean"}],
                    max_tokens=50
                )

            st.success("✅ OpenAI API 연결 성공!")
            st.write("응답:", response.choices[0].message.content)

        except Exception as e:
            st.error(f"❌ OpenAI API 연결 실패: {e}")
    else:
        st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다.")
        st.info("`.env` 파일에 `OPENAI_API_KEY`를 설정해주세요.")


# 전체 결과
st.header("📊 Day 1.3 체크포인트")

checks = [
    (".env 파일 존재", (PROJECT_ROOT / ".env").exists()),
    ("OpenAI API 키", bool(openai_key) and not openai_key.startswith("sk-proj-your")),
    ("레시피 API 키", bool(recipe_key)),
    ("영양정보 API 키", bool(nutrition_key)),
]

success_count = sum(1 for _, status in checks if status)
total_count = len(checks)

for name, status in checks:
    icon = "✅" if status else "❌"
    st.write(f"{icon} {name}")

if success_count == total_count:
    st.success(f"✅ Day 1.3 완료! 모든 환경변수가 설정되었습니다. ({success_count}/{total_count})")
elif success_count >= 3:  # 최소 3개 이상 (OpenAI 제외 가능)
    st.info(f"ℹ️ 대부분 설정 완료. ({success_count}/{total_count}) - OpenAI 키는 선택사항입니다.")
else:
    st.warning(f"⚠️ 진행 중: {success_count}/{total_count} 설정")
    st.code("cp .env.example .env && vi .env", language="bash")
