"""
Interview session business logic — keeps route handlers thin.
"""
from utils.session_store import sessions_db


def get_session_or_none(session_id: str):
    return sessions_db.get(session_id)


def save_evaluation(session_id: str, question_id: int, candidate_answer: str, eval_result: dict) -> None:
    session = sessions_db[session_id]
    session["answers"][question_id] = candidate_answer
    session["evaluations"][question_id] = eval_result
    sessions_db.persist(session_id)


def mark_skipped(session_id: str, question_id: int) -> None:
    session = sessions_db[session_id]
    session["answers"][question_id] = "No response provided."
    session["evaluations"][question_id] = {
        "similarity_score": 0.0,
        "technical_score": 0.0,
        "strengths": ["No answer submitted."],
        "weaknesses": ["Candidate skipped this question."],
        "suggestions": ["Answer all questions to receive comprehensive evaluations."],
    }
    sessions_db.persist(session_id)
