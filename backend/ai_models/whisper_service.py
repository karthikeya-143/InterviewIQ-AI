import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

try:
    import torch
    import librosa
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from utils.config import WHISPER_MODEL


class WhisperService:
    """
    Service for transcribing candidate speech to text using Whisper.
    Uses openai/whisper-tiny for lightweight and fast local CPU inference.
    """
    def __init__(self):
        self.model_name = WHISPER_MODEL
        self.pipe = None
        self.initialized = False
        
        # Smart pre-seeded transcripts for demo fallback
        self.fallback_transcripts = {
            "What is the difference between a list and a tuple in Python, and when would you use each?":
                "A list in Python is mutable, so it can be changed. A tuple is immutable and cannot be modified once created. Tuples are faster and use less memory.",
            
            "Explain Python's Global Interpreter Lock (GIL) and how it affects multi-threaded applications.":
                "The GIL is a lock that makes sure only one thread executes Python code at a time in CPython. This means multi-threading does not speed up CPU bound tasks.",
            
            "How do you manage memory and handle garbage collection in Python?":
                "Python uses reference counting for memory management and automatic garbage collection. It also has a cycle detector to clean up cyclic references.",
            
            "What are decorators in Python, and how do they work?":
                "Decorators in Python allow us to wrap a function to extend its behavior without editing the actual function code. We write them with the at sign.",

            "Explain the difference between eager execution and graph execution in TensorFlow.":
                "Eager execution runs code immediately, which is great for debugging. Graph execution compiles the code first, which is better for speed and deployment.",
            
            "How does the tf.data API help in building efficient input pipelines in TensorFlow?":
                "The tf.data API helps load, preprocess and prefetch data on background threads, preventing CPU and GPU bottlenecks during training.",
            
            "What is overfitting, and how do you prevent it in TensorFlow using regularization or dropout?":
                "Overfitting is when a model memorizes training data. In TensorFlow, we can prevent it using dropout layers, early stopping, and weight regularization.",
            
            "Explain the role of optimizers in training a neural network in TensorFlow.":
                "Optimizers calculate weight updates based on loss gradients during backpropagation. Popular choices are Adam, RMSprop and SGD.",

            "What is autograd in PyTorch and how does it facilitate backpropagation?":
                "Autograd is PyTorch's automatic differentiation engine. It builds a graph during the forward pass and calculates gradients when backward is called.",
            
            "Explain the difference between Dataset and DataLoader classes in PyTorch.":
                "Dataset holds the samples and labels, while DataLoader wraps it to provide batching, shuffling and multi-process data loading.",

            "What is the Virtual DOM, and how does React use it to optimize rendering performance?":
                "The Virtual DOM is a copy of the real DOM in memory. React changes it first, diffs it, and then applies only the necessary changes to the real DOM.",
            
            "Explain the difference between React state and props, and how data flows in a React app.":
                "State is local data managed within a component. Props are read-only variables passed from parent to child components.",

            "What are the key advantages of FastAPI compared to Flask or Django?":
                "FastAPI is extremely fast, built on Starlette and Uvicorn. It supports asynchronous code natively and does auto validation using Pydantic."
        }

    def _lazy_init_model(self):
        """
        Lazily initializes the Whisper pipeline to minimize server startup time.
        """
        if not self.initialized and TRANSFORMERS_AVAILABLE:
            try:
                print(f"Initializing Whisper STT model '{self.model_name}'...")
                self.pipe = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_name,
                    device=-1  # Force CPU
                )
                self.initialized = True
                print("Whisper STT model loaded successfully.")
            except Exception as e:
                print(f"Warning: Could not load Whisper model: {e}. Falling back to mock audio transcriber.")
                self.initialized = True # Prevent continuous retries

    def transcribe(self, audio_file_path: str, question_text: str = None) -> dict:
        """
        Transcribes the given audio file path.
        Returns transcript text and whether a fallback was used.
        """
        self._lazy_init_model()
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        if self.pipe:
            try:
                audio_data, sr = librosa.load(audio_file_path, sr=16000, mono=True)
                result = self.pipe(audio_data)
                transcript = result.get("text", "").strip()
                
                if transcript:
                    return {"transcript": transcript, "used_fallback": False}
            except Exception as e:
                print(f"Whisper inference error: {e}. Attempting fallback...")

        return {
            "transcript": self._get_fallback_transcript(question_text),
            "used_fallback": True,
        }

    def _get_fallback_transcript(self, question_text: str) -> str:
        """
        Generates a realistic transcript based on the interview question.
        """
        if not question_text:
            return "I am submitting my response to the question. I believe my background and experience align well with these requirements."
            
        # Try to find matching question in database
        for q, transcript in self.fallback_transcripts.items():
            words_q = set(question_text.lower().split())
            words_k = set(q.lower().split())
            common = words_q.intersection(words_k)
            if len(common) > 5 and len(common) / len(words_k) > 0.6:
                return transcript

        # Generic CNN question transcript
        if "cnn" in question_text.lower():
            if "why" in question_text.lower():
                return "I chose CNN because it works really well for image classification. It automatically learns local spatial features like edges and patterns using filters."
            elif "architecture" in question_text.lower():
                return "A typical CNN has input layers, convolutional layers with Relu activation, max pooling layers, and then fully connected layers at the end."
            else:
                return "Convolutional neural networks are great for computer vision because they use kernels to extract features from images automatically."

        # Generic projects/HR transcripts
        if "project" in question_text.lower():
            return "For this project, I designed the system architecture, managed the data pipeline, and implemented the core deep learning models. We achieved high accuracy and deployed it."
        
        if "team" in question_text.lower() or "disagreement" in question_text.lower():
            return "When working in a team, I focus on clear communication. I listen to other members' points of view, and we try to find a consensus based on project goals."

        return f"Regarding '{question_text}', I have worked with these technologies extensively and applied them in my previous projects to solve complex problems."

if __name__ == "__main__":
    service = WhisperService()
    print("WhisperService loaded.")
