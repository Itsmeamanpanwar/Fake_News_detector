from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


MODEL_NAME = "cross-encoder/nli-deberta-v3-small"


class NLIEvaluator:
    def __init__(self):
        self.device = (
            "mps" if torch.backends.mps.is_available() else "cpu"
        )

        print(f"Loading NLI model on: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME
        )
        self.model.to(self.device)
        self.model.eval()

        print("NLI model loaded successfully.")

    def evaluate(self, claim, evidence):
        if not claim.strip() or not evidence.strip():
            raise ValueError("Claim and evidence must not be empty.")

        inputs = self.tokenizer(
            evidence,
            claim,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probabilities = torch.softmax(logits, dim=-1)[0]

        # Read the label mapping from the model configuration.
        id2label = self.model.config.id2label

        scores = {
            str(id2label[index]).lower(): float(probabilities[index].item())
            for index in range(len(probabilities))
        }

        # NLI models can use different label naming conventions.
        def find_score(target):
            for label, score in scores.items():
                if target in label:
                    return score
            return None

        entailment = find_score("entail")
        contradiction = find_score("contradict")
        neutral = find_score("neutral")

        return {
            "entailment": entailment,
            "contradiction": contradiction,
            "neutral": neutral,
            "raw_scores": scores,
            "interpretation": max(
                scores, key=scores.get
            ),
        }


def main():
    evaluator = NLIEvaluator()

    claim = input("\nEnter a claim: ").strip()
    evidence = input("Enter an evidence passage: ").strip()

    try:
        result = evaluator.evaluate(claim, evidence)
    except ValueError as error:
        print(f"Error: {error}")
        return

    print("\nNLI RESULTS")
    print("=" * 40)

    for key in ("entailment", "contradiction", "neutral"):
        value = result[key]
        if value is not None:
            print(f"{key.title()}: {value:.4f}")

    print("Model label:", result["interpretation"])
    print("\nThese are model estimates, not proof of truth.")


if __name__ == "__main__":
    main()
