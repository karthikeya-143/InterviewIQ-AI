import os

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from utils.config import GENERATOR_MODEL


class ReferenceAnswerGenerator:
    """
    Generates reference answers for interview questions.
    Uses pre-defined professional answers for common questions,
    with a Seq2Seq transformer fallback for custom questions.
    """
    def __init__(self):
        self.model_name = GENERATOR_MODEL
        self.generator = None
        self.initialized_model = False
        
        # Predefined professional reference answers
        self.answer_db = {
            # Python
            "What is the difference between a list and a tuple in Python, and when would you use each?": 
                "A list is mutable, meaning its elements can be modified after creation, and is defined with square brackets []. A tuple is immutable, meaning it cannot be changed after creation, and is defined with parentheses (). Lists are slower than tuples and require more memory. Use lists for datasets that need to grow or change, and tuples for write-protected, fixed-size data configurations.",
            
            "Explain Python's Global Interpreter Lock (GIL) and how it affects multi-threaded applications.": 
                "The Global Interpreter Lock (GIL) is a mutex in the CPython implementation that prevents multiple native threads from executing Python bytecodes at once. It ensures thread safety but makes CPU-bound Python programs single-threaded in performance. To bypass GIL constraints, developers use multi-processing (using the multiprocessing module) instead of multi-threading for CPU-intensive tasks.",
            
            "How do you manage memory and handle garbage collection in Python?": 
                "Python manages memory automatically using a private heap. Garbage collection is done primarily via reference counting: Python tracks the number of references to each object and deallocates memory when reference counts drop to zero. To handle cyclic references (where two objects refer to each other), Python utilizes a cyclic garbage collector that periodically scans for and clears isolated cycles.",
            
            "What are decorators in Python, and how do they work?": 
                "Decorators in Python are a design pattern that allows a user to add new functionality to an existing object (like a function or class) without modifying its structure. They are written using the '@' symbol above the function definition and take the target function as an argument, wrap it with additional logic, and return the wrapper function.",

            # TensorFlow
            "Explain the difference between eager execution and graph execution in TensorFlow.": 
                "Eager execution evaluates operations immediately, returning concrete values, which makes debugging and prototyping highly intuitive. Graph execution builds a computational graph first, which is then compiled and optimized for deployment or parallelized execution. TensorFlow uses @tf.function to transition eager code into efficient symbolic graph execution.",
            
            "How does the tf.data API help in building efficient input pipelines in TensorFlow?": 
                "The tf.data API enables building complex input pipelines from simple, reusable pieces. It optimizes disk reads, batching, and preprocessing by running operations on background threads and prefetching data using CPU/GPU pipelining, minimizing the time the training loop waits for the next batch.",
            
            "What is overfitting, and how do you prevent it in TensorFlow using regularization or dropout?": 
                "Overfitting occurs when a deep learning model learns the training data's noise rather than general patterns, leading to poor generalization. In TensorFlow, it is prevented by adding L1/L2 weight regularization to layers, using Dropout layers (which randomly deactivate nodes during training), or employing EarlyStopping callbacks to halt training when validation loss stops improving.",
            
            "Explain the role of optimizers in training a neural network in TensorFlow.": 
                "Optimizers adjust the weights and biases of a neural network to minimize the loss function during training. They use the gradients computed during backpropagation. Popular optimizers in TensorFlow, like Adam, RMSprop, and SGD, adjust learning rates dynamically to help the model converge to a global minimum efficiently.",

            # PyTorch
            "What is autograd in PyTorch and how does it facilitate backpropagation?": 
                "Autograd is PyTorch's automatic differentiation engine. It records a graph of all operations performed on tensors during the forward pass. During the backward pass, calling '.backward()' on a scalar tensor computes the gradients of that tensor with respect to leaf tensors, automatically updating gradients for optimization.",
            
            "Explain the difference between Dataset and DataLoader classes in PyTorch.": 
                "In PyTorch, the 'Dataset' class is an abstract class representing a dataset, where you define '__len__' and '__getitem__' to fetch individual data items. The 'DataLoader' is a wrapper class that takes a Dataset and handles batching, shuffling, multi-process loading, and memory pinning for efficient model input feeding.",

            # React
            "What is the Virtual DOM, and how does React use it to optimize rendering performance?": 
                "The Virtual DOM is a lightweight, in-memory representation of the real DOM. When state changes, React builds a new Virtual DOM tree, compares it with the previous tree using a diffing algorithm (reconciliation), and updates only the changed parts of the real DOM. This minimizes expensive browser repaint operations.",
            
            "Explain the difference between React state and props, and how data flows in a React app.": 
                "State is private, local data managed inside a component that can change over time and trigger re-renders. Props are read-only configuration variables passed from a parent component down to child components. Data flows uni-directionally down from parents to children through props, and events flow upwards via callbacks.",

            # FastAPI
            "What are the key advantages of FastAPI compared to Flask or Django?": 
                "FastAPI is exceptionally fast (matching NodeJS and Go) because it runs on Starlette and Uvicorn. Key advantages include automatic data validation using Pydantic, automatic OpenAPI/Swagger documentation generation, native support for asynchronous programming (async/await), and type-hint-driven developer productivity."
        }

        # Project answers
        self.project_answer_prefix = (
            "A strong project answer should explain the problem domain, highlight the design decisions (such as choosing "
            "specific frameworks or architectures), detail the data pipeline (preprocessing, modeling, testing), and "
            "conclude with quantitative results (accuracy metrics, load testing, or user feedback) and key lessons learned."
        )

        # HR answers
        self.hr_answer_prefix = (
            "A model HR answer should use the STAR method: Describe the Situation, explain the Task at hand, "
            "detail the Actions you took, and summarize the Results achieved. Emphasize growth, teamwork, and problem-solving."
        )

    def _lazy_init_model(self):
        if not self.initialized_model and TRANSFORMERS_AVAILABLE:
            try:
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.initialized_model = True
            except Exception as e:
                print(f"Warning: Failed to load local reference answer generator model: {e}")
                self.initialized_model = True

    def generate_answer(self, question: str, category: str) -> str:
        """
        Retrieves or generates a reference answer for the given question.
        """
        self._lazy_init_model()
        
        # 1. Look in the expert database
        if question in self.answer_db:
            return self.answer_db[question]
            
        # 2. Key-based loose matching for technical questions
        question_lower = question.lower()
        for q_key, answer in self.answer_db.items():
            # If the user question contains significant portion of database question
            # or matches key terms (like GIL, Virtual DOM, etc.)
            words_q = set(question_lower.split())
            words_k = set(q_key.lower().split())
            common = words_q.intersection(words_k)
            # If high overlap, return the database answer
            if len(common) > 5 and len(common) / len(words_k) > 0.6:
                return answer

        # 3. Handle CNN specific questions (from user example)
        if "cnn" in question_lower:
            if "why" in question_lower or "choose" in question_lower:
                return "CNN (Convolutional Neural Network) is chosen for image classification because it preserves spatial structure. Unlike dense networks, CNNs use shared weights in convolution kernels, reducing parameters and automatically extracting hierarchy-invariant local features like edges, textures, and shapes."
            elif "architecture" in question_lower:
                return "The typical CNN architecture consists of input layers, convolutional layers (for feature extraction with filters), activation functions (like ReLU), pooling layers (like Max Pooling for downsampling and translational invariance), followed by fully connected dense layers and a softmax output layer for classification."
            else:
                return "CNN (Convolutional Neural Network) is a deep learning architecture designed for image processing and computer vision tasks. It automatically learns spatial features using convolution operations, kernels, pooling, and activation functions."

        if "overfitting" in question_lower:
            return "Overfitting happens when a machine learning model learns the details and noise of the training data too well, failing to generalize to new data. It can be prevented using techniques like dropout (random node deactivation), L1/L2 weight regularization, data augmentation, early stopping, and training on more diverse datasets."

        # 4. Generate dynamic answer using transformers Seq2Seq model
        if hasattr(self, 'model') and self.model and hasattr(self, 'tokenizer') and self.tokenizer:
            try:
                prompt = f"Provide a brief 2-3 sentence technical answer to: {question}"
                inputs = self.tokenizer(prompt, return_tensors="pt")
                outputs = self.model.generate(**inputs, max_length=150)
                ans = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
                if len(ans) > 20:
                    return ans
            except Exception as e:
                print(f"Transformers answer generation failed: {e}")

        # 5. Generic Category Fallbacks
        if category == "Project-Based":
            return f"{self.project_answer_prefix} For this specific project, describe the system components and how you solved issues like data processing and testing."
        elif category == "HR / Behavioral":
            return f"{self.hr_answer_prefix} Highlight your personal actions, communication skills, and the positive outcomes of your decision."
        else:
            # General Technical Fallback
            return f"This question queries concepts in software engineering. A comprehensive answer should define the concept, explain its core mechanics, list key advantages or use-cases, and describe potential constraints or alternative designs."

if __name__ == "__main__":
    generator = ReferenceAnswerGenerator()
    test_q = "What is the difference between a list and a tuple in Python, and when would you use each?"
    ans = generator.generate_answer(test_q, "Technical")
    print(f"Q: {test_q}\nA: {ans}\n")
    
    test_q2 = "Why did you choose CNN?"
    ans2 = generator.generate_answer(test_q2, "Technical")
    print(f"Q: {test_q2}\nA: {ans2}\n")
