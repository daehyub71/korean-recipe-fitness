"""NutritionCalculator Agent - 영양 정보 계산"""

import logging
from typing import Optional

from app.core.workflow.state import ChatState, NutritionInfo
from app.core.services.nutrition_db_service import get_nutrition_db_service

logger = logging.getLogger(__name__)


class NutritionCalculator:
    """영양 정보 계산 Agent

    NutritionDBService를 사용하여 영양정보 조회
    인분 수에 따라 영양정보 계산
    """

    def __init__(self):
        self.nutrition_db = get_nutrition_db_service()

    def calculate(self, state: ChatState) -> ChatState:
        """
        레시피 또는 음식명에 대한 영양 정보 계산

        Args:
            state: recipe, analyzed_query가 포함된 ChatState

        Returns:
            nutrition이 업데이트된 ChatState
        """
        analyzed_query = state.get("analyzed_query", {})
        recipe = state.get("recipe", {})

        # 음식명 결정 (레시피 이름 우선, 없으면 쿼리에서 추출)
        food_name = recipe.get("name", "") or analyzed_query.get("food_name", "")
        servings = analyzed_query.get("servings", 1)

        if not food_name:
            logger.warning("음식명이 없습니다.")
            state["nutrition"] = self._create_empty_nutrition("")
            return state

        logger.info(f"영양정보 조회: {food_name} ({servings}인분)")

        # 레시피에 영양정보가 있는 경우 (recipe DB에서 가져온 경우)
        recipe_nutrition = self._get_nutrition_from_recipe(recipe)
        if recipe_nutrition:
            nutrition_info = self._calculate_with_servings(recipe_nutrition, food_name, servings)
            state["nutrition"] = nutrition_info
            logger.info(f"레시피 영양정보 사용: {nutrition_info.get('calories', 0):.0f}kcal")
            return state

        # NutritionDB에서 검색
        if self.nutrition_db.is_ready:
            nutrition_info = self._search_nutrition_db(food_name, servings)
            if nutrition_info.get("calories", 0) > 0:
                state["nutrition"] = nutrition_info
                logger.info(f"영양DB 검색 결과: {nutrition_info.get('calories', 0):.0f}kcal")
                return state

        # 영양정보 없음
        logger.warning(f"'{food_name}' 영양정보를 찾을 수 없습니다.")
        state["nutrition"] = self._create_empty_nutrition(food_name, servings)
        return state

    def _get_nutrition_from_recipe(self, recipe: dict) -> Optional[dict]:
        """레시피 데이터에서 영양정보 추출"""
        import json
        from pathlib import Path

        # 레시피에 직접 영양정보가 있는 경우
        if "nutrition" in recipe and recipe["nutrition"]:
            return recipe["nutrition"]

        # recipe_id로 상세 정보 조회
        recipe_id = recipe.get("recipe_id", "")
        if not recipe_id:
            return None

        recipes_file = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "recipes.json"
        try:
            if recipes_file.exists():
                with open(recipes_file, "r", encoding="utf-8") as f:
                    recipes = json.load(f)

                for r in recipes:
                    if r.get("recipe_id") == recipe_id:
                        return r.get("nutrition", {})
        except Exception as e:
            logger.error(f"레시피 영양정보 조회 실패: {e}")

        return None

    def _search_nutrition_db(self, food_name: str, servings: int) -> NutritionInfo:
        """NutritionDB에서 영양정보 검색"""
        try:
            # 정확한 매칭 시도
            result = self.nutrition_db.get_nutrition(food_name)

            # 정확한 매칭 없으면 유사 검색
            if not result:
                similar_results = self.nutrition_db.search_similar(food_name, limit=3)
                if similar_results:
                    result = similar_results[0]
                    logger.info(f"유사 음식 매칭: {result.get('food_name', '')}")

            if result:
                nutrition = result.get("nutrition", {})
                return self._calculate_with_servings(nutrition, food_name, servings)

        except Exception as e:
            logger.error(f"영양정보 DB 검색 실패: {e}")

        return self._create_empty_nutrition(food_name, servings)

    def _calculate_with_servings(
        self,
        nutrition: dict,
        food_name: str,
        servings: int
    ) -> NutritionInfo:
        """인분 수에 따른 영양정보 계산"""
        multiplier = servings

        return NutritionInfo(
            food_name=food_name,
            serving_size=nutrition.get("serving_size", 100) * multiplier,
            servings=servings,
            calories=round(nutrition.get("calories", 0) * multiplier, 1),
            protein=round(nutrition.get("protein", 0) * multiplier, 1),
            fat=round(nutrition.get("fat", 0) * multiplier, 1),
            carbohydrate=round(nutrition.get("carbohydrate", 0) * multiplier, 1),
            sugar=round(nutrition.get("sugar", 0) * multiplier, 1),
            fiber=round(nutrition.get("fiber", 0) * multiplier, 1),
            sodium=round(nutrition.get("sodium", 0) * multiplier, 1),
            calcium=round(nutrition.get("calcium", 0) * multiplier, 1),
            iron=round(nutrition.get("iron", 0) * multiplier, 1),
            potassium=round(nutrition.get("potassium", 0) * multiplier, 1),
            vitamin_a=round(nutrition.get("vitamin_a", 0) * multiplier, 1),
            vitamin_c=round(nutrition.get("vitamin_c", 0) * multiplier, 1),
            cholesterol=round(nutrition.get("cholesterol", 0) * multiplier, 1)
        )

    def _create_empty_nutrition(self, food_name: str, servings: int = 1) -> NutritionInfo:
        """빈 영양정보 생성"""
        return NutritionInfo(
            food_name=food_name,
            serving_size=0,
            servings=servings,
            calories=0,
            protein=0,
            fat=0,
            carbohydrate=0,
            sugar=0,
            fiber=0,
            sodium=0,
            calcium=0,
            iron=0,
            potassium=0,
            vitamin_a=0,
            vitamin_c=0,
            cholesterol=0
        )


# 싱글톤 인스턴스
_nutrition_calculator: Optional[NutritionCalculator] = None


def get_nutrition_calculator() -> NutritionCalculator:
    """NutritionCalculator 싱글톤 인스턴스 반환"""
    global _nutrition_calculator
    if _nutrition_calculator is None:
        _nutrition_calculator = NutritionCalculator()
    return _nutrition_calculator


def calculate_nutrition(state: ChatState) -> ChatState:
    """LangGraph 노드 함수"""
    calculator = get_nutrition_calculator()
    return calculator.calculate(state)
