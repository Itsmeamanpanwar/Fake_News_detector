import hashlib
import os
import time
import requests

from datetime import datetime, timezone

from factcheck_engine.services.evidence_store import EvidenceStore


API_URL = "https://api.openalex.org/works"

HEADERS = {
    "User-Agent": "NLPFactCheckEducationalProject/0.1"
}


def reconstruct_abstract(inverted_index):
    """Reconstruct an abstract from OpenAlex's word-position index."""
    if not isinstance(inverted_index, dict) or not inverted_index:
        return ""

    words_by_position = {}

    for word, positions in inverted_index.items():
        for position in positions:
            words_by_position[position] = word

    if not words_by_position:
        return ""

    return " ".join(
        words_by_position[position]
        for position in sorted(words_by_position)
    ).strip()


class OpenAlexCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.store = EvidenceStore()

        # Optional: set OPENALEX_API_KEY in your environment.
        self.api_key = os.getenv("OPENALEX_API_KEY")

    def search(self, query, limit):
        params = {
            "search": query,
            "per_page": min(limit * 5, 50),
            "select": (
                "id,doi,title,publication_date,"
                "abstract_inverted_index,primary_location"
            ),
        }

        if self.api_key:
            params["api_key"] = self.api_key

        response = self.session.get(
            API_URL,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        return response.json().get("results", [])

    def collect(self, query, limit=5, topic="science"):
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if not 1 <= limit <= 10:
            raise ValueError("Limit must be between 1 and 10.")

        results = self.search(query, limit)

        saved = 0
        skipped = 0

        for item in results:
            if saved >= limit:
                break

            title = (item.get("title") or "").strip()
            abstract = reconstruct_abstract(
                item.get("abstract_inverted_index")
            )

            if len(abstract) < 100:
                skipped += 1
                print(
                    f"Skipped: {title or 'Untitled'} "
                    "(no usable abstract)"
                )
                continue

            work_id = item.get("id", "").strip()
            doi = item.get("doi")

            location = item.get("primary_location") or {}
            landing_url = location.get("landing_page_url")

            source_url = (
                doi
                or landing_url
                or work_id
            )

            if not title or not source_url.startswith("https://"):
                skipped += 1
                print("Skipped: missing title or valid source URL")
                continue

            record_id = "OA-" + hashlib.sha256(
                (work_id or source_url).encode("utf-8")
            ).hexdigest()[:16]

            source = location.get("source") or {}
            publisher = source.get("display_name") or "Unknown publisher"

            record = {
                "id": record_id,
                "title": title,
                "publisher": publisher,
                "url": source_url,
                "published": item.get("publication_date"),
                "retrieved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "text": abstract,
                "topic": topic,
                "evidence_status": "pending_review",
            }

            try:
                self.store.add(record)
                saved += 1
                print(f"Saved: {title}")

            except ValueError as error:
                skipped += 1
                print(f"Skipped: {title} ({error})")

            time.sleep(0.2)

        return {
            "found": len(results),
            "saved": saved,
            "skipped": skipped,
        }


def main():
    collector = OpenAlexCollector()

    query = input("Search scholarly publications: ").strip()
    topic = input(
        "Topic (science/health/technology/politics/general): "
    ).strip().lower() or "science"

    limit_text = input("Maximum records (1-10, default 5): ").strip()

    try:
        limit = int(limit_text) if limit_text else 5

        result = collector.collect(
            query=query,
            limit=limit,
            topic=topic,
        )

        print("\nOPENALEX COLLECTION SUMMARY")
        print("=" * 40)
        print("Search results:", result["found"])
        print("Saved:", result["saved"])
        print("Skipped:", result["skipped"])
        print("All new records remain pending review.")

    except (ValueError, requests.RequestException) as error:
        print("Collection failed:", error)


if __name__ == "__main__":
    main()
