from pydantic import BaseModel
from typing import List, Optional

class StartRequest(BaseModel):
    message: str

class AnswerRequest(BaseModel):
    session_id: str
    selected_option: str

class Hypothesis(BaseModel):
    name: str
    description: str
    probability: float
    key_evidence: List[str]

class QuestionResponse(BaseModel):
    question: str
    options: List[str]
    reasoning: Optional[str] = None
    targets: Optional[List[str]] = None
