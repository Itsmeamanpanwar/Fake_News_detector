import pandas as pd

DATASETS = {
    "COVID": "Datasets/COVID Fake News Data.csv",
    "AFGHANISTAN": "Datasets/afpfake.csv",
}

SEARCH_TERMS = {
    "COVID": ["corona", "coronavirus", "google", "2019-ncov", "cure"],
    "AFGHANISTAN": ["taliban", "video", "photo", "circulated"],
}

for name, path in DATASETS.items():
    print("\n" + "=" * 80)
    print(name, "DATASET")
    print("=" * 80)

    df = pd.read_csv(path)
    df = df.dropna(subset=["headlines", "outcome"]).copy()

    df["headlines"] = df["headlines"].astype(str).str.strip()
    df["outcome"] = pd.to_numeric(df["outcome"], errors="coerce")
    df = df.dropna(subset=["outcome"])
    df = df[df["outcome"].isin([0, 1])]

    df["label"] = df["outcome"].map({0: "FAKE", 1: "REAL"})

    print("\nRows by label:")
    print(df["label"].value_counts())

    for term in SEARCH_TERMS[name]:
        matches = df[
            df["headlines"].str.contains(term, case=False, regex=False)
        ]

        print(f"\n--- Term: {term!r} | Matches: {len(matches)} ---")

        if matches.empty:
            print("No matching examples.")
            continue

        print("Label counts:")
        print(matches["label"].value_counts().to_string())

        print("\nSample headlines:")
        for _, row in matches.head(8).iterrows():
            print(f"[{row['label']}] {row['headlines']}")

    print("\n--- Exact duplicate headlines with conflicting labels ---")

    conflicts = (
        df.groupby("headlines")["label"]
        .nunique()
    )

    conflict_texts = conflicts[conflicts > 1].index

    if len(conflict_texts) == 0:
        print("No exact conflicting-label duplicates found.")
    else:
        print(f"Found {len(conflict_texts)} conflicting headlines.")

        for headline in list(conflict_texts[:10]):
            print(f"\nHeadline: {headline}")
            print(
                df.loc[
                    df["headlines"] == headline,
                    ["label", "outcome"]
                ].to_string(index=False)
            )
