"""Schema module"""

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

__all__ = [
    # Request
    "SearchRequest",
    "UserProfileSchema",
    # Response
    "SearchResponse",
    "RecipeResponse",
    "NutritionResponse",
    "ExerciseResponse",
    "AnalyzedQueryResponse",
    "ErrorResponse",
    "HealthResponse",
]
