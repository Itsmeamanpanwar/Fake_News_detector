import re

import torch
from sentence_transformers import SentenceTransformer, util

from factcheck_engine.services.evidence_store import EvidenceStore


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Keep chunks relatively small for embedding and NLI models.
CHUNK_WORDS = 140
CHUNK_OVERLAP = 25


def split_into_chunks(text, chunk_words=CHUNK_WORDS, overlap=CHUNK_OVERLAP):
    """Split a document into overlapping word-based passages."""
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


class SemanticEvidenceRetriever:
    def __init__(self):
        self.store = EvidenceStore()

        self.device = (
            "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

        print(f"Loading embedding model on: {self.device}")

        self.model = SentenceTransformer(
            MODEL_NAME,
            device=self.device,
        )

        self.documents = []
        self.embeddings = None

        self.load_evidence()

    def load_evidence(self):
        records = self.store.load_all()
        passages = []

        for record in records:
            text = record.get("text", "").strip()

            if not text:
                continue

            chunks = split_into_chunks(text)

            for index, chunk in enumerate(chunks, start=1):
                passages.append({
                    "id": record["id"],
                    "passage_id": f"{record['id']}-P{index}",
                    "title": record["title"],
                    "publisher": record["publisher"],
                    "url": record["url"],
                    "published": record.get("published"),
                    "retrieved_at": record.get("retrieved_at"),
                    "topic": record.get("topic", "unknown"),
                    "evidence_status": record.get(
                        "evidence_status",
                        "pending_review",
                    ),
                    "text": chunk,
                })

        self.documents = passages

        if not passages:
            self.embeddings = None
            print("No evidence documents found in the local store.")
            return

        texts = [item["text"] for item in passages]

        print(
            f"Encoding {len(passages)} passages "
            f"from {len(records)} stored documents..."
        )

        self.embeddings = self.model.encode(
            texts,
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        print("Semantic evidence index is ready.")

    def search(self, claim, top_k=5):
        claim = claim.strip()

        if not claim:
            raise ValueError("Claim cannot be empty.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        if self.embeddings is None:
            return []

        query_embedding = self.model.encode(
            claim,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

        scores = util.cos_sim(
            query_embedding,
            self.embeddings,
        )[0]

        limit = min(top_k, len(self.documents))
        indices = torch.topk(scores, k=limit).indices.tolist()

        results = []

        for index in indices:
            result = dict(self.documents[index])
            result["similarity"] = round(
                float(scores[index].item()),
                4,
            )
            results.append(result)

        return results


def main():
    retriever = SemanticEvidenceRetriever()

    claim = input("\nEnter a claim or topic to search: ").strip()

    try:
        results = retriever.search(claim, top_k=5)
    except ValueError as error:
        print("Error:", error)
        return

    print("\nSEMANTIC RETRIEVAL RESULTS")
    print("=" * 65)

    if not results:
        print("No evidence passages are available.")
        return

    for rank, item in enumerate(results, start=1):
        print(f"\n{rank}. {item['title']}")
        print("Document ID:", item["id"])
        print("Passage ID:", item["passage_id"])
        print("Publisher:", item["publisher"])
        print("Topic:", item["topic"])
        print("Similarity:", item["similarity"])
        print("Status:", item["evidence_status"])
        print("Published:", item["published"] or "Unknown")
        print("Source:", item["url"])
        print("Passage:", item["text"])

    print("\nNote: similarity is not a truth or credibility score.")
    print("Retrieved documents still require source and evidence review.")


if __name__ == "__main__":
    main()
