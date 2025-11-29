"""API 클라이언트 - FastAPI 서버와 통신 또는 직접 워크플로우 호출"""

import logging
import time
import asyncio
from typing import Optional, Dict, List
import json
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

# API 서버 URL (환경변수 또는 기본값)
API_BASE_URL = "http://localhost:8000"


def search_recipes_multiple(query: str, limit: int = 9) -> Dict:
    """
    다중 레시피 검색 (그리드 표시용)

    Args:
        query: 검색 쿼리
        limit: 최대 결과 수

    Returns:
        {"success": bool, "recipes": List[Dict], "nutrition": Dict, "exercises": List}
    """
    try:
        from app.core.services.vector_db_service import get_vector_db_service
        from app.core.services.nutrition_db_service import get_nutrition_db_service

        vector_db = get_vector_db_service()
        nutrition_db = get_nutrition_db_service()

        if not vector_db or not vector_db.is_ready:
            # Fallback: recipes.json에서 직접 검색
            return _search_from_json(query, limit)

        # 벡터 검색으로 유사 레시피 찾기
        search_results = vector_db.search(query, top_k=limit)

        recipes = []
        first_nutrition = None

        for result in search_results:
            # 벡터 DB 결과는 직접 키로 접근 (metadata 없음)
            recipe_name = result.get("name", "")
            recipe_id = result.get("id", "")

            # 영양정보 조회
            nutrition = None
            if nutrition_db and nutrition_db.is_ready:
                nutrition_result = nutrition_db.get_nutrition(recipe_name)
                if nutrition_result:
                    nutrition = nutrition_result.get("nutrition", {})
                    if not first_nutrition:
                        first_nutrition = {
                            "food_name": recipe_name,
                            "servings": 1,
                            "serving_size": nutrition.get("serving_size", 100),
                            "calories": nutrition.get("calories", 0),
                            "protein": nutrition.get("protein", 0),
                            "fat": nutrition.get("fat", 0),
                            "carbohydrate": nutrition.get("carbohydrate", 0),
                            "sugar": nutrition.get("sugar", 0),
                            "fiber": nutrition.get("fiber", 0),
                            "sodium": nutrition.get("sodium", 0),
                            "calcium": nutrition.get("calcium", 0),
                            "iron": nutrition.get("iron", 0),
                            "potassium": nutrition.get("potassium", 0),
                            "vitamin_a": nutrition.get("vitamin_a", 0),
                            "vitamin_c": nutrition.get("vitamin_c", 0),
                            "cholesterol": nutrition.get("cholesterol", 0)
                        }

            calories = nutrition.get("calories", 0) if nutrition else _estimate_calories(recipe_name)

            # recipes.json에서 상세 정보 가져오기
            recipe_detail = _get_recipe_detail(recipe_id)

            recipes.append({
                "recipe_id": recipe_id,
                "name": recipe_name,
                "category": result.get("category", "한식"),
                "cooking_method": result.get("cooking_method", ""),
                "ingredients": recipe_detail.get("ingredients", []),
                "instructions": recipe_detail.get("instructions", []),
                "image_url": recipe_detail.get("image_url", ""),
                "calories": calories,
                "cooking_time": _estimate_cooking_time(recipe_name),
                "difficulty": _estimate_difficulty(recipe_name),
                "nutrition": nutrition,
                "source": "database"
            })

        # 운동 추천 (첫 번째 레시피 기준)
        exercises = []
        if first_nutrition and first_nutrition.get("calories", 0) > 0:
            exercises = _calculate_exercises(first_nutrition["calories"])

        return {
            "success": True,
            "recipes": recipes,
            "nutrition": first_nutrition,
            "exercises": exercises
        }

    except Exception as e:
        logger.error(f"다중 검색 실패: {e}")
        import traceback
        traceback.print_exc()
        return _search_from_json(query, limit)


def _search_from_json(query: str, limit: int = 9) -> Dict:
    """recipes.json에서 직접 검색 (Fallback)"""
    try:
        recipes_file = Path(__file__).parent.parent.parent / "data" / "processed" / "recipes.json"
        if not recipes_file.exists():
            return {"success": False, "recipes": [], "error": "레시피 파일 없음"}

        with open(recipes_file, "r", encoding="utf-8") as f:
            all_recipes = json.load(f)

        # 간단한 키워드 매칭
        query_lower = query.lower()
        matched = []
        for r in all_recipes:
            name = r.get("name", "").lower()
            if query_lower in name or any(query_lower in ing.lower() for ing in r.get("ingredients", [])):
                matched.append({
                    "recipe_id": r.get("recipe_id", ""),
                    "name": r.get("name", ""),
                    "category": r.get("category", "한식"),
                    "cooking_method": r.get("cooking_method", ""),
                    "ingredients": r.get("ingredients", []),
                    "instructions": r.get("instructions", []),
                    "image_url": r.get("image_url", ""),
                    "calories": _estimate_calories(r.get("name", "")),
                    "cooking_time": _estimate_cooking_time(r.get("name", "")),
                    "difficulty": _estimate_difficulty(r.get("name", "")),
                    "nutrition": r.get("nutrition"),
                    "source": "database"
                })
                if len(matched) >= limit:
                    break

        return {"success": True, "recipes": matched, "nutrition": None, "exercises": []}

    except Exception as e:
        logger.error(f"JSON 검색 실패: {e}")
        return {"success": False, "recipes": [], "error": str(e)}


