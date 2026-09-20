import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

POLICY_FILE = (
    BASE_DIR
    / "app"
    / "data"
    / "policies.json"
)


def _load_policies():

    with open(
        POLICY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_all_policies():

    return _load_policies()


def get_policy(policy_id: str):

    policies = _load_policies()

    policy_id = policy_id.strip().upper()

    for policy in policies:

        if policy.get("id", "").upper() == policy_id:

            return policy

    return None


def search_policy(query: str):

    policies = _load_policies()

    query_words = set(
        query.lower().split()
    )

    results = []

    for policy in policies:

        searchable_text = (
            f"{policy.get('id', '')} "
            f"{policy.get('title', '')} "
            f"{policy.get('rule', '')}"
        ).lower()

        score = sum(
            1
            for word in query_words
            if len(word) > 2
            and word in searchable_text
        )

        if score > 0:

            results.append(
                {
                    "policy": policy,
                    "score": score
                }
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results
