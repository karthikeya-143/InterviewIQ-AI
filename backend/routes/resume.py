import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from ai_models.resume_parser import ResumeParser

router = APIRouter(prefix="/resume", tags=["Resume"])
parser = ResumeParser()

# Temporary upload folder
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

class ResumeResponse(BaseModel):
    skills: list
    projects: list
    technologies: list
    education: list
    certifications: list
    raw_text_preview: str

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Uploads a PDF resume, validates it, and extracts key entities.
    """
    # Validate PDF extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported."
        )
    
    # Save the file temporarily
    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Parse the resume
        parsed_data = parser.parse(temp_file_path)
        
        # Format response
        return ResumeResponse(
            skills=parsed_data["skills"],
            projects=parsed_data["projects"],
            technologies=parsed_data["technologies"],
            education=parsed_data["education"],
            certifications=parsed_data["certifications"],
            raw_text_preview=parsed_data["raw_text"][:800] # Limit preview to 800 chars
        )
        
    except ValueError as val_err:
        # Catch PDF parsing errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse resume contents: {str(val_err)}"
        )
    except Exception as e:
        # General exception handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading/processing the resume: {str(e)}"
        )
    finally:
        # Clean up the file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error cleaning up temp file {temp_file_path}: {e}")
