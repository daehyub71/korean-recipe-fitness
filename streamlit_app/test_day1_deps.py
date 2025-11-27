"""Day 1 Test: 패키지 설치 확인"""

import streamlit as st
import importlib
import sys

st.set_page_config(
    page_title="Day 1 - 패키지 설치 확인",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Day 1.2: 패키지 설치 확인")

# 필수 패키지 목록
REQUIRED_PACKAGES = {
    "FastAPI": ["fastapi", "uvicorn"],
    "LangChain": ["langchain", "langgraph", "langchain_openai"],
    "Vector DB": ["faiss"],
    "OpenAI": ["openai"],
    "Database": ["sqlalchemy"],
    "Data Processing": ["pandas", "requests"],
    "Frontend": ["streamlit"],
    "Utilities": ["dotenv", "pydantic", "pydantic_settings"],
    "Testing": ["pytest", "pytest_asyncio", "httpx"],
}


def check_package(package_name: str) -> tuple[bool, str]:
    """패키지 import 가능 여부 확인 및 버전 반환"""
    try:
        # 특수한 패키지명 처리
        import_name = package_name
        if package_name == "faiss":
            import_name = "faiss"
        elif package_name == "dotenv":
            import_name = "dotenv"

        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        return True, version
    except ImportError as e:
        return False, str(e)


# 결과 표시
st.header("📋 패키지별 설치 상태")

total_success = 0
total_packages = 0

for category, packages in REQUIRED_PACKAGES.items():
    st.subheader(f"🔹 {category}")

    cols = st.columns(len(packages))
    for i, pkg in enumerate(packages):
        total_packages += 1
        success, version = check_package(pkg)
        if success:
            total_success += 1
            cols[i].success(f"✅ {pkg}\n`{version}`")
        else:
            cols[i].error(f"❌ {pkg}\n`{version[:30]}...`")


# Python 버전
st.header("🐍 Python 환경")

col1, col2, col3 = st.columns(3)
col1.metric("Python 버전", sys.version.split()[0])
col2.metric("설치된 패키지", total_success)
col3.metric("전체 패키지", total_packages)


# 전체 결과
st.header("📊 Day 1.2 체크포인트")

success_rate = total_success / total_packages * 100

if success_rate == 100:
    st.success(f"✅ Day 1.2 완료! 모든 패키지가 설치되었습니다. ({total_success}/{total_packages})")
else:
    st.warning(f"⚠️ 진행 중: {total_success}/{total_packages} 설치 ({success_rate:.0f}%)")
    st.code("pip install -r requirements.txt", language="bash")


# 추가 정보
with st.expander("📝 설치된 패키지 전체 목록"):
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=columns"],
        capture_output=True,
        text=True
    )
    st.code(result.stdout)
