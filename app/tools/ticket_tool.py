import json
import re
from pathlib import Path
import uuid
from datetime import datetime


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TICKET_FILE = (
    BASE_DIR
    / "app"
    / "data"
    / "tickets.json"
)


# =========================================================
# LOAD TICKETS
# =========================================================

def _load_tickets():

    if not TICKET_FILE.exists():

        raise FileNotFoundError(
            f"Ticket file not found: {TICKET_FILE}"
        )

    try:

        with open(
            TICKET_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Invalid tickets.json: {e}"
        )

    if isinstance(data, dict):

        return data.get(
            "tickets",
            []
        )

    return data


# =========================================================
# GET ALL TICKETS
# =========================================================

def get_all_tickets():

    return _load_tickets()


# =========================================================
# GET TICKET BY ID
# =========================================================

def get_ticket(
    ticket_id: str
):

    tickets = _load_tickets()

    ticket_id = (
        ticket_id
        .strip()
        .upper()
    )

    for ticket in tickets:

        current_id = str(
            ticket.get(
                "ticket_id",
                ""
            )
        ).upper()

        if current_id == ticket_id:

            return ticket

    return None


# =========================================================
# CHECK WHETHER TICKET IS CLOSED
# =========================================================

def is_ticket_closed(
    ticket: dict
):

    status = str(
        ticket.get(
            "status",
            ""
        )
    ).lower()

    closed_words = [
        "resolved",
        "rejected",
        "closed",
        "approved"
    ]

    return any(
        word in status
        for word in closed_words
    )


# =========================================================
# INTENT → TICKET KEYWORDS
# =========================================================

INTENT_TICKET_KEYWORDS = {

    "password_reset": [
        "password",
        "password reset",
        "locked out"
    ],

    "vpn_access": [
        "vpn",
        "vpn credential"
    ],

    "laptop": [
        "laptop",
        "laptop replacement",
        "screen",
        "hardware"
    ],

    "software_installation": [
        "software",
        "non-catalog",
        "installation"
    ],

    "printer": [
        "printer",
        "paper jam"
    ],

    "mailbox": [
        "mailbox",
        "quota"
    ],

    "guest_wifi": [
        "guest wi-fi",
        "guest wifi",
        "wi-fi",
        "wifi"
    ],

    "expense_access": [
        "expense",
        "expense software"
    ],

    "security_incident": [
        "phishing",
        "malware",
        "unauthorized access"
    ],

    "wfh_equipment": [
        "home office",
        "home office equipment",
        "monitor",
        "chair"
    ],

    "admin_access": [
        "admin access",
        "server access"
    ]
}


# =========================================================
# SEARCH TICKETS
# =========================================================

def search_tickets(
    query: str,
    intent: str | None = None,
    limit: int = 5
):

    tickets = _load_tickets()

    query_lower = query.lower()


    # =====================================================
    # 1. DIRECT TICKET ID SEARCH
    # =====================================================

    ticket_ids = re.findall(
        r"\bTK-\d+\b",
        query.upper()
    )

    if ticket_ids:

        direct_results = []

        for ticket_id in ticket_ids:

            ticket = get_ticket(
                ticket_id
            )

            if ticket:

                direct_results.append(
                    ticket
                )

        if direct_results:

            return direct_results[:limit]


    # =====================================================
    # 2. INTENT-AWARE SEARCH
    # =====================================================

    keywords = INTENT_TICKET_KEYWORDS.get(
        intent,
        []
    )


    results = []


    for ticket in tickets:

        ticket_id = str(
            ticket.get(
                "ticket_id",
                ""
            )
        )

        employee = str(
            ticket.get(
                "employee",
                ""
            )
        )

        issue = str(
            ticket.get(
                "issue",
                ticket.get(
                    "summary",
                    ""
                )
            )
        )

        status = str(
            ticket.get(
                "status",
                ""
            )
        )


        searchable = (
            f"{ticket_id} "
            f"{employee} "
            f"{issue} "
            f"{status}"
        ).lower()


        score = 0


        # -------------------------------------------------
        # Intent-specific matching
        # -------------------------------------------------

        for keyword in keywords:

            if keyword in searchable:

                # Strong score for exact issue matches
                if keyword in issue.lower():

                    score += 20

                else:

                    score += 10


        # -------------------------------------------------
        # Query-specific matching
        # -------------------------------------------------

        for keyword in keywords:

            if keyword in query_lower:

                if keyword in searchable:

                    score += 5


        # -------------------------------------------------
        # Keep only relevant tickets
        # -------------------------------------------------

        if score > 0:

            results.append(
                {
                    **ticket,
                    "_score": score
                }
            )


    # =====================================================
    # 3. SORT BY RELEVANCE
    # =====================================================

    results.sort(
        key=lambda x: x["_score"],
        reverse=True
    )


    # =====================================================
    # 4. REMOVE INTERNAL SCORE
    # =====================================================

    for result in results:

        result.pop(
            "_score",
            None
        )


    return results[:limit]

# =========================================================
# CREATE STRUCTURED TICKET
# =========================================================



CREATED_TICKET_FILE = (
    BASE_DIR
    / "app"
    / "data"
    / "created_tickets.json"
)


def _load_created_tickets():

    if not CREATED_TICKET_FILE.exists():
        return []

    try:
        with open(
            CREATED_TICKET_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception:
        return []


def create_ticket(
    employee_message: str,
    intent: str,
    action: str,
    destination: str | None = None,
    reason: str | None = None
):

    tickets = _load_created_tickets()

    ticket_number = 2000 + len(tickets) + 1

    ticket = {
        "ticket_id": f"NEW-{ticket_number}",
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "source": "Veridian Internal Service Agent",
        "employee_message": employee_message,
        "intent": intent,
        "action": action,
        "destination": destination,
        "reason": reason,
        "status": "Pending human action"
    }

    tickets.append(ticket)

    CREATED_TICKET_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CREATED_TICKET_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            tickets,
            file,
            indent=2,
            ensure_ascii=False
        )

    return ticket