def _get_recipe_detail(recipe_id: str) -> Dict:
    """recipes.json에서 레시피 상세 정보 가져오기"""
    try:
        recipes_file = Path(__file__).parent.parent.parent / "data" / "processed" / "recipes.json"
        if not recipes_file.exists():
            return {}

        with open(recipes_file, "r", encoding="utf-8") as f:
            all_recipes = json.load(f)

        for r in all_recipes:
            if str(r.get("recipe_id", "")) == str(recipe_id):
                return {
                    "ingredients": r.get("ingredients", []),
                    "instructions": r.get("instructions", []),
                    "image_url": r.get("image_url", ""),
                    "tips": r.get("tips", "")
                }

        return {}
    except Exception:
        return {}


def _estimate_calories(food_name: str) -> int:
    """칼로리 추정 (영양DB 없을 때 fallback)"""
    # 키워드 기반 대략적 추정
    if any(x in food_name for x in ["찌개", "국", "탕"]):
        return 250
    elif any(x in food_name for x in ["볶음", "구이"]):
        return 350
    elif any(x in food_name for x in ["밥", "비빔"]):
        return 450
    elif any(x in food_name for x in ["전", "튀김"]):
        return 400
    elif any(x in food_name for x in ["나물", "샐러드"]):
        return 100
    else:
        return 300


def _estimate_cooking_time(food_name: str) -> int:
    """조리 시간 추정 (분)"""
    if any(x in food_name for x in ["찌개", "탕", "조림"]):
        return 30
    elif any(x in food_name for x in ["볶음", "구이"]):
        return 20
    elif any(x in food_name for x in ["비빔밥", "덮밥"]):
        return 25
    elif any(x in food_name for x in ["전", "부침"]):
        return 25
    elif any(x in food_name for x in ["나물", "무침"]):
        return 15
    else:
        return 30


def _estimate_difficulty(food_name: str) -> str:
    """난이도 추정"""
    if any(x in food_name for x in ["탕", "갈비", "불고기"]):
        return "보통"
    elif any(x in food_name for x in ["찌개", "볶음", "비빔"]):
        return "쉬움"
    elif any(x in food_name for x in ["만두", "잡채", "전"]):
        return "보통"
    else:
        return "쉬움"


def _calculate_exercises(calories: float) -> List[Dict]:
    """칼로리 기반 운동 추천"""
    weight = 70  # 기본 체중

    exercises = [
        {"name": "걷기", "name_kr": "보통 걷기", "met": 3.5, "intensity": "low"},
        {"name": "자전거", "name_kr": "여가 자전거", "met": 5.5, "intensity": "medium"},
        {"name": "달리기", "name_kr": "조깅", "met": 8.0, "intensity": "high"}
    ]

    result = []
    for ex in exercises:
        duration = calories / (ex["met"] * weight / 60)
        result.append({
            "name": ex["name"],
            "name_kr": ex["name_kr"],
            "intensity": ex["intensity"],
            "duration_minutes": round(duration, 0),
            "calories_burned": round(calories, 0),
            "met": ex["met"],
            "description": "",
            "tips": ""
        })

    return result


def search_recipe(
    query: str,
    user_profile: Optional[Dict] = None,
    use_api: bool = False
) -> Dict:
    """
    레시피 검색 (API 또는 직접 호출)

    Args:
        query: 검색 쿼리
        user_profile: 사용자 프로필
        use_api: API 서버 사용 여부 (False면 직접 워크플로우 호출)

    Returns:
        검색 결과 딕셔너리
    """
    if use_api:
        return _search_via_api(query, user_profile)
    else:
        return _search_directly(query, user_profile)


def _search_via_api(query: str, user_profile: Optional[Dict] = None) -> Dict:
    """API 서버를 통한 검색"""
    try:
        import httpx

        request_data = {"query": query}
        if user_profile:
            request_data["user_profile"] = user_profile

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{API_BASE_URL}/api/search",
                json=request_data
            )
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        logger.warning("API 서버 연결 실패, 직접 호출로 전환")
        return _search_directly(query, user_profile)
    except Exception as e:
        logger.error(f"API 호출 실패: {e}")
        return {
            "success": False,
            "error": f"API 호출 실패: {str(e)}"
        }


