"""Day 1 Test: 영양정보 API 연결 테스트"""

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
    page_title="Day 1 - 영양정보 API 테스트",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Day 1.4-B: 식품영양성분 API 테스트")

# API 설정
API_KEY = os.getenv("NUTRITION_API_KEY", "")
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
SERVICE_NAME = "I2790"

# API 키 표시
st.header("🔑 API 설정")
col1, col2 = st.columns(2)
with col1:
    st.text_input("API Key", value=f"{API_KEY[:8]}...{API_KEY[-8:]}" if API_KEY else "미설정", disabled=True)
with col2:
    st.text_input("Service Name", value=SERVICE_NAME, disabled=True)


# API 연결 테스트
st.header("🔗 API 연결 상태")

if st.button("API 연결 테스트", key="test_connection"):
    if not API_KEY:
        st.error("❌ NUTRITION_API_KEY가 설정되지 않았습니다.")
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
                    col2.metric("전체 식품 수", f"{total:,}개")
                else:
                    st.warning(f"⚠️ API 응답: {code} - {msg}")
            else:
                st.error(f"❌ 예상치 못한 응답: {list(data.keys())}")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ API 호출 실패: {e}")


# 샘플 데이터 조회
st.header("📋 샘플 영양정보 조회")

sample_count = st.slider("조회할 식품 수", 1, 10, 5)

if st.button("샘플 조회", key="fetch_sample"):
    if not API_KEY:
        st.error("❌ NUTRITION_API_KEY가 설정되지 않았습니다.")
    else:
        url = f"{BASE_URL}/{API_KEY}/{SERVICE_NAME}/json/1/{sample_count}"
        try:
            with st.spinner("영양정보 조회 중..."):
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()

            if SERVICE_NAME in data and "row" in data[SERVICE_NAME]:
                items = data[SERVICE_NAME]["row"]
                st.success(f"✅ {len(items)}개 식품 조회 완료")

                for i, item in enumerate(items):
                    with st.expander(f"🍽️ {item.get('DESC_KOR', '이름없음')}", expanded=(i==0)):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**기본 정보**")
                            st.write(f"- 식품명: {item.get('DESC_KOR', '-')}")
                            st.write(f"- 식품코드: {item.get('FOOD_CD', '-')}")
                            st.write(f"- 데이터구분: {item.get('ANIMAL_PLANT', '-')}")
                            st.write(f"- 1회제공량: {item.get('SERVING_SIZE', '-')}g")

                        with col2:
                            st.write("**주요 영양정보**")
                            st.write(f"- 칼로리: {item.get('NUTR_CONT1', '-')} kcal")
                            st.write(f"- 탄수화물: {item.get('NUTR_CONT2', '-')} g")
                            st.write(f"- 단백질: {item.get('NUTR_CONT3', '-')} g")
                            st.write(f"- 지방: {item.get('NUTR_CONT4', '-')} g")
                            st.write(f"- 당류: {item.get('NUTR_CONT5', '-')} g")
                            st.write(f"- 나트륨: {item.get('NUTR_CONT6', '-')} mg")
            else:
                st.warning("데이터가 없습니다.")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ API 호출 실패: {e}")


# 수집된 데이터 확인
st.header("📁 수집된 데이터 확인")

raw_file = PROJECT_ROOT / "data" / "raw" / "nutrition_raw.json"
if raw_file.exists():
    with open(raw_file, "r", encoding="utf-8") as f:
        nutrition = json.load(f)

    st.success(f"✅ 수집된 영양정보: {len(nutrition):,}개")

    # 칼로리 분포 히스토그램
    import pandas as pd

    calories = []
    for item in nutrition:
        try:
            cal = float(item.get("NUTR_CONT1", 0) or 0)
            if 0 < cal < 2000:  # 이상치 제외
                calories.append(cal)
        except (ValueError, TypeError):
            pass

    if calories:
        st.subheader("칼로리 분포")
        df = pd.DataFrame({"칼로리 (kcal)": calories})
        st.bar_chart(df["칼로리 (kcal)"].value_counts().sort_index().head(50))

else:
    st.info("📝 아직 수집된 데이터가 없습니다.")
    st.code("python scripts/collect_nutrition.py", language="bash")


# 레시피-영양정보 매칭 테스트
st.header("🔄 레시피-영양정보 매칭 테스트")

recipe_file = PROJECT_ROOT / "data" / "raw" / "recipes_raw.json"

if recipe_file.exists() and raw_file.exists():
    with open(recipe_file, "r", encoding="utf-8") as f:
        recipes = json.load(f)
    with open(raw_file, "r", encoding="utf-8") as f:
        nutrition = json.load(f)

    # 영양정보 이름 목록 생성
    nutrition_names = {item.get("DESC_KOR", "").strip().lower() for item in nutrition if item.get("DESC_KOR")}

    # 매칭 테스트
    matched = 0
    for recipe in recipes[:100]:  # 처음 100개만 테스트
        recipe_name = recipe.get("RCP_NM", "").strip().lower()
        if recipe_name in nutrition_names or any(recipe_name in n for n in nutrition_names):
            matched += 1

    st.metric("매칭 테스트 (상위 100개)", f"{matched}개 매칭")
    st.progress(matched / 100)

    if matched < 50:
        st.info("💡 매칭률이 낮을 수 있습니다. 레시피와 영양정보 DB의 음식명이 다를 수 있습니다.")
        st.write("레시피 DB에는 자체 영양정보(INFO_ENG 등)가 포함되어 있어 영양정보 DB와 별도로 사용 가능합니다.")
else:
    st.info("📝 레시피와 영양정보 데이터를 먼저 수집해주세요.")


# 체크포인트
st.header("📊 Day 1.4-B 체크포인트")

checks = [
    ("NUTRITION_API_KEY 설정됨", bool(API_KEY)),
    ("nutrition_raw.json 존재", raw_file.exists()),
]

for name, status in checks:
    icon = "✅" if status else "❌"
    st.write(f"{icon} {name}")

if all(status for _, status in checks):
    st.success("✅ 영양정보 API 연동 완료!")
else:
    st.warning("⚠️ 일부 항목을 완료해주세요.")
