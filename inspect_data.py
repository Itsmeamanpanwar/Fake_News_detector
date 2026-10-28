import pandas as pd
from pathlib import Path

for p in Path("Datasets").glob("*.csv"):
    print("\n" + "=" * 60)
    print("FILE:", p)

    try:
        df = pd.read_csv(p, encoding="utf-8")

        print("SHAPE:", df.shape)
        print("COLUMNS:", df.columns.tolist())
        print("\nMISSING VALUES:")
        print(df.isnull().sum().to_string())

        for col in df.columns:
            if df[col].nunique() < 30:
                print("\nVALUES IN", repr(col))
                print(df[col].value_counts(dropna=False).head(20).to_string())

        print("\nSAMPLE ROWS:")
        for _, row in df.head(3).iterrows():
            for col in df.columns:
                value = str(row[col]).replace("\n", " ")
                print(f"{col}: {value[:200]}")
            print("-" * 30)

    except Exception as e:
        print("ERROR:", repr(e))
