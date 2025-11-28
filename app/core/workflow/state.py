"""LangGraph 워크플로우 State 정의"""

from typing import TypedDict, Optional, List, Literal


class UserProfile(TypedDict, total=False):
    """사용자 프로필 정보"""
    weight: float           # 체중 (kg)
    height: float           # 키 (cm)
    age: int                # 나이
    gender: Literal["male", "female"]  # 성별
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]  # 활동 수준


class AnalyzedQuery(TypedDict, total=False):
    """파싱된 쿼리 정보"""
    food_name: str          # 음식 이름
    servings: int           # 인분 수
    query_type: Literal["recipe", "nutrition", "exercise", "general"]  # 쿼리 유형
    original_query: str     # 원본 쿼리


class RecipeInfo(TypedDict, total=False):
    """레시피 정보"""
    recipe_id: str
    name: str
    category: str
    cooking_method: str
    ingredients: List[str]
    instructions: List[str]
    tips: str
    image_url: str


class NutritionInfo(TypedDict, total=False):
    """영양 정보"""
    food_name: str
    serving_size: float     # 1회 제공량 (g)
    servings: int           # 인분 수
    calories: float         # 칼로리 (kcal)
    protein: float          # 단백질 (g)
    fat: float              # 지방 (g)
    carbohydrate: float     # 탄수화물 (g)
    sugar: float            # 당류 (g)
    fiber: float            # 식이섬유 (g)
    sodium: float           # 나트륨 (mg)
    # 추가 영양소
    calcium: float          # 칼슘 (mg)
    iron: float             # 철분 (mg)
    potassium: float        # 칼륨 (mg)
    vitamin_a: float        # 비타민A (μg)
    vitamin_c: float        # 비타민C (mg)
    cholesterol: float      # 콜레스테롤 (mg)


class ExerciseRecommendation(TypedDict, total=False):
    """운동 추천 정보"""
    name: str               # 운동 이름
    name_kr: str            # 운동 이름 (한글)
    intensity: Literal["low", "medium", "high"]  # 강도
    duration_minutes: float  # 권장 운동 시간 (분)
    calories_burned: float  # 소모 칼로리 (kcal)
    met: float              # MET 값
    description: str        # 운동 설명
    tips: str               # 팁


class ChatState(TypedDict, total=False):
    """LangGraph 워크플로우 State

    전체 대화 흐름에서 사용되는 상태 정보를 담는 TypedDict

    Flow:
        1. user_query → QueryAnalyzer → analyzed_query
        2. analyzed_query → RecipeFetcher → recipe, recipe_source
        3. recipe → NutritionCalculator → nutrition
        4. nutrition + user_profile → ExerciseRecommender → exercise_recommendations
        5. all data → ResponseFormatter → response
    """
    # 입력
    user_query: str                                     # 사용자 쿼리
    user_profile: Optional[UserProfile]                 # 사용자 프로필 (선택)

    # QueryAnalyzer 출력
    analyzed_query: AnalyzedQuery                       # 파싱된 쿼리

    # RecipeFetcher 출력
    recipe: RecipeInfo                                  # 레시피 정보
    recipe_source: Literal["database", "llm_fallback"]  # 레시피 출처

    # NutritionCalculator 출력
    nutrition: NutritionInfo                            # 영양 정보

    # ExerciseRecommender 출력
    exercise_recommendations: List[ExerciseRecommendation]  # 운동 추천 목록

    # ResponseFormatter 출력
    response: str                                       # 최종 응답

    # 에러 처리
    error: Optional[str]                                # 에러 메시지


def create_initial_state(
    user_query: str,
    user_profile: Optional[UserProfile] = None
) -> ChatState:
    """초기 State 생성

    Args:
        user_query: 사용자 쿼리
        user_profile: 사용자 프로필 (선택)

    Returns:
        초기화된 ChatState
    """
    return ChatState(
        user_query=user_query,
        user_profile=user_profile,
        analyzed_query={},
        recipe={},
        recipe_source="database",
        nutrition={},
        exercise_recommendations=[],
        response="",
        error=None
    )


def get_default_user_profile() -> UserProfile:
    """기본 사용자 프로필 반환

    운동 추천 계산에 사용할 기본값
    """
    return UserProfile(
        weight=65.0,
        height=170.0,
        age=30,
        gender="male",
        activity_level="moderate"
    )
