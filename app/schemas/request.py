"""API 요청 스키마 정의"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class UserProfileSchema(BaseModel):
    """사용자 프로필 스키마"""
    weight: float = Field(default=65.0, ge=30, le=200, description="체중 (kg)")
    height: float = Field(default=170.0, ge=100, le=250, description="키 (cm)")
    age: int = Field(default=30, ge=10, le=100, description="나이")
    gender: Literal["male", "female"] = Field(default="male", description="성별")
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"] = Field(
        default="moderate",
        description="활동 수준 (sedentary/light/moderate/active/very_active)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "weight": 70.0,
                "height": 175.0,
                "age": 30,
                "gender": "male",
                "activity_level": "moderate"
            }
        }


class SearchRequest(BaseModel):
    """검색 요청 스키마"""
    query: str = Field(..., min_length=1, max_length=200, description="검색 쿼리")
    user_profile: Optional[UserProfileSchema] = Field(
        default=None,
        description="사용자 프로필 (선택)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "김치찌개 2인분 레시피 알려줘",
                "user_profile": {
                    "weight": 70.0,
                    "height": 175.0,
                    "age": 30,
                    "gender": "male",
                    "activity_level": "moderate"
                }
            }
        }
