import uvicorn
from utils.config import HOST, PORT
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.resume import router as resume_router
from routes.interview import router as interview_router
from routes.evaluation import router as evaluation_router
from routes.report import router as report_router

app = FastAPI(
    title="InterviewIQ AI Backend",
    description="AI-powered Interview Coach API featuring Resume Parsing, Whisper STT, and Sentence-BERT Evaluator.",
    version="1.0.0"
)

# CORS configuration
# Allows requests from Vite React frontend (usually port 5173 or 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for MVP simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(resume_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(evaluation_router, prefix="/api")
app.include_router(report_router, prefix="/api")

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

@app.get("/")
async def health_check():
    """
    Simple check endpoint to verify backend status.
    """
    return {
        "status": "healthy",
        "service": "InterviewIQ AI API",
        "message": "Welcome! The interview coach services are ready."
    }

if __name__ == "__main__":
    import os
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_dirs=[backend_dir],
    )