def _search_directly(query: str, user_profile: Optional[Dict] = None) -> Dict:
    """워크플로우 직접 호출"""
    try:
        from app.core.workflow.graph import run_workflow_sync
        from app.core.workflow.state import UserProfile

        start_time = time.time()

        # UserProfile 변환
        profile = None
        if user_profile:
            profile = UserProfile(
                weight_kg=user_profile.get("weight", 70),
                height_cm=user_profile.get("height", 170),
                age=user_profile.get("age", 30),
                gender=user_profile.get("gender", "male"),
                activity_level=user_profile.get("activity_level", "moderate")
            )

        # 워크플로우 실행
        final_state = run_workflow_sync(query, profile)

        # 처리 시간 계산
        processing_time_ms = (time.time() - start_time) * 1000

        # 응답 구성
        result = {
            "success": True,
            "message": "검색 완료",
            "processing_time_ms": processing_time_ms
        }

        # 분석된 쿼리
        analyzed = final_state.get("analyzed_query", {})
        if analyzed:
            result["analyzed_query"] = {
                "food_name": analyzed.get("food_name", ""),
                "servings": analyzed.get("servings", 1),
                "query_type": analyzed.get("query_type", "recipe"),
                "original_query": query
            }

        # 레시피
        recipe_data = final_state.get("recipe")
        if recipe_data:
            result["recipe"] = {
                "recipe_id": recipe_data.get("recipe_id", ""),
                "name": recipe_data.get("name", ""),
                "category": recipe_data.get("category", ""),
                "cooking_method": recipe_data.get("cooking_method", ""),
                "ingredients": recipe_data.get("ingredients", []),
                "instructions": recipe_data.get("instructions", []),
                "tips": recipe_data.get("tips", ""),
                "image_url": recipe_data.get("image_url", ""),
                "source": recipe_data.get("source", "database")
            }

        # 영양정보
        nutrition_data = final_state.get("nutrition")
        if nutrition_data:
            result["nutrition"] = {
                "food_name": nutrition_data.get("food_name", ""),
                "servings": nutrition_data.get("servings", 1),
                "serving_size": nutrition_data.get("serving_size", 0),
                "calories": nutrition_data.get("calories", 0),
                "protein": nutrition_data.get("protein", 0),
                "fat": nutrition_data.get("fat", 0),
                "carbohydrate": nutrition_data.get("carbohydrate", 0),
                "sugar": nutrition_data.get("sugar", 0),
                "fiber": nutrition_data.get("fiber", 0),
                "sodium": nutrition_data.get("sodium", 0),
                "calcium": nutrition_data.get("calcium", 0),
                "iron": nutrition_data.get("iron", 0),
                "potassium": nutrition_data.get("potassium", 0),
                "vitamin_a": nutrition_data.get("vitamin_a", 0),
                "vitamin_c": nutrition_data.get("vitamin_c", 0),
                "cholesterol": nutrition_data.get("cholesterol", 0)
            }

        # 운동 추천
        exercises_data = final_state.get("exercise_recommendations", [])
        result["exercises"] = [
            {
                "name": ex.get("name", ""),
                "name_kr": ex.get("name_kr", ""),
                "intensity": ex.get("intensity", "medium"),
                "duration_minutes": ex.get("duration_minutes", 0),
                "calories_burned": ex.get("calories_burned", 0),
                "met": ex.get("met", 0),
                "description": ex.get("description", ""),
                "tips": ex.get("tips", "")
            }
            for ex in exercises_data
        ]

        # 최종 응답 텍스트
        result["response"] = final_state.get("response", "")

        return result

    except Exception as e:
        logger.error(f"직접 검색 실패: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"검색 실패: {str(e)}"
        }


def check_health(use_api: bool = True) -> Dict:
    """
    서비스 상태 확인

    Args:
        use_api: API 서버 사용 여부

    Returns:
        상태 정보 딕셔너리
    """
    if use_api:
        return _check_health_via_api()
    else:
        return _check_health_directly()


def _check_health_via_api() -> Dict:
    """API 서버를 통한 상태 확인"""
    try:
        import httpx

        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE_URL}/api/health")
            response.raise_for_status()
            return response.json()

    except Exception as e:
        return {"status": "error", "error": str(e)}


def _check_health_directly() -> Dict:
    """직접 상태 확인"""
    services = {}

    # Vector DB 상태
    try:
        from app.core.services.vector_db_service import get_vector_db_service
        vector_service = get_vector_db_service()
        services["vector_db"] = {
            "ready": vector_service.is_ready if vector_service else False,
            "total_recipes": vector_service.total_recipes if vector_service else 0
        }
    except Exception as e:
        services["vector_db"] = {"ready": False, "error": str(e)}

    # Nutrition DB 상태
    try:
        from app.core.services.nutrition_db_service import get_nutrition_db_service
        nutrition_service = get_nutrition_db_service()
        services["nutrition_db"] = {
            "ready": nutrition_service.is_ready if nutrition_service else False,
            "total_records": nutrition_service.get_total_count() if nutrition_service else 0
        }
    except Exception as e:
        services["nutrition_db"] = {"ready": False, "error": str(e)}

    # OpenAI 상태
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

    return {"status": status, "services": services}
