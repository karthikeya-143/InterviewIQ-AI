import os
import re

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from utils.config import SBERT_MODEL


class AnswerEvaluator:
    """
    Evaluates candidate answers against reference answers.
    Computes semantic similarity using Sentence-BERT, maps it to a 10-point scale,
    and generates detailed feedback (Strengths, Weaknesses, Suggestions).
    """
    def __init__(self):
        self.model_name = SBERT_MODEL
        self.model = None
        self.initialized = False

    def _lazy_init_model(self):
        if not self.initialized and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print(f"Initializing Sentence-BERT model '{self.model_name}'...")
                self.model = SentenceTransformer(self.model_name)
                self.initialized = True
                print("Sentence-BERT loaded successfully.")
            except Exception as e:
                print(f"Warning: Failed to load Sentence-BERT: {e}. Falling back to TF-IDF cosine similarity.")
                self.initialized = True

    def evaluate(self, question: str, reference_answer: str, candidate_answer: str) -> dict:
        """
        Main evaluation function.
        Compares candidate answer against reference answer.
        """
        self._lazy_init_model()
        
        # Clean answers
        ref_clean = reference_answer.strip()
        cand_clean = candidate_answer.strip()
        
        # Edge case: candidate answer is empty or extremely short
        if len(cand_clean) < 5:
            return {
                "similarity_score": 0.0,
                "technical_score": 0.0,
                "strengths": ["None identified (Response was too short)."],
                "weaknesses": ["Candidate did not provide a substantial answer."],
                "suggestions": ["Please try to explain the concept in at least 2-3 sentences."]
            }
            
        similarity = 0.0
        
        # 1. Try Sentence-BERT
        if self.model:
            try:
                emb_ref = self.model.encode(ref_clean, convert_to_tensor=True)
                emb_cand = self.model.encode(cand_clean, convert_to_tensor=True)
                similarity = util.cos_sim(emb_ref, emb_cand).item()
                # Cosine similarity can theoretically be negative, keep it non-negative
                similarity = max(0.0, similarity)
            except Exception as e:
                print(f"Sentence-BERT evaluation error: {e}. Trying TF-IDF fallback...")
                similarity = -1.0 # trigger fallback
                
        # 2. Try TF-IDF Cosine Similarity Fallback
        if (similarity < 0.0 or not self.model) and SKLEARN_AVAILABLE:
            try:
                vectorizer = TfidfVectorizer().fit_transform([ref_clean, cand_clean])
                vectors = vectorizer.toarray()
                similarity = float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])
            except Exception as e:
                print(f"TF-IDF evaluation error: {e}. Using backup string matching...")
                # Backup character/word intersection similarity
                w1 = set(ref_clean.lower().split())
                w2 = set(cand_clean.lower().split())
                if w1:
                    similarity = len(w1.intersection(w2)) / len(w1)
                else:
                    similarity = 0.5
        elif not self.model and not SKLEARN_AVAILABLE:
            # Absolute fallback if no libraries loaded
            w1 = set(ref_clean.lower().split())
            w2 = set(cand_clean.lower().split())
            similarity = len(w1.intersection(w2)) / len(w1) if w1 else 0.5

        # Normalize score bounds
        similarity = min(1.0, max(0.0, similarity))
        
        # Map Similarity Score to Technical Score (0 to 10 scale)
        # E.g. Similarity of 0.85 maps to 8.5/10
        technical_score = round(similarity * 10, 1)
        
        # 3. Generate Strengths, Weaknesses, Suggestions
        feedback = self._generate_feedback(question, ref_clean, cand_clean, technical_score)
        
        return {
            "similarity_score": round(similarity, 2),
            "technical_score": technical_score,
            "strengths": feedback["strengths"],
            "weaknesses": feedback["weaknesses"],
            "suggestions": feedback["suggestions"]
        }

    def _generate_feedback(self, question: str, reference: str, candidate: str, score: float) -> dict:
        """
        Dynamically analyzes the text to find matching concepts or gaps.
        """
        strengths = []
        weaknesses = []
        suggestions = []
        
        cand_lower = candidate.lower()
        question_lower = question.lower()
        
        # General threshold-based feedback
        if score >= 8.5:
            strengths.append("Excellent conceptual accuracy and terminology matching.")
            suggestions.append("Keep up the high level of detail; try to include professional industry examples in real interviews.")
        elif score >= 6.0:
            strengths.append("Demonstrated a good basic understanding of the concept.")
            suggestions.append("Structure your answers by first defining the term, then giving technical details, and ending with a practical use case.")
        else:
            weaknesses.append("The response lacks sufficient detail or misses key aspects of the definition.")
            suggestions.append("Review the reference definition and practice explaining the core mechanics step-by-step.")

        # Question-specific semantic checks
        
        # 1. CNN specific questions
        if "cnn" in question_lower or "convolutional" in question_lower:
            # Check for convolution operation
            if "convolution" in cand_lower or "kernel" in cand_lower or "filter" in cand_lower:
                strengths.append("Correctly identified convolution operations/filters as the core feature extraction mechanism.")
            else:
                weaknesses.append("Missed explaining how convolution kernels or filters extract spatial features.")
                suggestions.append("Explain that CNNs use sliding filters (kernels) to automatically extract low-level features like edges.")
                
            # Check for pooling
            if "pool" in cand_lower or "subsample" in cand_lower or "sampling" in cand_lower:
                strengths.append("Demonstrated understanding of pooling/downsampling for dimensionality reduction.")
            else:
                weaknesses.append("Did not mention pooling layers (like Max Pooling) which help reduce dimensions.")
                suggestions.append("Discuss how pooling layers reduce the spatial size of representation to lower parameters and prevent overfitting.")
                
            # Check for image/spatial
            if "image" in cand_lower or "spatial" in cand_lower or "visual" in cand_lower:
                strengths.append("Accurately connected CNN architectures to image and spatial grid processing.")
            else:
                weaknesses.append("Failed to clearly state why CNN is preferred specifically for images compared to dense layers.")
                suggestions.append("Highlight that CNNs preserve spatial relationships in 2D grid inputs, unlike fully connected layers.")

        # 2. Python List vs Tuple
        elif "list" in question_lower and "tuple" in question_lower:
            if "mutab" in cand_lower: # matches mutable / immutability
                strengths.append("Correctly identified the primary difference of mutability between lists and tuples.")
            else:
                weaknesses.append("Omitted the foundational concept of mutability (list is changeable, tuple is not).")
                suggestions.append("Begin your explanation by stating that lists are mutable and tuples are immutable.")
                
            if "memory" in cand_lower or "speed" in cand_lower or "perform" in cand_lower or "faster" in cand_lower:
                strengths.append("Understood the performance and memory differences (tuples are lightweight/faster).")
            else:
                weaknesses.append("Did not mention the performance advantages of tuples (less memory, faster access).")
                suggestions.append("Mention that tuples are stored in a single block of memory, making them faster and more lightweight.")

        # 3. Python GIL
        elif "gil" in question_lower or "interpreter lock" in question_lower:
            if "single thread" in cand_lower or "one thread" in cand_lower or "prevent" in cand_lower:
                strengths.append("Correctly noted that GIL limits execution of bytecode to one thread at a time.")
            else:
                weaknesses.append("Did not clearly explain how the GIL prevents true parallel execution in CPU-bound threads.")
                suggestions.append("Explain that the GIL ensures thread safety in Python but restricts Python to single-threaded CPU execution.")
                
            if "multiprocess" in cand_lower or "process" in cand_lower:
                strengths.append("Good mention of multiprocessing as a solution to bypass GIL restrictions.")
            else:
                suggestions.append("Recommend using Python's multiprocessing module or running heavy computations in C/C++ extensions to bypass GIL.")

        # 4. Overfitting questions
        elif "overfitting" in question_lower:
            if "dropout" in cand_lower or "regular" in cand_lower or "early stop" in cand_lower or "augment" in cand_lower:
                strengths.append("Identified concrete techniques to combat overfitting (e.g., dropout, regularization, data augmentation).")
            else:
                weaknesses.append("Failed to suggest specific techniques to prevent overfitting in deep learning models.")
                suggestions.append("Discuss specific regularization techniques, such as Dropout, L1/L2 regularization, or Early Stopping.")
                
            if "memorize" in cand_lower or "noise" in cand_lower or "general" in cand_lower:
                strengths.append("Accurately defined overfitting as learning noise or failing to generalize.")
            else:
                weaknesses.append("Omitted explaining the root cause of overfitting (high variance, learning training noise).")
                suggestions.append("Explain that overfitting happens when a model learns training data details too well, making it fail on unseen data.")

        # 5. React Virtual DOM
        elif "virtual dom" in question_lower:
            if "memory" in cand_lower or "representation" in cand_lower or "copy" in cand_lower:
                strengths.append("Defined the Virtual DOM correctly as an in-memory representation of the real DOM.")
            if "diff" in cand_lower or "reconcil" in cand_lower or "compare" in cand_lower:
                strengths.append("Explained the reconciliation/diffing process and batching DOM updates.")
            else:
                weaknesses.append("Omitted how React diffs the old and new trees to update only what changed.")
                suggestions.append("Detail the diffing algorithm (reconciliation) that React runs to find modified elements and batch write updates.")

        # Clean duplicates
        strengths = sorted(list(set(strengths)))
        weaknesses = sorted(list(set(weaknesses)))
        suggestions = sorted(list(set(suggestions)))
        
        # Ensure we always return at least one strength/weakness/suggestion
        if not strengths:
            strengths.append("Provided a relevant answer that aligns with the topic domain.")
        if not weaknesses:
            weaknesses.append("No critical structural gaps identified.")
        if not suggestions:
            suggestions.append("Continue to practice articulating the concept clearly with professional vocabulary.")
            
        return {
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "suggestions": suggestions[:3]
        }

if __name__ == "__main__":
    evaluator = AnswerEvaluator()
    ref = "CNN automatically extracts image features using convolution and pooling operations."
    cand = "CNN learns features from image files using convolution filters. It is very useful."
    res = evaluator.evaluate("Explain CNN", ref, cand)
    print(res)
