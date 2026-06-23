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

router = APIRouter(prefix="/interview", tags=["Interview"])

# Reusable instances
q_gen = QuestionGenerator()
ans_gen = ReferenceAnswerGenerator()
whisper_srv = WhisperService()

# Temp directories for audio uploads
TEMP_AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Pydantic Schemas
class StartInterviewRequest(BaseModel):
    skills: List[str]
    projects: List[str]
    technologies: List[str]

class QuestionSchema(BaseModel):
    id: int
    question: str
    category: str

class StartInterviewResponse(BaseModel):
    session_id: str
    questions: List[QuestionSchema]

class TranscribeResponse(BaseModel):
    transcript: str

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
            "technologies": payload.technologies
        }
        
        # Generate the questions
        generated_questions = q_gen.generate(resume_data)
        
        # Populate reference answers for each question and save
        full_questions_list = []
        for item in generated_questions:
            ref_ans = ans_gen.generate_answer(item["question"], item["category"])
            full_questions_list.append({
                "id": item["id"],
                "question": item["question"],
                "category": item["category"],
                "reference_answer": ref_ans
            })
            
        # Create session ID
        session_id = str(uuid.uuid4())
        
        # Save session data
        sessions_db[session_id] = {
            "resume_data": resume_data,
            "questions": full_questions_list,
            "answers": {},
            "evaluations": {}
        }
        
        # Prepare response (do NOT expose reference answers to client yet)
        response_questions = [
            QuestionSchema(id=q["id"], question=q["question"], category=q["category"])
            for q in full_questions_list
        ]
        
        return StartInterviewResponse(
            session_id=session_id,
            questions=response_questions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize interview session: {str(e)}"
        )

@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    question_text: Optional[str] = Form(None)
):
    """
    Transcribes candidate response audio using local Whisper engine.
    """
    # Accept common audio files (WAV, WEBM, MP3, OGG)
    filename = file.filename.lower()
    allowed_extensions = (".wav", ".webm", ".mp3", ".ogg", ".m4a")
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported audio format. Supported: WAV, WebM, MP3, OGG, M4A."
        )

    # Save to temp audio file
    temp_file_path = os.path.join(TEMP_AUDIO_DIR, f"{uuid.uuid4()}_{file.filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Perform transcription
        transcript = whisper_srv.transcribe(temp_file_path, question_text)
        
        return TranscribeResponse(transcript=transcript)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error removing temp audio file: {e}")
