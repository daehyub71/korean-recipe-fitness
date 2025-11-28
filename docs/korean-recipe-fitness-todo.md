# 한국형 음식 레시피 & 운동 추천 서비스 - 상세 ToDo List

**프로젝트명**: Korean Recipe & Fitness Advisor
**작성일**: 2025-01-27
**개발기간**: 5일
**참조 문서**: [korean-recipe-fitness-plan.md](./korean-recipe-fitness-plan.md)

---

## Day 1: 프로젝트 셋업 & 데이터 수집

### 1.1 프로젝트 구조 생성
- [x] 프로젝트 루트 디렉토리 생성 (`korean-recipe-fitness/`)
- [x] 디렉토리 구조 생성
  ```
  korean-recipe-fitness/
  ├── app/
  │   ├── core/agents/
  │   ├── core/workflow/
  │   ├── core/services/
  │   ├── api/
  │   └── schemas/
  ├── scripts/
  ├── streamlit_app/
  ├── data/raw/
  ├── data/processed/
  ├── data/vector_db/
  ├── data/database/
  └── tests/
  ```
- [ ] Git 저장소 초기화 (`git init`)
- [x] `.gitignore` 파일 작성

#### Streamlit 테스트 1.1
```bash
# streamlit_app/test_day1_setup.py
# 프로젝트 구조 확인 테스트
streamlit run streamlit_app/test_day1_setup.py
```
- [x] 디렉토리 구조 시각화 확인

---

### 1.2 Python 환경 설정
- [x] 가상환경 생성 (`python3 -m venv venv`)
- [x] 가상환경 활성화 (`source venv/bin/activate`)
- [x] `requirements.txt` 작성
  ```
  fastapi>=0.109.0
  uvicorn[standard]>=0.27.0
  langchain>=0.1.0
  langgraph>=0.0.26
  langchain-openai>=0.0.5
  faiss-cpu>=1.9.0
  openai>=1.10.0
  sqlalchemy>=2.0.25
  pandas>=2.2.0
  requests>=2.31.0
  streamlit>=1.31.0
  python-dotenv>=1.0.0
  pydantic>=2.5.3
  pydantic-settings>=2.1.0
  pytest>=7.4.4
  httpx>=0.26.0
  ```
- [x] 의존성 설치 (`pip install -r requirements.txt`)

#### Streamlit 테스트 1.2
```bash
# streamlit_app/test_day1_deps.py
# 패키지 설치 확인 테스트
streamlit run streamlit_app/test_day1_deps.py
```
- [x] 모든 패키지 import 성공 확인

---

### 1.3 환경 변수 설정
- [x] `.env.example` 파일 작성
- [x] `.env` 파일 생성 (실제 값 입력)
  - [ ] `OPENAI_API_KEY`
  - [x] `RECIPE_API_KEY` (공공데이터포털 - 레시피)
  - [x] `NUTRITION_API_KEY` (공공데이터포털 - 영양정보)
- [x] `app/config.py` 작성 (pydantic-settings)

#### Streamlit 테스트 1.3
```bash
# streamlit_app/test_day1_config.py
# 환경변수 로드 테스트
streamlit run streamlit_app/test_day1_config.py
```
- [x] API 키 마스킹하여 표시
- [ ] OpenAI API 연결 테스트 (간단한 completion)

---

### 1.4 공공데이터 API 연동 (2개 API)

| API명 | 제공기관 | 용도 | 인증키 |
|-------|---------|------|--------|
| 조리식품의 레시피 DB | 식품의약품안전처 | 레시피 + 재료 + 조리법 | `` |
| 식품영양성분 DB | 식품의약품안전처 | 칼로리, 탄단지, 나트륨 등 | `...` |

> **Note**: 인증키는 `.env` 파일에 저장하여 관리

---

