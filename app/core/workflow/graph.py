"""LangGraph 워크플로우 정의"""

import logging
from pathlib import Path
from typing import Optional

from langgraph.graph import StateGraph, END

from app.core.workflow.state import ChatState, create_initial_state, UserProfile
from app.core.agents.query_analyzer import analyze_query
from app.core.agents.recipe_fetcher import fetch_recipe
from app.core.agents.nutrition_calculator import calculate_nutrition
from app.core.agents.exercise_recommender import recommend_exercises
from app.core.agents.response_formatter import format_response
from app.core.agents.llm_fallback import process_llm_fallback

logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """
    레시피 & 피트니스 워크플로우 생성

    Flow:
        query_analyzer → recipe_fetcher → llm_fallback → nutrition_calculator
        → exercise_recommender → response_formatter → END

    Returns:
        컴파일된 StateGraph
    """
    # StateGraph 생성
    workflow = StateGraph(ChatState)

    # 노드 추가
    workflow.add_node("query_analyzer", analyze_query)
    workflow.add_node("recipe_fetcher", fetch_recipe)
    workflow.add_node("llm_fallback", process_llm_fallback)
    workflow.add_node("nutrition_calculator", calculate_nutrition)
    workflow.add_node("exercise_recommender", recommend_exercises)
    workflow.add_node("response_formatter", format_response)

    # 엣지 연결 (순차적 실행)
    workflow.set_entry_point("query_analyzer")

    workflow.add_edge("query_analyzer", "recipe_fetcher")
    workflow.add_edge("recipe_fetcher", "llm_fallback")
    workflow.add_edge("llm_fallback", "nutrition_calculator")
    workflow.add_edge("nutrition_calculator", "exercise_recommender")
    workflow.add_edge("exercise_recommender", "response_formatter")
    workflow.add_edge("response_formatter", END)

    return workflow


def compile_workflow():
    """워크플로우 컴파일"""
    workflow = create_workflow()
    return workflow.compile()


# 싱글톤 컴파일된 워크플로우
_compiled_workflow = None


def get_compiled_workflow():
    """컴파일된 워크플로우 싱글톤 반환"""
    global _compiled_workflow
    if _compiled_workflow is None:
        _compiled_workflow = compile_workflow()
    return _compiled_workflow


async def run_workflow(
    user_query: str,
    user_profile: Optional[UserProfile] = None
) -> ChatState:
    """
    워크플로우 실행 (비동기)

    Args:
        user_query: 사용자 쿼리
        user_profile: 사용자 프로필 (선택)

    Returns:
        최종 ChatState
    """
    logger.info(f"워크플로우 시작: {user_query}")

    # 초기 State 생성
    initial_state = create_initial_state(user_query, user_profile)

    # 워크플로우 실행
    workflow = get_compiled_workflow()
    final_state = await workflow.ainvoke(initial_state)

    logger.info("워크플로우 완료")
    return final_state


def run_workflow_sync(
    user_query: str,
    user_profile: Optional[UserProfile] = None
) -> ChatState:
    """
    워크플로우 실행 (동기)

    Args:
        user_query: 사용자 쿼리
        user_profile: 사용자 프로필 (선택)

    Returns:
        최종 ChatState
    """
    logger.info(f"워크플로우 시작: {user_query}")

    # 초기 State 생성
    initial_state = create_initial_state(user_query, user_profile)

    # 워크플로우 실행
    workflow = get_compiled_workflow()
    final_state = workflow.invoke(initial_state)

    logger.info("워크플로우 완료")
    return final_state


def get_workflow_diagram() -> str:
    """
    워크플로우 다이어그램 (Mermaid 형식)

    Returns:
        Mermaid 다이어그램 문자열
    """
    return """
    graph TD
        A[Start] --> B[QueryAnalyzer]
        B --> C[RecipeFetcher]
        C --> D[LLM Fallback]
        D --> E[NutritionCalculator]
        E --> F[ExerciseRecommender]
        F --> G[ResponseFormatter]
        G --> H[End]

        subgraph "쿼리 분석"
            B[QueryAnalyzer<br/>음식명, 인분 추출]
        end

        subgraph "레시피 검색"
            C[RecipeFetcher<br/>Vector DB 검색]
            D[LLM Fallback<br/>GPT 레시피 생성]
        end

        subgraph "영양 분석"
            E[NutritionCalculator<br/>영양정보 조회/계산]
        end

        subgraph "운동 추천"
            F[ExerciseRecommender<br/>칼로리 기반 운동 추천]
        end

        subgraph "응답 생성"
            G[ResponseFormatter<br/>자연어 응답 생성]
        end
    """


