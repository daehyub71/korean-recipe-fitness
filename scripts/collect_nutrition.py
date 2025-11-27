"""
공공데이터포털 API 2: 식품영양성분 DB 수집
식품의약품안전처 제공
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional

import requests
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

# API 설정
API_KEY = os.getenv("NUTRITION_API_KEY")
BASE_URL = "http://openapi.foodsafetykorea.go.kr/api"
SERVICE_NAME = "I2790"  # 식품영양성분 DB 서비스명 (일반음식)

# 출력 디렉토리
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "nutrition_raw.json"


def fetch_nutrition_page(
    start_idx: int,
    end_idx: int,
    retry_count: int = 3,
    retry_delay: float = 1.0
) -> Optional[dict]:
    """
    영양성분 API 단일 페이지 호출

    Args:
        start_idx: 시작 인덱스
        end_idx: 종료 인덱스
        retry_count: 재시도 횟수
        retry_delay: 재시도 대기 시간 (초)

    Returns:
        API 응답 데이터 또는 None
    """
    url = f"{BASE_URL}/{API_KEY}/{SERVICE_NAME}/json/{start_idx}/{end_idx}"

    for attempt in range(retry_count):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # API 오류 체크
            if SERVICE_NAME in data:
                result = data[SERVICE_NAME]
                if "RESULT" in result:
                    code = result["RESULT"].get("CODE")
                    if code != "INFO-000":
                        logger.warning(f"API 오류 코드: {code} - {result['RESULT'].get('MSG')}")
                        if code == "INFO-200":  # 데이터 없음
                            return None
                return data

            logger.error(f"예상치 못한 응답 형식: {list(data.keys())}")
            return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"요청 실패 (시도 {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(retry_delay)
            continue

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return None

    return None


def get_total_count() -> int:
    """전체 영양성분 데이터 수 조회"""
    data = fetch_nutrition_page(1, 1)
    if data and SERVICE_NAME in data:
        return int(data[SERVICE_NAME].get("total_count", 0))
    return 0


def collect_all_nutrition(
    batch_size: int = 100,
    max_records: Optional[int] = None
) -> list[dict]:
    """
    전체 영양성분 데이터 수집

    Args:
        batch_size: 페이지당 레코드 수 (최대 1000)
        max_records: 최대 수집 레코드 수 (None이면 전체)

    Returns:
        수집된 영양성분 리스트
    """
    total_count = get_total_count()
    logger.info(f"전체 영양성분 데이터 수: {total_count}")

    if total_count == 0:
        logger.error("영양성분 데이터를 가져올 수 없습니다.")
        return []

    if max_records:
        total_count = min(total_count, max_records)
        logger.info(f"최대 {max_records}개까지 수집합니다.")

    all_nutrition = []
    start_idx = 1

    while start_idx <= total_count:
        end_idx = min(start_idx + batch_size - 1, total_count)
        logger.info(f"수집 중: {start_idx} ~ {end_idx} / {total_count}")

        data = fetch_nutrition_page(start_idx, end_idx)

        if data and SERVICE_NAME in data:
            rows = data[SERVICE_NAME].get("row", [])
            all_nutrition.extend(rows)
            logger.info(f"  → {len(rows)}개 데이터 추가 (총 {len(all_nutrition)}개)")
        else:
            logger.warning(f"  → 데이터 없음 (인덱스 {start_idx}~{end_idx})")

        start_idx = end_idx + 1

        # API 부하 방지
        time.sleep(0.5)

    return all_nutrition


def save_nutrition(nutrition: list[dict], output_path: Path) -> None:
    """영양성분 데이터 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nutrition, f, ensure_ascii=False, indent=2)

    logger.info(f"저장 완료: {output_path} ({len(nutrition)}개 영양정보)")


def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("식품영양성분 DB 수집 시작")
    logger.info("=" * 50)

    if not API_KEY:
        logger.error("NUTRITION_API_KEY 환경변수가 설정되지 않았습니다.")
        logger.info(".env 파일을 확인해주세요.")
        sys.exit(1)

    logger.info(f"API Key: {API_KEY[:8]}...{API_KEY[-8:]}")

    # 영양성분 수집
    nutrition = collect_all_nutrition(batch_size=100)

    if not nutrition:
        logger.error("수집된 영양성분 데이터가 없습니다.")
        sys.exit(1)

    # 저장
    save_nutrition(nutrition, OUTPUT_FILE)

    # 샘플 출력
    logger.info("\n샘플 영양성분:")
    if nutrition:
        sample = nutrition[0]
        for key, value in sample.items():
            logger.info(f"  {key}: {str(value)[:50]}")

    logger.info("=" * 50)
    logger.info("수집 완료!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
