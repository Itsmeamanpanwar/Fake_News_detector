import hashlib
import re
import time
import requests

from datetime import datetime, timezone

from factcheck_engine.services.evidence_store import EvidenceStore


API_URL = "https://api.crossref.org/works"

HEADERS = {
    "User-Agent": (
        "NLPFactCheckEducationalProject/0.1 "
        "(metadata collection)"
    )
}


def clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_publication_date(item):
    for key in ("published-print", "published-online", "published"):
        date_parts = (
            item.get(key, {}).get("date-parts", [])
        )

        if date_parts and date_parts[0]:
            parts = date_parts[0]

            year = parts[0]
            month = parts[1] if len(parts) > 1 else 1
            day = parts[2] if len(parts) > 2 else 1

            return f"{year:04d}-{month:02d}-{day:02d}"

    return None


class CrossrefCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.store = EvidenceStore()

    def search(self, query, limit=5):
        response = self.session.get(
            API_URL,
            params={
                "query": query,
                "rows": min(limit * 10, 50),
                "select": (
                    "DOI,title,author,publisher,"
                    "published,abstract,type,URL,container-title"
                ),
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()
        return data.get("message", {}).get("items", [])

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

            doi = item.get("DOI", "").strip()
            titles = item.get("title", [])
            title = titles[0].strip() if titles else ""

            abstract = clean_text(item.get("abstract", ""))

            if not doi or not title or len(abstract) < 50:
                print(
                    f"Skipped: {title or doi or 'Missing metadata'} "
                    "(no usable abstract or identifier)"
                )
                skipped += 1
                continue

            publisher = item.get("publisher", "Unknown publisher")

            record_id = "CR-" + hashlib.sha256(
                doi.lower().encode("utf-8")
            ).hexdigest()[:16]

            record = {
                "id": record_id,
                "title": title,
                "publisher": publisher,
                "url": f"https://doi.org/{doi}",
                "published": get_publication_date(item),
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
                print(f"Skipped: {title} ({error})")
                skipped += 1

            # Avoid sending requests too quickly.
            time.sleep(0.25)

        return {
            "found": len(results),
            "saved": saved,
            "skipped": skipped,
        }


def main():
    collector = CrossrefCollector()

    query = input("Search scholarly publications: ").strip()

    topic = input(
        "Topic category (science/health/technology/other): "
    ).strip().lower() or "science"

    limit_text = input(
        "Maximum records (1-10, default 5): "
    ).strip()

    try:
        limit = int(limit_text) if limit_text else 5

        if not topic:
            topic = "science"

        result = collector.collect(
            query=query,
            limit=limit,
            topic=topic,
        )

        print("\nCROSSREF COLLECTION SUMMARY")
        print("=" * 40)
        print("Search results:", result["found"])
        print("Saved:", result["saved"])
        print("Skipped:", result["skipped"])
        print("\nAll collected records remain pending review.")

    except (ValueError, requests.RequestException) as error:
        print("Collection failed:", error)


if __name__ == "__main__":
    main()
