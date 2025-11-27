"""
레시피 데이터 정제 스크립트
원본 데이터를 정규화하고 정제합니다.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 경로 설정
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "recipes_raw.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "recipes.json"


def clean_text(text: str) -> str:
    """텍스트 정제"""
    if not text:
        return ""
    # 공백 정규화
    text = " ".join(text.split())
    # 앞뒤 공백 제거
    return text.strip()


def parse_float(value: str, default: float = 0.0) -> float:
    """문자열을 float으로 변환"""
    if not value:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def extract_instructions(recipe: dict) -> list[str]:
    """조리법 추출 및 정제"""
    instructions = []
    for i in range(1, 21):  # MANUAL01 ~ MANUAL20
        key = f"MANUAL{i:02d}"
        step = recipe.get(key, "")
        if step:
            cleaned = clean_text(step)
            if cleaned:
                instructions.append(cleaned)
    return instructions


def extract_ingredients(recipe: dict) -> list[str]:
    """재료 추출 및 파싱"""
    parts = recipe.get("RCP_PARTS_DTLS", "")
    if not parts:
        return []

    # 콤마, 줄바꿈, | 등으로 분리
    import re
    parts = re.split(r"[,\n|•·]", parts)
    ingredients = []

    for part in parts:
        cleaned = clean_text(part)
        if cleaned and len(cleaned) > 1:
            ingredients.append(cleaned)

    return ingredients


def process_recipe(raw: dict) -> Optional[dict]:
    """단일 레시피 정제"""
    name = clean_text(raw.get("RCP_NM", ""))
    if not name:
        return None

    # 기본 정보
    processed = {
        "recipe_id": raw.get("RCP_SEQ", ""),
        "name": name,
        "category": clean_text(raw.get("RCP_PAT2", "기타")),
        "cooking_method": clean_text(raw.get("RCP_WAY2", "")),
        "serving_size": 1,  # 기본값 (원본에 없는 경우)
        "cooking_time": 0,  # 기본값 (원본에 없는 경우)
        "difficulty": "보통",  # 기본값
    }

    # 재료
    processed["ingredients"] = extract_ingredients(raw)

    # 조리법
    processed["instructions"] = extract_instructions(raw)

    # 영양정보
    processed["nutrition"] = {
        "calories": parse_float(raw.get("INFO_ENG")),
        "carbohydrate": parse_float(raw.get("INFO_CAR")),
        "protein": parse_float(raw.get("INFO_PRO")),
        "fat": parse_float(raw.get("INFO_FAT")),
        "sodium": parse_float(raw.get("INFO_NA")),
    }

    # 이미지
    processed["image_url"] = raw.get("ATT_FILE_NO_MAIN", "")

    # 해시태그
    processed["hash_tag"] = clean_text(raw.get("HASH_TAG", ""))

    # 팁
    tip = raw.get("RCP_NA_TIP", "")
    processed["tip"] = clean_text(tip) if tip else ""

    return processed


def process_all_recipes(raw_recipes: list[dict]) -> list[dict]:
    """전체 레시피 정제"""
    processed = []
    seen_names = set()

    for raw in raw_recipes:
        recipe = process_recipe(raw)
        if recipe:
            # 중복 제거 (이름 기준)
            if recipe["name"] not in seen_names:
                seen_names.add(recipe["name"])
                processed.append(recipe)

    return processed


def save_processed(recipes: list[dict], output_path: Path) -> None:
    """정제된 데이터 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)

    logger.info(f"저장 완료: {output_path} ({len(recipes)}개 레시피)")


def main():
    """메인 실행 함수"""
    logger.info("=" * 50)
    logger.info("레시피 데이터 정제 시작")
    logger.info("=" * 50)

    if not RAW_FILE.exists():
        logger.error(f"원본 파일이 없습니다: {RAW_FILE}")
        logger.info("먼저 python scripts/collect_recipes.py를 실행하세요.")
        sys.exit(1)

    # 원본 데이터 로드
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw_recipes = json.load(f)

    logger.info(f"원본 레시피 수: {len(raw_recipes)}")

    # 데이터 정제
    processed = process_all_recipes(raw_recipes)

    logger.info(f"정제 후 레시피 수: {len(processed)}")
    logger.info(f"중복 제거: {len(raw_recipes) - len(processed)}개")

    # 저장
    save_processed(processed, OUTPUT_FILE)

    # 통계
    categories = {}
    for recipe in processed:
        cat = recipe["category"]
        categories[cat] = categories.get(cat, 0) + 1

    logger.info("\n카테고리별 레시피 수:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        logger.info(f"  {cat}: {count}개")

    # 샘플 출력
    logger.info("\n샘플 레시피:")
    if processed:
        sample = processed[0]
        logger.info(f"  이름: {sample['name']}")
        logger.info(f"  카테고리: {sample['category']}")
        logger.info(f"  재료 수: {len(sample['ingredients'])}")
        logger.info(f"  조리법 단계: {len(sample['instructions'])}")
        logger.info(f"  칼로리: {sample['nutrition']['calories']} kcal")

    logger.info("=" * 50)
    logger.info("정제 완료!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
