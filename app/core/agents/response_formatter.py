"""ResponseFormatter Agent - 최종 응답 생성"""

import json
import logging
from typing import Optional

from openai import OpenAI

from app.config import get_settings
from app.core.workflow.state import ChatState

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """당신은 친근하고 전문적인 한국 음식 영양사 AI입니다.
사용자에게 레시피, 영양정보, 운동 추천을 자연스러운 한국어로 설명해주세요.

응답 형식:
1. 음식 소개 (1-2문장)
2. 레시피 (재료, 조리법)
3. 영양 정보 (칼로리, 주요 영양소)
4. 운동 추천 (강도별 운동과 시간)
5. 마무리 조언 (1문장)

주의사항:
- 마크다운 형식 사용 (##, *, - 등)
- 이모지를 적절히 사용하여 친근한 분위기
- 숫자는 쉽게 읽을 수 있도록 (예: 1,000 → 1,000)
- 운동 시간은 분 단위로 표시
"""


class ResponseFormatter:
    """최종 응답 생성 Agent

    모든 정보를 종합하여 자연스러운 응답 생성
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model

    def format(self, state: ChatState) -> ChatState:
        """
        전체 State를 기반으로 최종 응답 생성

        Args:
            state: 모든 정보가 포함된 ChatState

        Returns:
            response가 업데이트된 ChatState
        """
        logger.info("최종 응답 생성 시작")

        try:
            # GPT로 응답 생성
            response = self._generate_with_gpt(state)

            if response:
                state["response"] = response
                logger.info("GPT 응답 생성 완료")
            else:
                # Fallback: 템플릿 기반 응답
                response = self._generate_template_response(state)
                state["response"] = response
                logger.warning("템플릿 응답 사용")

        except Exception as e:
            logger.error(f"응답 생성 실패: {e}")
            state["response"] = self._generate_template_response(state)

        return state

    def _generate_with_gpt(self, state: ChatState) -> Optional[str]:
        """GPT를 사용한 응답 생성"""
        # State 정보 정리
        context = self._build_context(state)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT 응답 생성 오류: {e}")
            return None

    def _build_context(self, state: ChatState) -> str:
        """GPT 컨텍스트 빌드"""
        user_query = state.get("user_query", "")
        recipe = state.get("recipe", {})
        recipe_source = state.get("recipe_source", "database")
        nutrition = state.get("nutrition", {})
        exercises = state.get("exercise_recommendations", [])
        analyzed = state.get("analyzed_query", {})

        context_parts = [
            f"사용자 질문: {user_query}",
            f"음식명: {analyzed.get('food_name', '')}",
            f"인분 수: {analyzed.get('servings', 1)}인분",
            f"레시피 출처: {'데이터베이스' if recipe_source == 'database' else 'AI 생성'}",
        ]

        # 레시피 정보
        if recipe:
            context_parts.append(f"\n레시피 정보:")
            context_parts.append(f"- 음식명: {recipe.get('name', '')}")
            context_parts.append(f"- 분류: {recipe.get('category', '')}")
            context_parts.append(f"- 조리방법: {recipe.get('cooking_method', '')}")

            ingredients = recipe.get("ingredients", [])
            if ingredients:
                context_parts.append(f"- 재료: {', '.join(ingredients[:10])}")

            instructions = recipe.get("instructions", [])
            if instructions:
                context_parts.append(f"- 조리법: {' '.join(instructions[:5])}")

            if recipe.get("tips"):
                context_parts.append(f"- 팁: {recipe.get('tips')}")

        # 영양 정보
        if nutrition:
            context_parts.append(f"\n영양 정보 ({nutrition.get('servings', 1)}인분):")
            context_parts.append(f"- 칼로리: {nutrition.get('calories', 0):.0f}kcal")
            context_parts.append(f"- 단백질: {nutrition.get('protein', 0):.1f}g")
            context_parts.append(f"- 지방: {nutrition.get('fat', 0):.1f}g")
            context_parts.append(f"- 탄수화물: {nutrition.get('carbohydrate', 0):.1f}g")
            if nutrition.get("sodium", 0) > 0:
                context_parts.append(f"- 나트륨: {nutrition.get('sodium', 0):.0f}mg")

        # 운동 추천
        if exercises:
            context_parts.append(f"\n운동 추천 (소모 칼로리: {nutrition.get('calories', 0):.0f}kcal):")
            for ex in exercises:
                intensity_kr = {"low": "저강도", "medium": "중강도", "high": "고강도"}.get(
                    ex.get("intensity", ""), ""
                )
                context_parts.append(
                    f"- {intensity_kr}: {ex.get('name_kr', '')} "
                    f"({ex.get('duration_minutes', 0):.0f}분)"
                )

        return "\n".join(context_parts)

    def _generate_template_response(self, state: ChatState) -> str:
        """템플릿 기반 응답 생성 (Fallback)"""
        recipe = state.get("recipe", {})
        nutrition = state.get("nutrition", {})
        exercises = state.get("exercise_recommendations", [])
        analyzed = state.get("analyzed_query", {})
        recipe_source = state.get("recipe_source", "database")

        food_name = recipe.get("name", "") or analyzed.get("food_name", "음식")
        servings = analyzed.get("servings", 1)

        parts = []

        # 인사
        parts.append(f"## 🍳 {food_name} 정보\n")

        # 레시피
        if recipe.get("ingredients") or recipe.get("instructions"):
            parts.append(f"### 📝 레시피 ({servings}인분)")
            if recipe_source == "llm_fallback":
                parts.append("*AI가 생성한 레시피입니다.*\n")

            if recipe.get("ingredients"):
                parts.append("\n**재료:**")
                for ing in recipe.get("ingredients", [])[:10]:
                    parts.append(f"- {ing}")

            if recipe.get("instructions"):
                parts.append("\n**조리법:**")
                for i, inst in enumerate(recipe.get("instructions", []), 1):
                    parts.append(f"{i}. {inst}")

            if recipe.get("tips"):
                parts.append(f"\n💡 **팁:** {recipe.get('tips')}")
            parts.append("")

        # 영양 정보
        if nutrition.get("calories", 0) > 0:
            parts.append(f"### 🥗 영양 정보 ({servings}인분)")
            parts.append(f"- 🔥 칼로리: **{nutrition.get('calories', 0):.0f}kcal**")
            parts.append(f"- 🥩 단백질: {nutrition.get('protein', 0):.1f}g")
            parts.append(f"- 🧈 지방: {nutrition.get('fat', 0):.1f}g")
            parts.append(f"- 🍚 탄수화물: {nutrition.get('carbohydrate', 0):.1f}g")
            if nutrition.get("sodium", 0) > 0:
                parts.append(f"- 🧂 나트륨: {nutrition.get('sodium', 0):.0f}mg")
            parts.append("")

        # 운동 추천
        if exercises:
            parts.append(f"### 🏃 운동 추천")
            parts.append(f"*{nutrition.get('calories', 0):.0f}kcal를 소모하기 위한 운동:*\n")

            intensity_emoji = {"low": "🚶", "medium": "🚴", "high": "🏃"}
            intensity_kr = {"low": "저강도", "medium": "중강도", "high": "고강도"}

            for ex in exercises:
                emoji = intensity_emoji.get(ex.get("intensity", ""), "🏃")
                kr = intensity_kr.get(ex.get("intensity", ""), "")
                parts.append(
                    f"- {emoji} **{kr}** - {ex.get('name_kr', '')}: "
                    f"약 {ex.get('duration_minutes', 0):.0f}분"
                )
            parts.append("")

        # 마무리
        parts.append("---")
        parts.append("*맛있게 드시고, 건강한 하루 보내세요!* 😊")

        return "\n".join(parts)


# 싱글톤 인스턴스
_response_formatter: Optional[ResponseFormatter] = None


def get_response_formatter() -> ResponseFormatter:
    """ResponseFormatter 싱글톤 인스턴스 반환"""
    global _response_formatter
    if _response_formatter is None:
        _response_formatter = ResponseFormatter()
    return _response_formatter


def format_response(state: ChatState) -> ChatState:
    """LangGraph 노드 함수"""
    formatter = get_response_formatter()
    return formatter.format(state)
