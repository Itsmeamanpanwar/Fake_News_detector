import pandas as pd

files = [
    "Datasets/afpfake.csv",
    "Datasets/COVID Fake News Data.csv"
]

for file in files:
    print("\n" + "=" * 60)
    print("DATASET:", file)

    df = pd.read_csv(file, encoding="utf-8")

    print("Shape:", df.shape)
    print("Label counts:")
    print(df["outcome"].value_counts(dropna=False).to_string())

    print("\nFirst 5 headlines (shortened):")
    for i in range(min(5, len(df))):
        headline = repr(str(df.iloc[i]["headlines"])[:150])
        label = repr(df.iloc[i]["outcome"])
        print("Row", i, "| Label:", label, "| Headline:", headline)

    print("\nUnique labels:", df["outcome"].unique().tolist())
