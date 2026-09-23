import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Fertilizer Recommendation Dashboard", layout="wide")
st.title("🌱 Fertilizer Recommendation Dashboard")
st.write("Enter your field's soil and crop conditions to get a fertilizer recommendation.")
@st.cache_resource
def load_models():
    model = joblib.load('fertilizer_model_v2.pkl')
    dosage_model = joblib.load('dosage_model.pkl')
    le_soil = joblib.load('soil_encoder.pkl')
    le_crop = joblib.load('crop_encoder_v2.pkl')
    le_fert = joblib.load('fertilizer_encoder_v2.pkl')
    return model, dosage_model, le_soil, le_crop, le_fert

model, dosage_model, le_soil, le_crop, le_fert = load_models()

feature_cols = ['Temparature', 'Humidity ', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorous', 'soil_encoded', 'crop_encoded2']
st.sidebar.header("Field Conditions")

soil_type = st.sidebar.selectbox("Soil Type", options=list(le_soil.classes_))
crop_type = st.sidebar.selectbox("Crop Type", options=list(le_crop.classes_))
temperature = st.sidebar.slider("Temperature (°C)", 0, 50, 25)
humidity = st.sidebar.slider("Humidity (%)", 0, 100, 50)
moisture = st.sidebar.slider("Moisture (%)", 0, 100, 40)
nitrogen = st.sidebar.number_input("Nitrogen level", min_value=0, max_value=150, value=30)
potassium = st.sidebar.number_input("Potassium level", min_value=0, max_value=150, value=10)
phosphorous = st.sidebar.number_input("Phosphorous level", min_value=0, max_value=150, value=10)

predict_button = st.sidebar.button("Get Recommendation", type="primary")
if predict_button:
    soil_encoded = le_soil.transform([soil_type])[0]
    crop_encoded = le_crop.transform([crop_type])[0]

    input_data = pd.DataFrame(
        [[temperature, humidity, moisture, nitrogen, potassium, phosphorous, soil_encoded, crop_encoded]],
        columns=feature_cols
    )

    proba = model.predict_proba(input_data)[0]
    top_idx = proba.argmax()
    top_fertilizer = le_fert.classes_[top_idx]
    top_confidence = proba[top_idx]

    st.subheader("Recommendation")
    col1, col2 = st.columns(2)
    col1.metric("Recommended Fertilizer", top_fertilizer)
    col2.metric("Confidence", f"{top_confidence:.1%}")

    if top_confidence < 0.6:
        st.warning("⚠️ Low confidence — consider a manual soil test before applying.")
        st.subheader("Alternative Options")
    top3_idx = proba.argsort()[::-1][:3]
    alt_df = pd.DataFrame({
        'Fertilizer': [le_fert.classes_[i] for i in top3_idx],
        'Probability': [f"{proba[i]:.1%}" for i in top3_idx]
    })
    st.table(alt_df)
    st.subheader("Estimated Dosage")
    dosage_input = pd.DataFrame(
        [[temperature, humidity, moisture, nitrogen, potassium, phosphorous, soil_encoded, crop_encoded, top_idx]],
        columns=feature_cols + ['fertilizer_encoded2']
    )
    estimated_dosage = dosage_model.predict(dosage_input)[0]
    st.metric("Recommended Dosage", f"{estimated_dosage:.1f} kg/hectare")
    st.subheader("Cost & Sustainability Comparison")

    fertilizer_profile = {
        'Urea':      {'price_per_kg': 6,  'env_impact': 7},
        'DAP':       {'price_per_kg': 27, 'env_impact': 6},
        'MOP':       {'price_per_kg': 17, 'env_impact': 4},
        '14-35-14':  {'price_per_kg': 30, 'env_impact': 5},
        '28-28':     {'price_per_kg': 24, 'env_impact': 6},
        '17-17-17':  {'price_per_kg': 28, 'env_impact': 4},
        '20-20':     {'price_per_kg': 22, 'env_impact': 6},
        '10-26-26':  {'price_per_kg': 26, 'env_impact': 5},
    }

    comparison_data = []
    for i in top3_idx:
        fert_name = le_fert.classes_[i]
        profile = fertilizer_profile[fert_name]
        comparison_data.append({
            'Fertilizer': fert_name,
            'ML Confidence': f"{proba[i]:.1%}",
            'Price (₹/kg)': profile['price_per_kg'],
            'Env. Impact (1-10)': profile['env_impact']
        })

    st.table(pd.DataFrame(comparison_data))
    