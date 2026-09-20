import os
import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Veridian Internal Service Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURATION
# ============================================================

# Local development:
# http://127.0.0.1:8000
#
# Streamlit Cloud:
# Add API_URL to Streamlit Secrets.
#
# Example:
# API_URL = "https://your-fastapi-service.onrender.com"

try:
    API_URL = st.secrets.get(
        "API_URL",
        os.getenv("API_URL", "http://127.0.0.1:8000")
    )
except Exception:
    API_URL = os.getenv(
        "API_URL",
        "http://127.0.0.1:8000"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    .source-box {
        padding: 12px;
        border-radius: 8px;
        border: 1px solid rgba(128,128,128,0.3);
        margin-bottom: 8px;
    }

    .ticket-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.35);
        margin-top: 10px;
    }

    .small-text {
        font-size: 13px;
        opacity: 0.7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Veridian Internal Service Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered internal IT support agent for Veridian Corp"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System")

    st.write("**Architecture**")

    st.code(
        """Employee
   ↓
Streamlit
   ↓
FastAPI
   ↓
Agent
   ├── Intent Classification
   ├── Decision Engine
   ├── Policy RAG
   ├── Request Tool
   ├── Ticket Tool
   └── Audit
   ↓
Groq LLM
""",
        language="text",
    )

    st.divider()

    st.subheader("🔌 Backend")

    st.code(API_URL)

    if st.button("🔍 Check Backend Health", use_container_width=True):

        try:
            response = requests.get(
                f"{API_URL}/health",
                timeout=10,
            )

            if response.status_code == 200:
                st.success("Backend is running ✅")
                st.json(response.json())
            else:
                st.error(
                    f"Backend returned status {response.status_code}"
                )

        except Exception as e:
            st.error(f"Backend connection failed: {e}")

    st.divider()

    st.subheader("🎯 Demo Scenarios")

    demo_password = st.button(
        "🔐 Password Lockout",
        use_container_width=True,
    )

    demo_wifi = st.button(
        "📶 Guest Wi-Fi",
        use_container_width=True,
    )

    demo_phishing = st.button(
        "🚨 Phishing Incident",
        use_container_width=True,
    )

    demo_unknown = st.button(
        "❓ Unclear Request",
        use_container_width=True,
    )

    if demo_password:
        st.session_state.demo_message = (
            "I am locked out of my account, "
            "tried my password 6 times."
        )

    elif demo_wifi:
        st.session_state.demo_message = (
            "Can I get Wi-Fi access for a guest tomorrow?"
        )

    elif demo_phishing:
        st.session_state.demo_message = (
            "I think I got a phishing email asking for my login."
        )

    elif demo_unknown:
        st.session_state.demo_message = (
            "hey can you help, it's not working"
        )

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.rerun()


# ============================================================
# API FUNCTION
# ============================================================

def call_agent(message: str):

    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": message
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# DEMO MESSAGE
# ============================================================

demo_message = st.session_state.get(
    "demo_message",
    "",
)


if demo_message:

    st.info(
        f"Demo scenario selected: **{demo_message}**"
    )

    if st.button("▶️ Run Demo Scenario"):

        try:

            with st.spinner("Agent is analyzing the request..."):

                result = call_agent(demo_message)

            st.session_state.last_result = result

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": demo_message,
                }
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result.get(
                        "answer",
                        "No response generated."
                    ),
                }
            )

            st.session_state.demo_message = ""

            st.rerun()

        except Exception as e:

            st.error(
                f"Unable to contact backend: {e}"
            )


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.messages:

    st.subheader("💬 Conversation")

    for message in st.session_state.messages:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.write(message["content"])

        else:

            with st.chat_message("assistant"):
                st.write(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

user_message = st.chat_input(
    "Describe your IT issue..."
)


if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    try:

        with st.spinner("Veridian Agent is working..."):

            result = call_agent(user_message)

        st.session_state.last_result = result

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.get(
                    "answer",
                    "No response generated."
                ),
            }
        )

        st.rerun()

    except requests.exceptions.RequestException as e:

        st.error(
            f"Backend connection error: {e}"
        )

    except Exception as e:

        st.error(
            f"Unexpected error: {e}"
        )


# ============================================================
# RESULT DISPLAY
# ============================================================

result = st.session_state.last_result


