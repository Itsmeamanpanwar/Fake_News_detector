from factcheck_engine.services.semantic_retrieval import (
    SemanticEvidenceRetriever,
)
from factcheck_engine.services.nli import NLIEvaluator


class FactChecker:
    def __init__(self):
        print("\nInitializing semantic retrieval...")
        self.retriever = SemanticEvidenceRetriever()

        print("\nInitializing NLI evaluator...")
        self.nli = NLIEvaluator()

    def check_claim(self, claim, top_k=5, min_similarity=0.45):
        claim = claim.strip()

        if not claim:
            raise ValueError("Claim cannot be empty.")

        if not 0 <= min_similarity <= 1:
            raise ValueError("min_similarity must be between 0 and 1.")

        documents = self.retriever.search(claim, top_k=top_k)
        evaluated = []

        for document in documents:
            item = dict(document)
            item["nli"] = self.nli.evaluate(claim, document["text"])
            item["used_for_verdict"] = False
            evaluated.append(item)

        # Only reviewed, verified, relevant records may affect the verdict.
        usable = [
            item for item in evaluated
            if item.get("evidence_status") == "verified"
            and item.get("url", "").startswith("https://")
            and item.get("similarity", 0.0) >= min_similarity
        ]

        for item in usable:
            item["used_for_verdict"] = True

        if not usable:
            verdict = "INSUFFICIENT VERIFIED EVIDENCE"
        else:
            supports = [
                item for item in usable
                if item["nli"]["entailment"] is not None
                and item["nli"]["entailment"] >= 0.70
            ]

            contradicts = [
                item for item in usable
                if item["nli"]["contradiction"] is not None
                and item["nli"]["contradiction"] >= 0.70
            ]

            if supports and contradicts:
                verdict = "MIXED EVIDENCE"
            elif supports:
                verdict = "POTENTIALLY SUPPORTED"
            elif contradicts:
                verdict = "POTENTIALLY CONTRADICTED"
            else:
                verdict = "INCONCLUSIVE"

        return {
            "claim": claim,
            "verdict": verdict,
            "evidence": evaluated,
            "min_similarity": min_similarity,
        }
