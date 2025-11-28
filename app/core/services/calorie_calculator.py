"""CalorieCalculator 서비스 - 칼로리 소모 및 운동 추천 계산"""

import logging
from dataclasses import dataclass
from typing import List, Literal, Optional

logger = logging.getLogger(__name__)


# MET (Metabolic Equivalent of Task) 테이블
# MET 값: 운동 강도를 나타내는 지표 (1 MET = 휴식 시 에너지 소비량)
MET_TABLE = {
    # 저강도 운동 (MET 3.0-5.0)
    "walking_slow": {"name": "걷기 (느리게)", "name_kr": "천천히 걷기", "met": 3.0, "intensity": "low", "description": "시속 4km 이하로 느긋하게 걷기", "tips": "자연스럽게 팔을 흔들며 걸으세요"},
    "walking_moderate": {"name": "걷기 (보통)", "name_kr": "보통 걷기", "met": 3.5, "intensity": "low", "description": "시속 4-5km로 걷기", "tips": "대화할 수 있는 속도로 걸으세요"},
    "stretching": {"name": "스트레칭", "name_kr": "스트레칭", "met": 2.5, "intensity": "low", "description": "전신 스트레칭 및 유연성 운동", "tips": "각 동작을 15-30초씩 유지하세요"},
    "yoga_hatha": {"name": "요가 (하타)", "name_kr": "하타 요가", "met": 3.0, "intensity": "low", "description": "기본적인 요가 자세와 호흡", "tips": "호흡에 집중하며 천천히 하세요"},
    "light_housework": {"name": "가벼운 집안일", "name_kr": "가벼운 집안일", "met": 2.5, "intensity": "low", "description": "설거지, 빨래 개기 등", "tips": "일상 활동도 운동이 됩니다"},
    "tai_chi": {"name": "태극권", "name_kr": "태극권", "met": 3.0, "intensity": "low", "description": "느린 동작의 태극권", "tips": "균형과 호흡에 집중하세요"},
    "pilates_beginner": {"name": "필라테스 (초급)", "name_kr": "초급 필라테스", "met": 3.0, "intensity": "low", "description": "기본 필라테스 동작", "tips": "코어 근육을 의식하며 하세요"},

    # 중강도 운동 (MET 5.0-8.0)
    "walking_brisk": {"name": "걷기 (빠르게)", "name_kr": "빠르게 걷기", "met": 4.5, "intensity": "medium", "description": "시속 5.5-6.5km로 빠르게 걷기", "tips": "약간 숨이 찰 정도로 걸으세요"},
    "cycling_leisure": {"name": "자전거 (여가)", "name_kr": "여가 자전거", "met": 5.5, "intensity": "medium", "description": "시속 15-20km로 자전거 타기", "tips": "안전 장비를 착용하세요"},
    "swimming_leisure": {"name": "수영 (여가)", "name_kr": "여가 수영", "met": 6.0, "intensity": "medium", "description": "천천히 수영하기", "tips": "정기적인 휴식을 취하세요"},
    "dancing_aerobic": {"name": "에어로빅 댄스", "name_kr": "에어로빅", "met": 6.5, "intensity": "medium", "description": "중간 강도의 에어로빅", "tips": "음악에 맞춰 즐겁게 하세요"},
    "table_tennis": {"name": "탁구", "name_kr": "탁구", "met": 5.0, "intensity": "medium", "description": "탁구 경기", "tips": "워밍업 후 시작하세요"},
    "badminton": {"name": "배드민턴", "name_kr": "배드민턴", "met": 5.5, "intensity": "medium", "description": "배드민턴 경기", "tips": "파트너와 함께 즐기세요"},
    "golf_walking": {"name": "골프 (걷기)", "name_kr": "골프 (걷기)", "met": 4.5, "intensity": "medium", "description": "카트 없이 걸어서 골프", "tips": "스윙 전 스트레칭하세요"},
    "yoga_power": {"name": "요가 (파워)", "name_kr": "파워 요가", "met": 5.5, "intensity": "medium", "description": "강도 높은 요가", "tips": "자신의 수준에 맞게 하세요"},
    "elliptical": {"name": "일립티컬", "name_kr": "일립티컬", "met": 5.0, "intensity": "medium", "description": "일립티컬 머신 운동", "tips": "팔과 다리를 함께 사용하세요"},
    "hiking": {"name": "등산 (가벼운)", "name_kr": "가벼운 등산", "met": 6.0, "intensity": "medium", "description": "완만한 경사 등산", "tips": "등산화와 충분한 물을 준비하세요"},

    # 고강도 운동 (MET 8.0 이상)
    "running_slow": {"name": "달리기 (느리게)", "name_kr": "조깅", "met": 8.0, "intensity": "high", "description": "시속 8km로 조깅", "tips": "워밍업 후 시작하세요"},
    "running_moderate": {"name": "달리기 (보통)", "name_kr": "달리기", "met": 10.0, "intensity": "high", "description": "시속 10km로 달리기", "tips": "무리하지 말고 페이스 조절하세요"},
    "running_fast": {"name": "달리기 (빠르게)", "name_kr": "빠른 달리기", "met": 12.0, "intensity": "high", "description": "시속 12km 이상으로 달리기", "tips": "충분한 휴식이 필요합니다"},
    "cycling_vigorous": {"name": "자전거 (고강도)", "name_kr": "고강도 자전거", "met": 10.0, "intensity": "high", "description": "시속 25km 이상으로 자전거", "tips": "헬멧을 꼭 착용하세요"},
    "swimming_laps": {"name": "수영 (랩)", "name_kr": "수영 랩", "met": 8.0, "intensity": "high", "description": "빠른 속도로 수영", "tips": "충분한 워밍업이 필요합니다"},
    "jump_rope": {"name": "줄넘기", "name_kr": "줄넘기", "met": 11.0, "intensity": "high", "description": "보통 속도로 줄넘기", "tips": "착지 충격에 주의하세요"},
    "basketball": {"name": "농구", "name_kr": "농구", "met": 8.0, "intensity": "high", "description": "농구 경기", "tips": "발목 부상에 주의하세요"},
    "soccer": {"name": "축구", "name_kr": "축구", "met": 9.0, "intensity": "high", "description": "축구 경기", "tips": "스트레칭 후 시작하세요"},
    "tennis": {"name": "테니스", "name_kr": "테니스", "met": 8.0, "intensity": "high", "description": "테니스 경기", "tips": "라켓 그립을 확인하세요"},
    "weight_training": {"name": "웨이트 트레이닝", "name_kr": "웨이트 트레이닝", "met": 6.0, "intensity": "high", "description": "중량 운동", "tips": "올바른 자세가 중요합니다"},
    "crossfit": {"name": "크로스핏", "name_kr": "크로스핏", "met": 12.0, "intensity": "high", "description": "고강도 인터벌 트레이닝", "tips": "체력에 맞게 조절하세요"},
    "hiit": {"name": "HIIT", "name_kr": "고강도 인터벌", "met": 10.0, "intensity": "high", "description": "고강도 인터벌 트레이닝", "tips": "회복 시간을 충분히 가지세요"},
    "boxing": {"name": "복싱", "name_kr": "복싱", "met": 9.5, "intensity": "high", "description": "복싱 훈련", "tips": "손목 보호대를 착용하세요"},
    "kickboxing": {"name": "킥복싱", "name_kr": "킥복싱", "met": 10.0, "intensity": "high", "description": "킥복싱 훈련", "tips": "기본기를 먼저 익히세요"},
    "spinning": {"name": "스피닝", "name_kr": "스피닝", "met": 9.0, "intensity": "high", "description": "실내 자전거 스피닝", "tips": "충분한 수분을 섭취하세요"},
    "rowing": {"name": "로잉머신", "name_kr": "로잉머신", "met": 8.5, "intensity": "high", "description": "로잉머신 운동", "tips": "허리를 곧게 펴세요"},
    "stair_climbing": {"name": "계단 오르기", "name_kr": "계단 오르기", "met": 9.0, "intensity": "high", "description": "계단 빠르게 오르기", "tips": "무릎 부상에 주의하세요"},
    "mountain_hiking": {"name": "등산 (고강도)", "name_kr": "고강도 등산", "met": 8.0, "intensity": "high", "description": "가파른 산 등반", "tips": "등산 스틱을 사용하세요"},
}


