"""ExerciseRecommender Agent - 운동 추천"""

import logging
from typing import Optional, List

from app.core.workflow.state import ChatState, ExerciseRecommendation, get_default_user_profile
from app.core.services.calorie_calculator import (
    CalorieCalculator,
    UserProfile as CalcUserProfile
)

logger = logging.getLogger(__name__)


class ExerciseRecommender:
    """운동 추천 Agent

    섭취 칼로리를 기반으로 강도별 운동 추천
    """

    def recommend(self, state: ChatState) -> ChatState:
        """
        영양 정보의 칼로리를 기반으로 운동 추천

        Args:
            state: nutrition, user_profile이 포함된 ChatState

        Returns:
            exercise_recommendations가 업데이트된 ChatState
        """
        nutrition = state.get("nutrition", {})
        user_profile = state.get("user_profile") or get_default_user_profile()

        calories = nutrition.get("calories", 0)
        if calories <= 0:
            logger.warning("칼로리 정보가 없습니다.")
            state["exercise_recommendations"] = []
            return state

        logger.info(f"운동 추천 계산: {calories}kcal 소모 목표")

        # UserProfile 변환
        calc_profile = CalcUserProfile(
            weight=user_profile.get("weight", 65.0),
            height=user_profile.get("height", 170.0),
            age=user_profile.get("age", 30),
            gender=user_profile.get("gender", "male"),
            activity_level=user_profile.get("activity_level", "moderate")
        )

        # CalorieCalculator로 운동 추천
        calculator = CalorieCalculator(calc_profile)
        exercise_results = calculator.get_exercise_by_intensity(calories)

        # ExerciseRecommendation 형식으로 변환
        recommendations: List[ExerciseRecommendation] = []

        for intensity in ["low", "medium", "high"]:
            result = exercise_results.get(intensity)
            if result:
                rec = ExerciseRecommendation(
                    name=result.name,
                    name_kr=result.name_kr,
                    intensity=result.intensity,
                    duration_minutes=round(result.duration_minutes, 0),
                    calories_burned=round(result.calories_burned, 0),
                    met=result.met,
                    description=result.description,
                    tips=result.tips
                )
                recommendations.append(rec)
                logger.info(
                    f"  {result.intensity}: {result.name_kr} "
                    f"({result.duration_minutes:.0f}분, {result.calories_burned:.0f}kcal)"
                )

        state["exercise_recommendations"] = recommendations
        return state

    def get_additional_exercises(
        self,
        calories: float,
        user_profile: Optional[dict] = None,
        intensity: str = None
    ) -> List[ExerciseRecommendation]:
        """추가 운동 옵션 조회

        Args:
            calories: 목표 칼로리
            user_profile: 사용자 프로필
            intensity: 특정 강도 필터 (low/medium/high)

        Returns:
            운동 추천 리스트
        """
        profile_data = user_profile or get_default_user_profile()

        calc_profile = CalcUserProfile(
            weight=profile_data.get("weight", 65.0),
            height=profile_data.get("height", 170.0),
            age=profile_data.get("age", 30),
            gender=profile_data.get("gender", "male"),
            activity_level=profile_data.get("activity_level", "moderate")
        )

        calculator = CalorieCalculator(calc_profile)
        results = calculator.recommend_exercises(
            target_calories=calories,
            intensity_filter=intensity
        )

        recommendations = []
        for result in results:
            rec = ExerciseRecommendation(
                name=result.name,
                name_kr=result.name_kr,
                intensity=result.intensity,
                duration_minutes=round(result.duration_minutes, 0),
                calories_burned=round(result.calories_burned, 0),
                met=result.met,
                description=result.description,
                tips=result.tips
            )
            recommendations.append(rec)

        return recommendations


# 싱글톤 인스턴스
_exercise_recommender: Optional[ExerciseRecommender] = None


def get_exercise_recommender() -> ExerciseRecommender:
    """ExerciseRecommender 싱글톤 인스턴스 반환"""
    global _exercise_recommender
    if _exercise_recommender is None:
        _exercise_recommender = ExerciseRecommender()
    return _exercise_recommender


def recommend_exercises(state: ChatState) -> ChatState:
    """LangGraph 노드 함수"""
    recommender = get_exercise_recommender()
    return recommender.recommend(state)