def save_workflow_png(output_path: Optional[str] = None) -> str:
    """
    워크플로우 다이어그램을 PNG 파일로 저장

    Args:
        output_path: 저장할 파일 경로 (기본: docs/workflow_diagram.png)

    Returns:
        저장된 파일 경로
    """
    from io import BytesIO

    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow가 필요합니다: pip install pillow")

    # 기본 경로 설정
    if output_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        output_path = project_root / "docs" / "workflow_diagram.png"
    else:
        output_path = Path(output_path)

    # 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 워크플로우 컴파일
    compiled = compile_workflow()

    # PNG 생성 (langgraph의 draw_mermaid_png 사용)
    try:
        png_data = compiled.get_graph().draw_mermaid_png()

        # PNG 저장
        with open(output_path, "wb") as f:
            f.write(png_data)

        logger.info(f"워크플로우 다이어그램 저장: {output_path}")
        return str(output_path)

    except Exception as e:
        logger.warning(f"Mermaid PNG 생성 실패: {e}, Graphviz 방식으로 시도")

        # Graphviz 방식으로 시도
        try:
            png_data = compiled.get_graph().draw_png()

            with open(output_path, "wb") as f:
                f.write(png_data)

            logger.info(f"워크플로우 다이어그램 저장 (Graphviz): {output_path}")
            return str(output_path)

        except Exception as e2:
            logger.error(f"Graphviz PNG 생성도 실패: {e2}")
            # 수동으로 Graphviz DOT 생성
            return _save_workflow_png_manual(output_path)


def _save_workflow_png_manual(output_path: Path) -> str:
    """수동으로 Graphviz DOT를 생성하여 PNG 저장"""
    try:
        import graphviz
    except ImportError:
        raise ImportError("graphviz가 필요합니다: pip install graphviz")

    # DOT 그래프 생성
    dot = graphviz.Digraph(
        name="Korean Recipe Fitness Workflow",
        format="png",
        graph_attr={
            "rankdir": "TB",
            "splines": "ortho",
            "nodesep": "0.8",
            "ranksep": "1.0",
            "fontname": "Helvetica",
            "bgcolor": "white"
        },
        node_attr={
            "shape": "box",
            "style": "rounded,filled",
            "fontname": "Helvetica",
            "fontsize": "12",
            "margin": "0.3,0.2"
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "10"
        }
    )

    # 노드 정의
    nodes = [
        ("__start__", "START", "#e8f5e9", "ellipse"),
        ("query_analyzer", "QueryAnalyzer\n(음식명/인분 추출)", "#e3f2fd", "box"),
        ("recipe_fetcher", "RecipeFetcher\n(Vector DB 검색)", "#fff3e0", "box"),
        ("llm_fallback", "LLM Fallback\n(GPT 레시피 생성)", "#fce4ec", "box"),
        ("nutrition_calculator", "NutritionCalculator\n(영양정보 계산)", "#f3e5f5", "box"),
        ("exercise_recommender", "ExerciseRecommender\n(운동 추천)", "#e8eaf6", "box"),
        ("response_formatter", "ResponseFormatter\n(응답 생성)", "#e0f7fa", "box"),
        ("__end__", "END", "#ffebee", "ellipse"),
    ]

    for node_id, label, color, shape in nodes:
        dot.node(node_id, label, fillcolor=color, shape=shape)

    # 엣지 정의
    edges = [
        ("__start__", "query_analyzer"),
        ("query_analyzer", "recipe_fetcher"),
        ("recipe_fetcher", "llm_fallback"),
        ("llm_fallback", "nutrition_calculator"),
        ("nutrition_calculator", "exercise_recommender"),
        ("exercise_recommender", "response_formatter"),
        ("response_formatter", "__end__"),
    ]

    for src, dst in edges:
        dot.edge(src, dst)

    # PNG 저장
    output_stem = str(output_path.with_suffix(""))
    dot.render(output_stem, cleanup=True)

    logger.info(f"워크플로우 다이어그램 저장 (Manual): {output_path}")
    return str(output_path)
