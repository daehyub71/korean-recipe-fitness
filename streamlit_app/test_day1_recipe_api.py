"""Day 1 Test: 레시피 API 연결 테스트"""

import streamlit as st
import os
import sys
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(
    page_title="Day 1 - 레시피 API 테스트",
    page_icon="🍳",
    layout="wide"
)

st.title("🍳 Day 1.4-A: 조리식품 레시피 API 테스트")

# API 설정
API_KEY = os.getenv("RECIPE_API_KEY", "")
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
SERVICE_NAME = "COOKRCP01"

# API 키 표시
st.header("🔑 API 설정")
col1, col2 = st.columns(2)
with col1:
    st.text_input("API Key", value=f"{API_KEY[:4]}...{API_KEY[-4:]}" if API_KEY else "미설정", disabled=True)
with col2:
    st.text_input("Service Name", value=SERVICE_NAME, disabled=True)


# API 연결 테스트
st.header("🔗 API 연결 상태")

if st.button("API 연결 테스트", key="test_connection"):
    if not API_KEY:
        st.error("❌ RECIPE_API_KEY가 설정되지 않았습니다.")
    else:
        url = f"{BASE_URL}/{API_KEY}/{SERVICE_NAME}/json/1/1"
        try:
            with st.spinner("API 호출 중..."):
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()

            if SERVICE_NAME in data:
                result = data[SERVICE_NAME]
                code = result.get("RESULT", {}).get("CODE", "")
                msg = result.get("RESULT", {}).get("MSG", "")
                total = result.get("total_count", 0)

                if code == "INFO-000":
                    st.success(f"✅ API 연결 성공!")
                    col1, col2 = st.columns(2)
                    col1.metric("응답 코드", code)
                    col2.metric("전체 레시피 수", f"{total:,}개")
                else:
                    st.warning(f"⚠️ API 응답: {code} - {msg}")
            else:
                st.error(f"❌ 예상치 못한 응답: {list(data.keys())}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ API 호출 실패: {e}")


# 샘플 데이터 조회
st.header("📋 샘플 레시피 조회")

sample_count = st.slider("조회할 레시피 수", 1, 10, 5)

if st.button("샘플 조회", key="fetch_sample"):
    if not API_KEY:
        st.error("❌ RECIPE_API_KEY가 설정되지 않았습니다.")
    else:
        url = f"{BASE_URL}/{API_KEY}/{SERVICE_NAME}/json/1/{sample_count}"
        try:
            with st.spinner("레시피 조회 중..."):
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

            if SERVICE_NAME in data and "row" in data[SERVICE_NAME]:
                recipes = data[SERVICE_NAME]["row"]
                st.success(f"✅ {len(recipes)}개 레시피 조회 완료")

                for i, recipe in enumerate(recipes):
                    with st.expander(f"🍴 {recipe.get('RCP_NM', '이름없음')}", expanded=(i==0)):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**기본 정보**")
                            st.write(f"- 음식명: {recipe.get('RCP_NM', '-')}")
                            st.write(f"- 조리방법: {recipe.get('RCP_WAY2', '-')}")
                            st.write(f"- 분류: {recipe.get('RCP_PAT2', '-')}")
                            st.write(f"- 칼로리: {recipe.get('INFO_ENG', '-')} kcal")

                        with col2:
                            st.write("**영양정보**")
                            st.write(f"- 탄수화물: {recipe.get('INFO_CAR', '-')} g")
                            st.write(f"- 단백질: {recipe.get('INFO_PRO', '-')} g")
                            st.write(f"- 지방: {recipe.get('INFO_FAT', '-')} g")
                            st.write(f"- 나트륨: {recipe.get('INFO_NA', '-')} mg")

                        # 재료
                        ingredients = recipe.get('RCP_PARTS_DTLS', '')
                        if ingredients:
                            st.write("**재료**")
                            st.text(ingredients[:200] + "..." if len(ingredients) > 200 else ingredients)

                        # 조리법 (일부만)
                        for j in range(1, 4):
                            step = recipe.get(f'MANUAL0{j}', '')
                            if step:
                                st.write(f"**조리법 {j}**: {step[:100]}...")
            else:
                st.warning("데이터가 없습니다.")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ API 호출 실패: {e}")


# 수집된 데이터 확인
st.header("📁 수집된 데이터 확인")

raw_file = PROJECT_ROOT / "data" / "raw" / "recipes_raw.json"
if raw_file.exists():
    with open(raw_file, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    st.success(f"✅ 수집된 레시피: {len(recipes):,}개")

    # 카테고리별 분포
    categories = {}
    for recipe in recipes:
        cat = recipe.get("RCP_PAT2", "기타")
        categories[cat] = categories.get(cat, 0) + 1

    st.bar_chart(categories)

else:
    st.info("📝 아직 수집된 데이터가 없습니다.")
    st.code("python scripts/collect_recipes.py", language="bash")


# 체크포인트
st.header("📊 Day 1.4-A 체크포인트")

checks = [
    ("RECIPE_API_KEY 설정됨", bool(API_KEY)),
    ("recipes_raw.json 존재", raw_file.exists()),
]

for name, status in checks:
    icon = "✅" if status else "❌"
    st.write(f"{icon} {name}")

if all(status for _, status in checks):
    st.success("✅ 레시피 API 연동 완료!")
else:
    st.warning("⚠️ 일부 항목을 완료해주세요.")
