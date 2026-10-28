import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "evidence.json"
)


class EvidenceRetriever:
    def __init__(self, data_path=DATA_PATH):
        self.data_path = Path(data_path)
        self.documents = self._load_documents()

        if not self.documents:
            raise ValueError("The evidence collection is empty.")

        texts = [
            f"{doc['title']}. {doc['text']}"
            for doc in self.documents
        ]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        self.document_matrix = self.vectorizer.fit_transform(texts)

    def _load_documents(self):
        with self.data_path.open("r", encoding="utf-8") as file:
            documents = json.load(file)

        required = {"id", "title", "source", "url", "published", "text"}

        for index, document in enumerate(documents):
            missing = required - document.keys()

            if missing:
                raise ValueError(
                    f"Document {index} is missing fields: {sorted(missing)}"
                )

            if not document["text"].strip():
                raise ValueError(
                    f"Document {document['id']} has empty text."
                )

        return documents

    def search(self, claim, top_k=3):
        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("Enter a non-empty claim.")

        query_vector = self.vectorizer.transform([claim])

        scores = cosine_similarity(
            query_vector,
            self.document_matrix,
        )[0]

        ranked_indices = scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            document = self.documents[index]

            results.append({
                "id": document["id"],
                "title": document["title"],
                "source": document["source"],
                "url": document["url"],
                "published": document["published"],
                "text": document["text"],
                "retrieval_score": round(float(scores[index]), 4),
            })

        return results


if __name__ == "__main__":
    retriever = EvidenceRetriever()

    claim = input("Enter a claim to search for: ")

    for result in retriever.search(claim):
        print("\n" + "=" * 60)
        print("Title:", result["title"])
        print("Source:", result["source"])
        print("Retrieval score:", result["retrieval_score"])
        print("Evidence:", result["text"])
