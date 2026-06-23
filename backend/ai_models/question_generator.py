import random
import os

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class QuestionGenerator:
    """
    Generates tailored technical, project-based, and HR questions based on the candidate's resume content.
    """
    def __init__(self):
        self.model_name = "google/flan-t5-small"
        self.generator = None
        self.initialized_model = False
        
        # Expert question database for common technologies
        self.tech_question_db = {
            "python": [
                "What is the difference between a list and a tuple in Python, and when would you use each?",
                "Explain Python's Global Interpreter Lock (GIL) and how it affects multi-threaded applications.",
                "How do you manage memory and handle garbage collection in Python?",
                "What are decorators in Python, and how do they work?"
            ],
            "tensorflow": [
                "Explain the difference between eager execution and graph execution in TensorFlow.",
                "How does the tf.data API help in building efficient input pipelines in TensorFlow?",
                "What is overfitting, and how do you prevent it in TensorFlow using regularization or dropout?",
                "Explain the role of optimizers in training a neural network in TensorFlow."
            ],
            "pytorch": [
                "What is autograd in PyTorch and how does it facilitate backpropagation?",
                "Explain the difference between Dataset and DataLoader classes in PyTorch.",
                "How do you move tensors between CPU and GPU in PyTorch, and why is it important?",
                "Explain how PyTorch's dynamic computational graph differs from static computational graphs."
            ],
            "react": [
                "What is the Virtual DOM, and how does React use it to optimize rendering performance?",
                "Explain the difference between React state and props, and how data flows in a React app.",
                "What are React Hooks? Explain the use cases of useEffect and useMemo.",
                "How would you optimize a React application that is experiencing slow rendering times?"
            ],
            "fastapi": [
                "What are the key advantages of FastAPI compared to Flask or Django?",
                "How does FastAPI leverage Python type hints for data validation and documentation?",
                "Explain dependency injection in FastAPI and give a practical example.",
                "How do you handle asynchronous request routing and background tasks in FastAPI?"
            ],
            "javascript": [
                "Explain the difference between var, let, and const in JavaScript.",
                "What is the event loop in JavaScript and how does it handle asynchronous code execution?",
                "Explain promises and async/await syntax. How do they handle errors?",
                "What is a closure in JavaScript, and can you describe a practical use case?"
            ],
            "typescript": [
                "What are the main benefits of using TypeScript over JavaScript in large-scale applications?",
                "Explain the difference between an Interface and a Type Alias in TypeScript.",
                "What are generics in TypeScript and how do they help write reusable code?",
                "How does TypeScript's strict mode help catch errors during development?"
            ],
            "docker": [
                "What is the difference between a Docker container and a virtual machine?",
                "Explain the purpose of a Dockerfile, an Image, and a Container.",
                "What is multi-stage builds in Docker and how does it help reduce image sizes?",
                "How do you manage persistent data in Docker containers using volumes?"
            ],
            "kubernetes": [
                "What is a Pod in Kubernetes, and what is its relationship with container runtimes?",
                "Explain the difference between a Deployment and a Service in Kubernetes.",
                "What is a ConfigMap and a Secret in Kubernetes, and how are they used?",
                "How does Kubernetes handle horizontal pod autoscaling?"
            ],
            "aws": [
                "Explain the difference between AWS EC2, ECS, and AWS Lambda.",
                "What is an S3 bucket, and how do you secure access to files stored in it?",
                "Explain VPC (Virtual Private Cloud) and how it isolates resources in AWS.",
                "What is IAM (Identity and Access Management) and the principle of least privilege?"
            ],
            "mongodb": [
                "Explain the difference between SQL (relational) and NoSQL (document-based) databases like MongoDB.",
                "What is indexing in MongoDB and how does it improve query performance?",
                "How do you model one-to-many relationships in a MongoDB document design?",
                "What are aggregation pipelines in MongoDB and how do they work?"
            ],
            "postgresql": [
                "Explain the difference between INNER JOIN, LEFT JOIN, and outer joins in SQL.",
                "What are indexes, and what are the trade-offs of using too many indexes in PostgreSQL?",
                "Explain database normalization and why it is useful.",
                "How do you handle database transactions and ACID properties in PostgreSQL?"
            ]
        }

        # Project templates
        self.project_templates = [
            "For your project '{project}', why did you choose the specific architecture and tech stack?",
            "What was the most challenging technical hurdle you faced in '{project}', and how did you overcome it?",
            "How did you handle testing, deployment, or validation for '{project}'?",
            "If you had to rewrite '{project}' from scratch today, what design decisions or technologies would you change?"
        ]

        # HR templates
        self.hr_questions = [
            "Tell me about a time when you had to learn a new tool or technology quickly. How did you go about it?",
            "How do you handle disagreement within a technical project team or with a collaborator?",
            "Describe a project that failed or didn't meet expectations. What did you learn from it?",
            "How do you stay updated with the rapidly evolving trends in software engineering and Deep Learning?",
            "Why are you interested in this position, and how do your skills align with what you want to achieve next?"
        ]

    def _lazy_init_model(self):
        """
        Lazily initializes the HF transformer model if available.
        """
        if not self.initialized_model and TRANSFORMERS_AVAILABLE:
            try:
                # Use Seq2Seq pipeline with flan-t5-small
                self.generator = pipeline(
                    "text2text-generation",
                    model=self.model_name,
                    device=-1  # force CPU
                )
                self.initialized_model = True
            except Exception as e:
                print(f"Warning: Failed to load local question generator model: {e}. Falling back to rule-based engine.")
                self.initialized_model = True # set to True so we don't keep trying and failing

    def generate(self, resume_data: dict) -> list:
        """
        Generates 10 interview questions based on skills, projects, and technologies.
        - 5 Technical Questions
        - 3 Project-based Questions
        - 2 HR Questions
        """
        self._lazy_init_model()
        
        skills = resume_data.get("skills", [])
        projects = resume_data.get("projects", [])
        technologies = resume_data.get("technologies", [])
        
        # Combine skills and technologies for technical questions
        all_tech = list(set([s.lower() for s in skills] + [t.lower() for t in technologies]))
        
        # 1. Technical Questions (Goal: 5)
        tech_questions = []
        
        # Try to pull from DB first
        matched_keys = [k for k in self.tech_question_db.keys() if k in all_tech]
        random.shuffle(matched_keys)
        
        for key in matched_keys:
            db_questions = self.tech_question_db[key]
            # Pick a question not already selected
            for q in db_questions:
                if q not in tech_questions:
                    tech_questions.append(q)
                    break
            if len(tech_questions) >= 5:
                break
                
        # If we need more technical questions, generate generic tech questions or use HF model
        if len(tech_questions) < 5:
            # Fallback tech question templates
            remaining = 5 - len(tech_questions)
            generic_templates = [
                "Explain the core concepts and architecture of {tech}.",
                "What are the best practices for structuring code and managing state in {tech}?",
                "How does {tech} handle concurrency or performance optimization?",
                "What are the typical security considerations when working with {tech}?"
            ]
            
            # Select tech that weren't matched in database
            unmatched_tech = [t for t in all_tech if t not in self.tech_question_db]
            if not unmatched_tech:
                unmatched_tech = all_tech if all_tech else ["software engineering"]
                
            for i in range(remaining):
                tech = random.choice(unmatched_tech)
                template = random.choice(generic_templates)
                # Capitalize tech nicely
                tech_cap = tech.upper() if len(tech) <= 4 else tech.capitalize()
                q = template.format(tech=tech_cap)
                if q not in tech_questions:
                    tech_questions.append(q)
                    
        # 2. Project-based Questions (Goal: 3)
        proj_questions = []
        if projects:
            for i in range(3):
                proj = projects[i % len(projects)]
                template = self.project_templates[i % len(self.project_templates)]
                proj_questions.append(template.format(project=proj))
        else:
            # If no projects, add generic engineering design questions
            proj_questions = [
                "Explain your process for translating a system requirement into an architectural design.",
                "How do you handle software scalability and database indexing in your project designs?",
                "Describe a project architecture you designed recently and why you made those decisions."
            ]

        # 3. HR Questions (Goal: 2)
        hr_questions = random.sample(self.hr_questions, 2)
        
        # Combine all to 10 questions
        questions = tech_questions[:5] + proj_questions[:3] + hr_questions[:2]
        
        # If we have the transformer model loaded, we can use it to rephrase or add a unique twist to a few questions
        if self.generator:
            try:
                # Rephrase one question to demonstrate deep learning generation
                idx_to_rephrase = 0
                prompt = f"Rewrite this interview question to be more professional: {questions[idx_to_rephrase]}"
                res = self.generator(prompt, max_length=50, num_return_sequences=1)
                new_q = res[0]['generated_text'].strip()
                # Ensure it ended up as a proper question and is not empty
                if new_q and new_q.endswith('?') and len(new_q) > 15:
                    questions[idx_to_rephrase] = new_q
            except Exception as e:
                print(f"Failed to rephrase question using Flan-T5: {e}")
                
        # Format list with category info for backend management
        result = []
        for i, q in enumerate(questions):
            if i < 5:
                category = "Technical"
            elif i < 8:
                category = "Project-Based"
            else:
                category = "HR / Behavioral"
                
            result.append({
                "id": i + 1,
                "question": q,
                "category": category
            })
            
        return result

if __name__ == "__main__":
    generator = QuestionGenerator()
    test_data = {
        "skills": ["Python", "TensorFlow", "React"],
        "projects": ["Plant Disease Detection"],
        "technologies": ["Git", "Docker"]
    }
    qs = generator.generate(test_data)
    for q in qs:
        print(f"[{q['category']}] {q['question']}")
