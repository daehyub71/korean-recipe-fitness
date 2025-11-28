"""FastAPI 애플리케이션 엔트리포인트"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 초기화
    logger.info("🚀 Korean Recipe & Fitness API 시작")

    # 서비스 초기화
    try:
        from app.core.services.vector_db_service import get_vector_db_service
        from app.core.services.nutrition_service import get_nutrition_service

        vector_service = get_vector_db_service()
        if vector_service:
            logger.info(f"✅ Vector DB 로드 완료: {vector_service.get_total_count()}개 레시피")
        else:
            logger.warning("⚠️ Vector DB 로드 실패")

        nutrition_service = get_nutrition_service()
        if nutrition_service:
            logger.info(f"✅ Nutrition DB 로드 완료: {nutrition_service.get_total_count()}개 영양정보")
        else:
            logger.warning("⚠️ Nutrition DB 로드 실패")

    except Exception as e:
        logger.error(f"서비스 초기화 실패: {e}")

    yield

    # 종료 시 정리
    logger.info("👋 Korean Recipe & Fitness API 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="Korean Recipe & Fitness API",
    description="""
    한식 레시피 검색, 영양정보 분석, 운동 추천을 제공하는 AI 서비스

    ## 주요 기능
    - 🍳 **레시피 검색**: Vector DB 기반 유사도 검색 + LLM 폴백
    - 📊 **영양정보 분석**: 식약처 영양성분 DB 기반 분석
    - 🏃 **운동 추천**: 섭취 칼로리 기반 운동 추천 (저/중/고 강도)

    ## 워크플로우
    1. QueryAnalyzer: 쿼리 분석 (음식명, 인분 추출)
    2. RecipeFetcher: 레시피 검색
    3. LLM Fallback: DB에 없으면 GPT로 생성
    4. NutritionCalculator: 영양정보 계산
    5. ExerciseRecommender: 운동 추천
    6. ResponseFormatter: 응답 생성
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Streamlit 등 로컬 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Korean Recipe & Fitness API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
