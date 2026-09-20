import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

REQUEST_FILE = BASE_DIR / "app" / "data" / "requests.json"


# --------------------------------------------------
# Load requests
# --------------------------------------------------
def load_requests():

    with open(
        REQUEST_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        if "requests" in data:
            return data["requests"]

        for value in data.values():

            if isinstance(value, list):
                return value

    return []


# --------------------------------------------------
# Normalize text
# --------------------------------------------------
def normalize(text):

    return re.sub(
        r"\s+",
        " ",
        str(text).lower()
    ).strip()


# --------------------------------------------------
# Search employee requests
# --------------------------------------------------
def search_requests(
    message: str,
    intent: str | None = None
):

    query = normalize(message)

    requests = load_requests()

    # --------------------------------------------------
    # Strong intent-specific matching
    # --------------------------------------------------

    INTENT_KEYWORDS = {

        "password_reset": [
            "password",
            "locked out",
            "login locked",
            "failed attempts",
            "account locked"
        ],

        "vpn_access": [
            "vpn"
        ],

        "guest_wifi": [
            "guest wifi",
            "guest wi-fi",
            "wifi"
        ],

        "security_incident": [
            "phishing",
            "malware",
            "unauthorized access",
            "suspicious"
        ],

        "mailbox": [
            "mailbox",
            "email full",
            "quota"
        ],

        "laptop": [
            "laptop",
            "computer",
            "screen",
            "replacement"
        ],

        "software_installation": [
            "software",
            "install",
            "extension",
            "browser"
        ],

        "printer": [
            "printer",
            "paper jam"
        ],

        "expense_access": [
            "expense",
            "expense tool"
        ],

        "wfh_equipment": [
            "work from home",
            "wfh",
            "monitor",
            "chair",
            "equipment"
        ],

        "admin_access": [
            "admin access",
            "server access"
        ]
    }


    keywords = INTENT_KEYWORDS.get(
        intent,
        []
    )


    scored = []


    for request in requests:

        request_text = normalize(
            " ".join(
                str(value)
                for value in request.values()
            )
        )

        score = 0


        # --------------------------------------------------
        # Exact/strong phrase matching
        # --------------------------------------------------

        for keyword in keywords:

            if keyword in query and keyword in request_text:

                # Stronger weight for specific phrases
                if keyword in [
                    "locked out",
                    "failed attempts",
                    "account locked",
                    "phishing",
                    "malware",
                    "unauthorized access",
                    "guest wifi",
                    "guest wi-fi"
                ]:

                    score += 20

                else:

                    score += 10


        # --------------------------------------------------
        # Only keep reasonably relevant requests
        # --------------------------------------------------

        if score > 0:

            scored.append(
                (
                    score,
                    request
                )
            )


    # Highest relevance first
    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )


    # Return only strong matches
    return [
        item[1]
        for item in scored[:3]
    ]