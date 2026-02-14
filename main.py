from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import StartRequest, AnswerRequest
from session_manager import create_session, get_session, add_answer_to_session, update_hypotheses, delete_session
from llm_engine import (
    extract_intent_and_hypotheses,
    generate_adaptive_question,
    update_hypotheses as update_hyp_scores,
    evaluate_confidence,
    generate_final_response
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "Backend running"}

@app.post("/start")
def start_session(request: StartRequest):
    """Start a new diagnostic session"""
    
    # Extract intent and generate initial hypotheses
    intent_data = extract_intent_and_hypotheses(request.message)
    
    if "error" in intent_data:
        return {"error": "Failed to process your enquiry"}
    
    # Create session with hypotheses
    session_id = create_session(request.message, intent_data)
    session = get_session(session_id)
    
    # Generate first question
    question_data = generate_adaptive_question(
        original_issue=session["main_issue"],
        hypotheses=session["hypotheses"],
        answers_history=[],
        asked_questions=[]
    )
    
    # Add first question to the asked_questions list
    first_question = question_data.get("question", "")
    if first_question:
        session["asked_questions"].append(first_question)
    
    return {
        "session_id": session_id,
        "issue_summary": session["main_issue"],
        "risk_level": session["risk_level"],
        "question": question_data.get("question", ""),
        "options": question_data.get("options", []),
        "why_asking": question_data.get("why_asking", question_data.get("reasoning", "")),
        "question_number": 1
    }

@app.post("/answer")
def answer_question(request: AnswerRequest):
    """Process user's answer and generate next question or final response"""
    
    session = get_session(request.session_id)
    if not session:
        return {"error": "Invalid session"}
    
    # Store the answer with the last question
    last_question = session["asked_questions"][-1] if session["asked_questions"] else "Initial question"
    add_answer_to_session(request.session_id, last_question, request.selected_option)
    
    # Update hypothesis probabilities based on this answer
    updated_hypotheses = update_hyp_scores(
        original_issue=session["main_issue"],
        hypotheses=session["hypotheses"],
        last_question=last_question,
        last_answer=request.selected_option
    )
    update_hypotheses(request.session_id, updated_hypotheses)
    session = get_session(request.session_id)  # Refresh session
    
    # Evaluate confidence
    confidence_data = evaluate_confidence(
        original_issue=session["main_issue"],
        hypotheses=session["hypotheses"],
        answers_count=session["answer_count"],
        issue_type="general"  # Automatically detected in function
    )
    
    confidence_score = confidence_data.get("confidence_score", 0.5)
    verdict = confidence_data.get("verdict", "CONTINUE")
    
    # ENFORCE MINIMUM 4 QUESTIONS before giving final answer
    # This ensures we get enough context from the user
    min_questions_before_stop = 4
    max_questions = 8
    
    should_stop = (
        (verdict == "STOP" and session["answer_count"] >= min_questions_before_stop) or
        session["answer_count"] >= max_questions
    )
    
    if should_stop:
        final_response = generate_final_response(
            original_issue=session["main_issue"],
            hypotheses=session["hypotheses"],
            answers_history=session["answers_history"],
            risk_level=session["risk_level"]
        )
        
        # Clean up session
        delete_session(request.session_id)
        
        return {
            "status": "completed",
            "confidence": confidence_score,
            "final_response": final_response
        }
    
    # Generate next question
    question_data = generate_adaptive_question(
        original_issue=session["main_issue"],
        hypotheses=session["hypotheses"],
        answers_history=session["answers_history"],
        asked_questions=session["asked_questions"]
    )
    
    # Add the new question to asked_questions list to avoid repeating it
    new_question = question_data.get("question", "")
    if new_question and new_question not in session["asked_questions"]:
        session["asked_questions"].append(new_question)
    
    return {
        "status": "continue",
        "confidence": confidence_score,
        "question": question_data.get("question", ""),
        "options": question_data.get("options", []),
        "why_asking": question_data.get("why_asking", question_data.get("reasoning", "")),
        "question_number": session["answer_count"] + 1,
        "top_hypothesis": sorted(session["hypotheses"], key=lambda x: x["probability"], reverse=True)[0]["name"]
    }

@app.post("/debug/session/{session_id}")
def debug_session(session_id: str):
    """Debug endpoint to see session state"""
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    
    return {
        "main_issue": session["main_issue"],
        "hypotheses": session["hypotheses"],
        "answers_count": session["answer_count"],
        "risk_level": session["risk_level"]
    }
