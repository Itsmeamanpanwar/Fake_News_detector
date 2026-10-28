import pandas as pd
import joblib

from sklearn.model_selection import train_test_split

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
    print(name, "CONFIDENCE ANALYSIS")
    print("=" * 75)

    df = pd.read_csv(config["csv"], encoding="utf-8")
    df = df.dropna(subset=["headlines", "outcome"]).copy()

    df["headlines"] = df["headlines"].astype(str).str.strip()
    df["outcome"] = pd.to_numeric(df["outcome"], errors="coerce")

    df = df.dropna(subset=["outcome"])
    df = df[df["headlines"] != ""]
    df = df[df["outcome"].isin([0, 1])]

    conflicts = df.groupby("headlines")["outcome"].nunique()
    if (conflicts > 1).any():
        print("Conflicting labels found; skipping dataset.")
        continue

    df = df.drop_duplicates(subset=["headlines"], keep="first")

    X = df["headlines"]
    y = df["outcome"].astype(int)

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(config["model"])
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    # Column 0 corresponds to FAKE; column 1 corresponds to REAL.
    results = pd.DataFrame({
        "headline": X_test.values,
        "actual": y_test.values,
        "predicted": predictions,
        "fake_score": probabilities[:, 0],
        "real_score": probabilities[:, 1],
    })

    results["actual_label"] = results["actual"].map({
        0: "FAKE",
        1: "REAL",
    })

    results["predicted_label"] = results["predicted"].map({
        0: "FAKE",
        1: "REAL",
    })

    errors = results[results["actual"] != results["predicted"]].copy()

    # Confidence here means the model's score for its predicted class.
    errors["predicted_score"] = errors.apply(
        lambda row: row["fake_score"]
        if row["predicted"] == 0
        else row["real_score"],
        axis=1,
    )

    errors = errors.sort_values("predicted_score", ascending=False)

    print("Test examples:", len(results))
    print("Incorrect predictions:", len(errors))

    print("\n10 most confident incorrect predictions:")
    for _, row in errors.head(10).iterrows():
        print("\nActual:", row["actual_label"])
        print("Predicted:", row["predicted_label"])
        print("Predicted-class score:", round(row["predicted_score"], 4))
        print("Headline:", row["headline"])

    output_path = f"{name.lower()}_confidence_errors.csv"
    errors.to_csv(output_path, index=False, encoding="utf-8")
    print("\nSaved:", output_path)