if result:

    st.divider()

    # --------------------------------------------------------
    # AGENT DECISION
    # --------------------------------------------------------

    st.header("🧠 Agent Decision")

    intent = result.get(
        "intent",
        "unknown",
    )

    action = result.get(
        "action",
        "unknown",
    )

    policies = result.get(
        "policies",
        [],
    )

    policy_ids = result.get(
        "policy_ids",
        [],
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Intent",
            intent,
        )

    with col2:

        st.metric(
            "Action",
            action,
        )

    with col3:

        # IMPORTANT:
        # Use actual retrieved policies instead of policy_ids.
        st.metric(
            "RAG Policies",
            len(policies),
        )


    # --------------------------------------------------------
    # AGENT RESPONSE
    # --------------------------------------------------------

    st.subheader("💬 Agent Response")

    answer = result.get(
        "answer",
        "No response available.",
    )

    st.success(answer)


    # --------------------------------------------------------
    # RAG SOURCES
    # --------------------------------------------------------

    st.header("🔍 RAG Retrieved Sources")

    if policies:

        for policy in policies:

            policy_id = policy.get(
                "policy_id",
                "Unknown",
            )

            title = policy.get(
                "title",
                "Untitled Policy",
            )

            content = policy.get(
                "content",
                "",
            )

            distance = policy.get(
                "distance",
                None,
            )

            source = policy.get(
                "source",
                "Veridian Internal IT Knowledge Base",
            )

            with st.expander(
                f"📘 {policy_id} — {title}",
                expanded=(
                    policy_id
                    == policies[0].get(
                        "policy_id",
                        ""
                    )
                ),
            ):

                if distance is not None:
                    st.caption(
                        f"Vector distance: {distance}"
                    )

                st.write(content)

                st.caption(
                    f"Source: {source}"
                )

    else:

        st.info(
            "No policy sources were retrieved."
        )


    # --------------------------------------------------------
    # ESCALATION
    # --------------------------------------------------------

    escalation = result.get(
        "escalation",
        None,
    )

    if escalation:

        st.header("🚨 Escalation")

        destination = escalation.get(
            "destination",
            "Not specified",
        )

        reason = escalation.get(
            "reason",
            "",
        )

        st.error(
            f"**Destination:** {destination}"
        )

        if reason:
            st.write(
                f"**Reason:** {reason}"
            )


    # --------------------------------------------------------
    # MATCHED EMPLOYEE REQUESTS
    # --------------------------------------------------------

    matched_requests = result.get(
        "matched_requests",
        [],
    )

    st.header("📋 Related Employee Requests")

    if matched_requests:

        for request in matched_requests:

            with st.expander(
                request.get(
                    "request_id",
                    "Request",
                )
            ):

                st.write(
                    f"**Employee:** "
                    f"{request.get('employee', 'N/A')}"
                )

                st.write(
                    f"**Email:** "
                    f"{request.get('email', 'N/A')}"
                )

                st.write(
                    f"**Request:** "
                    f"{request.get('request', 'N/A')}"
                )

                st.write(
                    f"**Status:** "
                    f"{request.get('status', 'N/A')}"
                )

    else:

        st.info(
            "No related employee requests found."
        )


    # --------------------------------------------------------
    # MATCHED TICKETS
    # --------------------------------------------------------

    matched_tickets = result.get(
        "matched_tickets",
        [],
    )

    st.header("🎫 Related Tickets")

    if matched_tickets:

        for ticket in matched_tickets:

            with st.expander(
                ticket.get(
                    "ticket_id",
                    "Ticket",
                )
            ):

                st.write(
                    f"**Employee:** "
                    f"{ticket.get('employee', 'N/A')}"
                )

                st.write(
                    f"**Issue:** "
                    f"{ticket.get('issue', 'N/A')}"
                )

                st.write(
                    f"**Status:** "
                    f"{ticket.get('status', 'N/A')}"
                )

    else:

        st.info(
            "No related tickets found."
        )


    # --------------------------------------------------------
    # CREATED STRUCTURED TICKET
    # --------------------------------------------------------

    created_ticket = result.get(
        "created_ticket",
        None,
    )

    if created_ticket:

        st.header("🎫 Structured Ticket Created")

        st.success(
            "A structured ticket was created for human follow-up."
        )

        with st.container(border=True):

            st.write(
                f"**Ticket ID:** "
                f"{created_ticket.get('ticket_id', 'N/A')}"
            )

            st.write(
                f"**Created At:** "
                f"{created_ticket.get('created_at', 'N/A')}"
            )

            st.write(
                f"**Source:** "
                f"{created_ticket.get('source', 'N/A')}"
            )

            st.write(
                f"**Employee Message:** "
                f"{created_ticket.get('employee_message', 'N/A')}"
            )

            st.write(
                f"**Intent:** "
                f"{created_ticket.get('intent', 'N/A')}"
            )

            st.write(
                f"**Action:** "
                f"{created_ticket.get('action', 'N/A')}"
            )

            destination = created_ticket.get(
                "destination",
                None,
            )

            if destination:
                st.write(
                    f"**Destination:** {destination}"
                )

            reason = created_ticket.get(
                "reason",
                None,
            )

            if reason:
                st.write(
                    f"**Reason:** {reason}"
                )

            st.write(
                f"**Status:** "
                f"{created_ticket.get('status', 'N/A')}"
            )


    # --------------------------------------------------------
    # RAG ERROR
    # --------------------------------------------------------

    rag_error = result.get(
        "rag_error",
        None,
    )

    if rag_error:

        st.warning(
            f"RAG warning: {rag_error}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Veridian Corp Internal Service Agent • "
    "Assignment 2 • AI Agent Factory"
)