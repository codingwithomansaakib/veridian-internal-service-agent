# app/services/decision_engine.py

import re


def normalize_message(message: str) -> str:
    """
    Normalize employee message for intent classification.
    """
    text = message.lower().strip()

    # Normalize Wi-Fi variations
    text = re.sub(r"\bwi[\s-]?fi\b", "wifi", text)

    # Normalize extra spaces
    text = re.sub(r"\s+", " ", text)

    return text


def classify_intent(message: str) -> str:
    """
    Classify the employee request into a known IT support intent.
    """

    text = normalize_message(message)

    # ---------------------------------------------------------
    # SECURITY INCIDENT
    # ---------------------------------------------------------
    security_keywords = [
        "phishing",
        "phishing email",
        "malware",
        "virus",
        "unauthorized access",
        "hacked",
        "suspicious email",
        "suspicious link",
        "security incident",
        "clicked suspicious link",
        "credential theft",
    ]

    if any(keyword in text for keyword in security_keywords):
        return "security_incident"

    # ---------------------------------------------------------
    # PASSWORD RESET
    # ---------------------------------------------------------
    password_keywords = [
        "password reset",
        "reset password",
        "forgot password",
        "forgot my password",
        "password expired",
        "locked out",
        "account locked",
        "login password",
        "password",
    ]

    if any(keyword in text for keyword in password_keywords):
        return "password_reset"

    # ---------------------------------------------------------
    # VPN
    # ---------------------------------------------------------
    vpn_keywords = [
        "vpn",
        "vpn access",
        "vpn credential",
        "vpn credentials",
        "vpn expired",
        "vpn login",
    ]

    if any(keyword in text for keyword in vpn_keywords):
        return "vpn_access"

    # ---------------------------------------------------------
    # LAPTOP / HARDWARE
    # ---------------------------------------------------------
    laptop_keywords = [
        "laptop",
        "laptop replacement",
        "laptop broken",
        "laptop dead",
        "screen flickering",
        "screen broken",
        "hardware failure",
        "hardware problem",
        "computer not working",
    ]

    if any(keyword in text for keyword in laptop_keywords):
        return "laptop"

    # ---------------------------------------------------------
    # SOFTWARE INSTALLATION
    # ---------------------------------------------------------
    software_keywords = [
        "software",
        "install software",
        "software installation",
        "install application",
        "application installation",
        "non-catalog",
        "non catalog",
        "app installation",
        "productivity browser extension",
        "browser extension",
    ]

    if any(keyword in text for keyword in software_keywords):
        return "software_installation"

    # ---------------------------------------------------------
    # PRINTER
    # ---------------------------------------------------------
    printer_keywords = [
        "printer",
        "printing",
        "print",
        "paper jam",
        "printer jam",
        "print spooler",
    ]

    if any(keyword in text for keyword in printer_keywords):
        return "printer"

    # ---------------------------------------------------------
    # MAILBOX
    # ---------------------------------------------------------
    mailbox_keywords = [
        "mailbox",
        "mailbox full",
        "email full",
        "email storage",
        "mailbox quota",
        "quota",
        "mail storage",
    ]

    if any(keyword in text for keyword in mailbox_keywords):
        return "mailbox"

    # ---------------------------------------------------------
    # GUEST WIFI
    # ---------------------------------------------------------
    guest_wifi_keywords = [
        "guest wifi",
        "guest wi-fi",
        "guest access",
        "guest internet",
        "wifi for guest",
        "wifi access for guest",
    ]

    if any(keyword in text for keyword in guest_wifi_keywords):
        return "guest_wifi"

    # ---------------------------------------------------------
    # EXPENSE SOFTWARE
    # ---------------------------------------------------------
    expense_keywords = [
        "expense software",
        "expense tool",
        "expense application",
        "expense app",
        "expense login",
        "cannot login to expense",
        "can't login to expense",
    ]

    if any(keyword in text for keyword in expense_keywords):
        return "expense_access"

    # ---------------------------------------------------------
    # WORK FROM HOME EQUIPMENT
    # ---------------------------------------------------------
    wfh_keywords = [
        "wfh",
        "work from home",
        "home office",
        "home office equipment",
        "remote work equipment",
        "monitor for home",
        "chair for home",
        "home monitor",
    ]

    if any(keyword in text for keyword in wfh_keywords):
        return "wfh_equipment"

    # ---------------------------------------------------------
    # ADMIN ACCESS
    # ---------------------------------------------------------
    admin_keywords = [
        "admin access",
        "administrator access",
        "server access",
        "admin permission",
        "administrative access",
        "access to finance server",
        "access finance reporting server",
    ]

    if any(keyword in text for keyword in admin_keywords):
        return "admin_access"

    # ---------------------------------------------------------
    # UNKNOWN
    # ---------------------------------------------------------
    return "unknown"


