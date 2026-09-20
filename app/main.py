from fastapi import FastAPI

from app.models.schemas import ChatRequest, ChatResponse
from app.agent import run_agent
from app.tools.audit_tool import get_audit_log


app = FastAPI(
    title="Veridian Internal Service Agent",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Veridian IT Support Agent is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    result = run_agent(request.message)

    # IMPORTANT:
    # Return the complete agent result.
    return ChatResponse(**result)


@app.get("/audit")
def audit():

    return {
        "events": get_audit_log()
    }