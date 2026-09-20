from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# Embedding model
# --------------------------------------------------
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


# --------------------------------------------------
# ChromaDB
# --------------------------------------------------
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="veridian_it_policies"
)


# --------------------------------------------------
# Create embedding
# --------------------------------------------------
def create_embedding(text: str):
    vector = embedding_model.encode(
        text,
        normalize_embeddings=True
    )

    return vector.tolist()


# --------------------------------------------------
# Add policy
# --------------------------------------------------
def add_policy(
    policy_id: str,
    title: str,
    content: str
):
    document = (
        f"Policy ID: {policy_id}\n"
        f"Title: {title}\n"
        f"Rule: {content}"
    )

    embedding = create_embedding(document)

    collection.upsert(
        ids=[policy_id],
        embeddings=[embedding],
        documents=[document],
        metadatas=[
            {
                "policy_id": policy_id,
                "title": title,
                "source": "Veridian Internal IT Knowledge Base"
            }
        ]
    )


# --------------------------------------------------
# Intent → relevant policies
# --------------------------------------------------
INTENT_POLICY_MAP = {

    "password_reset": [
        "KB-01"
    ],

    "vpn_access": [
        "KB-02"
    ],

    "laptop": [
        "KB-03",
        "ASSET-01"
    ],

    "software_installation": [
        "KB-04"
    ],

    "printer": [
        "KB-05"
    ],

    "mailbox": [
        "KB-06"
    ],

    "guest_wifi": [
        "KB-07"
    ],

    "expense_access": [
        "KB-08"
    ],

    "security_incident": [
        "KB-09"
    ],

    "wfh_equipment": [
        "KB-10"
    ],

    "admin_access": [
        "ASSET-01"
    ]
}


# --------------------------------------------------
# Retrieve policies
# --------------------------------------------------
def retrieve_policies(
    query: str,
    top_k: int = 3,
    intent: str | None = None
):

    if collection.count() == 0:
        return []

    query_embedding = create_embedding(query)

    allowed_ids = INTENT_POLICY_MAP.get(intent)

    # --------------------------------------------------
    # If intent is known, retrieve only relevant policies
    # --------------------------------------------------
    if allowed_ids:

        try:

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(
                    max(top_k, len(allowed_ids)),
                    collection.count()
                ),
                where={
                    "policy_id": {
                        "$in": allowed_ids
                    }
                },
                include=[
                    "documents",
                    "metadatas",
                    "distances"
                ]
            )

        except Exception:

            # Fallback for older ChromaDB metadata/index issues
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(
                    collection.count(),
                    20
                ),
                include=[
                    "documents",
                    "metadatas",
                    "distances"
                ]
            )

    else:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(
                top_k,
                collection.count()
            ),
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    policies = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        policy_id = metadata.get("policy_id")

        # Additional safety filtering
        if allowed_ids and policy_id not in allowed_ids:
            continue

        policies.append(
            {
                "policy_id": policy_id,
                "title": metadata.get("title"),
                "content": document,
                "distance": float(distance),
                "source": metadata.get("source")
            }
        )

    return policies[:top_k]


# --------------------------------------------------
# Collection information
# --------------------------------------------------
def get_collection_info():

    return {
        "collection": collection.name,
        "documents": collection.count(),
        "embedding_model": EMBEDDING_MODEL_NAME
    }