"""
영양정보 SQLite 데이터베이스 빌드 스크립트
정제된 영양정보 데이터를 SQLite DB에 저장
"""

import json
import logging
import sqlite3
import sys
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 파일 경로
NUTRITION_FILE = PROJECT_ROOT / "data" / "processed" / "nutrition.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "database"
DB_FILE = OUTPUT_DIR / "nutrition.db"


def load_nutrition_data() -> list[dict]:
    """정제된 영양정보 데이터 로드"""
    if not NUTRITION_FILE.exists():
        logger.error(f"영양정보 파일이 없습니다: {NUTRITION_FILE}")
        return []

    with open(NUTRITION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def create_database(db_path: Path) -> sqlite3.Connection:
    """데이터베이스 및 테이블 생성"""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # 기존 테이블 삭제
    cursor.execute("DROP TABLE IF EXISTS nutrition")

    # 영양정보 테이블 생성
    cursor.execute("""
        CREATE TABLE nutrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_code TEXT,
            food_name TEXT NOT NULL,
            db_group TEXT,
            db_class TEXT,
            food_origin TEXT,
            category1 TEXT,
            category2 TEXT,
            serving_size REAL DEFAULT 0,
            calories REAL DEFAULT 0,
            water REAL DEFAULT 0,
            protein REAL DEFAULT 0,
            fat REAL DEFAULT 0,
            ash REAL DEFAULT 0,
            carbohydrate REAL DEFAULT 0,
            sugar REAL DEFAULT 0,
            fiber REAL DEFAULT 0,
            calcium REAL DEFAULT 0,
            iron REAL DEFAULT 0,
            phosphorus REAL DEFAULT 0,
            sodium REAL DEFAULT 0,
            potassium REAL DEFAULT 0,
            vitamin_a REAL DEFAULT 0,
            vitamin_c REAL DEFAULT 0,
            cholesterol REAL DEFAULT 0,
            saturated_fat REAL DEFAULT 0,
            trans_fat REAL DEFAULT 0
        )
    """)

    # 인덱스 생성
    cursor.execute("CREATE INDEX idx_food_name ON nutrition(food_name)")
    cursor.execute("CREATE INDEX idx_food_code ON nutrition(food_code)")
    cursor.execute("CREATE INDEX idx_category1 ON nutrition(category1)")
    cursor.execute("CREATE INDEX idx_db_group ON nutrition(db_group)")

    conn.commit()
    logger.info("데이터베이스 테이블 생성 완료")

    return conn


def insert_nutrition_data(conn: sqlite3.Connection, data: list[dict]):
    """영양정보 데이터 삽입"""
    cursor = conn.cursor()

    insert_sql = """
        INSERT INTO nutrition (
            food_code, food_name, db_group, db_class, food_origin,
            category1, category2, serving_size,
            calories, water, protein, fat, ash, carbohydrate, sugar, fiber,
            calcium, iron, phosphorus, sodium, potassium,
            vitamin_a, vitamin_c, cholesterol, saturated_fat, trans_fat
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    batch_size = 1000
    total = len(data)
    inserted = 0

    for i in range(0, total, batch_size):
        batch = data[i:i + batch_size]

        rows = []
        for item in batch:
            nutrition = item.get("nutrition", {})
            row = (
                item.get("food_code", ""),
                item.get("food_name", ""),
                item.get("db_group", ""),
                item.get("db_class", ""),
                item.get("food_origin", ""),
                item.get("category1", ""),
                item.get("category2", ""),
                item.get("serving_size", 0),
                nutrition.get("calories", 0),
                nutrition.get("water", 0),
                nutrition.get("protein", 0),
                nutrition.get("fat", 0),
                nutrition.get("ash", 0),
                nutrition.get("carbohydrate", 0),
                nutrition.get("sugar", 0),
                nutrition.get("fiber", 0),
                nutrition.get("calcium", 0),
                nutrition.get("iron", 0),
                nutrition.get("phosphorus", 0),
                nutrition.get("sodium", 0),
                nutrition.get("potassium", 0),
                nutrition.get("vitamin_a", 0),
                nutrition.get("vitamin_c", 0),
                nutrition.get("cholesterol", 0),
                nutrition.get("saturated_fat", 0),
                nutrition.get("trans_fat", 0)
            )
            rows.append(row)

        cursor.executemany(insert_sql, rows)
        conn.commit()

        inserted += len(batch)
        logger.info(f"삽입 진행: {inserted:,}/{total:,} ({inserted/total*100:.1f}%)")

    logger.info(f"총 {inserted:,}개 레코드 삽입 완료")


def verify_database(conn: sqlite3.Connection):
    """데이터베이스 검증"""
    cursor = conn.cursor()

    # 총 레코드 수
    cursor.execute("SELECT COUNT(*) FROM nutrition")
    total = cursor.fetchone()[0]
    logger.info(f"\n총 레코드 수: {total:,}")

    # DB 그룹별 분포
    cursor.execute("""
        SELECT db_group, COUNT(*) as cnt
        FROM nutrition
        GROUP BY db_group
        ORDER BY cnt DESC
    """)
    logger.info("\nDB 그룹별 분포:")
    for row in cursor.fetchall():
        logger.info(f"  {row[0]}: {row[1]:,}개")

    # 카테고리별 분포 (상위 10개)
    cursor.execute("""
        SELECT category1, COUNT(*) as cnt
        FROM nutrition
        WHERE category1 IS NOT NULL AND category1 != ''
        GROUP BY category1
        ORDER BY cnt DESC
        LIMIT 10
    """)
    logger.info("\n카테고리별 분포 (상위 10개):")
    for row in cursor.fetchall():
        logger.info(f"  {row[0]}: {row[1]:,}개")

    # 칼로리 통계
    cursor.execute("""
        SELECT
            AVG(calories) as avg_cal,
            MIN(calories) as min_cal,
            MAX(calories) as max_cal
        FROM nutrition
        WHERE calories > 0
    """)
    row = cursor.fetchone()
    logger.info(f"\n칼로리 통계:")
    logger.info(f"  평균: {row[0]:.1f} kcal")
    logger.info(f"  최소: {row[1]:.1f} kcal")
    logger.info(f"  최대: {row[2]:.1f} kcal")

    # 샘플 검색 테스트
    logger.info("\n검색 테스트:")
    test_queries = ["김치", "불고기", "비빔밥"]
    for query in test_queries:
        cursor.execute("""
            SELECT food_name, calories, protein, fat, carbohydrate
            FROM nutrition
            WHERE food_name LIKE ?
            LIMIT 3
        """, (f"%{query}%",))
        results = cursor.fetchall()
        logger.info(f"\n  '{query}' 검색 결과:")
        for r in results:
            logger.info(f"    {r[0]}: {r[1]:.0f}kcal, 단백질 {r[2]:.1f}g, 지방 {r[3]:.1f}g, 탄수화물 {r[4]:.1f}g")


def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("영양정보 SQLite DB 빌드 시작")
    logger.info("=" * 50)

    # 영양정보 데이터 로드
    nutrition_data = load_nutrition_data()
    if not nutrition_data:
        logger.error("영양정보 데이터가 없습니다.")
        sys.exit(1)

    logger.info(f"로드된 영양정보: {len(nutrition_data):,}개")

    # 데이터베이스 생성
    conn = create_database(DB_FILE)

    # 데이터 삽입
    insert_nutrition_data(conn, nutrition_data)

    # 검증
    verify_database(conn)

    conn.close()

    logger.info("\n" + "=" * 50)
    logger.info(f"빌드 완료: {DB_FILE}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
