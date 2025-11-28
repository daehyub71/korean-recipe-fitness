"""운동 추천 카드 컴포넌트"""

import streamlit as st
from typing import Dict, List


def get_intensity_emoji(intensity: str) -> str:
    """강도에 따른 이모지 반환"""
    emojis = {
        "low": "🚶",
        "medium": "🚴",
        "high": "🏃"
    }
    return emojis.get(intensity, "🏋️")


def get_intensity_color(intensity: str) -> str:
    """강도에 따른 색상 반환"""
    colors = {
        "low": "#4CAF50",      # 녹색
        "medium": "#FF9800",    # 주황색
        "high": "#F44336"       # 빨간색
    }
    return colors.get(intensity, "#9E9E9E")


def get_intensity_text(intensity: str) -> str:
    """강도 한글 텍스트 반환"""
    texts = {
        "low": "저강도",
        "medium": "중강도",
        "high": "고강도"
    }
    return texts.get(intensity, intensity)


def render_exercise_card(exercises: List[Dict]):
    """
    운동 추천 카드 렌더링

    Args:
        exercises: 운동 추천 리스트
    """
    if not exercises:
        st.warning("운동 추천 정보가 없습니다.")
        return

    st.subheader("🏃 운동 추천")
    st.caption("섭취 칼로리를 소모하기 위한 운동 추천입니다.")

    st.divider()

    # 강도별로 3열 표시
    cols = st.columns(3)

    for i, exercise in enumerate(exercises[:3]):  # 최대 3개
        with cols[i]:
            render_single_exercise(exercise)


def render_single_exercise(exercise: Dict):
    """
    단일 운동 카드 렌더링

    Args:
        exercise: 운동 정보 딕셔너리
    """
    intensity = exercise.get("intensity", "medium")
    emoji = get_intensity_emoji(intensity)
    color = get_intensity_color(intensity)
    intensity_text = get_intensity_text(intensity)

    # 카드 스타일
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}22, {color}11);
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    ">
        <h3 style="margin: 0; color: {color};">
            {emoji} {intensity_text}
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # 운동명
    name_kr = exercise.get("name_kr", exercise.get("name", "운동"))
    st.markdown(f"### {name_kr}")

    # 운동 정보
    duration = exercise.get("duration_minutes", 0)
    calories = exercise.get("calories_burned", 0)
    met = exercise.get("met", 0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("⏱️ 시간", f"{duration:.0f}분")
    with col2:
        st.metric("🔥 소모", f"{calories:.0f}kcal")

    # MET 값 표시
    if met > 0:
        st.caption(f"MET: {met:.1f}")

    # 설명
    description = exercise.get("description", "")
    if description:
        st.markdown(f"📝 {description}")

    # 팁
    tips = exercise.get("tips", "")
    if tips:
        st.info(f"💡 {tips}")


def render_exercise_summary(exercises: List[Dict]):
    """
    운동 요약 렌더링

    Args:
        exercises: 운동 추천 리스트
    """
    if not exercises:
        return

    st.markdown("### 운동 요약")

    # 총 소모 칼로리 계산 (가장 긴 운동 기준)
    max_exercise = max(exercises, key=lambda x: x.get("duration_minutes", 0))
    total_calories = max_exercise.get("calories_burned", 0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("권장 운동", f"{len(exercises)}가지")
    with col2:
        st.metric("예상 소모 칼로리", f"{total_calories:.0f} kcal")

    # 운동 리스트
    for exercise in exercises:
        intensity = exercise.get("intensity", "medium")
        emoji = get_intensity_emoji(intensity)
        name_kr = exercise.get("name_kr", "")
        duration = exercise.get("duration_minutes", 0)
        st.markdown(f"{emoji} **{name_kr}** - {duration:.0f}분")


def render_exercise_comparison(exercises: List[Dict]):
    """
    운동 비교 테이블 렌더링

    Args:
        exercises: 운동 추천 리스트
    """
    if not exercises:
        return

    st.markdown("### 📊 운동 비교")

    # 테이블 데이터 구성
    data = []
    for exercise in exercises:
        data.append({
            "강도": get_intensity_text(exercise.get("intensity", "medium")),
            "운동명": exercise.get("name_kr", ""),
            "시간(분)": exercise.get("duration_minutes", 0),
            "소모칼로리": exercise.get("calories_burned", 0),
            "MET": exercise.get("met", 0)
        })

    st.table(data)

    st.caption("""
    **MET (Metabolic Equivalent of Task)**: 운동 강도를 나타내는 지표
    - 1 MET = 안정 시 에너지 소비량
    - 3-6 MET = 중강도 운동
    - 6+ MET = 고강도 운동
    """)
