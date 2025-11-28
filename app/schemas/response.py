"""API 응답 스키마 정의"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class RecipeResponse(BaseModel):
    """레시피 응답 스키마"""
    recipe_id: str = Field(default="", description="레시피 ID")
    name: str = Field(..., description="음식명")
    category: str = Field(default="", description="카테고리")
    cooking_method: str = Field(default="", description="조리 방법")
    ingredients: List[str] = Field(default_factory=list, description="재료 목록")
    instructions: List[str] = Field(default_factory=list, description="조리 순서")
    tips: str = Field(default="", description="조리 팁")
    image_url: str = Field(default="", description="이미지 URL")
    source: Literal["database", "llm_fallback"] = Field(
        default="database",
        description="레시피 출처 (database: DB / llm_fallback: GPT 생성)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "recipe_id": "28",
                "name": "김치찌개",
                "category": "국/찌개",
                "cooking_method": "끓이기",
                "ingredients": ["김치 200g", "돼지고기 100g", "두부 1/2모", "대파 1대"],
                "instructions": ["1. 돼지고기를 볶는다", "2. 김치를 넣고 볶는다", "3. 물을 붓고 끓인다"],
                "tips": "묵은지를 사용하면 더 맛있어요",
                "image_url": "http://example.com/image.png",
                "source": "database"
            }
        }


class NutritionResponse(BaseModel):
    """영양정보 응답 스키마"""
    food_name: str = Field(..., description="음식명")
    servings: int = Field(default=1, ge=1, description="인분 수")
    serving_size: float = Field(default=0, ge=0, description="1회 제공량 (g)")
    calories: float = Field(default=0, ge=0, description="칼로리 (kcal)")
    protein: float = Field(default=0, ge=0, description="단백질 (g)")
    fat: float = Field(default=0, ge=0, description="지방 (g)")
    carbohydrate: float = Field(default=0, ge=0, description="탄수화물 (g)")
    sugar: float = Field(default=0, ge=0, description="당류 (g)")
    fiber: float = Field(default=0, ge=0, description="식이섬유 (g)")
    sodium: float = Field(default=0, ge=0, description="나트륨 (mg)")
    calcium: float = Field(default=0, ge=0, description="칼슘 (mg)")
    iron: float = Field(default=0, ge=0, description="철분 (mg)")
    potassium: float = Field(default=0, ge=0, description="칼륨 (mg)")
    vitamin_a: float = Field(default=0, ge=0, description="비타민A (μg)")
    vitamin_c: float = Field(default=0, ge=0, description="비타민C (mg)")
    cholesterol: float = Field(default=0, ge=0, description="콜레스테롤 (mg)")

    class Config:
        json_schema_extra = {
            "example": {
                "food_name": "김치찌개",
                "servings": 2,
                "serving_size": 400,
                "calories": 350,
                "protein": 20.5,
                "fat": 15.0,
                "carbohydrate": 30.0,
                "sugar": 5.0,
                "fiber": 3.0,
                "sodium": 1200,
                "calcium": 80,
                "iron": 2.5,
                "potassium": 450,
                "vitamin_a": 150,
                "vitamin_c": 15,
                "cholesterol": 45
            }
        }


class ExerciseResponse(BaseModel):
    """운동 추천 응답 스키마"""
    name: str = Field(..., description="운동명 (영문)")
    name_kr: str = Field(..., description="운동명 (한글)")
    intensity: Literal["low", "medium", "high"] = Field(..., description="강도")
    duration_minutes: float = Field(..., ge=0, description="권장 시간 (분)")
    calories_burned: float = Field(..., ge=0, description="소모 칼로리 (kcal)")
    met: float = Field(..., ge=0, description="MET 값")
    description: str = Field(default="", description="운동 설명")
    tips: str = Field(default="", description="운동 팁")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "running_slow",
                "name_kr": "조깅",
                "intensity": "high",
                "duration_minutes": 45,
                "calories_burned": 350,
                "met": 8.0,
                "description": "시속 8km로 조깅",
                "tips": "워밍업 후 시작하세요"
            }
        }


class AnalyzedQueryResponse(BaseModel):
    """분석된 쿼리 응답"""
    food_name: str = Field(..., description="추출된 음식명")
    servings: int = Field(default=1, ge=1, description="인분 수")
    query_type: str = Field(default="recipe", description="쿼리 유형")
    original_query: str = Field(..., description="원본 쿼리")


class SearchResponse(BaseModel):
    """통합 검색 응답 스키마"""
    success: bool = Field(default=True, description="성공 여부")
    message: str = Field(default="", description="메시지")

    # 분석된 쿼리
    analyzed_query: Optional[AnalyzedQueryResponse] = Field(
        default=None,
        description="분석된 쿼리 정보"
    )

    # 레시피
    recipe: Optional[RecipeResponse] = Field(
        default=None,
        description="레시피 정보"
    )

    # 영양정보
    nutrition: Optional[NutritionResponse] = Field(
        default=None,
        description="영양 정보"
    )

    # 운동 추천
    exercises: List[ExerciseResponse] = Field(
        default_factory=list,
        description="운동 추천 목록 (저/중/고강도)"
    )

    # 최종 응답
    response: str = Field(default="", description="자연어 응답")

    # 처리 시간
    processing_time_ms: float = Field(default=0, ge=0, description="처리 시간 (ms)")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "검색 완료",
                "analyzed_query": {
                    "food_name": "김치찌개",
                    "servings": 2,
                    "query_type": "recipe",
                    "original_query": "김치찌개 2인분 레시피"
                },
                "recipe": {
                    "name": "김치찌개",
                    "category": "국/찌개",
                    "ingredients": ["김치", "돼지고기", "두부"],
                    "instructions": ["1. 볶기", "2. 끓이기"],
                    "source": "database"
                },
                "nutrition": {
                    "food_name": "김치찌개",
                    "servings": 2,
                    "calories": 350,
                    "protein": 20.5,
                    "fat": 15.0,
                    "carbohydrate": 30.0
                },
                "exercises": [
                    {"name_kr": "걷기", "intensity": "low", "duration_minutes": 90},
                    {"name_kr": "자전거", "intensity": "medium", "duration_minutes": 50},
                    {"name_kr": "조깅", "intensity": "high", "duration_minutes": 35}
                ],
                "response": "김치찌개 2인분 레시피입니다...",
                "processing_time_ms": 1250.5
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    success: bool = Field(default=False, description="성공 여부")
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="상세 정보")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "쿼리 분석 실패",
                "detail": "음식명을 추출할 수 없습니다"
            }
        }


class HealthResponse(BaseModel):
    """헬스체크 응답 스키마"""
    status: str = Field(default="healthy", description="서비스 상태")
    services: dict = Field(default_factory=dict, description="서비스별 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "vector_db": {"ready": True, "total_recipes": 1139},
                    "nutrition_db": {"ready": True, "total_records": 167337},
                    "openai": {"ready": True}
                }
            }
        }
