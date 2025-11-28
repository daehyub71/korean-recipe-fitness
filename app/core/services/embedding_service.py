"""OpenAI 임베딩 서비스"""

import logging
import time
from typing import List, Optional

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """OpenAI 임베딩 서비스 클래스"""

    def __init__(self, model: str = "text-embedding-3-small"):
        """
        임베딩 서비스 초기화

        Args:
            model: OpenAI 임베딩 모델 (기본값: text-embedding-3-small)
                   - text-embedding-3-small: 1536 차원, 빠르고 저렴
                   - text-embedding-3-large: 3072 차원, 더 정확
        """
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = model
        self._dimension = 1536 if "small" in model else 3072

    @property
    def dimension(self) -> int:
        """임베딩 벡터 차원"""
        return self._dimension

    def get_embedding(self, text: str) -> List[float]:
        """
        단일 텍스트 임베딩 생성

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (List[float])
        """
        if not text or not text.strip():
            raise ValueError("텍스트가 비어있습니다.")

        # 텍스트 정규화
        text = text.strip().replace("\n", " ")

        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            raise

    def get_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ) -> List[List[float]]:
        """
        배치 임베딩 생성

        Args:
            texts: 임베딩할 텍스트 리스트
            batch_size: 배치 크기 (기본값: 100)
            retry_count: 재시도 횟수
            retry_delay: 재시도 대기 시간 (초)

        Returns:
            임베딩 벡터 리스트
        """
        if not texts:
            return []

        # 텍스트 정규화
        normalized_texts = [
            t.strip().replace("\n", " ") if t else ""
            for t in texts
        ]

        # 빈 텍스트 처리
        valid_indices = [i for i, t in enumerate(normalized_texts) if t]
        valid_texts = [normalized_texts[i] for i in valid_indices]

        if not valid_texts:
            return [[0.0] * self._dimension for _ in texts]

        all_embeddings = []

        # 배치 처리
        for i in range(0, len(valid_texts), batch_size):
            batch = valid_texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(valid_texts) + batch_size - 1) // batch_size

            logger.info(f"임베딩 생성 중: 배치 {batch_num}/{total_batches} ({len(batch)}개)")

            for attempt in range(retry_count):
                try:
                    response = self.client.embeddings.create(
                        input=batch,
                        model=self.model
                    )

                    # 응답에서 임베딩 추출 (인덱스 순서 보장)
                    batch_embeddings = [None] * len(batch)
                    for item in response.data:
                        batch_embeddings[item.index] = item.embedding

                    all_embeddings.extend(batch_embeddings)
                    break

                except Exception as e:
                    logger.warning(f"배치 임베딩 실패 (시도 {attempt + 1}/{retry_count}): {e}")
                    if attempt < retry_count - 1:
                        time.sleep(retry_delay)
                    else:
                        # 최종 실패 시 예외 발생
                        raise

            # API 부하 방지
            time.sleep(0.1)

        # 빈 텍스트 위치에 제로 벡터 삽입
        result = [[0.0] * self._dimension for _ in texts]
        for idx, emb in zip(valid_indices, all_embeddings):
            result[idx] = emb

        return result

    def compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        두 임베딩 벡터의 코사인 유사도 계산

        Args:
            embedding1: 첫 번째 임베딩 벡터
            embedding2: 두 번째 임베딩 벡터

        Returns:
            코사인 유사도 (0 ~ 1)
        """
        import numpy as np

        v1 = np.array(embedding1)
        v2 = np.array(embedding2)

        # 코사인 유사도
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


# 싱글톤 인스턴스
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """임베딩 서비스 싱글톤 인스턴스 반환"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
