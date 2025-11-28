"""
영양정보 데이터 정제 스크립트
data.go.kr 식품영양성분DB 원본 데이터 정제
"""

import json
import logging
import re
from pathlib import Path
from collections import Counter

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 입출력 파일 경로
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "nutrition_raw.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "nutrition.json"


def load_raw_data() -> list[dict]:
    """원본 데이터 로드"""
    if not RAW_FILE.exists():
        logger.error(f"원본 파일이 없습니다: {RAW_FILE}")
        return []

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_food_name(name: str) -> str:
    """음식명 정규화"""
    if not name:
        return ""

    # 앞뒤 공백 제거
    name = name.strip()

    # 언더스코어를 공백으로
    name = name.replace("_", " ")

    # 연속 공백 제거
    name = re.sub(r'\s+', ' ', name)

    return name


def parse_float(value) -> float:
    """문자열을 float로 변환 (None, 빈값, 문자 처리)"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if not value or value == '-':
            return 0.0
        try:
            # 숫자만 추출
            numeric = re.sub(r'[^\d.]', '', value)
            return float(numeric) if numeric else 0.0
        except ValueError:
            return 0.0
    return 0.0


def process_nutrition_item(item: dict) -> dict:
    """개별 영양정보 아이템 정제"""

    # 기본 정보
    processed = {
        "food_code": item.get("FOOD_CD", ""),
        "food_name": clean_food_name(item.get("FOOD_NM_KR", "")),
        "db_group": item.get("DB_GRP_NM", ""),  # 음식/가공식품 등
        "db_class": item.get("DB_CLASS_NM", ""),  # 품목대표/상용제품
        "food_origin": item.get("FOOD_OR_NM", ""),  # 가정식/외식 등
        "category1": item.get("FOOD_CAT1_NM", ""),  # 대분류 (밥류, 면류 등)
        "category2": item.get("FOOD_CAT2_NM", ""),  # 중분류
        "serving_size": parse_float(item.get("SERVING_SIZE", 0)),  # 1회 제공량
    }

    # 주요 영양성분 (AMT_NUM 필드)
    # data.go.kr API 응답 필드명 매핑
    nutrition = {
        "calories": parse_float(item.get("AMT_NUM1", 0)),      # 에너지 (kcal)
        "water": parse_float(item.get("AMT_NUM2", 0)),          # 수분 (g)
        "protein": parse_float(item.get("AMT_NUM3", 0)),        # 단백질 (g)
        "fat": parse_float(item.get("AMT_NUM4", 0)),            # 지방 (g)
        "ash": parse_float(item.get("AMT_NUM5", 0)),            # 회분 (g)
        "carbohydrate": parse_float(item.get("AMT_NUM7", 0)),   # 탄수화물 (g)
        "sugar": parse_float(item.get("AMT_NUM8", 0)),          # 당류 (g)
        "fiber": parse_float(item.get("AMT_NUM9", 0)),          # 식이섬유 (g)
        "calcium": parse_float(item.get("AMT_NUM10", 0)),       # 칼슘 (mg)
        "iron": parse_float(item.get("AMT_NUM11", 0)),          # 철 (mg)
        "phosphorus": parse_float(item.get("AMT_NUM12", 0)),    # 인 (mg)
        "sodium": parse_float(item.get("AMT_NUM13", 0)),        # 나트륨 (mg)
        "potassium": parse_float(item.get("AMT_NUM14", 0)),     # 칼륨 (mg)
        "vitamin_a": parse_float(item.get("AMT_NUM15", 0)),     # 비타민A (μg RAE)
        "vitamin_c": parse_float(item.get("AMT_NUM24", 0)),     # 비타민C (mg)
        "cholesterol": parse_float(item.get("AMT_NUM22", 0)),   # 콜레스테롤 (mg)
        "saturated_fat": parse_float(item.get("AMT_NUM18", 0)), # 포화지방 (g)
        "trans_fat": parse_float(item.get("AMT_NUM20", 0)),     # 트랜스지방 (g)
    }

    processed["nutrition"] = nutrition

    return processed


def remove_duplicates(items: list[dict]) -> list[dict]:
    """중복 제거 (food_code 기준)"""
    seen = set()
    unique = []

    for item in items:
        food_code = item.get("food_code", "")
        if food_code and food_code not in seen:
            seen.add(food_code)
            unique.append(item)
        elif not food_code:
            # food_code 없는 경우 음식명으로 중복 체크
            food_name = item.get("food_name", "")
            if food_name and food_name not in seen:
                seen.add(food_name)
                unique.append(item)

    return unique


def filter_valid_items(items: list[dict]) -> list[dict]:
    """유효한 아이템만 필터링"""
    valid = []

    for item in items:
        # 음식명 필수
        if not item.get("food_name"):
            continue

        # 칼로리가 0 이상 (음수 제외)
        calories = item.get("nutrition", {}).get("calories", 0)
        if calories < 0:
            continue

        valid.append(item)

    return valid


def process_all_nutrition(raw_data: list[dict]) -> list[dict]:
    """전체 영양정보 정제"""
    logger.info(f"원본 영양정보 수: {len(raw_data):,}")

    # 1. 개별 아이템 정제
    processed = [process_nutrition_item(item) for item in raw_data]
    logger.info(f"정제 완료: {len(processed):,}개")

    # 2. 유효한 아이템 필터링
    valid = filter_valid_items(processed)
    logger.info(f"유효 데이터: {len(valid):,}개")

    # 3. 중복 제거
    unique = remove_duplicates(valid)
    logger.info(f"중복 제거 후: {len(unique):,}개")

    return unique


def save_processed_data(data: list[dict], output_path: Path) -> None:
    """정제된 데이터 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"저장 완료: {output_path}")


def print_statistics(data: list[dict]) -> None:
    """통계 출력"""
    logger.info("\n" + "=" * 50)
    logger.info("영양정보 통계")
    logger.info("=" * 50)

    # DB 그룹별 분포
    db_groups = Counter(item.get("db_group", "기타") for item in data)
    logger.info("\nDB 그룹별 분포:")
    for group, count in db_groups.most_common():
        logger.info(f"  {group}: {count:,}개")

    # 카테고리1 분포 (상위 10개)
    categories = Counter(item.get("category1", "기타") for item in data)
    logger.info("\n카테고리별 분포 (상위 10개):")
    for cat, count in categories.most_common(10):
        logger.info(f"  {cat}: {count:,}개")

    # 칼로리 통계
    calories = [item["nutrition"]["calories"] for item in data if item["nutrition"]["calories"] > 0]
    if calories:
        logger.info(f"\n칼로리 통계:")
        logger.info(f"  평균: {sum(calories)/len(calories):.1f} kcal")
        logger.info(f"  최소: {min(calories):.1f} kcal")
        logger.info(f"  최대: {max(calories):.1f} kcal")

    # 샘플 출력
    logger.info("\n샘플 영양정보:")
    for item in data[:3]:
        logger.info(f"  {item['food_name']}: {item['nutrition']['calories']:.0f}kcal")


def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("영양정보 데이터 정제 시작")
    logger.info("=" * 50)

    # 원본 데이터 로드
    raw_data = load_raw_data()
    if not raw_data:
        logger.error("원본 데이터가 없습니다.")
        return

    # 정제
    processed_data = process_all_nutrition(raw_data)

    if not processed_data:
        logger.error("정제된 데이터가 없습니다.")
        return

    # 저장
    save_processed_data(processed_data, OUTPUT_FILE)

    # 통계 출력
    print_statistics(processed_data)

    logger.info("\n" + "=" * 50)
    logger.info("정제 완료!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
