import joblib

tests = {
    "covid": [
        "Public health officials recommend vaccination, ventilation, and staying home when sick to help reduce the spread of respiratory infections.",
        "A viral post claims that coronavirus does not exist.",
        "Researchers published a report on respiratory virus transmission.",
    ],
    "afghanistan": [
        "International organizations published reports discussing humanitarian conditions and access to essential services in Afghanistan.",
        "Officials discussed humanitarian assistance and regional security in Afghanistan.",
        "A viral post makes an unsupported claim about the Taliban.",
    ],
}

for name, texts in tests.items():
    path = f"models_sklearn/{name}_model.joblib"
    model = joblib.load(path)

    print("\n" + "=" * 60)
    print("MODEL:", name.upper())

    for text in texts:
        prediction = int(model.predict([text])[0])
        probabilities = model.predict_proba([text])[0]
        scores = dict(zip(model.classes_, probabilities))

        label = "FAKE" if prediction == 0 else "REAL"

        print("\nText:", text)
        print("Prediction:", label)
        print("FAKE score:", round(float(scores.get(0, 0)), 4))
        print("REAL score:", round(float(scores.get(1, 0)), 4))
