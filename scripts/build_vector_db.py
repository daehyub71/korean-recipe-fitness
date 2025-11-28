"""
FAISS 벡터 데이터베이스 빌드 스크립트
레시피 데이터를 임베딩하여 FAISS 인덱스 생성
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np
from dotenv import load_dotenv

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 환경변수 로드
load_dotenv(PROJECT_ROOT / ".env")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 파일 경로
RECIPES_FILE = PROJECT_ROOT / "data" / "processed" / "recipes.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "vector_db"
INDEX_FILE = OUTPUT_DIR / "faiss.index"
METADATA_FILE = OUTPUT_DIR / "metadata.json"


def load_recipes() -> List[Dict]:
    """정제된 레시피 데이터 로드"""
    if not RECIPES_FILE.exists():
        logger.error(f"레시피 파일이 없습니다: {RECIPES_FILE}")
        return []

    with open(RECIPES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def create_embedding_text(recipe: Dict) -> str:
    """
    레시피에서 임베딩용 텍스트 생성
    음식명 + 재료 + 카테고리를 결합
    """
    parts = []

    # 음식명
    name = recipe.get("name", "")
    if name:
        parts.append(f"음식명: {name}")

    # 카테고리
    category = recipe.get("category", "")
    if category:
        parts.append(f"분류: {category}")

    # 조리방법
    cooking_method = recipe.get("cooking_method", "")
    if cooking_method:
        parts.append(f"조리방법: {cooking_method}")

    # 재료 (문자열 리스트)
    ingredients = recipe.get("ingredients", [])
    if ingredients:
        # 최대 10개 재료만 사용
        ing_list = []
        for ing in ingredients[:10]:
            if isinstance(ing, str):
                ing_list.append(ing)
            elif isinstance(ing, dict):
                ing_list.append(ing.get("name", ""))
        ing_list = [i for i in ing_list if i]
        if ing_list:
            parts.append(f"재료: {', '.join(ing_list)}")

    return " | ".join(parts) if parts else name


def build_faiss_index(
    recipes: List[Dict],
    batch_size: int = 100
) -> tuple:
    """
    FAISS 인덱스 빌드

    Args:
        recipes: 레시피 데이터 리스트
        batch_size: 임베딩 배치 크기

    Returns:
        (faiss_index, metadata)
    """
    from app.core.services.embedding_service import get_embedding_service

    logger.info(f"총 {len(recipes)}개 레시피 임베딩 시작")

    # 임베딩 서비스
    embedding_service = get_embedding_service()
    dimension = embedding_service.dimension

    # 임베딩 텍스트 생성
    logger.info("임베딩 텍스트 생성 중...")
    embedding_texts = [create_embedding_text(r) for r in recipes]

    # 빈 텍스트 필터링
    valid_indices = [i for i, t in enumerate(embedding_texts) if t.strip()]
    valid_texts = [embedding_texts[i] for i in valid_indices]
    valid_recipes = [recipes[i] for i in valid_indices]

    logger.info(f"유효한 레시피: {len(valid_recipes)}개")

    if not valid_texts:
        logger.error("임베딩할 텍스트가 없습니다.")
        return None, None

    # 배치 임베딩 생성
    logger.info(f"임베딩 생성 중 (배치 크기: {batch_size})...")
    embeddings = embedding_service.get_embeddings_batch(valid_texts, batch_size=batch_size)

    # numpy 배열로 변환
    embeddings_array = np.array(embeddings, dtype=np.float32)
    logger.info(f"임베딩 shape: {embeddings_array.shape}")

    # FAISS 인덱스 생성 (L2 거리)
    logger.info("FAISS 인덱스 생성 중...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)

    logger.info(f"인덱스에 {index.ntotal}개 벡터 추가됨")

    # 메타데이터 생성
    metadata = {
        "total_recipes": len(valid_recipes),
        "dimension": dimension,
        "index_type": "IndexFlatL2",
        "recipes": []
    }

    for i, recipe in enumerate(valid_recipes):
        metadata["recipes"].append({
            "index": i,
            "id": recipe.get("recipe_id", ""),
            "name": recipe.get("name", ""),
            "category": recipe.get("category", ""),
            "cooking_method": recipe.get("cooking_method", ""),
            "embedding_text": embedding_texts[valid_indices[i]][:200]  # 미리보기용
        })

    return index, metadata


def save_index(index, metadata: Dict, output_dir: Path):
    """인덱스와 메타데이터 저장"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # FAISS 인덱스 저장
    index_path = output_dir / "faiss.index"
    faiss.write_index(index, str(index_path))
    logger.info(f"인덱스 저장 완료: {index_path}")

    # 메타데이터 저장
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info(f"메타데이터 저장 완료: {metadata_path}")


def test_search(index, metadata: Dict, query: str = "김치찌개"):
    """검색 테스트"""
    from app.core.services.embedding_service import get_embedding_service

    logger.info(f"\n검색 테스트: '{query}'")

    embedding_service = get_embedding_service()

    # 쿼리 임베딩
    query_embedding = embedding_service.get_embedding(query)
    query_vector = np.array([query_embedding], dtype=np.float32)

    # 검색
    k = 5
    distances, indices = index.search(query_vector, k)

    logger.info(f"상위 {k}개 결과:")
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx < len(metadata["recipes"]):
            recipe = metadata["recipes"][idx]
            # L2 거리를 유사도로 변환 (거리가 작을수록 유사)
            similarity = 1 / (1 + dist)
            logger.info(f"  {i+1}. {recipe['name']} (유사도: {similarity:.4f})")


def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("FAISS 벡터 DB 빌드 시작")
    logger.info("=" * 50)

    # 레시피 로드
    recipes = load_recipes()
    if not recipes:
        logger.error("레시피 데이터가 없습니다.")
        sys.exit(1)

    logger.info(f"로드된 레시피: {len(recipes)}개")

    # 인덱스 빌드
    index, metadata = build_faiss_index(recipes)

    if index is None:
        logger.error("인덱스 빌드 실패")
        sys.exit(1)

    # 저장
    save_index(index, metadata, OUTPUT_DIR)

    # 테스트
    test_search(index, metadata, "김치찌개")
    test_search(index, metadata, "된장찌개")
    test_search(index, metadata, "불고기")

    logger.info("\n" + "=" * 50)
    logger.info("빌드 완료!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
