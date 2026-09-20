from datetime import datetime


# =========================================================
# ESCALATION CREATION
# =========================================================

def create_escalation(
    reason: str,
    destination: str
):

    # Normalize destination

    if destination in [
        "IT",
        "IT Support",
        "escalate_to_it"
    ]:

        final_destination = "IT"


    elif destination in [
        "Security",
        "security",
        "escalate_security"
    ]:

        final_destination = "Security"


    else:

        final_destination = "Human Review"


    return {

        "destination":
            final_destination,

        "reason":
            reason,

        "status":
            "pending_human_action"
    }


# =========================================================
# SECURITY ESCALATION
# =========================================================

def escalate_to_security(
    reason: str
):

    return create_escalation(
        reason=reason,
        destination="Security"
    )


# =========================================================
# IT ESCALATION
# =========================================================

def escalate_to_it(
    reason: str
):

    return create_escalation(
        reason=reason,
        destination="IT"
    )


# =========================================================
# HUMAN REVIEW
# =========================================================

def escalate_to_human(
    reason: str
):

    return create_escalation(
        reason=reason,
        destination="Human Review"
    )
