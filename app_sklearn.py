from pathlib import Path

import joblib
import streamlit as st


st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="centered",
)

MODEL_DIR = Path(__file__).parent / "models_sklearn"


@st.cache_resource
def load_model(model_name):
    model_path = MODEL_DIR / model_name
    return joblib.load(model_path)


st.title("📰 Fake News Detection")
st.write(
    "Analyze a news headline or article using a machine-learning "
    "text classifier."
)

st.warning(
    "This tool estimates whether text resembles the FAKE or REAL "
    "examples in its training dataset. It does not independently "
    "verify facts or guarantee that an article is true."
)

model_choice = st.selectbox(
    "Choose a detection model",
    ["COVID-19 News", "Afghanistan News"],
)

model_files = {
    "COVID-19 News": "covid_model.joblib",
    "Afghanistan News": "afghanistan_model.joblib",
}

news_text = st.text_area(
    "Enter a news headline or article",
    height=220,
    placeholder="Paste your news text here...",
)

if st.button("Analyze News", type="primary"):
    if not news_text.strip():
        st.error("Please enter a headline or article first.")
    else:
        try:
            model = load_model(model_files[model_choice])

            prediction = int(model.predict([news_text.strip()])[0])
            probabilities = model.predict_proba([news_text.strip()])[0]

            classes = list(model.classes_)
            scores = dict(zip(classes, probabilities))

            label = "FAKE" if prediction == 0 else "REAL"

            if label == "FAKE":
                st.error("Prediction: FAKE NEWS")
            else:
                st.success("Prediction: REAL NEWS")

            st.subheader("Model scores")

            st.write(
                f"FAKE: {scores.get(0, 0.0) * 100:.2f}%"
            )
            st.progress(float(scores.get(0, 0.0)))

            st.write(
                f"REAL: {scores.get(1, 0.0) * 100:.2f}%"
            )
            st.progress(float(scores.get(1, 0.0)))

            st.caption(
                "These are model scores, not verified probabilities "
                "that the claims are false or true."
            )

        except Exception as exc:
            st.error(f"Could not analyze the text: {exc}")

st.divider()
st.caption("Local machine-learning demonstration")
