from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


DATASETS = {
    "covid": "Datasets/COVID Fake News Data.csv",
    "afghanistan": "Datasets/afpfake.csv",
}

# Keep the existing models intact.
MODEL_DIR = Path("models_sklearn_v2")
MODEL_DIR.mkdir(exist_ok=True)

# Verified against the original training notebooks.
# outcome 0 = FAKE
# outcome 1 = REAL
LABEL_NAMES = ["FAKE", "REAL"]


def train_model(name, csv_path):
    print("\n" + "=" * 70)
    print("TRAINING:", name.upper())
    print("=" * 70)

    df = pd.read_csv(csv_path, encoding="utf-8")

    required_columns = {"headlines", "outcome"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"{csv_path} must contain columns: {sorted(required_columns)}"
        )

    # Validate and clean rows.
    df = df.dropna(subset=["headlines", "outcome"]).copy()
    df["headlines"] = df["headlines"].astype(str).str.strip()
    df["outcome"] = pd.to_numeric(df["outcome"], errors="coerce")

    df = df.dropna(subset=["outcome"])
    df = df[df["headlines"] != ""]
    df = df[df["outcome"].isin([0, 1])]

    # Remove exact duplicate headlines BEFORE splitting.
    # Conflicting labels must be investigated rather than silently resolved.
    label_counts = df.groupby("headlines")["outcome"].nunique()
    conflicting = label_counts[label_counts > 1]

    if len(conflicting):
        raise ValueError(
            f"{name}: found {len(conflicting)} headlines with conflicting "
            "labels. Inspect these records before training."
        )

    original_rows = len(df)
    df = df.drop_duplicates(subset=["headlines"], keep="first")

    print("Rows before deduplication:", original_rows)
    print("Unique headlines retained:", len(df))
    print("Duplicate rows removed:", original_rows - len(df))

    X = df["headlines"]
    y = df["outcome"].astype(int)

    if y.nunique() != 2:
        raise ValueError(f"{name} must contain both classes, 0 and 1.")

    print("\nClass distribution:")
    print(y.map({0: "FAKE", 1: "REAL"}).value_counts().to_string())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("\nTraining examples:", len(X_train))
    print("Testing examples:", len(X_test))

    # Baseline: always predict the most common training label.
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(X_train.to_frame(), y_train)
    baseline_predictions = baseline.predict(X_test.to_frame())

    print("\n--- Majority-class baseline ---")
    print("Accuracy:", round(accuracy_score(y_test, baseline_predictions), 4))
    print(
        "Macro F1:",
        round(
            f1_score(
                y_test,
                baseline_predictions,
                labels=[0, 1],
                average="macro",
                zero_division=0,
            ),
            4,
        ),
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                max_features=50000,
                sublinear_tf=True,
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    print("\nTraining TF-IDF + Logistic Regression...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\n--- Model evaluation ---")
    print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
    print(
        "Macro F1:",
        round(
            f1_score(
                y_test,
                predictions,
                labels=[0, 1],
                average="macro",
                zero_division=0,
            ),
            4,
        ),
    )

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1],
            target_names=LABEL_NAMES,
            zero_division=0,
        )
    )

    print("Confusion matrix (rows=actual, columns=predicted)")
    print("Order: FAKE, REAL")
    print(confusion_matrix(y_test, predictions, labels=[0, 1]))

    output_path = MODEL_DIR / f"{name}_model.joblib"
    joblib.dump(model, output_path)

    print("\nSaved model to:", output_path)


if __name__ == "__main__":
    for name, csv_path in DATASETS.items():
        train_model(name, csv_path)

    print("\nBoth training jobs completed.")
