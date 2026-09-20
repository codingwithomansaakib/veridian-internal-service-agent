import requests
import streamlit as st


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Veridian IT Service Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #8fa7c7;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .answer {
        background: #191b22;
        border: 1px solid #343743;
        border-radius: 14px;
        padding: 20px;
        line-height: 1.7;
        margin-bottom: 15px;
    }

    .info-card {
        background: #191b22;
        border: 1px solid #343743;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .success-card {
        background: #17241d;
        border-left: 4px solid #39d98a;
        border-radius: 10px;
        padding: 14px;
    }

    .warning-card {
        background: #291d1e;
        border-left: 4px solid #ff5c5c;
        border-radius: 10px;
        padding: 14px;
    }

    .rag-card {
        background: #171b24;
        border-left: 4px solid #4da6ff;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DEMO SCENARIOS
# =========================================================

DEMO_SCENARIOS = [
    "I am locked out of my account. I tried my password 6 times.",
    "Can I get Wi-Fi access for a guest tomorrow?",
    "I think I got a phishing email asking for my login.",
    "I cannot log into the expense tool.",
    "My VPN credentials expired.",
    "My laptop is completely dead and I have had it 3.5 years.",
    "I work from home 4 days a week and need a monitor.",
    "My mailbox is full and I cannot send emails.",
    "A contractor needs VPN access next week.",
]


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# API REQUEST
# =========================================================

def call_agent(message: str):

    try:

        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message
            },
            timeout=90,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ FastAPI is not running.\n\n"
            "Start it with:\n\n"
            "`uvicorn app.main:app --reload`"
        )

        return None

    except requests.exceptions.Timeout:

        st.error(
            "⏱️ The request timed out. "
            "Check the FastAPI/Groq terminal."
        )

        return None

    except requests.exceptions.HTTPError as error:

        st.error(
            f"❌ FastAPI HTTP error: {error}"
        )

        return None

    except Exception as error:

        st.error(
            f"❌ Unexpected error: {error}"
        )

        return None


# =========================================================
# SAFE GET
# =========================================================

def get_value(
    data,
    key,
    default="Not available"
):

    value = data.get(
        key,
        default
    )

    if value is None:
        return default

    return value


# =========================================================
# DISPLAY RAG
# =========================================================

def display_rag(data):

    st.markdown(
        "### 🔍 RAG Retrieved Sources"
    )

    policies = data.get(
        "policies",
        []
    )

    policy_ids = data.get(
        "policy_ids",
        []
    )

    rag_error = data.get(
        "rag_error"
    )


    if rag_error:

        st.error(
            f"RAG Error: {rag_error}"
        )

        return


    if not policies:

        if policy_ids:

            st.warning(
                "Policy IDs were returned, "
                "but RAG policy details were not "
                "returned by the backend."
            )

        else:

            st.info(
                "No RAG policy was retrieved."
            )

        return


    for index, policy in enumerate(
        policies
    ):

        policy_id = policy.get(
            "policy_id",
            "Unknown"
        )

        title = policy.get(
            "title",
            "Unknown policy"
        )

        content = policy.get(
            "content",
            ""
        )

        distance = policy.get(
            "distance"
        )


        with st.expander(
            f"📘 {policy_id} — {title}",
            expanded=(index == 0),
        ):

            st.write(
                content
            )

            if distance is not None:

                st.caption(
                    f"Vector distance: "
                    f"{float(distance):.4f}"
                )


# =========================================================
# DISPLAY ESCALATION
# =========================================================

