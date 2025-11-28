"""QueryAnalyzer Agent - 사용자 쿼리 분석"""

import json
import logging
import re
from typing import Optional

from openai import OpenAI

from app.config import get_settings
from app.core.workflow.state import ChatState, AnalyzedQuery

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """당신은 한국 음식 관련 쿼리를 분석하는 AI 어시스턴트입니다.
사용자의 쿼리에서 다음 정보를 추출해주세요:

1. food_name: 음식 이름 (한글)
2. servings: 인분 수 (기본값: 1)
3. query_type: 쿼리 유형
   - "recipe": 레시피 요청
   - "nutrition": 영양정보 요청
   - "exercise": 운동 추천 요청
   - "general": 일반 질문

반드시 다음 JSON 형식으로만 응답하세요:
{
    "food_name": "음식이름",
    "servings": 1,
    "query_type": "recipe"
}

예시:
- "김치찌개 2인분 레시피 알려줘" → {"food_name": "김치찌개", "servings": 2, "query_type": "recipe"}
- "불고기 칼로리가 어떻게 돼?" → {"food_name": "불고기", "servings": 1, "query_type": "nutrition"}
- "비빔밥 먹고 운동 얼마나 해야해?" → {"food_name": "비빔밥", "servings": 1, "query_type": "exercise"}
- "된장찌개" → {"food_name": "된장찌개", "servings": 1, "query_type": "recipe"}
"""


class QueryAnalyzer:
    """사용자 쿼리 분석 Agent"""

    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model

    def analyze(self, state: ChatState) -> ChatState:
        """
        사용자 쿼리를 분석하여 음식명, 인분수, 쿼리 유형 추출

        Args:
            state: 현재 ChatState

        Returns:
            analyzed_query가 업데이트된 ChatState
        """
        user_query = state.get("user_query", "")
        if not user_query:
            state["error"] = "사용자 쿼리가 비어있습니다."
            return state

        logger.info(f"쿼리 분석 시작: {user_query}")

        try:
            # GPT로 쿼리 분석
            analyzed = self._analyze_with_gpt(user_query)

            if analyzed:
                state["analyzed_query"] = analyzed
                logger.info(f"쿼리 분석 완료: {analyzed}")
            else:
                # GPT 실패 시 기본 파싱 시도
                analyzed = self._fallback_parse(user_query)
                state["analyzed_query"] = analyzed
                logger.warning(f"GPT 분석 실패, 기본 파싱 사용: {analyzed}")

        except Exception as e:
            logger.error(f"쿼리 분석 실패: {e}")
            # 에러 발생 시 기본 파싱
            analyzed = self._fallback_parse(user_query)
            state["analyzed_query"] = analyzed

        return state

    def _analyze_with_gpt(self, query: str) -> Optional[AnalyzedQuery]:
        """GPT를 사용한 쿼리 분석"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                temperature=0,
                max_tokens=200
            )

            content = response.choices[0].message.content
            logger.debug(f"GPT 응답: {content}")

            # JSON 파싱
            parsed = self._parse_json(content)
            if parsed:
                return AnalyzedQuery(
                    food_name=parsed.get("food_name", ""),
                    servings=parsed.get("servings", 1),
                    query_type=parsed.get("query_type", "recipe"),
                    original_query=query
                )

            return None

        except Exception as e:
            logger.error(f"GPT 분석 오류: {e}")
            return None

    def _parse_json(self, text: str) -> Optional[dict]:
        """텍스트에서 JSON 추출 및 파싱"""
        try:
            # 직접 파싱 시도
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # JSON 블록 추출 시도
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None

    def _fallback_parse(self, query: str) -> AnalyzedQuery:
        """GPT 없이 기본 규칙 기반 파싱"""
        food_name = ""
        servings = 1
        query_type = "recipe"

        # 인분 수 추출 (예: "2인분", "3인분")
        servings_match = re.search(r'(\d+)\s*인분', query)
        if servings_match:
            servings = int(servings_match.group(1))

        # 쿼리 유형 추출
        if any(word in query for word in ["칼로리", "영양", "영양소", "성분"]):
            query_type = "nutrition"
        elif any(word in query for word in ["운동", "소모", "태우"]):
            query_type = "exercise"
        elif any(word in query for word in ["레시피", "만드는", "요리법", "조리법"]):
            query_type = "recipe"

        # 음식명 추출 (간단한 규칙: 첫 번째 명사 추출)
        # 인분, 레시피 등 키워드 제거 후 첫 단어
        clean_query = re.sub(r'\d+\s*인분', '', query)
        clean_query = re.sub(r'(레시피|만드는\s*법|요리법|조리법|알려줘|알려주세요|만들어줘)', '', clean_query)
        clean_query = re.sub(r'(칼로리|영양|운동|소모)', '', clean_query)
        words = clean_query.strip().split()
        if words:
            food_name = words[0]

        return AnalyzedQuery(
            food_name=food_name,
            servings=servings,
            query_type=query_type,
            original_query=query
        )


# 싱글톤 인스턴스
_query_analyzer: Optional[QueryAnalyzer] = None


def get_query_analyzer() -> QueryAnalyzer:
    """QueryAnalyzer 싱글톤 인스턴스 반환"""
    global _query_analyzer
    if _query_analyzer is None:
        _query_analyzer = QueryAnalyzer()
    return _query_analyzer


def analyze_query(state: ChatState) -> ChatState:
    """LangGraph 노드 함수"""
    analyzer = get_query_analyzer()
    return analyzer.analyze(state)
