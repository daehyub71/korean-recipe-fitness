# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Korean Recipe & Fitness Advisor - 한국 음식 레시피, 영양정보, 맞춤 운동 추천 AI 웹 서비스

## Common Commands

```bash
# Activate virtual environment
cd /Users/sunchulkim/src/korean-recipe-fitness
source venv/bin/activate

# Run FastAPI server
uvicorn app.main:app --reload --port 8000

# Run Streamlit app
streamlit run streamlit_app/main.py

# Data collection (batch)
python scripts/collect_recipes.py
python scripts/collect_nutrition.py
python scripts/process_recipes.py
python scripts/build_vector_db.py
python scripts/build_nutrition_db.py

# Run tests
pytest tests/ -v
```

## Architecture

### Batch Processing (1회 또는 주기적)
- `scripts/collect_recipes.py` - 공공데이터 레시피 API 수집
- `scripts/collect_nutrition.py` - 공공데이터 영양정보 API 수집
- `scripts/process_recipes.py` - 데이터 정제
- `scripts/build_vector_db.py` - FAISS 인덱스 빌드
- `scripts/build_nutrition_db.py` - SQLite 영양정보 빌드

### Real-time Processing (사용자 요청 시)
LangGraph 5-Agent Pipeline:
1. QueryAnalyzer → 2. RecipeFetcher → 3. NutritionCalculator → 4. ExerciseRecommender → 5. ResponseFormatter

## Key Files

| File | Purpose |
|------|---------|
| `app/config.py` | pydantic-settings 환경변수 관리 |
| `app/core/workflow/graph.py` | LangGraph 워크플로우 정의 |
| `app/core/workflow/state.py` | ChatState TypedDict 정의 |
| `app/core/services/calorie_calculator.py` | Mifflin-St Jeor + MET + EPOC 계산 |

## Environment Variables

Required in `.env`:
- `OPENAI_API_KEY` - OpenAI API key
- `RECIPE_API_KEY` - 공공데이터포털 조리식품 레시피 DB
- `NUTRITION_API_KEY` - 공공데이터포털 식품영양성분 DB

## Data Directories

```
data/
├── raw/                  # API 원본 응답
│   ├── recipes_raw.json
│   └── nutrition_raw.json
├── processed/            # 정제된 데이터
│   └── recipes.json
├── vector_db/            # FAISS 인덱스
│   ├── faiss.index
│   └── metadata.json
└── database/             # SQLite
    └── nutrition.db
```

## API Endpoints

- `POST /api/search` - 음식 검색 및 운동 추천
- `GET /api/health` - 헬스체크

## Streamlit Test Files

Day 1 테스트:
- `test_day1_setup.py` - 프로젝트 구조 확인
- `test_day1_deps.py` - 패키지 설치 확인
- `test_day1_config.py` - 환경변수 테스트
- `test_day1_recipe_api.py` - 레시피 API 테스트
- `test_day1_nutrition_api.py` - 영양정보 API 테스트
- `test_day1_data.py` - 데이터 정제 결과 확인

## Development Plan

상세 개발계획서: `docs/korean-recipe-fitness-plan.md`
상세 ToDo List: `docs/korean-recipe-fitness-todo.md`
