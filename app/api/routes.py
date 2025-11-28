"""API 라우트 정의"""

import time
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.request import SearchRequest, UserProfileSchema
from app.schemas.response import (
    SearchResponse,
    RecipeResponse,
    NutritionResponse,
    ExerciseResponse,
    AnalyzedQueryResponse,
    ErrorResponse,
    HealthResponse
)
from app.core.workflow.graph import run_workflow
from app.core.workflow.state import UserProfile
from app.core.services.vector_db_service import get_vector_db_service
from app.core.services.nutrition_db_service import get_nutrition_db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Recipe & Fitness"])


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 오류"}
    },
    summary="레시피 검색 및 영양정보/운동 추천",
    description="사용자 쿼리를 분석하여 레시피, 영양정보, 운동 추천을 제공합니다."
)
async def search(request: SearchRequest) -> SearchResponse:
    """
    레시피 검색 및 영양정보/운동 추천 통합 API

    - 쿼리 분석 (음식명, 인분 추출)
    - 레시피 검색 (Vector DB → LLM Fallback)
    - 영양정보 계산
    - 운동 추천 (칼로리 소모 기준)
    """
    start_time = time.time()

    try:
        logger.info(f"검색 요청: {request.query}")

        # UserProfile 변환
        user_profile: Optional[UserProfile] = None
        if request.user_profile:
            user_profile = UserProfile(
                weight_kg=request.user_profile.weight,
                height_cm=request.user_profile.height,
                age=request.user_profile.age,
                gender=request.user_profile.gender,
                activity_level=request.user_profile.activity_level
            )

        # 워크플로우 실행
        final_state = await run_workflow(request.query, user_profile)

        # 처리 시간 계산
        processing_time_ms = (time.time() - start_time) * 1000

        # 응답 구성
        response = SearchResponse(
            success=True,
            message="검색 완료",
            processing_time_ms=processing_time_ms
        )

        # 분석된 쿼리
        analyzed = final_state.get("analyzed_query", {})
        if analyzed:
            response.analyzed_query = AnalyzedQueryResponse(
                food_name=analyzed.get("food_name", ""),
                servings=analyzed.get("servings", 1),
                query_type=analyzed.get("query_type", "recipe"),
                original_query=request.query
            )

        # 레시피
        recipe_data = final_state.get("recipe")
        if recipe_data:
            response.recipe = RecipeResponse(
                recipe_id=recipe_data.get("recipe_id", ""),
                name=recipe_data.get("name", ""),
                category=recipe_data.get("category", ""),
                cooking_method=recipe_data.get("cooking_method", ""),
                ingredients=recipe_data.get("ingredients", []),
                instructions=recipe_data.get("instructions", []),
                tips=recipe_data.get("tips", ""),
                image_url=recipe_data.get("image_url", ""),
                source=recipe_data.get("source", "database")
            )

        # 영양정보
        nutrition_data = final_state.get("nutrition")
        if nutrition_data:
            response.nutrition = NutritionResponse(
                food_name=nutrition_data.get("food_name", ""),
                servings=nutrition_data.get("servings", 1),
                serving_size=nutrition_data.get("serving_size", 0),
                calories=nutrition_data.get("calories", 0),
                protein=nutrition_data.get("protein", 0),
                fat=nutrition_data.get("fat", 0),
                carbohydrate=nutrition_data.get("carbohydrate", 0),
                sugar=nutrition_data.get("sugar", 0),
                fiber=nutrition_data.get("fiber", 0),
                sodium=nutrition_data.get("sodium", 0),
                calcium=nutrition_data.get("calcium", 0),
                iron=nutrition_data.get("iron", 0),
                potassium=nutrition_data.get("potassium", 0),
                vitamin_a=nutrition_data.get("vitamin_a", 0),
                vitamin_c=nutrition_data.get("vitamin_c", 0),
                cholesterol=nutrition_data.get("cholesterol", 0)
            )

        # 운동 추천
        exercises_data = final_state.get("exercise_recommendations", [])
        response.exercises = [
            ExerciseResponse(
                name=ex.get("name", ""),
                name_kr=ex.get("name_kr", ""),
                intensity=ex.get("intensity", "medium"),
                duration_minutes=ex.get("duration_minutes", 0),
                calories_burned=ex.get("calories_burned", 0),
                met=ex.get("met", 0),
                description=ex.get("description", ""),
                tips=ex.get("tips", "")
            )
            for ex in exercises_data
        ]

        # 최종 응답 텍스트
        response.response = final_state.get("response", "")

        logger.info(f"검색 완료: {processing_time_ms:.0f}ms")
        return response

    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                success=False,
                error="검색 처리 중 오류가 발생했습니다",
                detail=str(e)
            ).model_dump()
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="서비스 상태 확인",
    description="서비스 및 의존성 상태를 확인합니다."
)
async def health_check() -> HealthResponse:
    """헬스체크 엔드포인트"""
    services = {}

    # Vector DB 상태
    try:
        vector_service = get_vector_db_service()
        total_recipes = vector_service.total_recipes if vector_service else 0
        services["vector_db"] = {
            "ready": vector_service.is_ready if vector_service else False,
            "total_recipes": total_recipes
        }
    except Exception as e:
        services["vector_db"] = {"ready": False, "error": str(e)}

    # Nutrition DB 상태
    try:
        nutrition_service = get_nutrition_db_service()
        total_nutrition = nutrition_service.get_total_count() if nutrition_service else 0
        services["nutrition_db"] = {
            "ready": nutrition_service.is_ready if nutrition_service else False,
            "total_records": total_nutrition
        }
    except Exception as e:
        services["nutrition_db"] = {"ready": False, "error": str(e)}

    # OpenAI 상태 (API 키 존재 여부만 확인)
    try:
        from app.config import get_settings
        settings = get_settings()
        services["openai"] = {
            "ready": bool(settings.openai_api_key),
            "model": settings.openai_model
        }
    except Exception as e:
        services["openai"] = {"ready": False, "error": str(e)}

    # 전체 상태 판단
    all_ready = all(s.get("ready", False) for s in services.values())
    status = "healthy" if all_ready else "degraded"

    return HealthResponse(status=status, services=services)
