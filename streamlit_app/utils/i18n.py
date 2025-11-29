"""다국어 지원 (한국어/영어)"""

import streamlit as st

# 번역 데이터
TRANSLATIONS = {
    "ko": {
        # 앱 이름
        "app_name": "AI K-Food",
        "app_subtitle": "한국 음식 레시피 & 피트니스 어드바이저",

        # 메인 페이지
        "main_title": "어떤 한국 음식이 궁금하신가요?",
        "search_placeholder": "요리 이름으로 검색해보세요 (예: 불고기, 비빔밥)",
        "search_button": "검색",
        "searching": "검색 중...",

        # 검색 결과
        "search_results": "검색 결과",
        "no_results": "검색 결과가 없습니다. 다른 검색어를 시도해보세요.",
        "sort_by": "정렬",
        "sort_latest": "최신순",
        "sort_cal_low": "칼로리 낮은순",
        "sort_cal_high": "칼로리 높은순",

        # 레시피 카드
        "view_recipe": "레시피 보기",
        "recipe_detail": "레시피 상세",
        "ingredients": "재료",
        "instructions": "조리 순서",
        "cooking_tips": "조리 팁",
        "no_ingredients": "재료 정보가 없습니다.",
        "no_instructions": "조리 순서 정보가 없습니다.",
        "calories": "칼로리",
        "cooking_time": "조리 시간",
        "difficulty": "난이도",
        "easy": "쉬움",
        "medium": "보통",
        "hard": "어려움",

        # 영양정보
        "nutrition_info": "영양정보",
        "nutrition_title": "영양 정보",
        "total_calories": "총 칼로리 (1인분)",
        "expected_cooking_time": "예상 조리 시간",
        "main_nutrients": "주요 영양소 구성",
        "daily_value": "일일 권장량 대비",
        "detailed_nutrition": "상세 영양 성분표",
        "serving_size": "1회 제공량 (300g) 기준",
        "compare_nutrition": "영양 정보 비교하기",
        "compare_desc": "다른 음식과 영양 정보를 비교해보세요.",
        "carbohydrate": "탄수화물",
        "protein": "단백질",
        "fat": "지방",
        "sodium": "나트륨",
        "sugar": "당류",
        "saturated_fat": "포화지방",
        "cholesterol": "콜레스테롤",
        "trans_fat": "트랜스지방",

        # 운동 추천
        "exercise_info": "운동정보",
        "exercise_title": "운동 추천",
        "intake_calories": "섭취 칼로리",
        "exercise_recommendation": "이 칼로리를 소모하기 위한 운동을 추천해드립니다.",
        "recommended_exercises": "추천 운동",
        "exercise_desc": "아래 운동 중 하나를 선택하여 섭취한 칼로리를 소모하세요.",
        "exercise_comparison": "운동 비교",
        "exercise_tips": "건강한 운동 팁",
        "time": "시간",
        "burn": "소모",
        "low_intensity": "저강도",
        "medium_intensity": "중강도",
        "high_intensity": "고강도",

        # 팁
        "tip_hydration": "수분 섭취",
        "tip_hydration_desc": "운동 전후로 충분한 물을 마셔주세요. 하루 2L 이상 권장합니다.",
        "tip_after_meal": "식후 운동",
        "tip_after_meal_desc": "식사 후 최소 1-2시간 후에 운동하는 것이 좋습니다.",
        "tip_stretching": "스트레칭",
        "tip_stretching_desc": "운동 전후 5-10분 스트레칭으로 부상을 예방하세요.",

        # 버튼
        "go_to_recipe_search": "레시피 검색으로 이동",
        "view_nutrition": "영양정보 보기",
        "view_exercise": "운동정보 보기",
        "add_favorite": "즐겨찾기",
        "added_to_favorite": "즐겨찾기에 추가되었습니다!",

        # 안내 메시지
        "search_first": "레시피를 먼저 검색해주세요.",

        # 푸터
        "footer_copyright": "© 2024 AI K-Food. All rights reserved.",
        "footer_links": "이용약관 | 개인정보 처리방침 | 문의하기",

        # 네비게이션
        "breadcrumb_home": "홈",
        "breadcrumb_recipe": "레시피 검색",
        "breadcrumb_nutrition": "영양 정보",
        "breadcrumb_exercise": "운동 추천",

        # 언어
        "language": "언어",
        "korean": "한국어",
        "english": "English",

        # 네비게이션 메뉴
        "nav_home": "홈",
        "nav_recipe": "레시피 검색",
        "nav_profile": "내 프로필",
        "nav_dashboard": "종합 정보",

        # 종합 페이지
        "dashboard_title": "완벽한 균형",
        "dashboard_subtitle": "선택한 요리에 대한 영양 정보 및 맞춤 운동 추천을 포함한 전체 개요입니다.",
        "ai_summary": "AI 요약",
        "ai_summary_text": "고단백 {food}은 운동 후 식사로 좋습니다. 회복을 돕기 위해 추천된 스트레칭 운동을 시도해보세요. 이 식사는 일일 칼로리 목표에 잘 맞습니다.",
        "main_dish": "메인 요리",
        "rating": "평점",
        "rating_suffix": "점",
        "start_cooking": "요리",
        "view_recipe_detail": "레시피 상세 보기",
        "calorie_balance": "칼로리 밸런스",
        "food_intake": "식사 섭취량",
        "exercise_burn": "운동 소모량",
        "total_calories_label": "총 칼로리",
        "minutes": "분",
        "jogging": "조깅",
        "hiit": "고강도 인터벌",
        "stretching": "스트레칭",
        "tag_spicy": "#매운맛",
        "tag_vegetarian": "#채식",
        "tag_easy": "#간편식"
    },
    "en": {
        # App name
        "app_name": "AI K-Food",
        "app_subtitle": "Korean Recipe & Fitness Advisor",

        # Main page
        "main_title": "What Korean food are you curious about?",
        "search_placeholder": "Search by dish name (e.g., Bulgogi, Bibimbap)",
        "search_button": "Search",
        "searching": "Searching...",

        # Search results
        "search_results": "Search Results",
        "no_results": "No results found. Try a different search term.",
        "sort_by": "Sort",
        "sort_latest": "Latest",
        "sort_cal_low": "Lowest Calories",
        "sort_cal_high": "Highest Calories",

        # Recipe card
        "view_recipe": "View Recipe",
        "recipe_detail": "Recipe Details",
        "ingredients": "Ingredients",
        "instructions": "Instructions",
        "cooking_tips": "Cooking Tips",
        "no_ingredients": "No ingredient information available.",
        "no_instructions": "No instruction information available.",
        "calories": "Calories",
        "cooking_time": "Cooking Time",
        "difficulty": "Difficulty",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",

        # Nutrition info
        "nutrition_info": "Nutrition",
        "nutrition_title": "Nutrition Information",
        "total_calories": "Total Calories (per serving)",
        "expected_cooking_time": "Expected Cooking Time",
        "main_nutrients": "Main Nutrient Composition",
        "daily_value": "% Daily Value",
        "detailed_nutrition": "Detailed Nutrition Facts",
        "serving_size": "Per serving (300g)",
        "compare_nutrition": "Compare Nutrition",
        "compare_desc": "Compare nutrition information with other foods.",
        "carbohydrate": "Carbohydrate",
        "protein": "Protein",
        "fat": "Fat",
        "sodium": "Sodium",
        "sugar": "Sugar",
        "saturated_fat": "Saturated Fat",
        "cholesterol": "Cholesterol",
        "trans_fat": "Trans Fat",

        # Exercise recommendation
        "exercise_info": "Exercise",
        "exercise_title": "Exercise Recommendations",
        "intake_calories": "Calories Consumed",
        "exercise_recommendation": "We recommend these exercises to burn off the calories.",
        "recommended_exercises": "Recommended Exercises",
        "exercise_desc": "Choose one of the exercises below to burn the consumed calories.",
        "exercise_comparison": "Exercise Comparison",
        "exercise_tips": "Healthy Exercise Tips",
        "time": "Time",
        "burn": "Burn",
        "low_intensity": "Low",
        "medium_intensity": "Medium",
        "high_intensity": "High",

        # Tips
        "tip_hydration": "Stay Hydrated",
        "tip_hydration_desc": "Drink plenty of water before and after exercise. 2L+ daily recommended.",
        "tip_after_meal": "Post-meal Exercise",
        "tip_after_meal_desc": "Wait at least 1-2 hours after eating before exercising.",
        "tip_stretching": "Stretching",
        "tip_stretching_desc": "Do 5-10 minutes of stretching before and after exercise to prevent injury.",

        # Buttons
        "go_to_recipe_search": "Go to Recipe Search",
        "view_nutrition": "View Nutrition",
        "view_exercise": "View Exercise",
        "add_favorite": "Add to Favorites",
        "added_to_favorite": "Added to favorites!",

        # Messages
        "search_first": "Please search for a recipe first.",

        # Footer
        "footer_copyright": "© 2024 AI K-Food. All rights reserved.",
        "footer_links": "Terms | Privacy Policy | Contact",

        # Navigation
        "breadcrumb_home": "Home",
        "breadcrumb_recipe": "Recipe Search",
        "breadcrumb_nutrition": "Nutrition Info",
        "breadcrumb_exercise": "Exercise Recommendation",

        # Language
        "language": "Language",
        "korean": "한국어",
        "english": "English",

        # Navigation menu
        "nav_home": "Home",
        "nav_recipe": "Recipe Search",
        "nav_profile": "My Profile",
        "nav_dashboard": "Dashboard",

        # Dashboard page
        "dashboard_title": "Perfect Balance",
        "dashboard_subtitle": "Complete overview including nutrition info and personalized exercise recommendations for your selected dish.",
        "ai_summary": "AI Summary",
        "ai_summary_text": "High-protein {food} is great for post-workout meals. Try the recommended stretching exercises to aid recovery. This meal fits well with your daily calorie goals.",
        "main_dish": "Main Dish",
        "rating": "Rating",
        "rating_suffix": "",
        "start_cooking": "Cook",
        "view_recipe_detail": "View Recipe Details",
        "calorie_balance": "Calorie Balance",
        "food_intake": "Food Intake",
        "exercise_burn": "Exercise Burn",
        "total_calories_label": "Total Calories",
        "minutes": "min",
        "jogging": "Jogging",
        "hiit": "HIIT",
        "stretching": "Stretching",
        "tag_spicy": "#Spicy",
        "tag_vegetarian": "#Vegetarian",
        "tag_easy": "#Easy"
    }
}


def get_lang() -> str:
    """현재 언어 설정 반환"""
    return st.session_state.get("language", "ko")


def set_lang(lang: str):
    """언어 설정 변경"""
    st.session_state.language = lang


def t(key: str) -> str:
    """번역 텍스트 반환"""
    lang = get_lang()
    return TRANSLATIONS.get(lang, TRANSLATIONS["ko"]).get(key, key)


def render_language_selector():
    """언어 선택 위젯 렌더링"""
    col1, col2 = st.columns([6, 1])
    with col2:
        current_lang = get_lang()
        lang_options = {"ko": "🇰🇷 한국어", "en": "🇺🇸 English"}
        selected = st.selectbox(
            t("language"),
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=0 if current_lang == "ko" else 1,
            key="lang_selector",
            label_visibility="collapsed"
        )
        if selected != current_lang:
            set_lang(selected)
            st.rerun()
