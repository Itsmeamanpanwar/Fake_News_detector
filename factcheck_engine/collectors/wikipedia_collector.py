import hashlib
import re
import time
from datetime import datetime, timezone
from urllib.parse import quote

import requests

from factcheck_engine.services.evidence_store import EvidenceStore


API_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": (
        "ResearchFactCheckPrototype/0.1 "
        "(educational NLP project)"
    )
}


def clean_text(text):
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


class WikipediaCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.store = EvidenceStore()

    def search(self, query, limit=5):
        response = self.session.get(
            API_URL,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
            },
            timeout=20,
        )
        response.raise_for_status()

        return response.json().get("query", {}).get("search", [])

    def fetch_page(self, title):
        response = self.session.get(
            API_URL,
            params={
                "action": "query",
                "prop": "extracts|info",
                "explaintext": 1,
                "exsectionformat": "plain",
                "inprop": "url",
                "titles": title,
                "format": "json",
            },
            timeout=30,
        )
        response.raise_for_status()

        pages = response.json().get("query", {}).get("pages", {})
        page = next(iter(pages.values()), None)

        if not page or "missing" in page:
            return None

        text = clean_text(page.get("extract", ""))
        url = page.get("fullurl", "")

        if len(text) < 100 or not url.startswith("https://"):
            return None

        page_title = page.get("title", title)
        page_id = str(page.get("pageid", ""))

        # Stable ID for the same Wikipedia page.
        record_id = "WIKI-" + hashlib.sha256(
            page_id.encode("utf-8")
        ).hexdigest()[:16]

        return {
            "id": record_id,
            "title": page_title,
            "publisher": "Wikipedia",
            "url": url,
            "published": None,
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "text": text,
            "topic": "general",
            "evidence_status": "pending_review",
        }

    def collect(self, query, limit=5):
        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if not 1 <= limit <= 10:
            raise ValueError("Limit must be between 1 and 10.")

        search_results = self.search(query, limit)
        saved = 0
        skipped = 0

        for item in search_results:
            title = item.get("title", "").strip()

            if not title:
                skipped += 1
                continue

            try:
                record = self.fetch_page(title)

                if not record:
                    skipped += 1
                    continue

                # Assign the broad topic supplied by the user.
                # This is a user-provided category, not AI verification.
                record["topic"] = "general"

                try:
                    self.store.add(record)
                    saved += 1
                    print(f"Saved: {record['title']}")
                except ValueError as error:
                    print(f"Skipped: {record['title']} ({error})")
                    skipped += 1

                # Be polite to the public API.
                time.sleep(0.5)

            except requests.RequestException as error:
                print(f"Request failed for {title}: {error}")
                skipped += 1

        return {
            "found": len(search_results),
            "saved": saved,
            "skipped": skipped,
        }


def main():
    collector = WikipediaCollector()

    query = input("Search for a topic: ").strip()

    try:
        limit_text = input("Maximum articles (1-10, default 5): ").strip()
        limit = int(limit_text) if limit_text else 5

        result = collector.collect(query, limit=limit)

        print("\nCOLLECTION SUMMARY")
        print("=" * 40)
        print("Search results:", result["found"])
        print("Saved:", result["saved"])
        print("Skipped:", result["skipped"])
        print("\nSaved records remain pending review.")

    except (ValueError, requests.RequestException) as error:
        print("Collection failed:", error)


if __name__ == "__main__":
    main()
