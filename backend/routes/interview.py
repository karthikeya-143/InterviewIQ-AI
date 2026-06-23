import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from ai_models.question_generator import QuestionGenerator
from ai_models.reference_answer_generator import ReferenceAnswerGenerator
from ai_models.whisper_service import WhisperService
from utils.session_store import sessions_db
from services.interview_service import mark_skipped

router = APIRouter(prefix="/interview", tags=["Interview"])

q_gen = QuestionGenerator()
ans_gen = ReferenceAnswerGenerator()
whisper_srv = WhisperService()

TEMP_AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)


class StartInterviewRequest(BaseModel):
    skills: List[str]
    projects: List[str]
    technologies: List[str]
    education: List[str] = []
    certifications: List[str] = []


class QuestionSchema(BaseModel):
    id: int
    question: str
    category: str


class StartInterviewResponse(BaseModel):
    session_id: str
    questions: List[QuestionSchema]


class TranscribeResponse(BaseModel):
    transcript: str
    used_fallback: bool = False


class SkipQuestionRequest(BaseModel):
    session_id: str
    question_id: int


class SkipQuestionResponse(BaseModel):
    question_id: int
    message: str


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(payload: StartInterviewRequest):
    """
    Starts a new mock interview session based on resume metadata.
    Generates 10 custom questions and their reference answers, saving them in session storage.
    """
    try:
        resume_data = {
            "skills": payload.skills,
            "projects": payload.projects,
            "technologies": payload.technologies,
            "education": payload.education,
            "certifications": payload.certifications,
        }

        generated_questions = q_gen.generate(resume_data)

        full_questions_list = []
        for item in generated_questions:
            ref_ans = ans_gen.generate_answer(item["question"], item["category"])
            full_questions_list.append({
                "id": item["id"],
                "question": item["question"],
                "category": item["category"],
                "reference_answer": ref_ans,
            })

        session_id = str(uuid.uuid4())

        sessions_db[session_id] = {
            "resume_data": resume_data,
            "questions": full_questions_list,
            "answers": {},
            "evaluations": {},
        }

        response_questions = [
            QuestionSchema(id=q["id"], question=q["question"], category=q["category"])
            for q in full_questions_list
        ]

        return StartInterviewResponse(
            session_id=session_id,
            questions=response_questions,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize interview session: {str(e)}",
        )


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    question_text: Optional[str] = Form(None),
):
    """Transcribes candidate response audio using local Whisper engine."""
    filename = file.filename.lower()
    allowed_extensions = (".wav", ".webm", ".mp3", ".ogg", ".m4a")
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported audio format. Supported: WAV, WebM, MP3, OGG, M4A.",
        )

    temp_file_path = os.path.join(TEMP_AUDIO_DIR, f"{uuid.uuid4()}_{file.filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = whisper_srv.transcribe(temp_file_path, question_text)

        return TranscribeResponse(
            transcript=result["transcript"],
            used_fallback=result.get("used_fallback", False),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(e)}",
        )
    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError as e:
                print(f"Error removing temp audio file: {e}")


@router.post("/skip", response_model=SkipQuestionResponse)
async def skip_question(payload: SkipQuestionRequest):
    """Marks a question as skipped with zero score so the candidate can proceed."""
    session_id = payload.session_id
    question_id = payload.question_id

    if session_id not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active interview session not found.",
        )

    session = sessions_db[session_id]
    target_q = next((q for q in session["questions"] if q["id"] == question_id), None)
    if not target_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question with ID {question_id} not found in this session.",
        )

    mark_skipped(session_id, question_id)

    return SkipQuestionResponse(
        question_id=question_id,
        message="Question skipped. You may proceed to the next question.",
    )