#### API 1: 조리식품 레시피 DB (식약처)
- [x] 공공데이터포털 API 키 발급 (https://www.data.go.kr)
  - [x] "조리식품의 레시피 DB" 검색 및 활용신청
- [x] `scripts/collect_recipes.py` 작성
  - [x] API 호출 함수 구현
  - [x] 페이지네이션 처리
  - [x] JSON 파일 저장 (`data/raw/recipes_raw.json`)
  - [x] 에러 핸들링 (재시도 로직)
- [x] 레시피 데이터 수집 실행 (1,139개 레시피)

#### Streamlit 테스트 1.4-A (레시피 API)
```bash
# streamlit_app/test_day1_recipe_api.py
streamlit run streamlit_app/test_day1_recipe_api.py
```
- [x] 레시피 API 연결 상태 표시
- [x] 샘플 레시피 5개 표시
- [x] 수집된 레시피 총 개수 표시 (1,139개)

---

#### API 2: 식품영양성분 DB (식약처)
- [x] 공공데이터포털 API 키 발급
  - [x] "식품영양성분 DB" 검색 및 활용신청
- [x] `scripts/collect_nutrition.py` 작성
  - [x] API 호출 함수 구현
  - [x] 페이지네이션 처리
  - [x] JSON 파일 저장 (`data/raw/nutrition_raw.json`)
  - [x] 에러 핸들링 (재시도 로직)
- [x] 영양정보 데이터 수집 실행 (167,337개)

#### Streamlit 테스트 1.4-B (영양정보 API)
```bash
# streamlit_app/test_day1_nutrition_api.py
streamlit run streamlit_app/test_day1_nutrition_api.py
```
- [x] 영양정보 API 연결 상태 표시
- [x] 샘플 영양정보 5개 표시
- [x] 수집된 영양정보 총 개수 표시 (167,337개)
- [x] 레시피와 영양정보 매칭 테스트 (음식명 기준)

---

### 1.5 데이터 정제
- [x] `scripts/process_recipes.py` 작성
  - [x] 중복 제거
  - [x] 필드 정규화 (음식명, 재료, 조리법)
  - [x] 빈 값 처리
  - [x] `data/processed/recipes.json` 저장
- [x] `scripts/process_nutrition.py` 작성
  - [x] 필드 매핑 (AMT_NUM1 → calories 등)
  - [x] 중복 제거, 유효성 검증
  - [x] `data/processed/nutrition.json` 저장
- [x] 데이터 정제 실행 (레시피: 1,139개, 영양정보: 167,337개)

#### Streamlit 테스트 1.5
```bash
# streamlit_app/test_day1_data.py
# 데이터 정제 결과 확인
streamlit run streamlit_app/test_day1_data.py
```
- [x] 원본 vs 정제 데이터 비교 (레코드 수)
- [x] 샘플 레시피 상세 표시
- [x] 카테고리별 레시피 수 차트

---

### Day 1 체크포인트
- [x] 프로젝트 구조 완성
- [x] 환경 설정 완료
- [x] 레시피 데이터 수집 완료 (1,139개)
- [x] 영양정보 데이터 수집 완료 (167,337개)
- [x] 데이터 정제 완료
- [ ] Git 커밋 (`Day 1 완료: 프로젝트 셋업 및 데이터 수집`)

---

## Day 2: 벡터 DB & 영양정보 DB 구축

### 2.1 임베딩 서비스 구현
- [x] `app/core/services/embedding_service.py` 작성
  - [x] `EmbeddingService` 클래스 생성
  - [x] `__init__`: OpenAI 클라이언트 초기화
  - [x] `get_embedding(text)`: 단일 텍스트 임베딩
  - [x] `get_embeddings_batch(texts)`: 배치 임베딩 (100개씩)
  - [x] 에러 핸들링 및 재시도 로직
  - [x] `compute_similarity()`: 코사인 유사도 계산

#### Streamlit 테스트 2.1
```bash
# streamlit_app/test_day2_embedding.py
# 임베딩 서비스 테스트
streamlit run streamlit_app/test_day2_embedding.py
```
- [ ] 테스트 문장 입력 → 임베딩 벡터 생성 (OPENAI_API_KEY 필요)
- [ ] 벡터 차원 표시 (1536 for small, 3072 for large)
- [ ] 두 문장 유사도 계산 테스트

---

### 2.2 FAISS 벡터 DB 빌드
- [x] `scripts/build_vector_db.py` 작성
  - [x] 레시피 데이터 로드
  - [x] 임베딩 텍스트 생성 (음식명 + 재료 + 카테고리)
  - [x] 배치 임베딩 생성
  - [x] FAISS IndexFlatL2 생성
  - [x] 인덱스 저장 (`data/vector_db/faiss.index`)
  - [x] 메타데이터 저장 (`data/vector_db/metadata.json`)
- [ ] 벡터 DB 빌드 실행 (**OPENAI_API_KEY 설정 필요**)

#### Streamlit 테스트 2.2
```bash
# streamlit_app/test_day2_faiss.py
# FAISS 벡터 DB 테스트
streamlit run streamlit_app/test_day2_faiss.py
```
- [ ] 인덱스 로드 성공 확인
- [ ] 벡터 수 표시
- [ ] 검색 테스트 (음식명 입력 → top-3 결과)
- [ ] 유사도 점수 표시

---

### 2.3 벡터 DB 서비스 구현
- [x] `app/core/services/vector_db_service.py` 작성
  - [x] `VectorDBService` 클래스 생성
  - [x] `__init__`: FAISS 인덱스 및 메타데이터 로드
  - [x] `search(query, top_k=3)`: 유사 레시피 검색
  - [x] `get_recipe_by_index(idx)`: 인덱스로 레시피 조회
  - [x] `get_recipe_by_name(name)`: 이름으로 레시피 조회
  - [x] `search_by_category(category)`: 카테고리 검색
  - [x] `get_similar_recipes(idx)`: 유사 레시피 검색

#### Streamlit 테스트 2.3
```bash
# streamlit_app/test_day2_search.py
# 레시피 검색 서비스 테스트
streamlit run streamlit_app/test_day2_search.py
```
- [ ] 음식명 입력 → 검색 결과 카드 표시
- [ ] 유사도 threshold 슬라이더 (0.5 ~ 1.0)
- [ ] "DB에 없음" 케이스 테스트

---

### 2.4 영양정보 SQLite DB 구축
- [x] `scripts/build_nutrition_db.py` 작성
  - [x] 정제된 영양정보 데이터 로드
  - [x] SQLite 테이블 생성 (확장된 스키마)
    ```sql
    CREATE TABLE nutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_code TEXT,
        food_name TEXT NOT NULL,
        db_group TEXT,
        db_class TEXT,
        food_origin TEXT,
        category1 TEXT,
        category2 TEXT,
        serving_size REAL,
        calories REAL,
        water REAL,
        protein REAL,
        fat REAL,
        ash REAL,
        carbohydrate REAL,
        sugar REAL,
        fiber REAL,
        calcium REAL,
        iron REAL,
        phosphorus REAL,
        sodium REAL,
        potassium REAL,
        vitamin_a REAL,
        vitamin_c REAL,
        cholesterol REAL,
        saturated_fat REAL,
        trans_fat REAL
    );
    ```
  - [x] 데이터 삽입 (배치 처리)
  - [x] 인덱스 생성 (`idx_food_name`, `idx_food_code`, `idx_category1`, `idx_db_group`)
- [x] 영양정보 DB 빌드 실행 (167,337개 레코드)

#### Streamlit 테스트 2.4
```bash
# streamlit_app/test_day2_nutrition.py
# 영양정보 DB 테스트
streamlit run streamlit_app/test_day2_nutrition.py
```
- [x] DB 연결 상태 표시
- [x] 총 레코드 수 표시 (167,337개)
- [x] 음식명 검색 → 영양정보 테이블 표시
- [x] 칼로리 분포 히스토그램

---

### 2.5 영양정보 서비스 구현
- [x] `app/core/services/nutrition_db_service.py` 작성
  - [x] `NutritionDBService` 클래스 생성
  - [x] `__init__`: SQLite 연결
  - [x] `get_nutrition(food_name)`: 영양정보 조회
  - [x] `search_similar(food_name)`: 유사 음식 검색 (LIKE 쿼리)
  - [x] `search_by_category(category)`: 카테고리 검색
  - [x] `get_by_calorie_range(min, max)`: 칼로리 범위 검색
  - [x] `get_low_calorie_foods()`: 저칼로리 음식 조회
  - [x] `get_high_protein_foods()`: 고단백 음식 조회
  - [x] `get_statistics()`: 통계 조회

#### Streamlit 테스트 2.5
```bash
# streamlit_app/test_day2_nutrition_service.py
# 영양정보 서비스 테스트
streamlit run streamlit_app/test_day2_nutrition_service.py
```
- [ ] 음식명 입력 → 영양정보 카드 표시
- [ ] 매칭 실패 시 유사 음식 추천
- [ ] 영양소 파이 차트 (탄단지 비율)

---

### Day 2 체크포인트
- [x] 임베딩 서비스 완성
- [ ] FAISS 벡터 DB 빌드 완료 (**OPENAI_API_KEY 설정 후 실행 필요**)
- [x] 벡터 검색 서비스 완성 (코드 완료)
- [x] 영양정보 SQLite DB 빌드 완료 (167,337개)
- [x] 영양정보 서비스 완성
- [ ] Git 커밋 (`Day 2 완료: 벡터 DB 및 영양정보 DB 구축`)

---

## Day 3: LangGraph 워크플로우 & Agent 구현

### 3.1 ChatState 정의
- [x] `app/core/workflow/state.py` 작성
  - [x] `UserProfile` TypedDict 정의
  - [x] `ChatState` TypedDict 정의
    ```python
    class ChatState(TypedDict):
        user_query: str
        user_profile: Optional[UserProfile]
        analyzed_query: dict
        recipe: dict
        recipe_source: Literal["database", "llm_fallback"]
        nutrition: dict
        exercise_recommendations: List[dict]
        response: str
    ```

#### Streamlit 테스트 3.1
```bash
# streamlit_app/test_day3_state.py
# ChatState 테스트
streamlit run streamlit_app/test_day3_state.py
```
- [ ] State 구조 시각화
- [ ] 샘플 State 생성 및 표시

---

### 3.2 Agent 1: QueryAnalyzer
- [x] `app/core/agents/query_analyzer.py` 작성
  - [x] GPT 프롬프트 설계
    - 음식명 추출
    - 인분 수 추출 (기본값: 1)
  - [x] `analyze(state: ChatState) -> ChatState` 함수 구현
  - [x] JSON 파싱 로직

#### Streamlit 테스트 3.2
```bash
# streamlit_app/test_day3_query_analyzer.py
# QueryAnalyzer 테스트
streamlit run streamlit_app/test_day3_query_analyzer.py
```
- [ ] 다양한 쿼리 입력 테스트
  - "김치찌개 2인분 레시피 알려줘"
  - "불고기"
  - "저녁으로 뭐 먹을까"
- [ ] 파싱 결과 JSON 표시

---

### 3.3 Agent 2: RecipeFetcher
- [x] `app/core/agents/recipe_fetcher.py` 작성
  - [x] VectorDBService 연동
  - [x] 유사도 threshold 처리 (0.5)
  - [x] `fetch(state: ChatState) -> ChatState` 함수 구현
  - [x] `recipe_source` 설정 ("database" or "llm_fallback")

#### Streamlit 테스트 3.3
```bash
# streamlit_app/test_day3_recipe_fetcher.py
# RecipeFetcher 테스트
streamlit run streamlit_app/test_day3_recipe_fetcher.py
```
- [ ] DB에 있는 음식 테스트 (김치찌개, 된장찌개)
- [ ] DB에 없는 음식 테스트 (피자, 파스타)
- [ ] 레시피 카드 표시 + source 표시

---

### 3.4 Agent 3: NutritionCalculator
- [x] `app/core/agents/nutrition_calculator.py` 작성
  - [x] NutritionDBService 연동
  - [x] 인분 수 반영 계산
  - [x] `calculate(state: ChatState) -> ChatState` 함수 구현

#### Streamlit 테스트 3.4
```bash
# streamlit_app/test_day3_nutrition_calc.py
# NutritionCalculator 테스트
streamlit run streamlit_app/test_day3_nutrition_calc.py
```
- [ ] 음식명 + 인분수 입력 → 영양정보 표시
- [ ] 영양소 바 차트

---

### 3.5 CalorieCalculator 서비스
- [x] `app/core/services/calorie_calculator.py` 작성
  - [x] `UserProfile` dataclass
  - [x] `CalorieCalculator` 클래스
    - [x] `calculate_bmr()`: Mifflin-St Jeor 공식
    - [x] `_get_epoc_factor()`: EPOC 계수
    - [x] `calculate_time_for_calories()`: 운동 시간 계산
    - [x] `recommend_exercises()`: 강도별 운동 추천
  - [x] MET 테이블 정의 (38개 운동)

#### Streamlit 테스트 3.5
```bash
# streamlit_app/test_day3_calorie_calc.py
# CalorieCalculator 테스트
streamlit run streamlit_app/test_day3_calorie_calc.py
```
- [ ] 사용자 프로필 입력 (체중, 키, 나이, 성별)
- [ ] 목표 칼로리 입력
- [ ] BMR 계산 결과 표시
- [ ] 강도별 운동 추천 표시 (시간 포함)

---

### 3.6 Agent 4: ExerciseRecommender
- [x] `app/core/agents/exercise_recommender.py` 작성
  - [x] CalorieCalculator 연동
  - [x] 사용자 프로필 처리 (없으면 기본값)
  - [x] `recommend(state: ChatState) -> ChatState` 함수 구현

#### Streamlit 테스트 3.6
```bash
# streamlit_app/test_day3_exercise.py
# ExerciseRecommender 테스트
streamlit run streamlit_app/test_day3_exercise.py
```
- [ ] 칼로리 입력 → 운동 추천 카드 3개 (저/중/고강도)
- [ ] 사용자 프로필 유무에 따른 결과 비교

---

### 3.7 Agent 5: ResponseFormatter
- [x] `app/core/agents/response_formatter.py` 작성
  - [x] GPT 프롬프트 설계 (자연어 응답 생성)
  - [x] 레시피 + 영양정보 + 운동 추천 통합
  - [x] `format(state: ChatState) -> ChatState` 함수 구현
  - [x] 템플릿 기반 fallback 응답 생성

#### Streamlit 테스트 3.7
```bash
# streamlit_app/test_day3_formatter.py
# ResponseFormatter 테스트
streamlit run streamlit_app/test_day3_formatter.py
```
- [ ] 전체 State 입력 → 최종 응답 표시
- [ ] Markdown 렌더링 확인

---

### 3.8 LLM Fallback 로직
- [x] `app/core/services/llm_service.py` 작성
  - [x] `LLMService` 클래스
  - [x] `generate_recipe(food_name)`: GPT로 레시피 생성
  - [x] `generate_nutrition(food_name)`: GPT로 영양정보 추정
- [x] `app/core/agents/llm_fallback.py` 작성
  - [x] LLMFallbackAgent 클래스
  - [x] RecipeFetcher와 연동

#### Streamlit 테스트 3.8
```bash
# streamlit_app/test_day3_fallback.py
# LLM Fallback 테스트
streamlit run streamlit_app/test_day3_fallback.py
```
- [ ] DB에 없는 음식 입력 → GPT 생성 레시피 표시
- [ ] "source: llm_fallback" 표시 확인

---

### 3.9 LangGraph 워크플로우 연결
- [x] `app/core/workflow/graph.py` 작성
  - [x] StateGraph 생성
  - [x] 노드 추가 (6개 Agent: QueryAnalyzer, RecipeFetcher, LLMFallback, NutritionCalculator, ExerciseRecommender, ResponseFormatter)
  - [x] 엣지 연결 (순차)
  - [x] 컴파일
  - [x] run_workflow_sync / run_workflow (비동기) 함수

#### Streamlit 테스트 3.9
```bash
# streamlit_app/test_day3_workflow.py
# LangGraph 워크플로우 통합 테스트
streamlit run streamlit_app/test_day3_workflow.py
```
- [ ] 워크플로우 다이어그램 시각화
- [ ] End-to-End 테스트
  - 입력: "김치찌개 2인분" + 사용자 프로필
  - 출력: 레시피 + 영양정보 + 운동 추천
- [ ] 각 Agent 처리 시간 표시

---

### Day 3 체크포인트
- [x] 6개 Agent 모두 구현 완료 (QueryAnalyzer, RecipeFetcher, NutritionCalculator, ExerciseRecommender, ResponseFormatter, LLMFallback)
- [x] CalorieCalculator 서비스 완성 (38개 운동, BMR/TDEE 계산, EPOC 적용)
- [x] LLM Fallback 로직 완성
- [x] LangGraph 워크플로우 연결 완료
- [ ] End-to-End 테스트 통과 (OPENAI_API_KEY 필요)
- [ ] Git 커밋 (`Day 3 완료: LangGraph 워크플로우 및 Agent 구현`)

---

## Day 4: FastAPI & Streamlit UI 통합

### 4.1 Pydantic 스키마 정의
- [ ] `app/schemas/request.py` 작성
  - [ ] `UserProfileSchema`
  - [ ] `SearchRequest`
- [ ] `app/schemas/response.py` 작성
  - [ ] `RecipeResponse`
  - [ ] `NutritionResponse`
  - [ ] `ExerciseResponse`
  - [ ] `SearchResponse`

#### Streamlit 테스트 4.1
```bash
# streamlit_app/test_day4_schemas.py
# 스키마 검증 테스트
streamlit run streamlit_app/test_day4_schemas.py
```
- [ ] 샘플 데이터로 스키마 검증
- [ ] 유효하지 않은 데이터 에러 표시

---

### 4.2 FastAPI 라우트 구현
- [ ] `app/api/routes.py` 작성
  - [ ] `POST /api/search`: 메인 검색 엔드포인트
  - [ ] `GET /api/health`: 헬스체크
- [ ] `app/main.py` 작성
  - [ ] FastAPI 앱 생성
  - [ ] 라우터 등록
  - [ ] CORS 설정
  - [ ] 시작 시 서비스 초기화 (FAISS 로드)

#### Streamlit 테스트 4.2
```bash
# 터미널 1: FastAPI 서버 실행
uvicorn app.main:app --reload --port 8000

# 터미널 2: API 테스트
# streamlit_app/test_day4_api.py
streamlit run streamlit_app/test_day4_api.py
```
- [ ] `/api/health` 호출 성공
- [ ] `/api/search` 호출 및 응답 표시
- [ ] 응답 시간 측정

---

### 4.3 Streamlit 메인 UI 구현
- [ ] `streamlit_app/main.py` 작성
  - [ ] 페이지 설정 (제목, 아이콘, 레이아웃)
  - [ ] 헤더 섹션
  - [ ] 검색 입력창 (`st.text_input`)
  - [ ] 사용자 프로필 입력 (`st.expander`)
    - 체중, 키, 나이, 성별
  - [ ] 검색 버튼

#### Streamlit 테스트 4.3
```bash
streamlit run streamlit_app/main.py
```
- [ ] UI 레이아웃 확인
- [ ] 입력 컴포넌트 동작 확인

---

### 4.4 레시피 결과 컴포넌트
- [ ] `streamlit_app/components/recipe_card.py` 작성
  - [ ] 레시피명 표시
  - [ ] 재료 목록 (bullet)
  - [ ] 조리법 (numbered)
  - [ ] 조리시간, 난이도, 인분
  - [ ] source 배지 (DB / GPT)

#### Streamlit 테스트 4.4
```bash
streamlit run streamlit_app/main.py
```
- [ ] 레시피 카드 스타일 확인
- [ ] 긴 조리법 스크롤 확인

---

### 4.5 영양정보 컴포넌트
- [ ] `streamlit_app/components/nutrition_card.py` 작성
  - [ ] `st.metric` 카드 (칼로리, 탄수화물, 단백질, 지방, 나트륨)
  - [ ] 영양소 비율 파이 차트 (`st.plotly_chart`)

#### Streamlit 테스트 4.5
```bash
streamlit run streamlit_app/main.py
```
- [ ] 영양정보 카드 배치 확인
- [ ] 파이 차트 인터랙티브 확인

---

### 4.6 운동 추천 컴포넌트
- [ ] `streamlit_app/components/exercise_card.py` 작성
  - [ ] 강도별 탭 (`st.tabs`)
  - [ ] 운동 카드 (운동명, 시간, MET)
  - [ ] EPOC 효과 표시

#### Streamlit 테스트 4.6
```bash
streamlit run streamlit_app/main.py
```
- [ ] 3개 탭 전환 확인
- [ ] 운동 카드 스타일 확인

---

### 4.7 API 연동 및 통합
- [ ] `streamlit_app/services/api_client.py` 작성
  - [ ] `search(query, user_profile)` 함수
  - [ ] httpx 비동기 호출
  - [ ] 에러 핸들링
- [ ] `streamlit_app/main.py` 업데이트
  - [ ] 검색 버튼 클릭 → API 호출
  - [ ] 로딩 스피너 (`st.spinner`)
  - [ ] 결과 컴포넌트 렌더링

#### Streamlit 테스트 4.7
```bash
# 터미널 1: FastAPI 서버
uvicorn app.main:app --reload --port 8000

# 터미널 2: Streamlit
streamlit run streamlit_app/main.py
```
- [ ] End-to-End 플로우 테스트
- [ ] 다양한 음식 검색 테스트
- [ ] 에러 케이스 테스트 (API 다운 시)

---

### 4.8 UI 스타일링
- [ ] Custom CSS 적용 (`st.markdown` with unsafe_allow_html)
- [ ] 카드 스타일 통일
- [ ] 반응형 레이아웃 (`st.columns`)
- [ ] 다크모드 고려

#### Streamlit 테스트 4.8
```bash
streamlit run streamlit_app/main.py
```
- [ ] 전체 UI 디자인 확인
- [ ] 모바일 뷰 확인 (브라우저 리사이즈)

---

### Day 4 체크포인트
- [ ] FastAPI 엔드포인트 완성
- [ ] Streamlit UI 완성
- [ ] API ↔ UI 통합 완료
- [ ] End-to-End 테스트 통과
- [ ] Git 커밋 (`Day 4 완료: FastAPI 및 Streamlit UI 통합`)

---

## Day 5: 테스트, 버그 수정, 문서화

### 5.1 유닛 테스트 작성
- [ ] `tests/test_embedding_service.py`
  - [ ] 임베딩 생성 테스트
  - [ ] 배치 임베딩 테스트
- [ ] `tests/test_vector_db_service.py`
  - [ ] 검색 테스트
  - [ ] threshold 테스트
- [ ] `tests/test_nutrition_db_service.py`
  - [ ] 조회 테스트
  - [ ] 유사 검색 테스트
- [ ] `tests/test_calorie_calculator.py`
  - [ ] BMR 계산 테스트 (남/여)
  - [ ] 운동 시간 계산 테스트
  - [ ] EPOC 적용 테스트

#### Streamlit 테스트 5.1
```bash
# pytest 실행 후 결과 표시
# streamlit_app/test_day5_pytest.py
streamlit run streamlit_app/test_day5_pytest.py
```
- [ ] 테스트 통과/실패 현황 표시
- [ ] 커버리지 표시

---

### 5.2 Agent 테스트 작성
- [ ] `tests/test_agents.py`
  - [ ] QueryAnalyzer 테스트
  - [ ] RecipeFetcher 테스트
  - [ ] NutritionCalculator 테스트
  - [ ] ExerciseRecommender 테스트
  - [ ] ResponseFormatter 테스트

#### Streamlit 테스트 5.2
```bash
streamlit run streamlit_app/test_day5_pytest.py
```
- [ ] Agent 테스트 결과 확인

---

### 5.3 통합 테스트 작성
- [ ] `tests/test_api.py`
  - [ ] `/api/health` 테스트
  - [ ] `/api/search` 정상 케이스
  - [ ] `/api/search` fallback 케이스
  - [ ] 잘못된 요청 테스트

#### Streamlit 테스트 5.3
```bash
streamlit run streamlit_app/test_day5_integration.py
```
- [ ] API 통합 테스트 결과 표시

---

### 5.4 버그 수정 및 최적화
- [ ] 발견된 버그 목록 정리
- [ ] 버그 수정
- [ ] 응답 시간 최적화
  - [ ] 임베딩 캐싱 고려
  - [ ] FAISS 검색 최적화
- [ ] 메모리 사용량 점검

#### Streamlit 테스트 5.4
```bash
streamlit run streamlit_app/test_day5_perf.py
```
- [ ] 응답 시간 측정 (평균, p95)
- [ ] 메모리 사용량 표시

---

### 5.5 문서화
- [ ] `README.md` 작성
  - [ ] 프로젝트 소개
  - [ ] 설치 방법
  - [ ] 실행 방법
  - [ ] API 문서 링크
  - [ ] 스크린샷
- [ ] `CLAUDE.md` 작성
  - [ ] 프로젝트 구조
  - [ ] 주요 명령어
  - [ ] 아키텍처 설명
- [ ] 코드 주석 정리

#### Streamlit 테스트 5.5
```bash
streamlit run streamlit_app/test_day5_docs.py
```
- [ ] README 렌더링 확인
- [ ] 문서 완성도 체크리스트

---

### 5.6 최종 테스트
- [ ] 전체 시나리오 테스트
  - [ ] DB에 있는 음식 검색
  - [ ] DB에 없는 음식 검색 (fallback)
  - [ ] 사용자 프로필 입력/미입력
  - [ ] 다양한 인분 수
- [ ] 에러 시나리오 테스트
  - [ ] API 키 없음
  - [ ] 네트워크 오류
  - [ ] 잘못된 입력

#### Streamlit 테스트 5.6
```bash
streamlit run streamlit_app/main.py
```
- [ ] 전체 시나리오 수동 테스트
- [ ] 최종 스크린샷 캡처

---

### Day 5 체크포인트
- [ ] 유닛 테스트 통과 (90% 이상)
- [ ] 통합 테스트 통과
- [ ] 버그 수정 완료
- [ ] 문서화 완료
- [ ] Git 커밋 (`Day 5 완료: 테스트 및 문서화`)
- [ ] 최종 Git 태그 (`v1.0.0`)

---

## 완료 조건

### 기능 완료
- [ ] 음식명 검색 → 레시피 표시
- [ ] 영양정보 (칼로리, 탄단지) 표시
- [ ] 맞춤형 운동 추천 (저/중/고강도)
- [ ] GPT Fallback (DB에 없는 음식)
- [ ] 사용자 프로필 기반 개인화

### 품질 완료
- [ ] 응답 시간 3초 이내
- [ ] 테스트 커버리지 80% 이상
- [ ] 문서화 완료
- [ ] 에러 핸들링 완료

### 배포 준비
- [ ] `.env.example` 완성
- [ ] `requirements.txt` 정리
- [ ] Dockerfile 작성 (선택)

---

## 테스트 파일 목록

| Day | 테스트 파일 | 용도 |
|-----|------------|------|
| 1 | `test_day1_setup.py` | 프로젝트 구조 확인 |
| 1 | `test_day1_deps.py` | 패키지 설치 확인 |
| 1 | `test_day1_config.py` | 환경변수 및 API 연결 |
| 1 | `test_day1_api.py` | 공공데이터 API 테스트 |
| 1 | `test_day1_data.py` | 데이터 정제 결과 확인 |
| 2 | `test_day2_embedding.py` | 임베딩 서비스 테스트 |
| 2 | `test_day2_faiss.py` | FAISS 벡터 DB 테스트 |
| 2 | `test_day2_search.py` | 레시피 검색 테스트 |
| 2 | `test_day2_nutrition.py` | 영양정보 DB 테스트 |
| 2 | `test_day2_nutrition_service.py` | 영양정보 서비스 테스트 |
| 3 | `test_day3_state.py` | ChatState 테스트 |
| 3 | `test_day3_query_analyzer.py` | QueryAnalyzer 테스트 |
| 3 | `test_day3_recipe_fetcher.py` | RecipeFetcher 테스트 |
| 3 | `test_day3_nutrition_calc.py` | NutritionCalculator 테스트 |
| 3 | `test_day3_calorie_calc.py` | CalorieCalculator 테스트 |
| 3 | `test_day3_exercise.py` | ExerciseRecommender 테스트 |
| 3 | `test_day3_formatter.py` | ResponseFormatter 테스트 |
| 3 | `test_day3_fallback.py` | LLM Fallback 테스트 |
| 3 | `test_day3_workflow.py` | LangGraph 워크플로우 통합 테스트 |
| 4 | `test_day4_schemas.py` | 스키마 검증 테스트 |
| 4 | `test_day4_api.py` | FastAPI 테스트 |
| 5 | `test_day5_pytest.py` | pytest 결과 표시 |
| 5 | `test_day5_integration.py` | 통합 테스트 결과 |
| 5 | `test_day5_perf.py` | 성능 테스트 |
| 5 | `test_day5_docs.py` | 문서 확인 |

---

**문서 끝**