def display_escalation(data):

    st.markdown(
        "### 🚨 Escalation"
    )

    escalation = data.get(
        "escalation"
    )


    if not escalation:

        st.success(
            "No escalation required."
        )

        return


    destination = escalation.get(
        "destination",
        "Unknown"
    )

    reason = escalation.get(
        "reason",
        "Human assistance required."
    )

    status = escalation.get(
        "status",
        "Pending"
    )


    st.markdown(
        f"""
        <div class="warning-card">

        <strong>Destination:</strong>
        {destination}

        <br><br>

        <strong>Reason:</strong>
        {reason}

        <br><br>

        <strong>Status:</strong>
        {status}

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DISPLAY REQUESTS
# =========================================================

def display_requests(data):

    st.markdown(
        "### 📋 Related Employee Requests"
    )

    requests_data = data.get(
        "matched_requests",
        []
    )


    if not requests_data:

        st.info(
            "No related employee request found."
        )

        return


    for request in requests_data:

        request_id = request.get(
            "request_id",
            "Unknown"
        )

        employee = request.get(
            "employee",
            "Unknown"
        )

        request_text = request.get(
            "request",
            request.get(
                "issue",
                "No description"
            )
        )

        status = request.get(
            "status",
            request.get(
                "initial_action",
                "Unknown"
            )
        )


        with st.expander(
            f"📋 {request_id} — {employee}"
        ):

            st.write(
                f"**Request:** {request_text}"
            )

            st.write(
                f"**Status:** {status}"
            )


# =========================================================
# DISPLAY TICKETS
# =========================================================

def display_tickets(data):

    st.markdown(
        "### 🎫 Related Tickets"
    )

    tickets_data = data.get(
        "matched_tickets",
        []
    )


    if not tickets_data:

        st.info(
            "No related ticket found."
        )

        return


    for ticket in tickets_data:

        ticket_id = ticket.get(
            "ticket_id",
            "Unknown"
        )

        employee = ticket.get(
            "employee",
            "Unknown"
        )

        issue = ticket.get(
            "issue",
            ticket.get(
                "summary",
                "No issue description"
            )
        )

        status = ticket.get(
            "status",
            "Unknown"
        )


        with st.expander(
            f"🎫 {ticket_id} — {employee}"
        ):

            st.write(
                f"**Issue:** {issue}"
            )

            st.write(
                f"**Status:** {status}"
            )


# =========================================================
# DISPLAY CREATED STRUCTURED TICKET
# =========================================================

def display_created_ticket(data):
    st.markdown("### 🎫 New Structured Ticket")
    created_ticket = data.get("created_ticket")
    if not created_ticket:
        st.info("No new ticket was created for this request.")
        return
    ticket_id = created_ticket.get("ticket_id", "Unknown")
    destination = created_ticket.get("destination", "Not specified")
    intent = created_ticket.get("intent", "Unknown")
    action = created_ticket.get("action", "Unknown")
    status = created_ticket.get("status", "Unknown")
    reason = created_ticket.get("reason", "Not specified")
    created_at = created_ticket.get("created_at", "Not available")
    st.markdown(
        f"""
        <div class="success-card">
            <strong>Ticket ID:</strong> {ticket_id}
            <br><br><strong>Destination:</strong> {destination}
            <br><br><strong>Intent:</strong> {intent}
            <br><br><strong>Action:</strong> {action}
            <br><br><strong>Status:</strong> {status}
            <br><br><strong>Reason:</strong> {reason}
            <br><br><strong>Created At:</strong> {created_at}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DISPLAY COMPLETE AGENT RESPONSE
# =========================================================

def display_agent_response(data):

    if not isinstance(
        data,
        dict
    ):

        st.error(
            "Invalid response received from FastAPI."
        )

        return


    # -----------------------------------------------------
    # BASIC VALUES
    # -----------------------------------------------------

    intent = get_value(
        data,
        "intent"
    )

    action = get_value(
        data,
        "action"
    )

    answer = get_value(
        data,
        "answer",
        "No answer returned."
    )

    policy_ids = data.get(
        "policy_ids",
        []
    )


    # -----------------------------------------------------
    # AI RESPONSE
    # -----------------------------------------------------

    st.markdown(
        "### 🤖 AI Agent Response"
    )

    st.markdown(
        f"""
        <div class="answer">
        {answer}
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # DECISION
    # -----------------------------------------------------

    st.markdown(
        "### 🧠 Agent Decision"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Intent",
            intent
        )


    with col2:

        st.metric(
            "Action",
            action
        )


    with col3:

        st.metric(
            "RAG Policies",
            len(policy_ids)
        )


    # -----------------------------------------------------
    # POLICY IDS
    # -----------------------------------------------------

    if policy_ids:

        st.markdown(
            f"""
            <div class="success-card">

            <strong>📚 Policies Used:</strong>
            {" • ".join(policy_ids)}

            </div>
            """,
            unsafe_allow_html=True,
        )


    # -----------------------------------------------------
    # RAG
    # -----------------------------------------------------

    display_rag(data)


    # -----------------------------------------------------
    # ESCALATION
    # -----------------------------------------------------

    display_escalation(data)


    # -----------------------------------------------------
    # REQUESTS
    # -----------------------------------------------------

    display_requests(data)


    # -----------------------------------------------------
    # TICKETS
    # -----------------------------------------------------

    display_tickets(data)

    # -----------------------------------------------------
    # NEW STRUCTURED TICKET
    # -----------------------------------------------------

    display_created_ticket(data)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🤖 Demo scenarios"
    )

    st.caption(
        "Try predefined Assignment 2 scenarios"
    )


    for index, scenario in enumerate(
        DEMO_SCENARIOS
    ):

        if st.button(
            scenario,
            key=f"scenario_{index}",
            use_container_width=True,
        ):

            st.session_state.pending_message = scenario

            st.rerun()


    st.divider()


    st.markdown(
        "### ⚙️ AI Architecture"
    )


    st.markdown(
        """
        <div class="info-card">

        🧠 <strong>LLM:</strong> Groq

        <br>🔍 <strong>RAG:</strong> Active

        <br>🗄️ <strong>Vector DB:</strong> ChromaDB

        <br>🧩 <strong>Embeddings:</strong>
        Sentence Transformers

        <br>⚙️ <strong>Decision Engine:</strong>
        Active

        <br>🚨 <strong>Escalation:</strong>
        Active

        <br>📝 <strong>Audit:</strong>
        Active

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.divider()


    # Backend status

    try:

        health = requests.get(
            f"{API_URL}/health",
            timeout=3,
        )

        if health.ok:

            st.success(
                "🟢 FastAPI Connected"
            )

        else:

            st.warning(
                "🟡 FastAPI responded with an error"
            )

    except Exception:

        st.error(
            "🔴 FastAPI Offline"
        )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="title">'
    '🤖 Veridian Internal IT Service Agent'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Assignment 2 — Policy-grounded Internal IT Support'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# PROCESS PENDING DEMO
# =========================================================

if (
    "pending_message"
    in st.session_state
):

    message = st.session_state.pop(
        "pending_message"
    )


    st.session_state.messages.append(
        {
            "role": "user",
            "content": message,
        }
    )


    result = call_agent(
        message
    )


    if result is not None:

        st.session_state.messages.append(
            {
                "role": "assistant",
                "data": result,
            }
        )


    st.rerun()


# =========================================================
# CHAT HISTORY
# =========================================================

for item in st.session_state.messages:

    role = item.get(
        "role"
    )


    with st.chat_message(
        role
    ):

        if role == "user":

            st.write(
                item.get(
                    "content",
                    ""
                )
            )

        else:

            display_agent_response(
                item.get(
                    "data",
                    {}
                )
            )


# =========================================================
# CHAT INPUT
# =========================================================

user_message = st.chat_input(
    "Describe your IT problem..."
)


if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )


    result = call_agent(
        user_message
    )


    if result is not None:

        st.session_state.messages.append(
            {
                "role": "assistant",
                "data": result,
            }
        )


    st.rerun()