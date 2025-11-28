"""영양정보 SQLite 데이터베이스 서비스"""

import logging
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "database" / "nutrition.db"


class NutritionDBService:
    """영양정보 데이터베이스 서비스 클래스"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        영양정보 DB 서비스 초기화

        Args:
            db_path: SQLite DB 파일 경로
        """
        self.db_path = db_path or DB_PATH
        self._conn: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """DB 연결 획득"""
        if self._conn is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"영양정보 DB 파일이 없습니다: {self.db_path}")
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        """DB 연결 종료"""
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def is_ready(self) -> bool:
        """서비스 준비 상태"""
        return self.db_path.exists()

    def get_total_count(self) -> int:
        """총 레코드 수 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM nutrition")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"총 레코드 수 조회 실패: {e}")
            return 0

    def get_nutrition(self, food_name: str) -> Optional[Dict]:
        """
        음식명으로 영양정보 조회 (정확한 매칭)

        Args:
            food_name: 음식 이름

        Returns:
            영양정보 딕셔너리 또는 None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM nutrition
                WHERE food_name = ?
                LIMIT 1
            """, (food_name,))

            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None

        except Exception as e:
            logger.error(f"영양정보 조회 실패: {e}")
            return None

    def search_similar(
        self,
        food_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        유사 음식 검색 (LIKE 쿼리)

        Args:
            food_name: 검색할 음식 이름
            limit: 최대 결과 수

        Returns:
            영양정보 리스트
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM nutrition
                WHERE food_name LIKE ?
                ORDER BY
                    CASE
                        WHEN food_name = ? THEN 0
                        WHEN food_name LIKE ? THEN 1
                        ELSE 2
                    END,
                    food_name
                LIMIT ?
            """, (f"%{food_name}%", food_name, f"{food_name}%", limit))

            return [self._row_to_dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"유사 음식 검색 실패: {e}")
            return []

    def search_by_category(
        self,
        category: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        카테고리로 검색

        Args:
            category: 카테고리명
            limit: 최대 결과 수

        Returns:
            영양정보 리스트
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM nutrition
                WHERE category1 LIKE ? OR category2 LIKE ?
                LIMIT ?
            """, (f"%{category}%", f"%{category}%", limit))

            return [self._row_to_dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"카테고리 검색 실패: {e}")
            return []

    def get_by_calorie_range(
        self,
        min_cal: float,
        max_cal: float,
        limit: int = 20
    ) -> List[Dict]:
        """
        칼로리 범위로 검색

        Args:
            min_cal: 최소 칼로리
            max_cal: 최대 칼로리
            limit: 최대 결과 수

        Returns:
            영양정보 리스트
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM nutrition
                WHERE calories BETWEEN ? AND ?
                ORDER BY calories
                LIMIT ?
            """, (min_cal, max_cal, limit))

            return [self._row_to_dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"칼로리 범위 검색 실패: {e}")
            return []

    def get_low_calorie_foods(
        self,
        max_calories: float = 200,
        limit: int = 20
    ) -> List[Dict]:
        """저칼로리 음식 조회"""
        return self.get_by_calorie_range(1, max_calories, limit)

    def get_high_protein_foods(
        self,
        min_protein: float = 20,
        limit: int = 20
    ) -> List[Dict]:
        """고단백 음식 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM nutrition
                WHERE protein >= ?
                ORDER BY protein DESC
                LIMIT ?
            """, (min_protein, limit))

            return [self._row_to_dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"고단백 음식 조회 실패: {e}")
            return []

    def get_statistics(self) -> Dict:
        """영양정보 통계 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            stats = {}

            # 총 레코드 수
            cursor.execute("SELECT COUNT(*) FROM nutrition")
            stats["total_count"] = cursor.fetchone()[0]

            # DB 그룹별 분포
            cursor.execute("""
                SELECT db_group, COUNT(*) as cnt
                FROM nutrition
                GROUP BY db_group
                ORDER BY cnt DESC
            """)
            stats["db_groups"] = {row[0]: row[1] for row in cursor.fetchall()}

            # 카테고리별 분포 (상위 10개)
            cursor.execute("""
                SELECT category1, COUNT(*) as cnt
                FROM nutrition
                WHERE category1 IS NOT NULL AND category1 != ''
                GROUP BY category1
                ORDER BY cnt DESC
                LIMIT 10
            """)
            stats["top_categories"] = {row[0]: row[1] for row in cursor.fetchall()}

            # 칼로리 통계
            cursor.execute("""
                SELECT AVG(calories), MIN(calories), MAX(calories)
                FROM nutrition
                WHERE calories > 0
            """)
            row = cursor.fetchone()
            stats["calories"] = {
                "avg": round(row[0], 1) if row[0] else 0,
                "min": round(row[1], 1) if row[1] else 0,
                "max": round(row[2], 1) if row[2] else 0
            }

            return stats

        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Row 객체를 딕셔너리로 변환"""
        d = dict(row)

        # 영양정보를 중첩 구조로 정리
        nutrition_fields = [
            "calories", "water", "protein", "fat", "ash",
            "carbohydrate", "sugar", "fiber", "calcium", "iron",
            "phosphorus", "sodium", "potassium", "vitamin_a",
            "vitamin_c", "cholesterol", "saturated_fat", "trans_fat"
        ]

        nutrition = {}
        for field in nutrition_fields:
            if field in d:
                nutrition[field] = d.pop(field)

        d["nutrition"] = nutrition
        return d


# 싱글톤 인스턴스
_nutrition_db_service: Optional[NutritionDBService] = None


def get_nutrition_db_service() -> NutritionDBService:
    """영양정보 DB 서비스 싱글톤 인스턴스 반환"""
    global _nutrition_db_service
    if _nutrition_db_service is None:
        _nutrition_db_service = NutritionDBService()
    return _nutrition_db_service
