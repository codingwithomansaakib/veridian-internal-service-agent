import os
import streamlit as st
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL") or st.secrets.get(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not configured")

client = Groq(api_key=GROQ_API_KEY)


# ---------------------------------------------------------
# System Prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are Veridian Corp's Internal IT Service Agent.

Your job is to help employees using ONLY the supplied
Veridian policy, employee request, ticket and decision
context.

IMPORTANT RULES:

1. Never invent a Veridian policy.
2. Never invent an employee request.
3. Never invent a ticket.
4. Never create approval requirements that are not present
   in the supplied context.
5. Treat the decision engine as authoritative.
6. Do not override the decision engine.
7. If the case requires human intervention, clearly explain
   that it must be routed to the appropriate team.
8. Security incidents must follow the supplied security
   policy.
9. Keep the answer clear and professional.
10. Use the retrieved RAG policies as the knowledge source.

Answer the employee directly.

Include when relevant:

- What is happening
- What the policy says
- Required action
- Approval requirement
- Escalation
- Relevant policy ID
"""


# ---------------------------------------------------------
# Generate Answer
# ---------------------------------------------------------

def generate_answer(
    user_message: str,
    policy_context: str = "",
    request_context: str = "",
    ticket_context: str = "",
    decision_context: str = ""
) -> str:

    prompt = f"""
EMPLOYEE MESSAGE:
{user_message}


RETRIEVED VERIDIAN POLICIES:
{policy_context}


RELATED EMPLOYEE REQUESTS:
{request_context}


RELATED TICKETS:
{ticket_context}


DECISION ENGINE RESULT:
{decision_context}


Using only the information above, provide the final
employee-facing response.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,

        max_tokens=700
    )

    return response.choices[0].message.content.strip()