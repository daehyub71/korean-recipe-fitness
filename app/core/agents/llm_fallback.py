"""LLM Fallback Agent - DB에 없는 레시피/영양정보 생성"""

import logging
from typing import Optional

from app.core.workflow.state import ChatState, RecipeInfo, NutritionInfo
from app.core.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class LLMFallbackAgent:
    """LLM Fallback Agent

    Vector DB나 Nutrition DB에서 찾을 수 없는 경우
    GPT를 사용하여 레시피/영양정보 생성
    """

    def __init__(self):
        self.llm_service = get_llm_service()

    def process(self, state: ChatState) -> ChatState:
        """
        recipe_source가 llm_fallback인 경우 레시피/영양정보 생성

        Args:
            state: ChatState

        Returns:
            recipe, nutrition이 업데이트된 ChatState
        """
        recipe_source = state.get("recipe_source", "database")

        # DB에서 찾은 경우 스킵
        if recipe_source == "database":
            logger.debug("DB 레시피 사용, fallback 스킵")
            return state

        analyzed_query = state.get("analyzed_query", {})
        food_name = analyzed_query.get("food_name", "")
        servings = analyzed_query.get("servings", 1)

        if not food_name:
            logger.warning("음식명이 없어 LLM fallback 불가")
            return state

        logger.info(f"LLM Fallback 시작: {food_name}")

        # 레시피 생성
        recipe = state.get("recipe", {})
        if not recipe.get("ingredients") and not recipe.get("instructions"):
            generated_recipe = self.llm_service.generate_recipe(food_name, servings)
            if generated_recipe:
                # 기존 이미지 URL 보존 (recipe_fetcher에서 설정한 fallback 이미지)
                existing_image_url = recipe.get("image_url", "") if recipe else ""
                state["recipe"] = RecipeInfo(
                    recipe_id="",
                    name=generated_recipe.get("name", food_name),
                    category=generated_recipe.get("category", ""),
                    cooking_method=generated_recipe.get("cooking_method", ""),
                    ingredients=generated_recipe.get("ingredients", []),
                    instructions=generated_recipe.get("instructions", []),
                    tips=generated_recipe.get("tips", ""),
                    image_url=existing_image_url  # 기존 이미지 URL 유지
                )
                logger.info("레시피 생성 완료")

        # 영양정보 생성 (영양정보가 없는 경우)
        nutrition = state.get("nutrition", {})
        if nutrition.get("calories", 0) <= 0:
            generated_nutrition = self.llm_service.generate_nutrition(food_name, servings)
            if generated_nutrition:
                state["nutrition"] = NutritionInfo(
                    food_name=food_name,
                    serving_size=generated_nutrition.get("serving_size", 100),
                    servings=servings,
                    calories=generated_nutrition.get("calories", 0),
                    protein=generated_nutrition.get("protein", 0),
                    fat=generated_nutrition.get("fat", 0),
                    carbohydrate=generated_nutrition.get("carbohydrate", 0),
                    sugar=generated_nutrition.get("sugar", 0),
                    fiber=generated_nutrition.get("fiber", 0),
                    sodium=generated_nutrition.get("sodium", 0),
                    calcium=0,
                    iron=0,
                    potassium=0,
                    vitamin_a=0,
                    vitamin_c=0,
                    cholesterol=0
                )
                logger.info("영양정보 생성 완료")

        return state


# 싱글톤 인스턴스
_llm_fallback_agent: Optional[LLMFallbackAgent] = None


def get_llm_fallback_agent() -> LLMFallbackAgent:
    """LLMFallbackAgent 싱글톤 인스턴스 반환"""
    global _llm_fallback_agent
    if _llm_fallback_agent is None:
        _llm_fallback_agent = LLMFallbackAgent()
    return _llm_fallback_agent


def process_llm_fallback(state: ChatState) -> ChatState:
    """LangGraph 노드 함수"""
    agent = get_llm_fallback_agent()
    return agent.process(state)
