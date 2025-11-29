# Korean Recipe & Fitness Advisor

한국 음식 이름을 입력하면 레시피, 영양정보(칼로리), 그리고 해당 칼로리를 소모하기 위한 맞춤형 운동을 추천하는 AI 기반 웹 서비스

## Features

- **레시피 검색**: 한국 음식 레시피 RAG 검색 (공공데이터 기반)
- **영양정보 제공**: 칼로리, 탄수화물, 단백질, 지방, 나트륨 등
- **맞춤 운동 추천**: 사용자 프로필 기반 전문적 칼로리 소모 계산 (Mifflin-St Jeor + MET + EPOC)
- **GPT Fallback**: DB에 없는 음식은 GPT가 레시피 생성

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI, LangGraph, LangChain |
| LLM | OpenAI GPT-4o-mini |
| Embedding | OpenAI text-embedding-3-large (3072차원) |
| Vector DB | FAISS (IndexFlatL2) |
| Database | SQLite (영양정보) |
| Frontend | Streamlit |
| Data Source | 공공데이터포털 (식품의약품안전처) |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    [배치 처리] - 1회 또는 주기적              │
├─────────────────────────────────────────────────────────────┤
│  공공데이터 API → 데이터 정제 → 임베딩 생성 → FAISS/SQLite   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  [실시간 처리] - 사용자 요청 시               │
├─────────────────────────────────────────────────────────────┤
│  QueryAnalyzer → RecipeFetcher → LLMFallback                │
│       ↓              ↓                ↓                     │
│  NutritionCalculator → ExerciseRecommender → ResponseFormatter │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
korean-recipe-fitness/
├── app/
│   ├── config.py                 # pydantic-settings 설정
│   ├── main.py                   # FastAPI 엔트리포인트
│   ├── core/
│   │   ├── agents/               # LangGraph Agents (6개)
│   │   ├── workflow/             # LangGraph 워크플로우
│   │   └── services/             # 비즈니스 로직
│   ├── api/                      # REST API 라우트
│   └── schemas/                  # Pydantic 스키마
├── scripts/
│   ├── collect_recipes.py        # 레시피 API 수집
│   ├── collect_nutrition.py      # 영양정보 API 수집
│   ├── process_recipes.py        # 데이터 정제
│   ├── build_vector_db.py        # FAISS 인덱스 빌드
│   └── build_nutrition_db.py     # SQLite 영양정보 빌드
├── streamlit_app/
│   ├── main.py                   # Streamlit UI
│   └── components/               # UI 컴포넌트
├── data/
│   ├── raw/                      # 원본 데이터
│   ├── processed/                # 정제된 데이터
│   ├── vector_db/                # FAISS 인덱스
│   └── database/                 # SQLite DB
├── docs/
│   ├── korean-recipe-fitness-plan.md   # 개발계획서
│   └── korean-recipe-fitness-todo.md   # 상세 ToDo
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/korean-recipe-fitness.git
cd korean-recipe-fitness

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Environment Variables

```bash
# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# 공공데이터포털 API (식품의약품안전처)
RECIPE_API_KEY=your-recipe-api-key
NUTRITION_API_KEY=your-nutrition-api-key
```

API 키 발급: https://www.data.go.kr

## Usage

### 1. Data Collection (Batch)

```bash
# 레시피 데이터 수집
python scripts/collect_recipes.py

# 영양정보 데이터 수집
python scripts/collect_nutrition.py

# 데이터 정제
python scripts/process_recipes.py

# FAISS 벡터 DB 빌드
python scripts/build_vector_db.py

# 영양정보 SQLite DB 빌드
python scripts/build_nutrition_db.py
```

### 2. Run Application

```bash
# Terminal 1: FastAPI Backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Streamlit Frontend
streamlit run streamlit_app/main.py
```

### 3. Access

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs

### 4. Streamlit Cloud Deployment

1. GitHub에 저장소 푸시
2. [share.streamlit.io](https://share.streamlit.io) 접속 후 로그인
3. "New app" 클릭 → 저장소 선택
4. Settings:
   - Main file path: `streamlit_app/main.py`
   - Python version: 3.11
5. Secrets 설정 (Settings → Secrets):
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   RECIPE_API_KEY = "your-recipe-api-key"
   NUTRITION_API_KEY = "your-nutrition-api-key"
   ```

**참고**: `.streamlit/secrets.toml.example` 파일 형식 참조

## Known Limitations

- **영양정보 DB**: Streamlit Cloud에서는 파일 크기 제한으로 영양정보 DB (~120MB)가 배포되지 않음
- **LLM Fallback**: 영양정보 DB가 없을 경우 GPT가 영양정보를 추정하여 생성
- **정확도**: GPT 생성 영양정보는 참고용이며, 정확한 영양 정보는 공공데이터 기반 결과 사용 권장

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/search` | 음식 검색 및 운동 추천 |
| GET | `/api/health` | 서버 상태 확인 |

## LangGraph Workflow

6-Agent Pipeline:

1. **QueryAnalyzer** - 음식명 추출, 인분 수 파악 (GPT)
2. **RecipeFetcher** - 레시피 검색 (FAISS)
3. **LLMFallback** - DB에 없는 레시피/영양정보 생성 (GPT)
4. **NutritionCalculator** - 칼로리/영양성분 조회 (SQLite)
5. **ExerciseRecommender** - 운동 종류/시간 계산 (MET Table)
6. **ResponseFormatter** - 최종 응답 생성 (GPT)

## Calorie Calculation

전문적인 칼로리 소모 계산 방식 적용:

- **BMR**: Mifflin-St Jeor 공식 (1990)
- **MET**: Compendium of Physical Activities 2024
- **EPOC**: 운동 후 추가 칼로리 소모 반영
  - 고강도 (MET ≥ 8): +15%
  - 중강도 (MET 4~8): +7%
  - 저강도 (MET < 4): +0%

## Data Sources

| API | Provider | Usage |
|-----|----------|-------|
| 조리식품의 레시피 DB | 식품의약품안전처 | 레시피 + 재료 + 조리법 |
| 식품영양성분 DB | 식품의약품안전처 | 칼로리, 탄단지, 나트륨 등 |

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=app --cov-report=html

# Streamlit tests (Day 1)
streamlit run streamlit_app/test_day1_setup.py
streamlit run streamlit_app/test_day1_deps.py
streamlit run streamlit_app/test_day1_config.py
streamlit run streamlit_app/test_day1_recipe_api.py
streamlit run streamlit_app/test_day1_nutrition_api.py
streamlit run streamlit_app/test_day1_data.py
```

## License

MIT License

## Author

Created with Claude Code
