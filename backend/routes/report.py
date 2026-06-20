from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
from utils.session_store import sessions_db

router = APIRouter(prefix="/interview", tags=["Report"])

# Pydantic Schemas
class ReportRequest(BaseModel):
    session_id: str

class QuestionReportDetail(BaseModel):
    id: int
    question: str
    category: str
    candidate_answer: str
    reference_answer: str
    similarity_score: float
    technical_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]

class ReportResponse(BaseModel):
    overall_score: int
    technical_score: int
    average_similarity: int
    resume_summary: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    details: List[QuestionReportDetail]

@router.post("/report", response_model=ReportResponse)
async def generate_report(payload: ReportRequest):
    """
    Compiles session data and calculates final score metrics.
    Aggregates strengths, weaknesses, and actionable suggestions.
    """
    session_id = payload.session_id

    # Validate session
    if session_id not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found. Please verify the Session ID."
        )

    session = sessions_db[session_id]
    questions = session["questions"]
    answers = session["answers"]
    evaluations = session["evaluations"]

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No questions generated for this session."
        )

    # Gather detailed results per question
    detailed_questions = []
    total_similarity = 0.0
    total_technical = 0.0
    evaluated_count = 0
    
    # Aggregated lists
    aggregated_strengths = []
    aggregated_weaknesses = []
    aggregated_suggestions = []

    for q in questions:
        q_id = q["id"]
        
        # Check if candidate answered
        cand_ans = answers.get(q_id, "No response provided.")
        eval_data = evaluations.get(q_id, {
            "similarity_score": 0.0,
            "technical_score": 0.0,
            "strengths": ["No answer submitted."],
            "weaknesses": ["Candidate skipped this question."],
            "suggestions": ["Answer all questions to receive comprehensive evaluations."]
        })

        # Calculate averages for questions that were actually evaluated
        # If the candidate answer is "No response provided", we still count it as a 0 in overall metrics
        similarity = eval_data["similarity_score"]
        technical = eval_data["technical_score"]
        
        total_similarity += similarity
        total_technical += technical
        evaluated_count += 1

        # Populate detailed question stats
        detailed_questions.append(
            QuestionReportDetail(
                id=q_id,
                question=q["question"],
                category=q["category"],
                candidate_answer=cand_ans,
                reference_answer=q["reference_answer"],
                similarity_score=similarity,
                technical_score=technical,
                strengths=eval_data["strengths"],
                weaknesses=eval_data["weaknesses"],
                suggestions=eval_data["suggestions"]
            )
        )

        # Aggregate feedback (only from questions where a candidate provided an answer)
        if cand_ans != "No response provided.":
            # Filter out generic high-score suggestions or low-score warnings for clean aggregation
            for s in eval_data["strengths"]:
                if s not in aggregated_strengths and not s.startswith("Excellent") and not s.startswith("Provided a relevant"):
                    aggregated_strengths.append(s)
            for w in eval_data["weaknesses"]:
                if w not in aggregated_weaknesses and not w.startswith("No critical") and not w.startswith("Candidate skipped"):
                    aggregated_weaknesses.append(w)
            for sug in eval_data["suggestions"]:
                if sug not in aggregated_suggestions and not sug.startswith("Continue to") and not sug.startswith("Answer all"):
                    aggregated_suggestions.append(sug)

    # Compute averages
    avg_similarity_pct = 0
    avg_technical_pct = 0
    overall_score = 0
    
    if evaluated_count > 0:
        avg_similarity_pct = int(round((total_similarity / evaluated_count) * 100))
        # Technical score is on 0-10 scale, convert to percentage scale (0-100)
        avg_technical_pct = int(round((total_technical / evaluated_count) * 10))
        # Overall score can be average of both or equal to similarity percentage
        overall_score = int(round((avg_similarity_pct + avg_technical_pct) / 2))

    # Add default items if aggregated lists are empty
    if not aggregated_strengths:
        # Check if the user scored generally high
        if overall_score >= 80:
            aggregated_strengths.append("Strong technical vocabulary across multiple topics.")
            aggregated_strengths.append("Consistent accuracy matching standard reference definitions.")
        else:
            aggregated_strengths.append("Attempted multiple questions under simulated pressure.")
            
    if not aggregated_weaknesses:
        if overall_score < 70:
            aggregated_weaknesses.append("Descriptions lack specific architectural keywords and parameter settings.")
        else:
            aggregated_weaknesses.append("Slight brevity in explaining edge cases or optimizations.")
            
    if not aggregated_suggestions:
        if overall_score < 70:
            aggregated_suggestions.append("Spend more time defining foundational deep learning/NLP concepts before interviews.")
        else:
            aggregated_suggestions.append("Provide concrete project use cases when explaining system components.")

    # Deduplicate and limit to top 4 for a clean report UI
    return ReportResponse(
        overall_score=overall_score,
        technical_score=avg_technical_pct,
        average_similarity=avg_similarity_pct,
        resume_summary=session["resume_data"],
        strengths=list(set(aggregated_strengths))[:4],
        weaknesses=list(set(aggregated_weaknesses))[:4],
        suggestions=list(set(aggregated_suggestions))[:4],
        details=detailed_questions
    )
