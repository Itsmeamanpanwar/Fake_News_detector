import pandas as pd

path = "Datasets/COVID Fake News Data.csv"

df = pd.read_csv(path)
df = df.dropna(subset=["headlines", "outcome"]).copy()

df["headlines"] = df["headlines"].astype(str).str.strip()
df["outcome"] = pd.to_numeric(df["outcome"], errors="coerce")
df = df.dropna(subset=["outcome"])
df = df[df["outcome"].isin([0, 1])]

print("Original usable rows:", len(df))
print("Unique headline texts:", df["headlines"].nunique())

duplicate_mask = df["headlines"].duplicated(keep=False)
duplicate_rows = df[duplicate_mask]

print("Rows participating in duplicates:", len(duplicate_rows))
print(
    "Distinct headlines occurring more than once:",
    duplicate_rows["headlines"].nunique()
)

deduplicated = df.drop_duplicates(subset=["headlines"], keep="first")

print("Rows after deduplication:", len(deduplicated))
print("Rows removed:", len(df) - len(deduplicated))

labels_per_headline = df.groupby("headlines")["outcome"].nunique()
conflicts = labels_per_headline[labels_per_headline > 1]

print("\nConflicting headline groups:", len(conflicts))

print("\nFive duplicate examples:")

examples = list(duplicate_rows.groupby("headlines"))

for headline, group in examples[:5]:
    print("\nHeadline:", headline)
    print("Label counts:")
    print(group["outcome"].value_counts().to_dict())