@dataclass
class UserProfile:
    """사용자 신체 정보"""
    weight: float  # kg
    height: float  # cm
    age: int
    gender: Literal["male", "female"]
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"] = "moderate"


@dataclass
class ExerciseResult:
    """운동 추천 결과"""
    name: str
    name_kr: str
    intensity: Literal["low", "medium", "high"]
    duration_minutes: float
    calories_burned: float
    met: float
    description: str
    tips: str


class CalorieCalculator:
    """칼로리 소모 및 운동 추천 계산기"""

    # 활동 레벨에 따른 TDEE 계수
    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,      # 거의 운동 안함
        "light": 1.375,        # 주 1-3회 가벼운 운동
        "moderate": 1.55,      # 주 3-5회 적당한 운동
        "active": 1.725,       # 주 6-7회 활발한 운동
        "very_active": 1.9     # 매우 활발한 운동 (하루 2회 등)
    }

    # EPOC (Excess Post-exercise Oxygen Consumption) 계수
    # 운동 후 추가 칼로리 소모율
    EPOC_FACTORS = {
        "low": 0.05,      # 저강도: 5% 추가
        "medium": 0.10,   # 중강도: 10% 추가
        "high": 0.15      # 고강도: 15% 추가
    }

    def __init__(self, user_profile: Optional[UserProfile] = None):
        """
        Args:
            user_profile: 사용자 프로필 (없으면 기본값 사용)
        """
        self.user_profile = user_profile or self._get_default_profile()

    def _get_default_profile(self) -> UserProfile:
        """기본 사용자 프로필"""
        return UserProfile(
            weight=65.0,
            height=170.0,
            age=30,
            gender="male",
            activity_level="moderate"
        )

    def calculate_bmr(self, profile: Optional[UserProfile] = None) -> float:
        """
        BMR (기초대사량) 계산 - Mifflin-St Jeor 공식

        남성: BMR = 10 × 체중(kg) + 6.25 × 키(cm) - 5 × 나이 + 5
        여성: BMR = 10 × 체중(kg) + 6.25 × 키(cm) - 5 × 나이 - 161

        Args:
            profile: 사용자 프로필 (기본값: 인스턴스 프로필)

        Returns:
            BMR (kcal/day)
        """
        p = profile or self.user_profile

        bmr = 10 * p.weight + 6.25 * p.height - 5 * p.age

        if p.gender == "male":
            bmr += 5
        else:
            bmr -= 161

        return round(bmr, 1)

    def calculate_tdee(self, profile: Optional[UserProfile] = None) -> float:
        """
        TDEE (총 일일 에너지 소비량) 계산

        TDEE = BMR × 활동 계수

        Args:
            profile: 사용자 프로필

        Returns:
            TDEE (kcal/day)
        """
        p = profile or self.user_profile
        bmr = self.calculate_bmr(p)
        multiplier = self.ACTIVITY_MULTIPLIERS.get(p.activity_level, 1.55)

        return round(bmr * multiplier, 1)

    def _get_epoc_factor(self, intensity: str) -> float:
        """EPOC 계수 반환"""
        return self.EPOC_FACTORS.get(intensity, 0.10)

    def calculate_calories_burned(
        self,
        exercise_key: str,
        duration_minutes: float,
        profile: Optional[UserProfile] = None
    ) -> float:
        """
        운동으로 소모되는 칼로리 계산

        칼로리 = MET × 체중(kg) × 시간(hr) × (1 + EPOC계수)

        Args:
            exercise_key: 운동 키 (MET_TABLE)
            duration_minutes: 운동 시간 (분)
            profile: 사용자 프로필

        Returns:
            소모 칼로리 (kcal)
        """
        p = profile or self.user_profile

        if exercise_key not in MET_TABLE:
            logger.warning(f"알 수 없는 운동: {exercise_key}")
            return 0

        exercise = MET_TABLE[exercise_key]
        met = exercise["met"]
        intensity = exercise["intensity"]

        # 기본 칼로리 소모
        hours = duration_minutes / 60
        base_calories = met * p.weight * hours

        # EPOC 적용
        epoc_factor = self._get_epoc_factor(intensity)
        total_calories = base_calories * (1 + epoc_factor)

        return round(total_calories, 1)

    def calculate_time_for_calories(
        self,
        target_calories: float,
        exercise_key: str,
        profile: Optional[UserProfile] = None
    ) -> float:
        """
        목표 칼로리를 소모하기 위한 운동 시간 계산

        Args:
            target_calories: 목표 칼로리 (kcal)
            exercise_key: 운동 키
            profile: 사용자 프로필

        Returns:
            필요 운동 시간 (분)
        """
        p = profile or self.user_profile

        if exercise_key not in MET_TABLE:
            return 0

        exercise = MET_TABLE[exercise_key]
        met = exercise["met"]
        intensity = exercise["intensity"]
        epoc_factor = self._get_epoc_factor(intensity)

        # 칼로리 = MET × 체중 × 시간(hr) × (1 + EPOC)
        # 시간 = 칼로리 / (MET × 체중 × (1 + EPOC))
        hours = target_calories / (met * p.weight * (1 + epoc_factor))
        minutes = hours * 60

        return round(minutes, 1)

    def recommend_exercises(
        self,
        target_calories: float,
        profile: Optional[UserProfile] = None,
        intensity_filter: Optional[Literal["low", "medium", "high"]] = None
    ) -> List[ExerciseResult]:
        """
        목표 칼로리 소모를 위한 운동 추천

        각 강도별로 2-3개씩 추천

        Args:
            target_calories: 목표 칼로리 (kcal)
            profile: 사용자 프로필
            intensity_filter: 특정 강도만 필터 (선택)

        Returns:
            운동 추천 리스트
        """
        p = profile or self.user_profile
        recommendations = []

        # 강도별 대표 운동 선택
        exercises_by_intensity = {
            "low": ["walking_moderate", "yoga_hatha", "stretching", "pilates_beginner"],
            "medium": ["walking_brisk", "cycling_leisure", "swimming_leisure", "badminton", "yoga_power"],
            "high": ["running_slow", "running_moderate", "jump_rope", "swimming_laps", "hiit", "cycling_vigorous"]
        }

        intensities = [intensity_filter] if intensity_filter else ["low", "medium", "high"]

        for intensity in intensities:
            exercise_keys = exercises_by_intensity.get(intensity, [])

            for key in exercise_keys[:3]:  # 강도당 최대 3개
                if key not in MET_TABLE:
                    continue

                exercise = MET_TABLE[key]
                duration = self.calculate_time_for_calories(target_calories, key, p)
                calories = self.calculate_calories_burned(key, duration, p)

                result = ExerciseResult(
                    name=exercise["name"],
                    name_kr=exercise["name_kr"],
                    intensity=exercise["intensity"],
                    duration_minutes=duration,
                    calories_burned=calories,
                    met=exercise["met"],
                    description=exercise["description"],
                    tips=exercise["tips"]
                )
                recommendations.append(result)

        return recommendations

    def get_exercise_by_intensity(
        self,
        target_calories: float,
        profile: Optional[UserProfile] = None
    ) -> dict:
        """
        강도별 대표 운동 1개씩 추천

        Args:
            target_calories: 목표 칼로리
            profile: 사용자 프로필

        Returns:
            {"low": ExerciseResult, "medium": ExerciseResult, "high": ExerciseResult}
        """
        p = profile or self.user_profile
        result = {}

        # 강도별 대표 운동
        representative = {
            "low": "walking_moderate",
            "medium": "cycling_leisure",
            "high": "running_slow"
        }

        for intensity, key in representative.items():
            exercise = MET_TABLE[key]
            duration = self.calculate_time_for_calories(target_calories, key, p)
            calories = self.calculate_calories_burned(key, duration, p)

            result[intensity] = ExerciseResult(
                name=exercise["name"],
                name_kr=exercise["name_kr"],
                intensity=exercise["intensity"],
                duration_minutes=duration,
                calories_burned=calories,
                met=exercise["met"],
                description=exercise["description"],
                tips=exercise["tips"]
            )

        return result


# 싱글톤 인스턴스
_calorie_calculator: Optional[CalorieCalculator] = None


def get_calorie_calculator(
    user_profile: Optional[UserProfile] = None
) -> CalorieCalculator:
    """CalorieCalculator 싱글톤 인스턴스 반환"""
    global _calorie_calculator
    if _calorie_calculator is None or user_profile:
        _calorie_calculator = CalorieCalculator(user_profile)
    return _calorie_calculator
