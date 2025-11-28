"""
공공데이터포털 API 2: 식품영양성분 DB 수집
식품의약품안전처 제공 (data.go.kr)
API: FoodNtrCpntDbInfo02 - 식품영양성분DB(가공식품+음식)
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import quote

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

# API 설정 (data.go.kr 식품영양성분DB)
API_KEY = os.getenv("NUTRITION_API_KEY")
BASE_URL = "https://apis.data.go.kr/1471000/FoodNtrCpntDbInfo02"
OPERATION = "getFoodNtrCpntDbInq02"  # 주의: Info가 아닌 Inq (Inquiry)

# 출력 디렉토리
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "nutrition_raw.json"


def fetch_nutrition_page(
    page_no: int = 1,
    num_of_rows: int = 100,
    retry_count: int = 3,
    retry_delay: float = 1.0
) -> Optional[dict]:
    """
    영양성분 API 단일 페이지 호출

    Args:
        page_no: 페이지 번호 (1부터 시작)
        num_of_rows: 페이지당 레코드 수
        retry_count: 재시도 횟수
        retry_delay: 재시도 대기 시간 (초)

    Returns:
        API 응답 데이터 또는 None
    """
    # URL 인코딩된 API 키 사용
    encoded_key = quote(API_KEY, safe='')

    url = f"{BASE_URL}/{OPERATION}"
    params = {
        "serviceKey": API_KEY,  # 일부 API는 인코딩 안된 키 필요
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "type": "json"
    }

    for attempt in range(retry_count):
        try:
            response = requests.get(url, params=params, timeout=30)

            # 디버깅: 첫 요청의 URL과 상태 코드 출력
            if page_no == 1 and attempt == 0:
                logger.info(f"요청 URL: {response.url[:100]}...")
                logger.info(f"상태 코드: {response.status_code}")

            response.raise_for_status()

            data = response.json()

            # 응답 구조 확인 (body > items)
            if "body" in data:
                body = data["body"]
                total_count = body.get("totalCount", 0)
                items = body.get("items", [])

                return {
                    "total_count": total_count,
                    "items": items,
                    "page_no": page_no
                }

            # 오류 응답 체크
            if "header" in data:
                result_code = data["header"].get("resultCode")
                result_msg = data["header"].get("resultMsg")
                if result_code != "00":
                    logger.warning(f"API 오류: [{result_code}] {result_msg}")
                    return None

            logger.error(f"예상치 못한 응답 형식: {list(data.keys())}")
            logger.debug(f"응답 내용: {str(data)[:500]}")
            return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"요청 실패 (시도 {attempt + 1}/{retry_count}): {e}")
            if attempt < retry_count - 1:
                time.sleep(retry_delay)
            continue

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            # 응답 내용 확인
            logger.debug(f"응답 내용: {response.text[:500]}")
            return None

    return None


def get_total_count() -> int:
    """전체 영양성분 데이터 수 조회"""
    data = fetch_nutrition_page(page_no=1, num_of_rows=1)
    if data:
        return data.get("total_count", 0)
    return 0


def collect_all_nutrition(
    num_of_rows: int = 100,
    max_records: Optional[int] = None
) -> list[dict]:
    """
    전체 영양성분 데이터 수집

    Args:
        num_of_rows: 페이지당 레코드 수 (최대 1000)
        max_records: 최대 수집 레코드 수 (None이면 전체)

    Returns:
        수집된 영양성분 리스트
    """
    total_count = get_total_count()
    logger.info(f"전체 영양성분 데이터 수: {total_count:,}")

    if total_count == 0:
        logger.error("영양성분 데이터를 가져올 수 없습니다.")
        return []

    if max_records:
        total_count = min(total_count, max_records)
        logger.info(f"최대 {max_records:,}개까지 수집합니다.")

    all_nutrition = []
    page_no = 1
    total_pages = (total_count + num_of_rows - 1) // num_of_rows

    while len(all_nutrition) < total_count:
        logger.info(f"수집 중: 페이지 {page_no}/{total_pages} (현재 {len(all_nutrition):,}개)")

        data = fetch_nutrition_page(page_no=page_no, num_of_rows=num_of_rows)

        if data and data.get("items"):
            items = data["items"]
            all_nutrition.extend(items)
            logger.info(f"  → {len(items)}개 데이터 추가 (총 {len(all_nutrition):,}개)")
        else:
            logger.warning(f"  → 데이터 없음 (페이지 {page_no})")
            # 연속 3페이지 데이터 없으면 중단
            if page_no > 3:
                break

        page_no += 1

        # API 부하 방지
        time.sleep(0.3)

    return all_nutrition


def save_nutrition(nutrition: list[dict], output_path: Path) -> None:
    """영양성분 데이터 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nutrition, f, ensure_ascii=False, indent=2)

    logger.info(f"저장 완료: {output_path} ({len(nutrition):,}개 영양정보)")


def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("식품영양성분 DB 수집 시작")
    logger.info("API: data.go.kr FoodNtrCpntDbInfo02")
    logger.info("=" * 50)

    if not API_KEY:
        logger.error("NUTRITION_API_KEY 환경변수가 설정되지 않았습니다.")
        logger.info(".env 파일을 확인해주세요.")
        sys.exit(1)

    logger.info(f"API Key: {API_KEY[:10]}...{API_KEY[-10:]}")

    # 영양성분 수집
    nutrition = collect_all_nutrition(num_of_rows=100)

    if not nutrition:
        logger.error("수집된 영양성분 데이터가 없습니다.")
        sys.exit(1)

    # 저장
    save_nutrition(nutrition, OUTPUT_FILE)

    # 샘플 출력
    logger.info("\n샘플 영양성분:")
    if nutrition:
        sample = nutrition[0]
        for key, value in list(sample.items())[:10]:
            logger.info(f"  {key}: {str(value)[:50]}")

    logger.info("=" * 50)
    logger.info("수집 완료!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
