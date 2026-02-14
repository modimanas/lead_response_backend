import uuid

sessions = {}

def create_session(original_message, intent_data):
    """Create a new diagnostic session with hypotheses"""
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "original_message": original_message,
        "main_issue": intent_data.get("main_issue", ""),
        "risk_level": intent_data.get("risk_level", "low"),
        "hypotheses": intent_data.get("hypotheses", []),
        "answers_history": [],  # Track all Q&A pairs
        "asked_questions": [],
        "answer_count": 0
    }

    return session_id

def get_session(session_id):
    """Get session data"""
    return sessions.get(session_id)

def add_answer_to_session(session_id, question, answer):
    """Add an answer to the session's history"""
    session = sessions.get(session_id)
    if session:
        session["answers_history"].append({
            "question": question,
            "answer": answer
        })
        # Only add to asked_questions if it's not already there (avoid duplicates)
        if question not in session["asked_questions"]:
            session["asked_questions"].append(question)
        session["answer_count"] += 1

def update_hypotheses(session_id, updated_hypotheses):
    """Update hypotheses in session"""
    session = sessions.get(session_id)
    if session:
        session["hypotheses"] = updated_hypotheses

def delete_session(session_id):
    """Delete session after completion"""
    if session_id in sessions:
        del sessions[session_id]
