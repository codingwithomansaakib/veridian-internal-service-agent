# Veridian Internal Service Agent

## Assignment 2 — Policy-Grounded Internal IT Support

An Agentic AI prototype for Veridian Corp's internal IT support.

The agent combines:

- FastAPI backend
- Streamlit frontend
- Groq LLM
- ChromaDB
- Sentence Transformers
- RAG policy retrieval
- Intent classification
- Deterministic decision engine
- Employee request search
- Ticket search
- Escalation routing
- Audit logging

---

## Architecture

Employee
   ↓
Streamlit UI
   ↓
FastAPI `/chat`
   ↓
Intent Classification
   ↓
Decision Engine
   ↓
RAG Policy Retrieval
   ↓
Employee Request / Ticket Search
   ↓
Escalation Routing
   ↓
Groq LLM
   ↓
Final Grounded Response
   ↓
Audit Log

---

## Project Structure

```text
veridian-it-agent/
│
├── app/
│   ├── data/
│   │   ├── policies.json
│   │   ├── requests.json
│   │   └── tickets.json
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── rag/
│   │   ├── ingest.py
│   │   └── vector_store.py
│   │
│   ├── services/
│   │   └── decision_engine.py
│   │
│   ├── tools/
│   │   ├── audit_tool.py
│   │   ├── escalation_tool.py
│   │   ├── policy_tool.py
│   │   ├── request_tool.py
│   │   └── ticket_tool.py
│   │
│   ├── agent.py
│   ├── llm_agent.py
│   └── main.py
│
├── frontend/
│   └── streamlit_app.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
