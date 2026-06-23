from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from utils.session_store import sessions_db
from ai_models.evaluator import AnswerEvaluator

router = APIRouter(prefix="/interview", tags=["Evaluation"])
evaluator = AnswerEvaluator()

class EvaluateAnswerRequest(BaseModel):
    session_id: str
    question_id: int
    candidate_answer: str

class EvaluateAnswerResponse(BaseModel):
    question_id: int
    candidate_answer: str
    reference_answer: str
    similarity_score: float
    technical_score: float
    strengths: list
    weaknesses: list
    suggestions: list

@router.post("/evaluate", response_model=EvaluateAnswerResponse)
async def evaluate_answer(payload: EvaluateAnswerRequest):
    """
    Compares the candidate's transcribed answer with the reference answer.
    Computes scores and stores them in session state.
    """
    session_id = payload.session_id
    question_id = payload.question_id
    candidate_ans = payload.candidate_answer

    # Validate session
    if session_id not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active interview session not found. Please upload resume and start interview again."
        )

    session = sessions_db[session_id]
    
    # Find matching question in session
    target_q = None
    for q in session["questions"]:
        if q["id"] == question_id:
            target_q = q
            break
            
    if not target_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question with ID {question_id} not found in this session."
        )
        
    try:
        # Run evaluation service
        eval_result = evaluator.evaluate(
            question=target_q["question"],
            reference_answer=target_q["reference_answer"],
            candidate_answer=candidate_ans
        )
        
        # Save candidate answer and evaluation to session memory
        session["answers"][question_id] = candidate_ans
        session["evaluations"][question_id] = eval_result
        
        return EvaluateAnswerResponse(
            question_id=question_id,
            candidate_answer=candidate_ans,
            reference_answer=target_q["reference_answer"],
            similarity_score=eval_result["similarity_score"],
            technical_score=eval_result["technical_score"],
            strengths=eval_result["strengths"],
            weaknesses=eval_result["weaknesses"],
            suggestions=eval_result["suggestions"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate candidate answer: {str(e)}"
        )
