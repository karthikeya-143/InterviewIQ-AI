# InterviewIQ AI - AI-Powered Mock Interview Coach

InterviewIQ AI is an intelligent mock interview platform designed to help software engineering candidates prepare for technical, project-based, and HR screenings. It parses the candidate's resume, generates personalized questions, captures audio answers, performs automated speech-to-text transcription, and evaluates the semantic quality of answers using local deep learning models.

---

## 🚀 Key Features

- **Resume Upload & Parsing**: Parses PDF resumes to extract core skills, technologies, education, projects, and certifications.
- **Dynamic Q&A Generation**: Uses local NLP heuristics and text-generation transformers to formulate 10 custom interview questions (5 Technical, 3 Project-Based, 2 HR/Behavioral) and matching target answers.
- **Voice Interview Simulator**: Interactive session room with speech visualization that records voice responses using the browser HTML5 MediaRecorder.
- **Whisper Speech-to-Text**: Transcribes WAV/WebM speech audio responses into high-fidelity text transcripts using OpenAI's `whisper-tiny` model.
- **Sentence-BERT Semantic Scoring**: Calculates cosine similarity embeddings between the candidate's answer and reference answer using Sentence-BERT (`all-MiniLM-L6-v2`) to derive a 10-point Technical Score.
- **Performance Dashboard**: Beautiful, glassmorphic dark-mode interface summarizing overall percentage scores, strengths, conceptual gaps, actionable tips, and per-question breakdowns.
- **Dual Answer Modes**: Record voice answers via microphone or type text responses directly.
- **Session Persistence**: Interview sessions saved to `backend/data/sessions.json` survive server restarts.

---

## 🛠️ Technology Stack

- **Frontend**: React.js, Tailwind CSS v3, Axios, React Router, Lucide React Icons
- **Backend**: FastAPI, Python (Uvicorn server)
- **Deep Learning & NLP**:
  - Sentence-BERT (`sentence-transformers/all-MiniLM-L6-v2`) for answer matching
  - Whisper (`openai/whisper-tiny` pipeline) for audio transcription
  - Seq2Seq (`google/flan-t5-small` pipeline) for question generation fallback
  - `pdfplumber` for PDF parsing heuristics
  - `scikit-learn` for TF-IDF cosine similarity fallbacks
  - `librosa` and `soundfile` for audio decoding and 16kHz resampling
- **Utilities**: NumPy, Pandas, Pydantic, Uuid, unittest

---

## 📂 Production-Ready Directory Structure

```text
InterviewIQ AI/
├── backend/
│   ├── ai_models/
│   │   ├── resume_parser.py
│   │   ├── question_generator.py
│   │   ├── reference_answer_generator.py
│   │   ├── whisper_service.py
│   │   └── evaluator.py
│   ├── routes/
│   │   ├── resume.py
│   │   ├── interview.py
│   │   ├── evaluation.py
│   │   └── report.py
│   ├── services/
│   │   └── interview_service.py
│   ├── utils/
│   │   ├── config.py
│   │   └── session_store.py
│   ├── main.py
│   ├── test_app.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── ResumeUpload.jsx
│   │   │   ├── ResumeAnalysis.jsx
│   │   │   ├── Interview.jsx
│   │   │   ├── Results.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── routes/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   └── favicon.svg
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── .env.example
└── README.md
```

---

## 💻 Installation & Setup Guide (Windows)

Follow these steps to run the application entirely locally on your system:

### Prerequisites
- [Miniconda](https://docs.anaconda.com/miniconda/) or Python 3.10+
- [Node.js](https://nodejs.org/) (v18 or higher)
- npm (v9 or higher)

---

### Step 1: Clone and Set Up the Backend

1. Navigate to the project root directory:
   ```powershell
   cd "c:\Users\DELL\OneDrive\Documents\InterviewIQ AI"
   ```
2. Create and activate a Python virtual environment (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   pip install -r backend/requirements.txt
   ```

---

### Step 2: Download AI Model Weights (Automatic on First Run)
When you start the backend server for the first time, it will automatically download the lightweight open-source weights from Hugging Face:
- `all-MiniLM-L6-v2` (~90 MB)
- `whisper-tiny` (~150 MB)
- `flan-t5-small` (~300 MB)

*Note: Ensure you have an active internet connection on first run. Subsequent runs execute completely offline.*

---

### Step 3: Set Up the Frontend

1. Navigate to the frontend folder:
   ```powershell
   cd frontend
   ```
2. Install Node dependencies:
   ```powershell
   npm install
   ```

---

## 🏃 Run the Application

You need to run both the backend and frontend servers in separate command windows:

### Start FastAPI Backend
1. Open a terminal, go to project root, and activate virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
2. Run the FastAPI development server:
   ```powershell
   python backend/main.py
   ```
   The backend will start and listen on **`http://127.0.0.1:8000`**. You can view Swagger documentation at `http://127.0.0.1:8000/docs`.

### Start Vite React Frontend
1. Open a second terminal, navigate to the `frontend` folder:
   ```powershell
   cd frontend
   ```
2. Launch Vite development server:
   ```powershell
   npm run dev
   ```
   The application will start on **`http://localhost:5173`** (or the port specified in terminal outputs). Open this link in your browser to start practicing!

---

## 🧪 Run Backend Automated Tests
To run unit and integration tests verifying the pipeline logic:
```powershell
python backend/test_app.py
```

## Author

B.karthikeya
