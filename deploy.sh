#!/bin/bash
# Cloud Run 배포 스크립트
# 사용법: ./deploy.sh

set -e

# 설정
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-fleet-resolver-479703-h2}"
REGION="${GOOGLE_CLOUD_LOCATION:-asia-northeast3}"
SERVICE_NAME="korean-recipe-fitness"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================="
echo "🍳 AI K-Food Cloud Run 배포"
echo "========================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "========================================="

# 1. 프로젝트 설정 확인
echo ""
echo "📋 Step 1: GCP 프로젝트 설정 확인..."
gcloud config set project ${PROJECT_ID}

# 2. 필요한 API 활성화
echo ""
echo "🔧 Step 2: 필요한 API 활성화..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# 3. Secret Manager에 시크릿 생성 (처음 한 번만)
echo ""
echo "🔐 Step 3: Secret Manager 설정 확인..."
if ! gcloud secrets describe openai-api-key --project=${PROJECT_ID} > /dev/null 2>&1; then
    echo "⚠️  OpenAI API 키를 Secret Manager에 등록해주세요:"
    echo "    gcloud secrets create openai-api-key --replication-policy='automatic'"
    echo "    echo -n 'YOUR_OPENAI_API_KEY' | gcloud secrets versions add openai-api-key --data-file=-"
    echo ""
    read -p "시크릿을 등록했으면 Enter를 누르세요..."
fi

# 4. Docker 이미지 빌드
echo ""
echo "🐳 Step 4: Docker 이미지 빌드..."
docker build -t ${IMAGE_NAME}:latest .

# 5. Container Registry에 푸시
echo ""
echo "📤 Step 5: Container Registry에 푸시..."
docker push ${IMAGE_NAME}:latest

# 6. Cloud Run 배포
echo ""
echo "🚀 Step 6: Cloud Run 배포..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --set-env-vars "STREAMLIT_SERVER_PORT=8080,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest"

# 7. 서비스 URL 출력
echo ""
echo "========================================="
echo "✅ 배포 완료!"
echo "========================================="
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "🌐 서비스 URL: ${SERVICE_URL}"
echo ""
echo "💡 팁:"
echo "   - 로그 확인: gcloud run logs read ${SERVICE_NAME} --region ${REGION}"
echo "   - 서비스 삭제: gcloud run services delete ${SERVICE_NAME} --region ${REGION}"
echo "========================================="
