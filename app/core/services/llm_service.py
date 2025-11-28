"""LLM 서비스 - GPT를 사용한 레시피/영양정보 생성"""

import json
import logging
import re
from typing import Optional, Dict, List

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


RECIPE_GENERATION_PROMPT = """당신은 한국 요리 전문가입니다.
사용자가 요청한 음식의 레시피를 JSON 형식으로 생성해주세요.

요청 음식: {food_name}
인분 수: {servings}

반드시 다음 JSON 형식으로만 응답하세요:
{{
    "name": "음식명",
    "category": "분류 (예: 국/찌개, 반찬, 밥, 면, 후식 등)",
    "cooking_method": "조리방법 (예: 끓이기, 볶음, 구이, 찜 등)",
    "ingredients": ["재료1 (양)", "재료2 (양)", ...],
    "instructions": ["1. 첫번째 단계", "2. 두번째 단계", ...],
    "tips": "조리 팁",
    "estimated_time": 30
}}

정확한 한국 요리 레시피를 제공하되, 양은 요청된 인분 수에 맞게 조절해주세요.
"""


NUTRITION_ESTIMATION_PROMPT = """당신은 영양학 전문가입니다.
주어진 음식의 영양정보를 추정하여 JSON 형식으로 응답해주세요.

음식명: {food_name}
인분 수: {servings}

1인분 기준 영양정보를 추정하고, 인분 수를 곱하여 계산해주세요.

반드시 다음 JSON 형식으로만 응답하세요:
{{
    "food_name": "음식명",
    "serving_size": 1회 제공량(g),
    "servings": {servings},
    "calories": 칼로리(kcal),
    "protein": 단백질(g),
    "fat": 지방(g),
    "carbohydrate": 탄수화물(g),
    "sodium": 나트륨(mg),
    "sugar": 당류(g),
    "fiber": 식이섬유(g)
}}

한국 음식의 일반적인 영양정보를 참고하여 합리적인 수치를 제공해주세요.
모든 수치는 숫자만 입력 (단위 제외).
"""


class LLMService:
    """GPT를 사용한 레시피/영양정보 생성 서비스"""

    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model

    def generate_recipe(
        self,
        food_name: str,
        servings: int = 1
    ) -> Optional[Dict]:
        """
        GPT로 레시피 생성

        Args:
            food_name: 음식 이름
            servings: 인분 수

        Returns:
            레시피 정보 딕셔너리 또는 None
        """
        logger.info(f"GPT 레시피 생성: {food_name} ({servings}인분)")

        prompt = RECIPE_GENERATION_PROMPT.format(
            food_name=food_name,
            servings=servings
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Korean cuisine expert. Always respond in valid JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            content = response.choices[0].message.content
            recipe = self._parse_json(content)

            if recipe:
                # 기본 필드 보장
                recipe.setdefault("name", food_name)
                recipe.setdefault("category", "기타")
                recipe.setdefault("cooking_method", "")
                recipe.setdefault("ingredients", [])
                recipe.setdefault("instructions", [])
                recipe.setdefault("tips", "")
                recipe.setdefault("image_url", "")
                recipe["recipe_id"] = ""  # LLM 생성 레시피는 ID 없음

                logger.info(f"레시피 생성 완료: {recipe.get('name')}")
                return recipe

        except Exception as e:
            logger.error(f"레시피 생성 실패: {e}")

        return None

    def generate_nutrition(
        self,
        food_name: str,
        servings: int = 1
    ) -> Optional[Dict]:
        """
        GPT로 영양정보 추정

        Args:
            food_name: 음식 이름
            servings: 인분 수

        Returns:
            영양정보 딕셔너리 또는 None
        """
        logger.info(f"GPT 영양정보 추정: {food_name} ({servings}인분)")

        prompt = NUTRITION_ESTIMATION_PROMPT.format(
            food_name=food_name,
            servings=servings
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert. Always respond in valid JSON format only with numeric values."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )

            content = response.choices[0].message.content
            nutrition = self._parse_json(content)

            if nutrition:
                # 숫자 필드 변환 및 기본값 설정
                numeric_fields = [
                    "serving_size", "servings", "calories", "protein",
                    "fat", "carbohydrate", "sodium", "sugar", "fiber"
                ]

                for field in numeric_fields:
                    if field in nutrition:
                        try:
                            nutrition[field] = float(nutrition[field])
                        except (ValueError, TypeError):
                            nutrition[field] = 0

                nutrition.setdefault("food_name", food_name)
                nutrition.setdefault("servings", servings)

                logger.info(f"영양정보 추정 완료: {nutrition.get('calories', 0):.0f}kcal")
                return nutrition

        except Exception as e:
            logger.error(f"영양정보 추정 실패: {e}")

        return None

    def _parse_json(self, text: str) -> Optional[Dict]:
        """텍스트에서 JSON 추출 및 파싱"""
        # 직접 파싱 시도
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 코드 블록 내 JSON 추출
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        # 중괄호로 둘러싸인 JSON 추출
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None


# 싱글톤 인스턴스
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """LLMService 싱글톤 인스턴스 반환"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
