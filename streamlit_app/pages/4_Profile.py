import streamlit as st
import sys
from pathlib import Path

# Project Root Setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(STREAMLIT_APP))

from utils.style import load_css

st.set_page_config(page_title="My Profile", page_icon="👤", layout="wide")
load_css()

def main():
    st.markdown('<h1 class="main-header">My Profile</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage your physical stats for better recommendations.</p>', unsafe_allow_html=True)

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "weight": 70.0,
            "height": 170.0,
            "age": 30,
            "gender": "male",
            "activity_level": "moderate"
        }
    
    profile = st.session_state.user_profile

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            new_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(profile["weight"]), step=0.5)
            new_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(profile["height"]), step=0.5)
            new_age = st.number_input("Age", min_value=10, max_value=100, value=int(profile["age"]), step=1)
        
        with col2:
            gender_options = ["male", "female"]
            new_gender = st.selectbox("Gender", options=gender_options, index=gender_options.index(profile["gender"]))
            
            activity_options = ["sedentary", "light", "moderate", "active", "very_active"]
            new_activity = st.selectbox("Activity Level", options=activity_options, index=activity_options.index(profile["activity_level"]))
            
        if st.button("Save Profile", type="primary"):
            st.session_state.user_profile = {
                "weight": new_weight,
                "height": new_height,
                "age": new_age,
                "gender": new_gender,
                "activity_level": new_activity
            }
            st.success("Profile updated successfully!")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # BMI Calculator
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Your BMI Analysis")
    
    height_m = new_height / 100
    bmi = new_weight / (height_m ** 2)
    
    col_bmi1, col_bmi2 = st.columns([1, 3])
    with col_bmi1:
        st.metric("BMI", f"{bmi:.1f}")
    
    with col_bmi2:
        if bmi < 18.5:
            st.info("Underweight")
        elif bmi < 25:
            st.success("Normal weight")
        elif bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
            
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
