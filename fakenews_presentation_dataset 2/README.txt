Fake News Detection — Presentation Demo Dataset

Files:
1. presentation_claims.csv
   Twelve demo claims with expected outcomes and evidence metadata.
   Use this as a presentation/test checklist.

2. presentation_evidence.jsonl
   Eleven source/evidence records intended for the project's JSONL evidence store.
   These are demo seed records, not a benchmark dataset.

IMPORTANT:
- Verify that every source URL loads and that the linked source supports the paraphrased evidence text before submission.
- The expected verdicts are reference expectations, not guaranteed model outputs.
- NLI scores are not truth probabilities. The model can disagree with the expected verdict.
- Do not report these records as a formal accuracy benchmark.
- One claim intentionally has no attached evidence to demonstrate insufficient evidence.
- Before merging into the existing evidence store, back up your current evidence file and check for duplicate IDs/URLs.
