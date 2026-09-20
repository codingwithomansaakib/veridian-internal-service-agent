from datetime import datetime
from pathlib import Path
import json


# =========================================================
# AUDIT LOG CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

AUDIT_FILE = BASE_DIR / "audit_log.json"


# =========================================================
# LOAD EXISTING AUDIT LOG
# =========================================================

def _load_audit_log():

    if not AUDIT_FILE.exists():
        return []

    try:
        with open(
            AUDIT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return []


# =========================================================
# SAVE AUDIT LOG
# =========================================================

def _save_audit_log(events):

    with open(
        AUDIT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            events,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# RECORD AUDIT EVENT
# =========================================================

def record_audit(
    message: str,
    intent: str,
    action: str
):

    events = _load_audit_log()

    event = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "message": message,
        "intent": intent,
        "action": action
    }

    events.append(event)

    _save_audit_log(events)

    return event


# =========================================================
# GET AUDIT LOG
# =========================================================

def get_audit_log():

    return _load_audit_log()


# =========================================================
# CLEAR AUDIT LOG
# =========================================================

def clear_audit_log():

    _save_audit_log([])

    return {
        "status": "success",
        "message": "Audit log cleared"
    }
