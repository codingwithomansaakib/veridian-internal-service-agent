import json
from pathlib import Path
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]
POLICY_FILE = BASE_DIR / "data" / "policies.json"


INTENT_POLICY_MAP = {
    "password_reset": ["KB-01"],
    "vpn_access": ["KB-02"],
    "laptop": ["KB-03", "ASSET-01"],
    "software_installation": ["KB-04"],
    "printer": ["KB-05"],
    "mailbox": ["KB-06"],
    "guest_wifi": ["KB-07"],
    "expense_access": ["KB-08"],
    "security_incident": ["KB-09"],
    "wfh_equipment": ["KB-10"],
    "admin_access": ["ASSET-01"],
}


@lru_cache(maxsize=1)
def load_policies():
    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def build_index():
    policies = load_policies()

    documents = []

    for policy in policies:
        documents.append(
            " ".join([
                str(policy.get("policy_id", "")),
                str(policy.get("title", "")),
                str(policy.get("content", "")),
            ])
        )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(documents)

    return vectorizer, matrix


def retrieve_policies(query: str, top_k: int = 3, intent: str | None = None):
    policies = load_policies()

    if not policies:
        return []

    vectorizer, matrix = build_index()

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, matrix)[0]

    allowed_ids = INTENT_POLICY_MAP.get(intent)

    results = []

    for index, score in enumerate(similarities):
        policy = policies[index]
        policy_id = policy.get("policy_id", "")

        # Give priority to the policy matching the detected intent.
        if allowed_ids and policy_id in allowed_ids:
            score += 0.50

        results.append((score, policy))

    results.sort(key=lambda x: x[0], reverse=True)

    output = []

    for score, policy in results[:top_k]:
        output.append({
            "policy_id": policy.get("policy_id", ""),
            "title": policy.get("title", ""),
            "content": policy.get("content", ""),
            "distance": round(1 - min(score, 1.0), 4),
            "source": "Veridian Internal IT Knowledge Base",
        })

    return output