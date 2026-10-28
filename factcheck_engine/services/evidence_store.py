import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_STORE = (
    PROJECT_ROOT
    / "factcheck_engine"
    / "data"
    / "processed"
    / "evidence.jsonl"
)


REQUIRED_FIELDS = (
    "id",
    "title",
    "publisher",
    "url",
    "text",
    "topic",
)


def validate_record(record):
    """Validate required fields without claiming that a source is trustworthy."""

    if not isinstance(record, dict):
        raise ValueError("Evidence record must be a dictionary.")

    for field in REQUIRED_FIELDS:
        value = record.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Required field '{field}' must be a non-empty string."
            )

    parsed_url = urlparse(record["url"])

    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("Source URL must be a valid HTTPS URL.")

    if len(record["text"].strip()) < 30:
        raise ValueError("Evidence text is too short.")

    record.setdefault("published", None)
    record.setdefault("retrieved_at", datetime.now(
        timezone.utc
    ).isoformat())
    record.setdefault("evidence_status", "pending_review")

    return record


class EvidenceStore:
    def __init__(self, path=DEFAULT_STORE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self):
        """Read all records from the JSONL store."""

        if not self.path.exists():
            return []

        records = []

        with self.path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid JSON on line {line_number}: {error}"
                    ) from error

        return records

    def add(self, record):
        """Add a new record unless its ID or URL already exists."""

        record = validate_record(dict(record))
        existing = self.load_all()

        for item in existing:
            if item.get("id") == record["id"]:
                raise ValueError(
                    f"Evidence ID already exists: {record['id']}"
                )

            if item.get("url") == record["url"]:
                raise ValueError(
                    f"Source URL already exists: {record['url']}"
                )

        with self.path.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

        return record

    def count(self):
        return len(self.load_all())


def main():
    store = EvidenceStore()

    print("Evidence store:", store.path)
    print("Existing records:", store.count())
    print("New evidence will be marked pending_review.")


if __name__ == "__main__":
    main()
