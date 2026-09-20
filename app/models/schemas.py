from typing import Any

from pydantic import BaseModel, Field


# =========================================================
# CHAT REQUEST
# =========================================================

class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        description="Employee's IT support question"
    )


# =========================================================
# RAG POLICY
# =========================================================

class PolicyResult(BaseModel):

    policy_id: str

    title: str

    content: str

    distance: float | None = None

    source: str | None = (
        "Veridian Internal IT Knowledge Base"
    )


# =========================================================
# EMPLOYEE REQUEST
# =========================================================

class RequestResult(BaseModel):

    request_id: str | None = None

    employee: str | None = None

    email: str | None = None

    date_opened: str | None = None

    request: str | None = None

    status: str | None = None


# =========================================================
# EXISTING TICKET
# =========================================================

class TicketResult(BaseModel):

    ticket_id: str | None = None

    employee: str | None = None

    issue: str | None = None

    status: str | None = None


# =========================================================
# CREATED STRUCTURED TICKET
# =========================================================

class CreatedTicket(BaseModel):

    ticket_id: str

    created_at: str

    source: str

    employee_message: str

    intent: str

    action: str

    destination: str | None = None

    reason: str | None = None

    status: str


# =========================================================
# CHAT RESPONSE
# =========================================================

class ChatResponse(BaseModel):

    intent: str

    answer: str

    action: str

    policy_ids: list[str] = Field(
        default_factory=list
    )

    escalation: dict[str, Any] | None = None

    # -----------------------------------------------------
    # RAG RESULTS
    # -----------------------------------------------------

    policies: list[PolicyResult] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # EXISTING EMPLOYEE REQUESTS
    # -----------------------------------------------------

    matched_requests: list[RequestResult] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # EXISTING TICKETS
    # -----------------------------------------------------

    matched_tickets: list[TicketResult] = Field(
        default_factory=list
    )

    # -----------------------------------------------------
    # NEW STRUCTURED TICKET
    # -----------------------------------------------------

    created_ticket: CreatedTicket | None = None

    # -----------------------------------------------------
    # RAG ERROR / DEBUG INFORMATION
    # -----------------------------------------------------

    rag_error: str | None = None
