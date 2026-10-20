import streamlit as st

FT_TO_M = 0.3048
LB_TO_KG = 0.45359237

CATEGORIES = [
    (18.5, "Underweight", "#3b82f6"),
    (25.0, "Normal weight", "#16a34a"),
    (30.0, "Overweight", "#f59e0b"),
    (float("inf"), "Obese", "#dc2626"),
]


def to_meters(height: float, unit: str) -> float:
    return height * FT_TO_M if unit == "feet" else height


def to_kg(weight: float, unit: str) -> float:
    return weight * LB_TO_KG if unit == "lbs" else weight


def compute_bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / height_m ** 2


def classify(bmi: float):
    for upper, label, color in CATEGORIES:
        if bmi < upper:
            return label, color


st.set_page_config(page_title="BMI Calculator", layout="centered")
st.title("Body Mass Index Calculator")
st.write("Enter your height and weight in either unit system.")

col1, col2 = st.columns(2)
with col1:
    h_unit = st.radio("Height unit", ["feet", "meters"], horizontal=True)
    h_default, h_step = (5.5, 0.1) if h_unit == "feet" else (1.68, 0.01)
    height = st.number_input(f"Height ({h_unit})", min_value=0.0,
                             value=h_default, step=h_step, format="%.2f")
with col2:
    w_unit = st.radio("Weight unit", ["lbs", "kilograms"], horizontal=True)
    w_default = 150.0 if w_unit == "lbs" else 68.0
    weight = st.number_input(f"Weight ({w_unit})", min_value=0.0,
                             value=w_default, step=1.0, format="%.1f")

if height <= 0 or weight <= 0:
    st.warning("Height and weight must both be greater than zero.")
else:
    h_m = to_meters(height, h_unit)
    w_kg = to_kg(weight, w_unit)
    bmi = compute_bmi(w_kg, h_m)
    label, color = classify(bmi)

    st.markdown(
        f"""
        <div style="margin-top:1rem;padding:1.25rem;border-radius:12px;
                    background:{color}1a;border:2px solid {color};text-align:center">
            <div style="font-size:1rem;color:#555">Your BMI</div>
            <div style="font-size:3rem;font-weight:700;color:{color}">{bmi:.1f}</div>
            <div style="font-size:1.25rem;font-weight:600;color:{color}">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Computed as {w_kg:.1f} kg / ({h_m:.2f} m)² — "
               "BMI = weight (kg) / height (m)²")

with st.expander("BMI categories (WHO)"):
    st.markdown(
        "- **Underweight:** below 18.5\n"
        "- **Normal weight:** 18.5 – 24.9\n"
        "- **Overweight:** 25.0 – 29.9\n"
        "- **Obese:** 30.0 and above"
    )