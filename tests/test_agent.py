from app.services.decision_engine import classify_intent,decide
def test_password_lockout():
    m="I am locked out and tried my password 6 times"; i=classify_intent(m); assert i=="password_reset"; assert decide(i,m)["action"]=="escalate_to_it"
def test_phishing():
    m="I received a phishing email asking for my login"; i=classify_intent(m); assert i=="security_incident"; assert decide(i,m)["action"]=="escalate_security"
def test_guest_wifi():
    m="Can I get guest wifi tomorrow?"; assert classify_intent(m)=="guest_wifi"
