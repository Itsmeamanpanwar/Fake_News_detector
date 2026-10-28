import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


DATASETS = {
    "COVID": {
        "csv": "Datasets/COVID Fake News Data.csv",
        "model": "models_sklearn_v2/covid_model.joblib",
    },
    "AFGHANISTAN": {
        "csv": "Datasets/afpfake.csv",
        "model": "models_sklearn_v2/afghanistan_model.joblib",
    },
}


for name, config in DATASETS.items():
    print("\n" + "=" * 75)
    print(name, "ERROR ANALYSIS")
    print("=" * 75)

    df = pd.read_csv(config["csv"], encoding="utf-8")
    df = df.dropna(subset=["headlines", "outcome"]).copy()

    df["headlines"] = df["headlines"].astype(str).str.strip()
    df["outcome"] = pd.to_numeric(df["outcome"], errors="coerce")

    df = df.dropna(subset=["outcome"])
    df = df[df["headlines"] != ""]
    df = df[df["outcome"].isin([0, 1])]

    # Match the training script's deduplication and split.
    label_counts = df.groupby("headlines")["outcome"].nunique()
    conflicts = label_counts[label_counts > 1]

    if len(conflicts):
        print("Conflicting labels found; skipping this dataset.")
        continue

    df = df.drop_duplicates(subset=["headlines"], keep="first")

    X = df["headlines"]
    y = df["outcome"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(config["model"])

    predictions = model.predict(X_test)

    results = pd.DataFrame({
        "headline": X_test.values,
        "actual": y_test.values,
        "predicted": predictions,
    })

    results["actual_label"] = results["actual"].map({
        0: "FAKE",
        1: "REAL",
    })

    results["predicted_label"] = results["predicted"].map({
        0: "FAKE",
        1: "REAL",
    })

    errors = results[results["actual"] != results["predicted"]]

    print("Test examples:", len(results))
    print("Incorrect predictions:", len(errors))

    print("\nClassification report:")
    print(classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["FAKE", "REAL"],
        zero_division=0,
    ))

    for category in ["REAL", "FAKE"]:
        print(f"\n--- Actual {category} predicted incorrectly ---")

        wrong = errors[errors["actual_label"] == category]

        if wrong.empty:
            print("No errors in this category.")
            continue

        for _, row in wrong.head(10).iterrows():
            print(f"\nActual: {row['actual_label']}")
            print(f"Predicted: {row['predicted_label']}")
            print(f"Headline: {row['headline']}")

    output_path = Path(f"{name.lower()}_errors.csv")
    errors.to_csv(output_path, index=False, encoding="utf-8")

    print("\nSaved incorrect predictions to:", output_path)
