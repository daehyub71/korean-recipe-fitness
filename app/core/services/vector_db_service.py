"""FAISS 벡터 데이터베이스 서비스"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import faiss
import numpy as np

from app.core.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "data" / "vector_db"


class VectorDBService:
    """FAISS 벡터 데이터베이스 서비스 클래스"""

    def __init__(
        self,
        index_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None
    ):
        """
        벡터 DB 서비스 초기화

        Args:
            index_path: FAISS 인덱스 파일 경로
            metadata_path: 메타데이터 JSON 파일 경로
        """
        self.index_path = index_path or VECTOR_DB_DIR / "faiss.index"
        self.metadata_path = metadata_path or VECTOR_DB_DIR / "metadata.json"

        self.index: Optional[faiss.Index] = None
        self.metadata: Dict = {}
        self.recipes: List[Dict] = []

        self._load()

    def _load(self):
        """인덱스와 메타데이터 로드"""
        # FAISS 인덱스 로드
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            logger.info(f"FAISS 인덱스 로드 완료: {self.index.ntotal}개 벡터")
        else:
            logger.warning(f"FAISS 인덱스 파일 없음: {self.index_path}")

        # 메타데이터 로드
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.recipes = self.metadata.get("recipes", [])
            logger.info(f"메타데이터 로드 완료: {len(self.recipes)}개 레시피")
        else:
            logger.warning(f"메타데이터 파일 없음: {self.metadata_path}")

    @property
    def is_ready(self) -> bool:
        """서비스 준비 상태"""
        return self.index is not None and len(self.recipes) > 0

    @property
    def total_recipes(self) -> int:
        """총 레시피 수"""
        return len(self.recipes)

    def search(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.5
    ) -> List[Dict]:
        """
        쿼리로 레시피 검색

        Args:
            query: 검색 쿼리
            top_k: 반환할 최대 결과 수
            similarity_threshold: 최소 유사도 임계값 (0 ~ 1)

        Returns:
            검색 결과 리스트 (유사도 포함)
        """
        if not self.is_ready:
            logger.warning("벡터 DB가 준비되지 않았습니다.")
            return []

        try:
            # 쿼리 임베딩
            embedding_service = get_embedding_service()
            query_embedding = embedding_service.get_embedding(query)
            query_vector = np.array([query_embedding], dtype=np.float32)

            # FAISS 검색 (L2 거리)
            distances, indices = self.index.search(query_vector, top_k)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.recipes):
                    continue

                # L2 거리를 유사도로 변환
                # 거리가 작을수록 유사함 → 1 / (1 + dist)
                similarity = 1 / (1 + float(dist))

                if similarity < similarity_threshold:
                    continue

                recipe = self.recipes[idx].copy()
                recipe["similarity"] = round(similarity, 4)
                recipe["distance"] = round(float(dist), 4)
                results.append(recipe)

            return results

        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []

    def get_recipe_by_index(self, idx: int) -> Optional[Dict]:
        """
        인덱스로 레시피 조회

        Args:
            idx: 레시피 인덱스

        Returns:
            레시피 정보 또는 None
        """
        if 0 <= idx < len(self.recipes):
            return self.recipes[idx].copy()
        return None

    def get_recipe_by_name(self, name: str) -> Optional[Dict]:
        """
        이름으로 레시피 조회 (정확한 매칭)

        Args:
            name: 레시피 이름

        Returns:
            레시피 정보 또는 None
        """
        for recipe in self.recipes:
            if recipe.get("name") == name:
                return recipe.copy()
        return None

    def search_by_category(self, category: str, top_k: int = 10) -> List[Dict]:
        """
        카테고리로 레시피 검색

        Args:
            category: 카테고리명
            top_k: 최대 결과 수

        Returns:
            레시피 리스트
        """
        results = []
        for recipe in self.recipes:
            if category in recipe.get("category", ""):
                results.append(recipe.copy())
                if len(results) >= top_k:
                    break
        return results

    def get_similar_recipes(
        self,
        recipe_idx: int,
        top_k: int = 5
    ) -> List[Dict]:
        """
        특정 레시피와 유사한 레시피 검색

        Args:
            recipe_idx: 기준 레시피 인덱스
            top_k: 반환할 결과 수

        Returns:
            유사 레시피 리스트
        """
        if not self.is_ready:
            return []

        if recipe_idx < 0 or recipe_idx >= self.index.ntotal:
            return []

        try:
            # 해당 레시피의 벡터 가져오기
            vector = self.index.reconstruct(recipe_idx)
            query_vector = np.array([vector], dtype=np.float32)

            # 검색 (자기 자신 제외하기 위해 top_k + 1)
            distances, indices = self.index.search(query_vector, top_k + 1)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == recipe_idx:  # 자기 자신 제외
                    continue
                if idx < 0 or idx >= len(self.recipes):
                    continue

                similarity = 1 / (1 + float(dist))
                recipe = self.recipes[idx].copy()
                recipe["similarity"] = round(similarity, 4)
                results.append(recipe)

                if len(results) >= top_k:
                    break

            return results

        except Exception as e:
            logger.error(f"유사 레시피 검색 실패: {e}")
            return []


# 싱글톤 인스턴스
_vector_db_service: Optional[VectorDBService] = None


def get_vector_db_service() -> VectorDBService:
    """벡터 DB 서비스 싱글톤 인스턴스 반환"""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service
