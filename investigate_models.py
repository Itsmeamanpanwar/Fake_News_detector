import joblib
import numpy as np

MODELS = {
    "COVID": "models_sklearn/covid_model.joblib",
    "AFGHANISTAN": "models_sklearn/afghanistan_model.joblib",
}

for name, path in MODELS.items():
    print("\n" + "=" * 70)
    print(name, "MODEL")
    print("=" * 70)

    model = joblib.load(path)

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]

    feature_names = vectorizer.get_feature_names_out()
    coefficients = classifier.coef_[0]

    # Positive coefficients favor label 1 (REAL).
    # Negative coefficients favor label 0 (FAKE).
    fake_indices = np.argsort(coefficients)[:20]
    real_indices = np.argsort(coefficients)[-20:][::-1]

    print("\nWords/features associated with FAKE:")
    for i in fake_indices:
        print(f"{feature_names[i]:35s} {coefficients[i]: .4f}")

    print("\nWords/features associated with REAL:")
    for i in real_indices:
        print(f"{feature_names[i]:35s} {coefficients[i]: .4f}")

    print("\nNote: These are learned associations, not proof of causation.")
