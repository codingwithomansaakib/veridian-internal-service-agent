import json
from pathlib import Path

from app.rag.vector_store import (
    add_policy,
    get_collection_info
)


# =========================================================
# POLICY FILE
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

POLICY_FILE = (
    BASE_DIR
    / "app"
    / "data"
    / "policies.json"
)


# =========================================================
# LOAD POLICIES
# =========================================================

def load_policies():

    if not POLICY_FILE.exists():

        raise FileNotFoundError(
            f"Policy file not found: {POLICY_FILE}"
        )

    with open(
        POLICY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# INGEST POLICIES
# =========================================================

def ingest_policies():

    policies = load_policies()

    print()
    print("=" * 60)
    print("VERIDIAN IT RAG INGESTION")
    print("=" * 60)

    print(
        f"Found {len(policies)} policies"
    )

    print()

    for policy in policies:

        # YOUR JSON USES "id"
        policy_id = policy.get("id")

        # YOUR JSON USES "title"
        title = policy.get(
            "title",
            policy_id
        )

        # YOUR JSON USES "rule"
        content = policy.get(
            "rule",
            ""
        )

        if not policy_id:

            print(
                "Skipping policy without ID"
            )

            continue

        if not content:

            print(
                f"Skipping {policy_id}: "
                "missing rule"
            )

            continue

        print(
            f"🔄 Embedding: "
            f"{policy_id} - {title}"
        )

        add_policy(
            policy_id=policy_id,

            title=title,

            content=content
        )

        print(
            f"✅ Added: {policy_id}"
        )

    print()
    print("=" * 60)
    print("RAG INGESTION COMPLETE")
    print("=" * 60)

    info = get_collection_info()

    print(
        f"Vector Database : "
        f"{info['vector_database']}"
    )

    print(
        f"Collection      : "
        f"{info['collection']}"
    )

    print(
        f"Documents       : "
        f"{info['documents']}"
    )

    print(
        f"Embedding Model : "
        f"{info['embedding_model']}"
    )

    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    ingest_policies()