import joblib
import numpy as np

MODELS = {
    "COVID": "models_sklearn_v2/covid_model.joblib",
    "AFGHANISTAN": "models_sklearn_v2/afghanistan_model.joblib",
}

EXAMPLES = {
    "COVID": [
        (
            "Says of President Donald Trump's actions on the coronavirus: "
            "No. 1, he fired the pandemic team two years ago. "
            "No. 2, he's been defunding the Centers for Disease Control."
        ),
    ],
    "AFGHANISTAN": [
        "Taliban sentenced 229 Christian missionaries to death",
        (
            "We had already issued several thousand Special Immigrant Visas "
            "to the Afghan translators when I came into office."
        ),
    ],
}


def explain(model, text, top_n=10):
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]

    vector = vectorizer.transform([text])
    prediction = int(model.predict([text])[0])
    scores = model.predict_proba([text])[0]

    # For this binary classifier, positive contributions favor REAL,
    # while negative contributions favor FAKE.
    coefficients = classifier.coef_[0]
    feature_names = vectorizer.get_feature_names_out()

    contributions = vector.multiply(coefficients).toarray()[0]
    active_indices = np.flatnonzero(vector.toarray()[0])

    active_indices = sorted(
        active_indices,
        key=lambda i: abs(contributions[i]),
        reverse=True,
    )

    print("\nText:", text)
    print("Prediction:", "REAL" if prediction == 1 else "FAKE")
    print(f"FAKE score: {scores[0]:.4f}")
    print(f"REAL score: {scores[1]:.4f}")

    print("\nFeatures pushing toward REAL:")
    real_features = [
        i for i in active_indices if contributions[i] > 0
    ][:top_n]

    for i in real_features:
        print(
            f"  {feature_names[i]:35s} "
            f"{contributions[i]:+.4f}"
        )

    print("\nFeatures pushing toward FAKE:")
    fake_features = [
        i for i in active_indices if contributions[i] < 0
    ][:top_n]

    for i in fake_features:
        print(
            f"  {feature_names[i]:35s} "
            f"{contributions[i]:+.4f}"
        )


for name, path in MODELS.items():
    print("\n" + "=" * 75)
    print(name, "PREDICTION EXPLANATIONS")
    print("=" * 75)

    model = joblib.load(path)

    for example in EXAMPLES[name]:
        explain(model, example)
