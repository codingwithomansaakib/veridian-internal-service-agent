# =========================================================
# VERIDIAN INTERNAL SERVICE AGENT
# Agent Orchestrator
# =========================================================

from app.services.decision_engine import (
    classify_intent,
    decide
)

from app.tools.request_tool import (
    search_requests
)

from app.tools.ticket_tool import (
    search_tickets,
    create_ticket
)

from app.tools.escalation_tool import (
    create_escalation
)

from app.tools.audit_tool import (
    record_audit
)

from app.rag.vector_store import (
    retrieve_policies
)

from app.llm_agent import (
    generate_answer
)


# =========================================================
# HELPER: FORMAT RAG POLICIES
# =========================================================

def format_policy_context(policies):

    if not policies:

        return (
            "No relevant Veridian policy "
            "was retrieved."
        )

    context = []

    for policy in policies:

        context.append(
            f"""
Policy ID:
{policy.get("policy_id", "Unknown")}

Title:
{policy.get("title", "Unknown")}

Content:
{policy.get("content", "")}
"""
        )

    return "\n".join(context)


# =========================================================
# HELPER: FORMAT REQUESTS
# =========================================================

def format_request_context(requests):

    if not requests:

        return (
            "No related employee request found."
        )

    context = []

    for item in requests[:3]:

        request_data = item.get(
            "request",
            item
        )

        context.append(
            str(request_data)
        )

    return "\n".join(context)


# =========================================================
# HELPER: FORMAT TICKETS
# =========================================================

def format_ticket_context(tickets):

    if not tickets:

        return (
            "No related ticket found."
        )

    context = []

    for item in tickets[:3]:

        ticket_data = item.get(
            "ticket",
            item
        )

        context.append(
            str(ticket_data)
        )

    return "\n".join(context)


# =========================================================
# HELPER: GET POLICY IDS
# =========================================================

def get_policy_ids(policies):

    return [
        policy.get("policy_id")
        for policy in policies
        if policy.get("policy_id")
    ]


# =========================================================
# MAIN AGENT
# =========================================================

def run_agent(message: str):

    # =====================================================
    # 1. CLASSIFY USER INTENT
    # =====================================================

    intent = classify_intent(
        message
    )


    # =====================================================
    # 2. DECISION ENGINE
    # =====================================================

    decision = decide(
        intent,
        message
    )

    action = decision.get(
        "action",
        "unknown"
    )


    # =====================================================
    # 3. FOLLOW-UP FOR UNCLEAR REQUESTS
    # =====================================================

    if action == "ask_follow_up":

        follow_up_question = decision.get(
            "follow_up_question",
            "Could you provide more details about your IT issue?"
        )

        answer = (
            decision.get(
                "reason",
                "I need more information "
                "to understand your request."
            )
            + "\n\n"
            + follow_up_question
        )

        try:

            record_audit(
                message,
                intent,
                "ask_follow_up"
            )

        except Exception as e:

            print(
                f"Audit error: {e}"
            )

        return {

            "intent":
                intent,

            "answer":
                answer,

            "action":
                "ask_follow_up",

            "policy_ids":
                [],

            "policies":
                [],

            "escalation":
                None,

            "matched_requests":
                [],

            "matched_tickets":
                [],

            "created_ticket":
                None,

            "rag_error":
                None
        }


    # =====================================================
    # 4. RAG RETRIEVAL
    # =====================================================

    rag_error = None

    try:

        policies = retrieve_policies(

            query=message,

            top_k=3,

            intent=intent
        )

    except Exception as e:

        print(
            f"RAG retrieval error: {e}"
        )

        rag_error = str(e)

        policies = []


    # =====================================================
    # 5. EMPLOYEE REQUEST SEARCH
    # =====================================================

    try:

        requests = search_requests(

            message,

            intent
        )

    except Exception as e:

        print(
            f"Request search error: {e}"
        )

        requests = []


    # =====================================================
    # 6. EXISTING TICKET SEARCH
    # =====================================================

    try:

        tickets = search_tickets(

            message,

            intent
        )

    except Exception as e:

        print(
            f"Ticket search error: {e}"
        )

        tickets = []


    # =====================================================
    # 7. ESCALATION
    # =====================================================

    escalation = None


    # -----------------------------------------------------
    # IT ESCALATION
    # -----------------------------------------------------

    if action == "escalate_to_it":

        escalation = create_escalation(

            reason=decision.get(
                "reason",
                "IT assistance required."
            ),

            destination="IT"
        )


    # -----------------------------------------------------
    # SECURITY ESCALATION
    # -----------------------------------------------------

    elif action == "escalate_security":

        escalation = create_escalation(

            reason=decision.get(
                "reason",
                "Security assistance required."
            ),

            destination="Security"
        )


    # -----------------------------------------------------
    # HUMAN REVIEW
    # -----------------------------------------------------

    elif action == "human_review":

        escalation = create_escalation(

            reason=decision.get(
                "reason",
                "Human review required."
            ),

            destination="Human Review"
        )


    # =====================================================
    # 8. CREATE STRUCTURED TICKET
    # =====================================================

    created_ticket = None


    if action in [
        "escalate_to_it",
        "escalate_security",
        "human_review"
    ]:

        try:

            destination = None

            if escalation:

                destination = escalation.get(
                    "destination"
                )


            created_ticket = create_ticket(

                employee_message=message,

                intent=intent,

                action=action,

                destination=destination,

                reason=decision.get(
                    "reason",
                    ""
                )
            )

        except Exception as e:

            print(
                f"Ticket creation error: {e}"
            )

            created_ticket = None


    # =====================================================
    # 9. CREATE POLICY CONTEXT
    # =====================================================

    policy_context = format_policy_context(
        policies
    )


    # =====================================================
    # 10. CREATE REQUEST CONTEXT
    # =====================================================

    request_context = format_request_context(
        requests
    )


    # =====================================================
    # 11. CREATE TICKET CONTEXT
    # =====================================================

    ticket_context = format_ticket_context(
        tickets
    )


    # =====================================================
    # 12. CREATE DECISION CONTEXT
    # =====================================================

    decision_context = f"""
Intent:
{intent}

Action:
{action}

Reason:
{decision.get("reason", "")}

Escalation:
{escalation}

Created Ticket:
{created_ticket}
"""


    # =====================================================
    # 13. GROQ LLM
    # =====================================================

    try:

        answer = generate_answer(

            user_message=message,

            policy_context=policy_context,

            request_context=request_context,

            ticket_context=ticket_context,

            decision_context=decision_context
        )

    except Exception as e:

        print(
            f"Groq LLM error: {e}"
        )

        # Deterministic fallback

        answer = decision.get(

            "reason",

            "Your request requires "
            "further assistance."
        )


    # =====================================================
    # 14. AUDIT LOG
    # =====================================================

    try:

        record_audit(

            message,

            intent,

            action
        )

    except Exception as e:

        print(
            f"Audit error: {e}"
        )


    # =====================================================
    # 15. RETURN AGENT RESULT
    # =====================================================

    return {

        "intent":
            intent,

        "answer":
            answer,

        "action":
            action,

        "policy_ids":
            get_policy_ids(
                policies
            ),

        "policies":
            policies,

        "escalation":
            escalation,

        "matched_requests":
            requests,

        "matched_tickets":
            tickets,

        "created_ticket":
            created_ticket,

        "rag_error":
            rag_error
    }