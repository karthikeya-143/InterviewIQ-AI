import os
import re
import pdfplumber

class ResumeParser:
    """
    Service for parsing PDF resumes and extracting structured data:
    skills, projects, technologies, education, and certifications.
    """
    def __init__(self):
        # Predefined common technical skills keywords
        self.skills_db = [
            # Programming Languages
            "python", "javascript", "typescript", "c++", "c#", "java", "ruby", "go", "rust", "php", "swift", "kotlin", "sql", "r", "html", "css",
            # Frameworks & Libraries
            "react", "angular", "vue", "next.js", "vite", "fastapi", "django", "flask", "express", "node.js", "node", "spring boot", "laravel",
            "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "opencv", "numpy", "pandas", "nltk", "spacy", "huggingface", "transformers",
            # DevOps & Cloud
            "docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "git", "github", "gitlab", "terraform", "ansible",
            # Databases
            "mongodb", "postgresql", "mysql", "redis", "sqlite", "oracle", "cassandra"
        ]

        # Predefined technology keywords (non-language/framework tools/platforms)
        self.tech_db = [
            "git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "unix", "nginx", "apache", "heroku", "netlify", "vercel",
            "firebase", "supabase", "graphql", "rest api", "grpc", "jira", "confluence", "slack", "postman", "swagger"
        ]

        # Common education markers
        self.education_degrees = [
            "b.tech", "b.e", "b.s", "b.sc", "m.tech", "m.e", "m.s", "m.sc", "ph.d", "bachelor", "master", "doctorate", "diploma",
            "computer science", "information technology", "electrical engineering", "data science", "artificial intelligence"
        ]

    def extract_text(self, pdf_path: str) -> str:
        """
        Extracts raw text from a PDF file using pdfplumber.
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            # Raise exception so caller can handle validation failure
            raise ValueError(f"Could not parse PDF file: {str(e)}")
        
        return text

    def parse(self, pdf_path: str) -> dict:
        """
        Main parser function that orchestrates the extraction process.
        """
        raw_text = self.extract_text(pdf_path)
        
        # Lowercase text for matching
        text_lower = raw_text.lower()
        
        # 1. Extract Skills
        skills = self._extract_skills(text_lower)
        
        # 2. Extract Technologies
        technologies = self._extract_technologies(text_lower, skills)
        
        # 3. Extract Education
        education = self._extract_education(raw_text)
        
        # 4. Extract Certifications
        certifications = self._extract_certifications(raw_text)
        
        # 5. Extract Projects
        projects = self._extract_projects(raw_text)
        
        return {
            "skills": skills,
            "projects": projects,
            "technologies": technologies,
            "education": education,
            "certifications": certifications,
            "raw_text": raw_text[:5000] # store preview of text
        }

    def _extract_skills(self, text_lower: str) -> list:
        found_skills = set()
        for skill in self.skills_db:
            # Word boundary check, specifically handling characters like C++ or .NET
            pattern = r'\b' + re.escape(skill) + r'\b'
            if skill in ["c++", "c#", "next.js", "node.js"]:
                # Custom pattern for c++/c#/next.js since \b doesn't match boundaries with non-alphanumeric chars
                pattern = r'(?:^|[\s,;:\(\)])' + re.escape(skill) + r'(?:$|[\s,;:\(\)])'
                
            if re.search(pattern, text_lower):
                # Standardize capitalization
                found_skills.add(self._standardize_name(skill))
        return sorted(list(found_skills))

    def _extract_technologies(self, text_lower: str, skills: list) -> list:
        found_techs = set()
        for tech in self.tech_db:
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, text_lower):
                found_techs.add(self._standardize_name(tech))
        
        # Add some skills to technologies if they fit best (e.g., Docker, AWS, Git)
        for skill in skills:
            if skill.lower() in self.tech_db:
                found_techs.add(skill)
                
        return sorted(list(found_techs))

    def _extract_education(self, raw_text: str) -> list:
        education_entries = []
        lines = raw_text.split('\n')
        
        # Simple line-by-line scanning for degrees or institute details
        for line in lines:
            line_lower = line.lower()
            # If line contains major degree words
            found_degree = False
            for degree in ["b.tech", "b.e.", "b.e", "b.s.", "b.s", "b.sc", "m.tech", "m.e.", "m.s.", "m.s", "m.sc", "ph.d", "bachelor", "master", "phd"]:
                if re.search(r'\b' + re.escape(degree) + r'\b', line_lower):
                    found_degree = True
                    break
            
            if found_degree or any(kw in line_lower for kw in ["university", "college", "institute", "school"]):
                cleaned_line = line.strip()
                if len(cleaned_line) > 5 and len(cleaned_line) < 150:
                    education_entries.append(cleaned_line)
                    
        # Dedup keeping order
        seen = set()
        unique_edu = []
        for edu in education_entries:
            if edu.lower() not in seen:
                seen.add(edu.lower())
                unique_edu.append(edu)
                
        # If nothing found, return a default parsing placeholder
        if not unique_edu:
            # Look for lines containing "Education" and grab the next 2 lines
            for i, line in enumerate(lines):
                if "education" in line.lower() and i + 1 < len(lines):
                    edu_line = lines[i+1].strip()
                    if edu_line:
                        unique_edu.append(edu_line)
                        break
                        
        return unique_edu[:3] # Limit to top 3

    def _extract_certifications(self, raw_text: str) -> list:
        certs = []
        lines = raw_text.split('\n')
        in_cert_section = False
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            # Detect section start
            if any(keyword in line_lower for keyword in ["certification", "certifications", "licenses & certifications"]):
                in_cert_section = True
                continue
            
            # Detect another section start, ending certifications
            if in_cert_section and any(keyword in line_lower for keyword in ["skills", "education", "experience", "projects", "employment"]):
                in_cert_section = False
                break
                
            if in_cert_section:
                cleaned = line.strip()
                if cleaned and len(cleaned) > 3 and len(cleaned) < 120:
                    certs.append(cleaned)
                    
        # Fallback keyword matching
        if not certs:
            cert_keywords = ["certified", "aws", "google cloud", "azure", "coursera", "udemy", "certification"]
            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in cert_keywords) and not any(deg in line_lower for deg in ["degree", "bachelor", "master"]):
                    cleaned = line.strip()
                    if len(cleaned) > 5 and len(cleaned) < 100:
                        # Clean bullet points
                        cleaned = re.sub(r'^[\s•\-*]+', '', cleaned)
                        certs.append(cleaned)
                        
        seen = set()
        unique_certs = []
        for cert in certs:
            if cert.lower() not in seen:
                seen.add(cert.lower())
                unique_certs.append(cert)
                
        return unique_certs[:5]

    def _extract_projects(self, raw_text: str) -> list:
        projects = []
        lines = raw_text.split('\n')
        in_project_section = False
        current_project = ""
        
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            
            # Detect section start
            if any(keyword in line_lower for keyword in ["projects", "personal projects", "academic projects", "key projects"]):
                in_project_section = True
                continue
                
            # Detect section end
            if in_project_section and any(keyword in line_lower for keyword in ["skills", "education", "experience", "certifications", "employment", "hobbies"]):
                in_project_section = False
                break
                
            if in_project_section:
                cleaned = line.strip()
                if cleaned:
                    # If line starts with a bullet or looks like a title
                    if re.match(r'^[\s•\-*#\d\.]+', cleaned) or (len(cleaned) < 50 and not cleaned.endswith('.')):
                        if current_project:
                            projects.append(current_project)
                        # Clean the bullet points from title
                        current_project = re.sub(r'^[\s•\-*#\d\.\)]+', '', cleaned).strip()
                    else:
                        if current_project:
                            # Append details to current project
                            current_project += " - " + cleaned
                        else:
                            current_project = cleaned
                            
        if current_project:
            projects.append(current_project)
            
        # Clean and format project lines
        cleaned_projects = []
        for proj in projects:
            p_clean = proj.strip()
            if len(p_clean) > 5 and len(p_clean) < 250:
                cleaned_projects.append(p_clean)
                
        # Heuristic fallback if section parser missed
        if not cleaned_projects:
            # Look for lines containing tech skills and action verbs
            action_verbs = ["built", "developed", "created", "designed", "implemented", "worked on"]
            for line in lines:
                line_lower = line.lower()
                if any(verb in line_lower for verb in action_verbs) and len(line) < 150:
                    cleaned = re.sub(r'^[\s•\-*]+', '', line).strip()
                    cleaned_projects.append(cleaned)
                    
        seen = set()
        unique_proj = []
        for p in cleaned_projects:
            # Keep first 40-50 characters as project name
            short_name = p.split(' - ')[0]
            if short_name.lower() not in seen:
                seen.add(short_name.lower())
                unique_proj.append(short_name)
                
        return unique_proj[:4]

    def _standardize_name(self, name: str) -> str:
        """
        Standardizes capitalization of tech skills.
        """
        mapping = {
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "c++": "C++", "c#": "C#", "java": "Java", "ruby": "Ruby", "go": "Go",
            "rust": "Rust", "php": "PHP", "swift": "Swift", "kotlin": "Kotlin",
            "sql": "SQL", "r": "R", "html": "HTML", "css": "CSS", "react": "React",
            "angular": "Angular", "vue": "Vue", "next.js": "Next.js", "vite": "Vite",
            "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "express": "Express",
            "node.js": "Node.js", "node": "Node.js", "spring boot": "Spring Boot",
            "laravel": "Laravel", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
            "keras": "Keras", "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
            "opencv": "OpenCV", "numpy": "NumPy", "pandas": "Pandas", "nltk": "NLTK",
            "spacy": "spaCy", "huggingface": "Hugging Face", "transformers": "Transformers",
            "docker": "Docker", "kubernetes": "Kubernetes", "aws": "AWS", "gcp": "GCP",
            "azure": "Azure", "jenkins": "Jenkins", "git": "Git", "github": "GitHub",
            "gitlab": "GitLab", "terraform": "Terraform", "ansible": "Ansible",
            "mongodb": "MongoDB", "postgresql": "PostgreSQL", "mysql": "MySQL",
            "redis": "Redis", "sqlite": "SQLite", "oracle": "Oracle", "cassandra": "Cassandra",
            "linux": "Linux", "unix": "Unix", "nginx": "Nginx", "apache": "Apache",
            "heroku": "Heroku", "netlify": "Netlify", "vercel": "Vercel",
            "firebase": "Firebase", "supabase": "Supabase", "graphql": "GraphQL",
            "rest api": "REST API", "grpc": "gRPC", "jira": "Jira", "confluence": "Confluence",
            "slack": "Slack", "postman": "Postman", "swagger": "Swagger"
        }
        return mapping.get(name.lower(), name.capitalize())

if __name__ == "__main__":
    parser = ResumeParser()
    print("ResumeParser initialized successfully!")
