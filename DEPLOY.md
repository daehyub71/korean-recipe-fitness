# Cloud Run 배포 가이드

## 사전 준비

### 1. GCP 프로젝트 설정
```bash
# 프로젝트 ID 확인
gcloud config get-value project

# 프로젝트 설정 (필요시)
gcloud config set project fleet-resolver-479703-h2
```

### 2. 필요한 API 활성화
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 3. Secret Manager에 API 키 등록
```bash
# OpenAI API 키 등록
gcloud secrets create openai-api-key --replication-policy='automatic'
echo -n 'YOUR_OPENAI_API_KEY' | gcloud secrets versions add openai-api-key --data-file=-

# (선택) Vertex AI는 서비스 계정으로 자동 인증됨
```

## 배포 방법

### 방법 1: 스크립트 사용 (권장)
```bash
./deploy.sh
```

### 방법 2: 수동 배포
```bash
# 1. Docker 이미지 빌드
docker build -t gcr.io/fleet-resolver-479703-h2/korean-recipe-fitness:latest .

# 2. Container Registry에 푸시
docker push gcr.io/fleet-resolver-479703-h2/korean-recipe-fitness:latest

# 3. Cloud Run 배포
gcloud run deploy korean-recipe-fitness \
    --image gcr.io/fleet-resolver-479703-h2/korean-recipe-fitness:latest \
    --region asia-northeast3 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

### 방법 3: Cloud Build 사용 (CI/CD)
```bash
# 수동 트리거
gcloud builds submit --config cloudbuild.yaml

# GitHub 연동 시 자동 배포 설정
# Cloud Build > 트리거 > GitHub 연결
```

## 환경 변수

| 변수 | 설명 | 필수 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | ✅ |
| `GOOGLE_CLOUD_PROJECT` | GCP 프로젝트 ID | ✅ (자동 설정) |
| `STREAMLIT_SERVER_PORT` | 서버 포트 (8080) | ✅ (자동 설정) |

## 배포 후 확인

```bash
# 서비스 상태 확인
gcloud run services describe korean-recipe-fitness --region asia-northeast3

# 로그 확인
gcloud run logs read korean-recipe-fitness --region asia-northeast3 --limit 50

# 서비스 URL 확인
gcloud run services describe korean-recipe-fitness \
    --region asia-northeast3 \
    --format 'value(status.url)'
```

## 비용 최적화

### 현재 설정
- **Memory**: 2Gi (FAISS 인덱스 로딩 필요)
- **CPU**: 2 (빠른 응답)
- **Min instances**: 0 (콜드 스타트 허용, 비용 절약)
- **Max instances**: 10

### 콜드 스타트 줄이기 (선택)
```bash
# 최소 1개 인스턴스 유지 (추가 비용 발생)
gcloud run services update korean-recipe-fitness \
    --region asia-northeast3 \
    --min-instances 1
```

## 문제 해결

### 1. 메모리 부족
```bash
# 메모리 증가
gcloud run services update korean-recipe-fitness \
    --region asia-northeast3 \
    --memory 4Gi
```

### 2. 타임아웃
```bash
# 타임아웃 증가 (최대 3600초)
gcloud run services update korean-recipe-fitness \
    --region asia-northeast3 \
    --timeout 600
```

### 3. 시크릿 권한 오류
```bash
# Cloud Run 서비스 계정에 Secret Manager 접근 권한 부여
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 서비스 삭제
```bash
gcloud run services delete korean-recipe-fitness --region asia-northeast3
```
