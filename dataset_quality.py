import pandas as pd

DATASETS = {
    "COVID": "Datasets/COVID Fake News Data.csv",
    "AFGHANISTAN": "Datasets/afpfake.csv",
}

for name, path in DATASETS.items():
    print("\n" + "=" * 70)
    print(name, "DATA QUALITY REPORT")
    print("=" * 70)

    df = pd.read_csv(path)
    df = df.dropna(subset=["headlines", "outcome"]).copy()

    df["headlines"] = df["headlines"].astype(str).str.strip()
    df["outcome"] = pd.to_numeric(df["outcome"], errors="coerce")
    df = df.dropna(subset=["outcome"])
    df = df[df["outcome"].isin([0, 1])]

    df["label"] = df["outcome"].map({0: "FAKE", 1: "REAL"})

    print("\n1. Label distribution")
    print(df["label"].value_counts().to_string())

    print("\n2. Exact duplicate headlines")
    duplicate_mask = df["headlines"].duplicated(keep=False)
    duplicates = df[duplicate_mask]

    print("Rows participating in duplicates:", len(duplicates))

    if not duplicates.empty:
        print(
            duplicates.groupby("headlines")["label"]
            .nunique()
            .value_counts()
            .rename("Number of headline groups")
            .to_string()
        )

    print("\n3. Headlines appearing under both labels")
    label_counts = df.groupby("headlines")["label"].nunique()
    conflicting = label_counts[label_counts > 1].index

    print("Number of conflicting headlines:", len(conflicting))

    for headline in list(conflicting[:5]):
        print("\nHeadline:", headline)
        print(
            df.loc[
                df["headlines"] == headline,
                ["label", "outcome"]
            ].to_string(index=False)
        )

    print("\n4. Sample REAL headlines")
    for headline in df.loc[df["label"] == "REAL", "headlines"].head(5):
        print("-", headline)

    print("\n5. Sample FAKE headlines")
    for headline in df.loc[df["label"] == "FAKE", "headlines"].head(5):
        print("-", headline)
