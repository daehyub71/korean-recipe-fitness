"""RecipeFetcher Agent - 레시피 검색"""

import logging
from typing import Optional

from app.core.workflow.state import ChatState, RecipeInfo
from app.core.services.vector_db_service import get_vector_db_service

logger = logging.getLogger(__name__)


class RecipeFetcher:
    """레시피 검색 Agent

    VectorDBService를 사용하여 레시피 검색
    유사도가 낮으면 LLM fallback 마킹
    """

    def __init__(self, similarity_threshold: float = 0.5):
        """
        Args:
            similarity_threshold: 최소 유사도 임계값 (0.5 권장)
        """
        self.similarity_threshold = similarity_threshold
        self.vector_db = get_vector_db_service()

    def fetch(self, state: ChatState) -> ChatState:
        """
        분석된 쿼리를 기반으로 레시피 검색

        검색 우선순위:
        1. 정확한 이름 매칭
        2. 이름에 검색어가 포함된 레시피 (짧은 이름 우선)
        3. 벡터 유사도 검색

        Args:
            state: analyzed_query가 포함된 ChatState

        Returns:
            recipe, recipe_source가 업데이트된 ChatState
        """
        analyzed_query = state.get("analyzed_query", {})
        food_name = analyzed_query.get("food_name", "")

        if not food_name:
            logger.warning("음식명이 없습니다.")
            state["recipe_source"] = "llm_fallback"
            state["recipe"] = {}
            return state

        logger.info(f"레시피 검색: {food_name}")

        # Vector DB 준비 확인
        if not self.vector_db.is_ready:
            logger.warning("Vector DB가 준비되지 않았습니다. LLM fallback 사용")
            state["recipe_source"] = "llm_fallback"
            state["recipe"] = self._create_empty_recipe(food_name)
            return state

        try:
            best_match = None
            use_llm_fallback = False

            # 1단계: 정확한 이름 매칭
            exact_match = self.vector_db.get_recipe_by_name(food_name)
            if exact_match:
                logger.info(f"정확한 매칭: {exact_match.get('name')}")
                best_match = exact_match

            # 2단계: 이름에 검색어가 포함된 레시피 (짧은 이름 우선)
            # 단, 검색어가 기본 요리명(예: 김치찌개, 불고기)이고 정확한 매칭이 없으면
            # 변형 레시피보다 LLM fallback이 더 적합함
            fallback_image_recipe = None  # LLM fallback 시 이미지 참조용
            if not best_match:
                containing_recipes = []
                for recipe in self.vector_db.recipes:
                    recipe_name = recipe.get("name", "")
                    # 검색어가 레시피 이름에 포함되어 있는지 확인
                    if food_name in recipe_name:
                        containing_recipes.append(recipe)

                if containing_recipes:
                    # 이름 길이가 짧은 순으로 정렬
                    containing_recipes.sort(key=lambda x: len(x.get("name", "")))
                    candidate = containing_recipes[0]
                    candidate_name = candidate.get("name", "")

                    # 검색어와 후보 이름이 거의 같은 경우만 사용
                    # 차이가 1글자 이내이거나, 검색어 길이의 20% 이내인 경우만 매칭
                    # 예: "된장국"(3) vs "된장국"(3) OK, "김치찌개"(4) vs "완자김치찌개"(6) NO
                    len_diff = len(candidate_name) - len(food_name)
                    if len_diff <= 1 or (len(food_name) >= 4 and len_diff <= len(food_name) * 0.25):
                        best_match = candidate
                        logger.info(f"이름 포함 매칭: {candidate_name} (후보 {len(containing_recipes)}개)")
                    else:
                        # 변형 레시피만 있으면 LLM fallback 사용 (이미지는 변형 레시피에서 차용)
                        logger.info(f"'{food_name}'의 변형 레시피만 존재 ({candidate_name} 등). LLM fallback 사용")
                        use_llm_fallback = True
                        fallback_image_recipe = candidate  # 이미지 참조용으로 저장

            # 3단계: 벡터 유사도 검색 (LLM fallback이 결정되지 않은 경우에만)
            if not best_match and not use_llm_fallback:
                results = self.vector_db.search(
                    query=food_name,
                    top_k=5,
                    similarity_threshold=self.similarity_threshold
                )

                if results:
                    # 검색어가 포함된 결과 우선
                    for result in results:
                        if food_name in result.get("name", ""):
                            best_match = result
                            break

                    # 없으면 가장 유사한 결과 사용
                    if not best_match:
                        best_match = results[0]

                    logger.info(f"벡터 검색 결과: {best_match.get('name')} (유사도: {best_match.get('similarity', 0):.4f})")

            if best_match:
                # 상세 레시피 정보 조회
                recipe_info = self._get_full_recipe(best_match)
                state["recipe"] = recipe_info
                state["recipe_source"] = "database"
            else:
                # 검색 결과 없음 → LLM fallback
                logger.info(f"'{food_name}' 검색 결과 없음. LLM fallback 사용")
                state["recipe_source"] = "llm_fallback"
                # fallback_image_recipe가 있으면 해당 이미지 사용
                fallback_image_url = self._get_recipe_image(fallback_image_recipe) if fallback_image_recipe else ""
                state["recipe"] = self._create_empty_recipe(food_name, fallback_image_url)

        except Exception as e:
            logger.error(f"레시피 검색 실패: {e}")
            state["recipe_source"] = "llm_fallback"
            state["recipe"] = self._create_empty_recipe(food_name)

        return state

    def _get_full_recipe(self, search_result: dict) -> RecipeInfo:
        """검색 결과에서 상세 레시피 정보 추출"""
        import json
        from pathlib import Path

        # 메타데이터에서 기본 정보 추출
        recipe_id = search_result.get("id", "")
        name = search_result.get("name", "")

        # 전체 레시피 파일에서 상세 정보 조회
        recipes_file = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "recipes.json"

        try:
            if recipes_file.exists():
                with open(recipes_file, "r", encoding="utf-8") as f:
                    recipes = json.load(f)

                # recipe_id 또는 name으로 매칭
                for recipe in recipes:
                    if recipe.get("recipe_id") == recipe_id or recipe.get("name") == name:
                        return RecipeInfo(
                            recipe_id=recipe.get("recipe_id", ""),
                            name=recipe.get("name", ""),
                            category=recipe.get("category", ""),
                            cooking_method=recipe.get("cooking_method", ""),
                            ingredients=recipe.get("ingredients", []),
                            instructions=recipe.get("instructions", []),
                            tips=recipe.get("tip", ""),
                            image_url=recipe.get("image_url", "")
                        )
        except Exception as e:
            logger.error(f"상세 레시피 조회 실패: {e}")

        # 기본 정보만 반환
        return RecipeInfo(
            recipe_id=recipe_id,
            name=name,
            category=search_result.get("category", ""),
            cooking_method=search_result.get("cooking_method", ""),
            ingredients=[],
            instructions=[],
            tips="",
            image_url=""
        )

    def _get_recipe_image(self, recipe_metadata: dict) -> str:
        """레시피 메타데이터에서 이미지 URL 조회"""
        import json
        from pathlib import Path

        recipe_id = recipe_metadata.get("id", "")
        name = recipe_metadata.get("name", "")

        recipes_file = Path(__file__).parent.parent.parent.parent / "data" / "processed" / "recipes.json"

        try:
            if recipes_file.exists():
                with open(recipes_file, "r", encoding="utf-8") as f:
                    recipes = json.load(f)

                for recipe in recipes:
                    if recipe.get("recipe_id") == recipe_id or recipe.get("name") == name:
                        return recipe.get("image_url", "")
        except Exception as e:
            logger.error(f"이미지 URL 조회 실패: {e}")

        return ""

    def _create_empty_recipe(self, food_name: str, fallback_image_url: str = "") -> RecipeInfo:
        """빈 레시피 정보 생성 (LLM fallback용)"""
        return RecipeInfo(
            recipe_id="",
            name=food_name,
            category="",
            cooking_method="",
            ingredients=[],
            instructions=[],
            tips="",
            image_url=fallback_image_url  # 유사 레시피 이미지 사용
        )


# 싱글톤 인스턴스
_recipe_fetcher: Optional[RecipeFetcher] = None


def get_recipe_fetcher() -> RecipeFetcher:
    """RecipeFetcher 싱글톤 인스턴스 반환"""
    global _recipe_fetcher
    if _recipe_fetcher is None:
        _recipe_fetcher = RecipeFetcher()
    return _recipe_fetcher


def fetch_recipe(state: ChatState) -> ChatState:
    """LangGraph 노드 함수"""
    fetcher = get_recipe_fetcher()
    return fetcher.fetch(state)