def decide(intent: str, message: str) -> dict:
    """
    Determine the action the agent should take.

    Possible actions:
    - provide_instructions
    - escalate_to_it
    - escalate_security
    - human_review
    - ask_follow_up
    """

    text = normalize_message(message)

    # =========================================================
    # PASSWORD RESET
    # =========================================================
    if intent == "password_reset":

        failed_attempts = re.search(
            r"(\d+)\s*(?:failed\s*)?(?:attempts?|times?)",
            text
        )

        if failed_attempts:
            attempts = int(failed_attempts.group(1))

            if attempts >= 5:
                return {
                    "action": "escalate_to_it",
                    "reason": (
                        "The employee reports that the account was locked "
                        "after multiple failed password attempts."
                    ),
                }

        if any(
            phrase in text
            for phrase in [
                "locked out",
                "account locked",
                "cannot login",
                "can't login",
                "unable to login",
            ]
        ):
            return {
                "action": "escalate_to_it",
                "reason": (
                    "The employee appears to be locked out and requires "
                    "IT assistance according to the password reset policy."
                ),
            }

        return {
            "action": "provide_instructions",
            "reason": (
                "The employee can use the self-service password reset "
                "process."
            ),
        }

    # =========================================================
    # SECURITY INCIDENT
    # =========================================================
    if intent == "security_incident":
        return {
            "action": "escalate_security",
            "reason": (
                "The request involves a potential security incident "
                "such as phishing, malware, or unauthorized access."
            ),
        }

    # =========================================================
    # GUEST WIFI
    # =========================================================
    if intent == "guest_wifi":
        return {
            "action": "provide_instructions",
            "reason": (
                "Guest Wi-Fi credentials can be generated through the "
                "front-desk kiosk."
            ),
        }

    # =========================================================
    # EXPENSE ACCESS
    # =========================================================
    if intent == "expense_access":
        if any(
            phrase in text
            for phrase in [
                "cannot login",
                "can't login",
                "login issue",
                "not able to login",
                "technical issue",
            ]
        ):
            return {
                "action": "escalate_to_it",
                "reason": (
                    "IT can assist with technical or login issues once "
                    "the Finance-managed expense account exists."
                ),
            }

        return {
            "action": "human_review",
            "reason": (
                "Expense software access is granted by Finance rather "
                "than IT."
            ),
        }

    # =========================================================
    # VPN
    # =========================================================
    if intent == "vpn_access":

        if "contractor" in text:
            return {
                "action": "human_review",
                "reason": (
                    "Contractors require manager approval through the "
                    "access request form for VPN access."
                ),
            }

        if any(
            phrase in text
            for phrase in [
                "expired",
                "credential expired",
                "credentials expired",
            ]
        ):
            return {
                "action": "escalate_to_it",
                "reason": (
                    "The employee reports expired VPN credentials."
                ),
            }

        return {
            "action": "provide_instructions",
            "reason": (
                "Full-time employees receive VPN access automatically; "
                "VPN credentials expire every 90 days and must be renewed."
            ),
        }

    # =========================================================
    # SOFTWARE INSTALLATION
    # =========================================================
    if intent == "software_installation":

        if any(
            phrase in text
            for phrase in [
                "non-catalog",
                "non catalog",
                "browser extension",
                "extension",
            ]
        ):
            return {
                "action": "human_review",
                "reason": (
                    "Non-catalog software requires IT Security review "
                    "before installation."
                ),
            }

        return {
            "action": "provide_instructions",
            "reason": (
                "Standard software available in the company catalog "
                "can be self-installed."
            ),
        }

    # =========================================================
    # PRINTER
    # =========================================================
    if intent == "printer":

        if "paper jam" in text:
            return {
                "action": "provide_instructions",
                "reason": (
                    "The employee should check the printer queue and "
                    "restart the print spooler. If the issue persists, "
                    "a ticket should be logged with the printer asset tag."
                ),
            }

        return {
            "action": "provide_instructions",
            "reason": (
                "The employee should check the print queue and restart "
                "the print spooler."
            ),
        }

    # =========================================================
    # MAILBOX
    # =========================================================
    if intent == "mailbox":

        if any(
            phrase in text
            for phrase in [
                "increase",
                "increase quota",
                "more storage",
                "increase mailbox",
            ]
        ):
            return {
                "action": "human_review",
                "reason": (
                    "Mailbox increases above the default 25GB require "
                    "manager approval and are capped at 50GB."
                ),
            }

        return {
            "action": "provide_instructions",
            "reason": (
                "The default mailbox size is 25GB. The employee should "
                "archive old mail when the mailbox is full."
            ),
        }

    # =========================================================
    # WFH EQUIPMENT
    # =========================================================
    if intent == "wfh_equipment":

        return {
            "action": "human_review",
            "reason": (
                "WFH equipment eligibility requires manager sign-off "
                "and Finance processing before IT ships the equipment."
            ),
        }

    # =========================================================
    # LAPTOP
    # =========================================================
    if intent == "laptop":

        # Hardware failure
        if any(
            phrase in text
            for phrase in [
                "dead",
                "hardware failure",
                "hardware problem",
                "screen flickering",
                "screen broken",
            ]
        ):
            return {
                "action": "human_review",
                "reason": (
                    "The request may involve verified hardware failure. "
                    "Laptop replacement eligibility depends on the "
                    "replacement policy and hardware verification."
                ),
            }

        return {
            "action": "human_review",
            "reason": (
                "Laptop replacement eligibility depends on the "
                "four-year refresh cycle or verified hardware failure."
            ),
        }

    # =========================================================
    # ADMIN ACCESS
    # =========================================================
    if intent == "admin_access":

        return {
            "action": "human_review",
            "reason": (
                "Administrative/server access requires human review "
                "and appropriate justification/approval."
            ),
        }

    # =========================================================
    # UNKNOWN / UNCLEAR REQUEST
    # =========================================================
    return {
        "action": "ask_follow_up",
        "reason": (
            "I need a little more information before I can determine "
            "the correct IT support workflow."
        ),
        "follow_up_question": (
            "Could you describe what is not working and tell me whether "
            "this involves your laptop, VPN, software, printer, email, "
            "Wi-Fi, or another IT service?"
        ),
    }